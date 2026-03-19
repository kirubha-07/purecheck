import os
import pickle
import json
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import numpy as np
from django.utils import timezone
from django.db.models import Avg, Count
from core.models import Complaint, RiskScore


class RiskScorerAgent:
    """
    Calculate risk scores for food items in a city using XGBoost model
    with SHAP explanability and confidence scores.
    Falls back to weighted formula if model unavailable.
    """
    
    def __init__(self):
        """Initialize with ML model, scaler, and SHAP explainer."""
        self.model = self._load_model()
        self.scaler = self._load_scaler()
        self.shap_explainer = self._load_shap_explainer()
        self.metadata = self._load_metadata()
        self.festival_months = {'10', '11', '01', '04'}  # Oct, Nov, Jan, Apr
        self.feature_names = None
        if self.metadata:
            self.feature_names = self.metadata.get('feature_names')
    
    def _load_model(self):
        """Load XGBoost model from disk, return None if not available."""
        try:
            model_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'ml',
                'saved_models',
                'risk_model.pkl'
            )
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                print("[RiskScorer] [OK] Loaded XGBoost model")
                return model
        except Exception as e:
            print(f"[RiskScorer] Could not load model: {e}")
        
        return None
    
    def _load_scaler(self):
        """Load feature scaler from disk."""
        try:
            scaler_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'ml',
                'saved_models',
                'feature_scaler.pkl'
            )
            if os.path.exists(scaler_path):
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                print("[RiskScorer] [OK] Loaded feature scaler")
                return scaler
        except Exception as e:
            print(f"[RiskScorer] Could not load scaler: {e}")
        
        return None
    
    def _load_shap_explainer(self):
        """Load SHAP explainer from disk."""
        try:
            explainer_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'ml',
                'saved_models',
                'shap_explainer.pkl'
            )
            if os.path.exists(explainer_path):
                with open(explainer_path, 'rb') as f:
                    explainer = pickle.load(f)
                print("[RiskScorer] [OK] Loaded SHAP explainer")
                return explainer
        except Exception as e:
            print(f"[RiskScorer] Could not load SHAP explainer: {e}")
        
        return None
    
    def _load_metadata(self):
        """Load model metadata."""
        try:
            metadata_path = os.path.join(
                os.path.dirname(__file__),
                '..',
                'ml',
                'saved_models',
                'model_metadata.json'
            )
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                print("[RiskScorer] [OK] Loaded model metadata")
                return metadata
        except Exception as e:
            print(f"[RiskScorer] Could not load metadata: {e}")
        
        return None
    
    def calculate_risk_score_with_explanation(self, city: str, food_item: str) -> Dict:
        """
        Calculate risk score with SHAP explanation and confidence.
        
        Returns:
            {
                'risk_score': float,
                'confidence': float,
                'data_source': str,
                'shap_explanation': dict or None,
                'features': dict
            }
        """
        try:
            features = self._extract_features(city, food_item)
            
            result = {
                'city': city,
                'food_item': food_item,
                'features': features,
                'shap_explanation': None
            }
            
            # If model is available, use it
            if self.model and self.scaler and self.feature_names:
                # Scale features
                features_array = np.array([[
                    features['complaint_count'],
                    features['severity_avg'],
                    features['season_flag'],
                    features['source_weight'],
                    features['recency_weight'],
                    features.get('trend_score', 0.5),
                    features.get('adulterant_count', 1)
                ]])
                
                features_scaled = self.scaler.transform(features_array)
                
                # Predict
                score = float(self.model.predict(features_scaled)[0])
                score = max(0, min(100, score))
                
                # Compute SHAP values if explainer available
                if self.shap_explainer:
                    shap_values = self.shap_explainer.shap_values(features_scaled)
                    shap_explanation = self._format_shap_explanation(
                        shap_values[0], 
                        self.feature_names, 
                        features_array[0]
                    )
                    result['shap_explanation'] = shap_explanation
                
                # Confidence score
                confidence = self._compute_confidence(score, features)
                result['confidence'] = confidence
                result['data_source'] = 'ml_model'
                
            else:
                # Use weighted formula
                score = self._weighted_formula(features)
                confidence = self._compute_confidence(score, features)
                result['confidence'] = confidence
                result['data_source'] = 'weighted_formula'
            
            result['risk_score'] = score
            
            print(f"[RiskScorer] {food_item} in {city}: {score:.1f} (confidence: {result['confidence']:.2f})")
            return result
        
        except Exception as e:
            print(f"[RiskScorer] Error calculating score: {e}")
            return {
                'risk_score': 0.0,
                'confidence': 0.0,
                'data_source': 'error',
                'shap_explanation': None,
                'features': {}
            }
    
    def _format_shap_explanation(self, shap_values: np.ndarray, feature_names: list, features: np.ndarray) -> dict:
        """Format SHAP values into human-readable explanation."""
        explanation = {
            'base_value': float(np.mean(np.abs(shap_values))),
            'features': []
        }
        
        # Sort by absolute SHAP value
        indices = np.argsort(np.abs(shap_values))[::-1][:5]  # Top 5 features
        
        for idx in indices:
            if idx < len(feature_names):
                explanation['features'].append({
                    'name': feature_names[idx],
                    'value': float(features[idx]),
                    'shap_value': float(shap_values[idx]),
                    'impact': 'increases' if shap_values[idx] > 0 else 'decreases'
                })
        
        return explanation
    
    def _compute_confidence(self, score: float, features: Dict) -> float:
        """
        Compute confidence score based on features and prediction.
        
        High confidence when:
        - Multiple data points available
        - Recent complaints exist
        - Credible sources
        
        Returns:
            Confidence 0.0-1.0
        """
        confidence = 0.5  # Base confidence
        
        # More complaints = higher confidence
        if features['complaint_count'] > 0:
            confidence += min(0.2, features['complaint_count'] / 50)
        
        # Recent activity increases confidence
        if features['recency_weight'] > 0:
            confidence += min(0.15, features['recency_weight'] / 20)
        
        # Credible sources increase confidence
        if features['source_weight'] > 0.7:
            confidence += 0.15
        
        return max(0.0, min(1.0, confidence))
    
    def _extract_features(self, city: str, food_item: str) -> Dict:
        """Extract features from database for risk calculation."""
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # Feature 1: Complaint count in last 30 days
        complaints_30 = Complaint.objects.filter(
            city__iexact=city,
            food_item__iexact=food_item,
            created_at__gte=last_30_days
        )
        complaint_count = complaints_30.count()
        
        # Feature 2: Average severity
        severity_avg = float(
            complaints_30.aggregate(Avg('severity'))['severity__avg'] or 2.0
        )
        
        # Feature 3: Season flag (festival months get higher weight)
        current_month = str(now.month).zfill(2)
        season_flag = 1 if current_month in self.festival_months else 0
        
        # Feature 4: Source weight (weighted by credibility)
        source_weight = 0.0
        if complaint_count > 0:
            for complaint in complaints_30:
                if complaint.source == 'FSSAI':
                    source_weight += 1.0
                elif complaint.source == 'NEWS':
                    source_weight += 0.8
                else:  # CITIZEN
                    source_weight += 0.5
            source_weight = source_weight / complaint_count
        
        # Feature 5: Recency weight (recent complaints matter more)
        recent_complaints = Complaint.objects.filter(
            city__iexact=city,
            food_item__iexact=food_item,
            created_at__gte=last_7_days
        ).count()
        recency_weight = recent_complaints * 2
        
        # Feature 6: Trend score (recent vs total)
        trend_score = recent_complaints / max(1, complaint_count)
        
        # Feature 7: Adulterant diversity
        adulterant_count = complaints_30.values('adulterant').distinct().count()
        
        return {
            'complaint_count': float(complaint_count),
            'severity_avg': severity_avg,
            'season_flag': float(season_flag),
            'source_weight': source_weight,
            'recency_weight': float(recency_weight),
            'trend_score': trend_score,
            'adulterant_count': float(adulterant_count)
        }
    
    def _weighted_formula(self, features: Dict) -> float:
        """
        Calculate risk using weighted formula if model unavailable.
        """
        base = 20
        score = base
        
        # Normalize and weight each feature
        score += features['complaint_count'] * 1.5
        score += features['severity_avg'] * 8
        score += features['season_flag'] * 10
        score += features['source_weight'] * 10
        score += features['recency_weight'] * 2
        score += features.get('trend_score', 0.5) * 15
        score += features.get('adulterant_count', 1) * 5
        
        return max(0, min(100, score))


def calculate_risk_score_with_explanation(city: str, food_item: str) -> Dict:
    """Helper function to calculate risk score with explanation."""
    scorer = RiskScorerAgent()
    return scorer.calculate_risk_score_with_explanation(city, food_item)


def calculate_risk_score(city: str, food_item: str) -> float:
    """Legacy helper function - returns only the score."""
    scorer = RiskScorerAgent()
    features = scorer._extract_features(city, food_item)

    feature_vector = [
        features['complaint_count'],
        features['severity_avg'],
        features['season_flag'],
        features['source_weight'],
        features['recency_weight'],
        features.get('trend_score', 0.5),
        features.get('adulterant_count', 1),
    ]

    if scorer.model and scorer.scaler:
        features_scaled = scorer.scaler.transform([feature_vector])
        risk_score = float(scorer.model.predict(features_scaled)[0])
        return max(0.0, min(100.0, risk_score))

    return scorer._weighted_formula(features)
