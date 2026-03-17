import os
import pickle
import json
import numpy as np
import pandas as pd
from datetime import timedelta
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import shap
import warnings
warnings.filterwarnings('ignore')

from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Complaint


class Command(BaseCommand):
    help = 'Train XGBoost ML model with SHAP explainability for risk scoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--synthetic',
            action='store_true',
            help='Use synthetic data instead of real data'
        )

    def handle(self, *args, **options):
        using_synthetic = options['synthetic']
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write("PureCheck ML Model Training (with SHAP Explainability)")
        self.stdout.write("="*70)
        
        # Load data
        self.stdout.write("\n[Training] Loading data...")
        if using_synthetic:
            df = self.generate_synthetic_data(500)
            data_source = "synthetic"
        else:
            df = self.extract_features_from_db()
            if df is None or len(df) < 20:
                self.stdout.write("[Training] Insufficient real data, using synthetic...")
                df = self.generate_synthetic_data(500)
                data_source = "synthetic"
            else:
                data_source = "real"
        
        self.stdout.write(f"[Training] Data source: {data_source.upper()}")
        self.stdout.write(f"[Training] Samples: {len(df)}")
        
        # Prepare data
        feature_cols = [col for col in df.columns if col not in ['risk_score', 'city', 'food_item']]
        X = df[feature_cols]
        y = df['risk_score']
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )
        
        self.stdout.write(f"[Training] Train: {len(X_train)}, Test: {len(X_test)}")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        self.stdout.write("\n[Training] Training XGBoost...")
        model = XGBRegressor(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='reg:squarederror',
            random_state=42,
            verbosity=0
        )
        model.fit(X_train_scaled, y_train, eval_set=[(X_test_scaled, y_test)], verbose=False)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        mape = mean_absolute_percentage_error(y_test, y_pred)
        
        self.stdout.write(f"\n[Training] Model Performance:")
        self.stdout.write(f"  MAE:  {mae:.4f}")
        self.stdout.write(f"  RMSE: {rmse:.4f}")
        self.stdout.write(f"  MAPE: {mape:.4f}")
        self.stdout.write(f"  R²:   {r2:.4f}")
        
        # Compute SHAP
        self.stdout.write("\n[Training] Computing SHAP explainer...")
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_test_scaled)
        feature_importance = np.abs(shap_values).mean(axis=0)
        
        self.stdout.write(f"\n[Training] Feature Importance:")
        for i, (name, imp) in enumerate(sorted(zip(feature_cols, feature_importance), key=lambda x: x[1], reverse=True)):
            self.stdout.write(f"  {i+1}. {name:<20s}: {imp:.4f}")
        
        # Save models
        self.stdout.write("\n[Training] Saving models...")
        # Path: backend/ml/saved_models
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        model_dir = os.path.join(backend_dir, 'ml', 'saved_models')
        os.makedirs(model_dir, exist_ok=True)
        self.stdout.write(f"[Training] Saving to: {model_dir}")
        
        with open(os.path.join(model_dir, 'risk_model.pkl'), 'wb') as f:
            pickle.dump(model, f)
        self.stdout.write("  ✓ Model saved")
        
        with open(os.path.join(model_dir, 'feature_scaler.pkl'), 'wb') as f:
            pickle.dump(scaler, f)
        self.stdout.write("  ✓ Scaler saved")
        
        with open(os.path.join(model_dir, 'shap_explainer.pkl'), 'wb') as f:
            pickle.dump(explainer, f)
        self.stdout.write("  ✓ SHAP explainer saved")
        
        metadata = {
            'feature_names': feature_cols,
            'data_source': data_source,
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'timestamp': str(timezone.now()),
            'version': '2.0-shap',
            'mae': float(mae),
            'rmse': float(rmse),
            'r2': float(r2)
        }
        with open(os.path.join(model_dir, 'model_metadata.json'), 'w') as f:
            json.dump(metadata, f, indent=2)
        self.stdout.write("  ✓ Metadata saved")
        
        self.stdout.write("\n" + "="*70)
        self.stdout.write("✓ Training Complete!")
        self.stdout.write("="*70 + "\n")

    def extract_features_from_db(self):
        """Extract real features from database."""
        try:
            complaints = Complaint.objects.all()
            if complaints.count() < 10:
                return None
            
            self.stdout.write(f"[Training] Found {complaints.count()} complaints in DB")
            data = []
            
            cities = complaints.values_list('city', flat=True).distinct()
            foods = complaints.values_list('food_item', flat=True).distinct()
            
            for city in cities:
                for food in foods:
                    city_food = complaints.filter(city=city, food_item=food)
                    if not city_food.exists():
                        continue
                    
                    severity_vals = list(city_food.values_list('severity', flat=True))
                    severity_avg = np.mean(severity_vals) if severity_vals else 2.5
                    
                    month = int(city_food.latest('created_at').created_at.strftime('%m'))
                    season_flag = 1 if month in [10, 11, 1, 4] else 0
                    
                    source_scores = {'FSSAI': 1.0, 'NEWS': 0.8, 'CITIZEN': 0.5}
                    source_weights = [source_scores.get(c.source, 0.5) for c in city_food]
                    source_weight = np.mean(source_weights) if source_weights else 0.5
                    
                    recency_days = [(timezone.now() - c.created_at).days for c in city_food]
                    recency_weight = 10 / (1 + np.mean(recency_days) / 10) if recency_days else 0
                    
                    trend_score = 0.5
                    adulterant_count = city_food.values('adulterant').distinct().count()
                    
                    risk_score = (
                        20 + city_food.count() * 1.5 + severity_avg * 8 +
                        season_flag * 10 + source_weight * 15 +
                        recency_weight * 3 + trend_score * 20 + adulterant_count * 5
                    )
                    risk_score = max(0, min(100, risk_score))
                    
                    data.append({
                        'complaint_count': float(city_food.count()),
                        'severity_avg': severity_avg,
                        'season_flag': float(season_flag),
                        'source_weight': source_weight,
                        'recency_weight': recency_weight,
                        'trend_score': trend_score,
                        'adulterant_count': float(adulterant_count),
                        'risk_score': risk_score
                    })
            
            if len(data) < 20:
                return None
            
            self.stdout.write(f"[Training] Extracted {len(data)} city-food combinations")
            return pd.DataFrame(data)
        except Exception as e:
            self.stdout.write(f"[Training] Error extracting DB data: {e}")
            return None

    def generate_synthetic_data(self, n_samples=500):
        """Generate synthetic training data."""
        np.random.seed(42)
        data = []
        
        for _ in range(n_samples):
            complaint_count = np.random.exponential(5)
            complaint_count = min(50, complaint_count)
            severity_avg = np.random.uniform(1, 5)
            season_flag = np.random.choice([0, 1], p=[0.7, 0.3])
            source_weight = np.random.beta(2, 5)
            recency_weight = np.random.exponential(3)
            recency_weight = min(20, recency_weight)
            trend_score = np.random.uniform(0, 1)
            adulterant_count = np.random.randint(1, 6)
            
            risk_score = (
                25 + complaint_count * 1.5 + severity_avg * 8 +
                season_flag * 10 + source_weight * 15 +
                recency_weight * 3 + trend_score * 20 + adulterant_count * 5
            )
            risk_score += np.random.normal(0, 5)
            risk_score = max(0, min(100, risk_score))
            
            data.append({
                'complaint_count': complaint_count,
                'severity_avg': severity_avg,
                'season_flag': season_flag,
                'source_weight': source_weight,
                'recency_weight': recency_weight,
                'trend_score': trend_score,
                'adulterant_count': float(adulterant_count),
                'risk_score': risk_score
            })
        
        self.stdout.write(f"[Training] Generated {n_samples} synthetic samples")
        return pd.DataFrame(data)
