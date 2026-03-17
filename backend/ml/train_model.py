import os
import sys
import pickle
import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import shap
import warnings
warnings.filterwarnings('ignore')

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from core.models import Complaint, RiskScore, AuditLog
from django.utils import timezone


def extract_features_from_complaints(complaints_qs, lookback_days=90):
    """
    Extract real features from complaint database.
    
    Args:
        complaints_qs: QuerySet of Complaint objects
        lookback_days: Days to look back for recency calculation
    
    Returns:
        DataFrame with engineered features
    """
    data = []
    cutoff_date = timezone.now() - timedelta(days=lookback_days)
    
    # Group complaints by city-food combination
    cities = complaints_qs.values_list('city', flat=True).distinct()
    foods = complaints_qs.values_list('food_item', flat=True).distinct()
    
    for city in cities:
        for food in foods:
            city_food_complaints = complaints_qs.filter(city=city, food_item=food)
            
            if not city_food_complaints.exists():
                continue
            
            all_complaints = city_food_complaints
            recent_complaints = city_food_complaints.filter(created_at__gte=cutoff_date)
            
            # Feature 1: Complaint count (absolute)
            complaint_count = all_complaints.count()
            
            # Feature 2: Severity average
            severity_values = list(all_complaints.values_list('severity', flat=True))
            severity_avg = np.mean(severity_values) if severity_values else 2.5
            
            # Feature 3: Season flag (1 if Oct/Nov/Jan/Apr for India harvest/festival seasons)
            latest_month = int(all_complaints.latest('created_at').created_at.strftime('%m'))
            season_flag = 1 if latest_month in [10, 11, 1, 4] else 0
            
            # Feature 4: Source credibility weight (FSSAI=1.0, NEWS=0.8, CITIZEN=0.5)
            source_scores = {
                'FSSAI': 1.0,
                'NEWS': 0.8,
                'CITIZEN': 0.5
            }
            source_weights = [source_scores.get(c.source, 0.5) for c in all_complaints]
            source_weight = np.mean(source_weights) if source_weights else 0.5
            
            # Feature 5: Recency weight (recent complaints matter more)
            recency_days = [(timezone.now() - c.created_at).days for c in all_complaints]
            if recency_days:
                # Inverse: more recent = higher weight
                recency_weight = 10 / (1 + np.mean(recency_days) / 10)
            else:
                recency_weight = 0
            
            # Feature 6: Trend (increase/decrease in recent complaints)
            trend_score = recent_complaints.count() / max(1, all_complaints.count())
            
            # Feature 7: Adulterant diversity (# of different adulterants)
            adulterant_count = all_complaints.values('adulterant').distinct().count()
            
            # Target: Calculate empirical risk score from complaints
            # Formula: base score + weighted impact of each feature
            base_risk = 20
            target_risk_score = (
                base_risk +
                complaint_count * 1.5 +
                severity_avg * 8 +
                season_flag * 10 +
                source_weight * 15 +
                recency_weight * 3 +
                trend_score * 20 +
                adulterant_count * 5
            )
            target_risk_score = max(0, min(100, target_risk_score))
            
            data.append({
                'city': city,
                'food_item': food,
                'complaint_count': complaint_count,
                'severity_avg': severity_avg,
                'season_flag': season_flag,
                'source_weight': source_weight,
                'recency_weight': recency_weight,
                'trend_score': trend_score,
                'adulterant_count': adulterant_count,
                'risk_score': target_risk_score
            })
    
    return pd.DataFrame(data)


def generate_synthetic_data(n_samples=500):
    """
    Generate synthetic training data with realistic distributions.
    
    Args:
        n_samples: Number of synthetic samples to generate
    
    Returns:
        DataFrame with features and labels
    """
    np.random.seed(42)
    
    cities = ['Trichy', 'Coimbatore', 'Chennai', 'Madurai', 'Salem']
    foods = ['milk', 'oil', 'rice', 'turmeric', 'sweets', 'ghee', 'paneer', 'vegetables']
    months = [f'{2024}-{m:02d}' for m in range(1, 13)] + [f'{2025}-{m:02d}' for m in range(1, 13)]
    
    data = []
    
    for _ in range(n_samples):
        # Feature 1: Complaint count (0-50, skewed towards low)
        complaint_count = np.random.exponential(5)
        complaint_count = min(50, complaint_count)
        
        # Feature 2: Severity average (1-5)
        severity_avg = np.random.uniform(1, 5)
        
        # Feature 3: Season flag (1 if Oct/Nov/Jan/Apr, else 0)
        month = np.random.choice(months)
        month_num = int(month.split('-')[1])
        season_flag = 1 if month_num in [10, 11, 1, 4] else 0
        
        # Feature 4: Source weight (0-1, weighted towards credible sources)
        source_weight = np.random.beta(2, 5)  # Biased towards lower values (CITIZEN reports)
        
        # Feature 5: Recency weight (0-20+, recent complaints matter more)
        recency_weight = np.random.exponential(3)
        recency_weight = min(20, recency_weight)
        
        # Generate label based on features
        # Higher complaint count, higher severity, festival season, credible source → higher risk
        base_risk = 25
        risk_score = (
            base_risk +
            complaint_count * 0.8 +
            severity_avg * 6 +
            season_flag * 15 +
            source_weight * 20 +
            recency_weight * 2
        )
        
        # Add noise
        risk_score += np.random.normal(0, 5)
        risk_score = max(0, min(100, risk_score))
        
        data.append({
            'complaint_count': complaint_count,
            'severity_avg': severity_avg,
            'season_flag': season_flag,
            'source_weight': source_weight,
            'recency_weight': recency_weight,
            'risk_score': risk_score
        })
    
    return pd.DataFrame(data)


def generate_synthetic_data(n_samples=500):
    """
    Generate synthetic training data with realistic distributions.
    Falls back to this if real data is insufficient.
    
    Args:
        n_samples: Number of synthetic samples to generate
    
    Returns:
        DataFrame with features and labels
    """
    np.random.seed(42)
    
    data = []
    
    for _ in range(n_samples):
        # Feature 1: Complaint count (0-50, skewed towards low)
        complaint_count = np.random.exponential(5)
        complaint_count = min(50, complaint_count)
        
        # Feature 2: Severity average (1-5)
        severity_avg = np.random.uniform(1, 5)
        
        # Feature 3: Season flag (1 if Oct/Nov/Jan/Apr, else 0)
        season_flag = np.random.choice([0, 1], p=[0.7, 0.3])
        
        # Feature 4: Source weight (0-1, weighted towards credible sources)
        source_weight = np.random.beta(2, 5)
        
        # Feature 5: Recency weight (0-20+, recent complaints matter more)
        recency_weight = np.random.exponential(3)
        recency_weight = min(20, recency_weight)
        
        # Feature 6: Trend score (0-1)
        trend_score = np.random.uniform(0, 1)
        
        # Feature 7: Adulterant count (1-5)
        adulterant_count = np.random.randint(1, 6)
        
        # Generate label based on features
        base_risk = 25
        risk_score = (
            base_risk +
            complaint_count * 1.5 +
            severity_avg * 8 +
            season_flag * 10 +
            source_weight * 15 +
            recency_weight * 3 +
            trend_score * 20 +
            adulterant_count * 5
        )
        
        # Add noise
        risk_score += np.random.normal(0, 5)
        risk_score = max(0, min(100, risk_score))
        
        data.append({
            'complaint_count': complaint_count,
            'severity_avg': severity_avg,
            'season_flag': season_flag,
            'source_weight': source_weight,
            'recency_weight': recency_weight,
            'trend_score': trend_score,
            'adulterant_count': adulterant_count,
            'risk_score': risk_score
        })
    
    return pd.DataFrame(data)


def train_xgboost_model_with_shap(X, y, X_test, y_test):
    """
    Train XGBoost model and compute SHAP explainer.
    
    Args:
        X: Training features
        y: Training labels
        X_test: Test features
        y_test: Test labels
    
    Returns:
        Tuple of (trained_model, shap_explainer, scaler, feature_names)
    """
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model on scaled data
    model = XGBRegressor(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror',
        random_state=42,
        verbosity=0,
        eval_metric='mae'
    )
    
    model.fit(X_scaled, y, eval_set=[(X_test_scaled, y_test)], verbose=False)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    mape = mean_absolute_percentage_error(y_test, y_pred)
    
    print("\n" + "="*70)
    print("XGBoost Model Training Complete (with SHAP Explainability)")
    print("="*70)
    print(f"  Samples: {len(X)} training, {len(X_test)} testing")
    print(f"\nTest Set Performance Metrics:")
    print(f"  MAE (Mean Absolute Error):      {mae:.4f}")
    print(f"  RMSE (Root Mean Squared Error): {rmse:.4f}")
    print(f"  MAPE (Mean Absolute % Error):   {mape:.4f}")
    print(f"  R² Score:                       {r2:.4f}")
    
    # Compute SHAP explainer
    print(f"\nComputing SHAP explainer (this may take a moment)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test_scaled)
    
    # Feature importance from SHAP
    feature_importance = np.abs(shap_values).mean(axis=0)
    
    print(f"\nFeature Importance (from SHAP values):")
    feature_names = X.columns.tolist()
    for i, (name, importance) in enumerate(sorted(zip(feature_names, feature_importance), key=lambda x: x[1], reverse=True)):
        print(f"  {i+1}. {name:<20s}: {importance:.4f}")
    
    print("="*70 + "\n")
    
    return model, explainer, scaler, feature_names


def compute_confidence_score(prediction, y_train):
    """
    Compute confidence score based on prediction and training distribution.
    
    Args:
        prediction: Model prediction value
        y_train: Training labels for distribution analysis
    
    Returns:
        Confidence score 0.0-1.0
    """
    train_std = np.std(y_train)
    train_mean = np.mean(y_train)
    
    # Confidence decreases as prediction moves away from training distribution center
    z_score = abs(prediction - train_mean) / (train_std + 1e-6)
    confidence = 1.0 / (1.0 + z_score * 0.1)  # Sigmoid-like function
    
    return max(0.0, min(1.0, confidence))


def main():
    """Main entry point for training the model with SHAP explainability."""
    print("\n" + "="*70)
    print("PureCheck ML Model Training Pipeline (v2 with SHAP)")
    print("="*70)
    
    # Step 1: Try real data, fallback to synthetic
    print("\n[Training] Step 1: Loading training data...")
    try:
        # Try to get real data from database
        all_complaints = Complaint.objects.all()
        
        if all_complaints.count() >= 20:
            print(f"[Training] Found {all_complaints.count()} complaints in database")
            print("[Training] Extracting features from real complaint data...")
            df = extract_features_from_complaints(all_complaints, lookback_days=90)
            
            if len(df) >= 20:
                print(f"[Training] Extracted {len(df)} city-food combinations from real data")
                data_source = "real"
            else:
                print(f"[Training] Only {len(df)} combinations found, using synthetic data instead...")
                df = generate_synthetic_data(n_samples=500)
                data_source = "synthetic"
        else:
            print(f"[Training] Only {all_complaints.count()} complaints found, using synthetic data...")
            df = generate_synthetic_data(n_samples=500)
            data_source = "synthetic"
    except Exception as e:
        print(f"[Training] Error loading real data: {e}")
        print("[Training] Falling back to synthetic data...")
        df = generate_synthetic_data(n_samples=500)
        data_source = "synthetic"
    
    print(f"[Training] Data source: {data_source.upper()}")
    print(f"[Training] Total samples: {len(df)}")
    print(f"[Training] Features: {[c for c in df.columns if c != 'risk_score']}")
    
    # Step 2: Prepare data
    print("\n[Training] Step 2: Preparing training/test split...")
    
    feature_cols = [col for col in df.columns if col not in ['risk_score', 'city', 'food_item']]
    X = df[feature_cols]
    y = df['risk_score']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )
    
    print(f"[Training] Training set: {len(X_train)} samples")
    print(f"[Training] Test set: {len(X_test)} samples")
    
    # Step 3: Train model with SHAP
    print("\n[Training] Step 3: Training XGBoost model with SHAP...")
    model, explainer, scaler, feature_names = train_xgboost_model_with_shap(
        X_train, y_train, X_test, y_test
    )
    
    # Step 4: Save model, scaler, and explainer
    print("[Training] Step 4: Saving models and explainer...")
    model_dir = os.path.dirname(__file__)
    saved_models_dir = os.path.join(model_dir, 'saved_models')
    os.makedirs(saved_models_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(saved_models_dir, 'risk_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"  ✓ Saved model: {model_path}")
    
    # Save scaler
    scaler_path = os.path.join(saved_models_dir, 'feature_scaler.pkl')
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"  ✓ Saved scaler: {scaler_path}")
    
    # Save explainer
    explainer_path = os.path.join(saved_models_dir, 'shap_explainer.pkl')
    with open(explainer_path, 'wb') as f:
        pickle.dump(explainer, f)
    print(f"  ✓ Saved SHAP explainer: {explainer_path}")
    
    # Save metadata
    metadata = {
        'feature_names': feature_names,
        'data_source': data_source,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'timestamp': str(timezone.now()),
        'version': '2.0-shap'
    }
    metadata_path = os.path.join(saved_models_dir, 'model_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"  ✓ Saved metadata: {metadata_path}")
    
    print("\n" + "="*70)
    print("Training Complete! Model ready for production risk scoring.")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
