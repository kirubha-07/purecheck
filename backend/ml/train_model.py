import os
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


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


def train_xgboost_model(df):
    """
    Train XGBoost model on the dataset.
    
    Args:
        df: DataFrame with features and 'risk_score' label
    
    Returns:
        Trained XGBRegressor model
    """
    X = df[['complaint_count', 'severity_avg', 'season_flag', 'source_weight', 'recency_weight']]
    y = df['risk_score']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    model = XGBRegressor(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        objective='reg:squarederror',
        random_state=42,
        verbosity=0
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print("\n" + "="*60)
    print("XGBoost Model Training Complete")
    print("="*60)
    print(f"Test Set Performance:")
    print(f"  MAE (Mean Absolute Error): {mae:.4f}")
    print(f"  RMSE (Root Mean Squared Error): {rmse:.4f}")
    print(f"  R² Score: {r2:.4f}")
    print("="*60 + "\n")
    
    return model


def main():
    """Main entry point for training the model."""
    print("\n" + "="*60)
    print("PureCheck ML Model Training Pipeline")
    print("="*60)
    
    # Step 1: Generate synthetic data
    print("\n[Training] Step 1: Generating synthetic data...")
    df = generate_synthetic_data(n_samples=500)
    print(f"[Training] Generated {len(df)} synthetic samples")
    print(f"[Training] Features: {list(df.columns[:-1])}")
    print(f"[Training] Target: risk_score (0-100)")
    
    # Step 2: Train model
    print("\n[Training] Step 2: Training XGBoost model...")
    model = train_xgboost_model(df)
    
    # Step 3: Save model
    print("[Training] Step 3: Saving model...")
    model_dir = os.path.dirname(__file__)
    saved_models_dir = os.path.join(model_dir, 'saved_models')
    os.makedirs(saved_models_dir, exist_ok=True)
    
    model_path = os.path.join(saved_models_dir, 'risk_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"[Training] Model saved to: {model_path}")
    
    # Step 4: Save dataset for reference
    csv_path = os.path.join(saved_models_dir, 'training_data.csv')
    df.to_csv(csv_path, index=False)
    print(f"[Training] Training data saved to: {csv_path}")
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
