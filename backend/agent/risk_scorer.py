import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, Tuple
import numpy as np
from django.utils import timezone
from django.db.models import Avg, Count
from core.models import Complaint, RiskScore


class RiskScorerAgent:
    """
    Calculate risk scores for food items in a city using XGBoost model
    or weighted formula if model is unavailable.
    """
    
    def __init__(self):
        """Initialize with loaded ML model if available."""
        self.model = self._load_model()
        self.festival_months = {'10', '11', '01', '04'}  # Oct, Nov, Jan, Apr
    
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
                print("[RiskScorer] Loaded XGBoost model from disk")
                return model
        except Exception as e:
            print(f"[RiskScorer] Could not load model: {e}")
        
        return None
    
    def calculate_risk_score(self, city: str, food_item: str) -> float:
        """
        Calculate risk score (0-100) for a food item in a city.
        
        Features:
        1. complaint_count: Number of complaints last 30 days
        2. severity_avg: Average severity of complaints
        3. season_flag: 1 if festival month, else 0
        4. source_weight: Weighted by source (FSSAI=1.0, NEWS=0.7, CITIZEN=0.4)
        5. recency_weight: Complaints in last 7 days weighted 2x
        
        Args:
            city: City name
            food_item: Food item name
        
        Returns:
            Risk score 0-100
        """
        try:
            features = self._extract_features(city, food_item)
            
            # If model is available, use it
            if self.model:
                features_array = np.array([[
                    features['complaint_count'],
                    features['severity_avg'],
                    features['season_flag'],
                    features['source_weight'],
                    features['recency_weight']
                ]])
                score = float(self.model.predict(features_array)[0])
                score = max(0, min(100, score))  # Clamp to 0-100
            else:
                # Use weighted formula
                score = self._weighted_formula(features)
            
            print(f"[RiskScorer] {food_item} in {city}: {score:.1f}")
            return score
        
        except Exception as e:
            print(f"[RiskScorer] Error calculating score: {e}")
            return 0.0
    
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
                    source_weight += 0.7
                else:  # CITIZEN
                    source_weight += 0.4
            source_weight = source_weight / complaint_count
        
        # Feature 5: Recency weight (recent complaints matter more)
        recent_complaints = Complaint.objects.filter(
            city__iexact=city,
            food_item__iexact=food_item,
            created_at__gte=last_7_days
        ).count()
        recency_weight = recent_complaints * 2
        
        return {
            'complaint_count': float(complaint_count),
            'severity_avg': severity_avg,
            'season_flag': float(season_flag),
            'source_weight': source_weight,
            'recency_weight': float(recency_weight)
        }
    
    def _weighted_formula(self, features: Dict) -> float:
        """
        Calculate risk using weighted formula if model unavailable.
        Weights: base=20, complaints=15, severity=15, season=10,
                 source=15, recency=25
        """
        base = 20
        score = base
        
        # Normalize and weight each feature
        score += features['complaint_count'] * 1.5          # Up to 45
        score += features['severity_avg'] * 8               # Up to 40
        score += features['season_flag'] * 10               # Up to 10
        score += features['source_weight'] * 10             # Up to 10
        score += features['recency_weight'] * 2             # Up to varies
        
        return max(0, min(100, score))


def calculate_risk_score(city: str, food_item: str) -> float:
    """Helper function to calculate risk score."""
    scorer = RiskScorerAgent()
    return scorer.calculate_risk_score(city, food_item)
