import pickle
import json
import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Dict

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
from django.utils import timezone
from django.db.models import Avg
from core.models import Complaint
from ml.shap_explainer import format_shap_explanation


MODEL_DIR = Path(__file__).resolve().parent.parent / 'ml' / 'saved_models'
logger = logging.getLogger(__name__)
REQUIRED_ML_ARTIFACTS = {
    'risk_model': ['model.pkl', 'risk_model.pkl'],
    'scaler': ['scaler.pkl', 'feature_scaler.pkl'],
    'shap_explainer': ['shap_explainer.pkl'],
}
FEATURE_ORDER = [
    'complaint_count',
    'severity_avg',
    'season_flag',
    'source_weight',
    'recency_weight',
    'trend_score',
    'adulterant_count',
]


def get_ml_runtime_status() -> Dict:
    """Return ML runtime availability status for transparency endpoints."""
    model_loaded = any((MODEL_DIR / name).exists() for name in REQUIRED_ML_ARTIFACTS['risk_model'])
    scaler_loaded = any((MODEL_DIR / name).exists() for name in REQUIRED_ML_ARTIFACTS['scaler'])
    shap_enabled = any((MODEL_DIR / name).exists() for name in REQUIRED_ML_ARTIFACTS['shap_explainer'])
    ml_enabled = bool(model_loaded and scaler_loaded)
    missing_artifacts = []
    if not model_loaded:
        missing_artifacts.extend(REQUIRED_ML_ARTIFACTS['risk_model'])
    if not scaler_loaded:
        missing_artifacts.extend(REQUIRED_ML_ARTIFACTS['scaler'])
    if not shap_enabled:
        missing_artifacts.extend(REQUIRED_ML_ARTIFACTS['shap_explainer'])

    if missing_artifacts:
        logger.error(
            "ML artifacts missing under %s: %s",
            MODEL_DIR,
            missing_artifacts,
        )

    return {
        'ml_enabled': ml_enabled,
        'model_loaded': model_loaded and scaler_loaded,
        'shap_enabled': shap_enabled,
        'mode': 'ML' if ml_enabled else 'FALLBACK',
        'missing_artifacts': missing_artifacts,
    }


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
        self.feature_names = self.metadata.get('feature_names') if self.metadata else FEATURE_ORDER
        self.uses_ml_model = bool(self.model and self.scaler)

        if self.uses_ml_model:
            logger.info("ML model loaded successfully")
            logger.info("[RiskScorer] Using ML model from %s", MODEL_DIR)
        else:
            logger.warning("[RiskScorer] ML artifacts missing in %s", MODEL_DIR)
            logger.warning("Fallback scoring used")
    
    def _load_model(self):
        """Load XGBoost model from disk, return None if not available."""
        candidate_paths = [
            MODEL_DIR / 'model.pkl',
            MODEL_DIR / 'risk_model.pkl',
        ]
        try:
            for model_path in candidate_paths:
                if not model_path.exists():
                    continue
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                logger.info("[RiskScorer] Loaded XGBoost model from %s", model_path)
                return model
            logger.warning("[RiskScorer] Missing model files: %s", candidate_paths)
        except Exception as e:
            logger.warning("[RiskScorer] Could not load model: %s", e)
        
        return None
    
    def _load_scaler(self):
        """Load feature scaler from disk."""
        candidate_paths = [
            MODEL_DIR / 'scaler.pkl',
            MODEL_DIR / 'feature_scaler.pkl',
        ]
        try:
            for scaler_path in candidate_paths:
                if not scaler_path.exists():
                    continue
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                logger.info("[RiskScorer] Loaded feature scaler from %s", scaler_path)
                return scaler
            logger.warning("[RiskScorer] Missing scaler files: %s", candidate_paths)
        except Exception as e:
            logger.warning("[RiskScorer] Could not load scaler: %s", e)
        
        return None
    
    def _load_shap_explainer(self):
        """Load SHAP explainer from disk."""
        try:
            explainer_path = MODEL_DIR / 'shap_explainer.pkl'
            if explainer_path.exists():
                with open(explainer_path, 'rb') as f:
                    explainer = pickle.load(f)
                logger.info("[RiskScorer] Loaded SHAP explainer")
                return explainer
            logger.warning("[RiskScorer] SHAP explainer not found: %s", explainer_path)
        except Exception as e:
            logger.warning("[RiskScorer] Could not load SHAP explainer: %s", e)
        
        return None
    
    def _load_metadata(self):
        """Load model metadata."""
        try:
            metadata_path = MODEL_DIR / 'model_metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                logger.info("[RiskScorer] Loaded model metadata")
                return metadata
            logger.warning("[RiskScorer] Missing metadata file: %s", metadata_path)
        except Exception as e:
            logger.warning("[RiskScorer] Could not load metadata: %s", e)
        
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
            if self.uses_ml_model:
                features_array = np.array([[features[name] for name in FEATURE_ORDER]], dtype=float)
                features_scaled = self.scaler.transform(features_array)

                ml_score = float(self.model.predict(features_scaled)[0])
                ml_score = max(0, min(100, ml_score))
                rule_score = self._weighted_formula(features)
                score = max(0, min(100, (0.7 * ml_score) + (0.3 * rule_score)))
                
                # Compute SHAP values if explainer available
                if self.shap_explainer:
                    shap_values = self.shap_explainer.shap_values(features_scaled)
                    shap_explanation = format_shap_explanation(
                        shap_values[0], 
                        self.feature_names, 
                        features_array[0]
                    )
                    result['shap_explanation'] = shap_explanation
                else:
                    result['shap_explanation'] = self._build_fallback_explanation(features)
                
                # Confidence score
                confidence = self._compute_confidence(score, features)
                result['confidence'] = confidence
                result['data_source'] = 'ml_blended'
                result['score_source'] = 'ML+RULE'
                result['ml_enabled'] = True
                logger.info('[RiskScorer] Using blended ML + rule scoring')
                logger.info('ML scoring used')
                
            else:
                # Use weighted formula
                score = self._weighted_formula(features)
                confidence = self._compute_confidence(score, features)
                result['confidence'] = confidence
                result['data_source'] = 'weighted_formula'
                result['score_source'] = 'RULE_ONLY'
                result['ml_enabled'] = False
                result['shap_explanation'] = self._build_fallback_explanation(features)
                logger.warning('Fallback scoring used')
            
            result['risk_score'] = score
            
            logger.info(
                "[RiskScorer] %s in %s: %.1f (confidence: %.2f)",
                food_item,
                city,
                score,
                result['confidence'],
            )
            return result
        
        except Exception as e:
            logger.exception("[RiskScorer] Error calculating score: %s", e)
            return {
                'risk_score': 0.0,
                'confidence': 0.0,
                'data_source': 'error',
                'shap_explanation': None,
                'features': {}
            }

    def _build_fallback_explanation(self, features: Dict) -> Dict:
        """Build structured explanation when SHAP explainer is unavailable."""
        ranked = sorted(features.items(), key=lambda item: abs(float(item[1])), reverse=True)
        top_factors = [
            {
                'name': name,
                'value': float(value),
                'impact': 'increases' if float(value) >= 0 else 'decreases',
            }
            for name, value in ranked[:3]
        ]
        return {
            'top_factors': top_factors,
            'reasoning': 'Fallback explanation generated from rule-based feature magnitudes because SHAP explainer is unavailable.',
            'confidence_score': 0.6,
            'model_version': self.metadata.get('version', 'fallback') if self.metadata else 'fallback',
        }
    
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

    feature_vector = [features[name] for name in FEATURE_ORDER]

    if scorer.model and scorer.scaler:
        features_scaled = scorer.scaler.transform([feature_vector])
        risk_score = float(scorer.model.predict(features_scaled)[0])
        return max(0.0, min(100.0, risk_score))

    return scorer._weighted_formula(features)
