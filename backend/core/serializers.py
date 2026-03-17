from rest_framework import serializers
from core.models import Complaint, RiskScore, LiveAlert


class ComplaintSerializer(serializers.ModelSerializer):
    """Serializer for Complaint model."""
    
    class Meta:
        model = Complaint
        fields = [
            'id',
            'source',
            'city',
            'state',
            'food_item',
            'adulterant',
            'severity',
            'raw_text',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class RiskScoreSerializer(serializers.ModelSerializer):
    """Serializer for RiskScore model with SHAP explanation."""
    
    # Format SHAP explanation for API response
    shap_explanation = serializers.SerializerMethodField()
    
    class Meta:
        model = RiskScore
        fields = [
            'id',
            'city',
            'food_item',
            'food_category',
            'risk_score',
            'confidence_score',
            'adulterant',
            'complaint_count',
            'severity_avg',
            'month',
            'shap_explanation',
            'last_updated',
        ]
        read_only_fields = ['id', 'last_updated']
    
    def get_shap_explanation(self, obj):
        """Return formatted SHAP explanation."""
        if isinstance(obj.shap_explanation, dict) and obj.shap_explanation:
            return {
                'base_value': obj.shap_explanation.get('base_value', 0),
                'features': obj.shap_explanation.get('features', []),
                'model_version': obj.shap_explanation.get('model_version', 'v2')
            }
        return None


class LiveAlertSerializer(serializers.ModelSerializer):
    """Serializer for LiveAlert model."""
    
    class Meta:
        model = LiveAlert
        fields = [
            'id',
            'message',
            'city',
            'food_item',
            'risk_level',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
