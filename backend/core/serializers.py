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
    """Serializer for RiskScore model."""
    
    class Meta:
        model = RiskScore
        fields = [
            'id',
            'city',
            'food_item',
            'risk_score',
            'adulterant',
            'complaint_count',
            'month',
            'last_updated',
        ]
        read_only_fields = ['id', 'last_updated']


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
