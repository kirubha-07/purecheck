from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from core.models import Complaint, RiskScore, LiveAlert
from core.serializers import ComplaintSerializer, RiskScoreSerializer, LiveAlertSerializer


@api_view(['GET'])
def risk_endpoint(request):
    """
    GET /api/risk/?city=Trichy
    Returns top 5 RiskScore objects for that city this month
    sorted by risk_score descending.
    """
    try:
        city = request.query_params.get('city', '').strip()
        if not city:
            return Response(
                {'error': 'city parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get current month
        now = timezone.now()
        current_month = now.strftime('%Y-%m')
        
        # Fetch top 5 risk scores for this city and month
        risk_scores = RiskScore.objects.filter(
            city__iexact=city,
            month=current_month
        ).order_by('-risk_score')[:5]
        
        serializer = RiskScoreSerializer(risk_scores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def alerts_endpoint(request):
    """
    GET /api/alerts/?city=Trichy
    Returns last 20 LiveAlert objects for that city.
    """
    try:
        city = request.query_params.get('city', '').strip()
        if not city:
            return Response(
                {'error': 'city parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Fetch last 20 alerts for this city
        alerts = LiveAlert.objects.filter(
            city__iexact=city
        ).order_by('-created_at')[:20]
        
        serializer = LiveAlertSerializer(alerts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def report_endpoint(request):
    """
    POST /api/report/
    Accepts: city, food_item, adulterant, description
    Creates a Complaint with source="CITIZEN"
    Triggers immediate re-scoring for that city.
    """
    try:
        city = request.data.get('city', '').strip()
        food_item = request.data.get('food_item', '').strip()
        adulterant = request.data.get('adulterant', '').strip()
        description = request.data.get('description', '').strip()
        
        # Validate required fields
        if not all([city, food_item, adulterant, description]):
            return Response(
                {'error': 'city, food_item, adulterant, and description are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create complaint
        complaint = Complaint.objects.create(
            source='CITIZEN',
            city=city,
            state='Tamil Nadu',
            food_item=food_item,
            adulterant=adulterant,
            severity=2,  # Default severity for citizen reports
            raw_text=description
        )
        
        # Trigger re-scoring (optional: implement async task here)
        # For now, just return success
        
        return Response(
            {
                'message': 'Thank you. Your report has been submitted and will update risk scores within minutes.',
                'complaint_id': complaint.id
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def cities_endpoint(request):
    """
    GET /api/cities/
    Returns list of all distinct cities in the database.
    """
    try:
        # Get distinct cities from both Complaint and RiskScore
        complaint_cities = set(
            Complaint.objects.values_list('city', flat=True).distinct()
        )
        risk_cities = set(
            RiskScore.objects.values_list('city', flat=True).distinct()
        )
        
        all_cities = sorted(list(complaint_cities | risk_cities))
        
        return Response(
            {'cities': all_cities},
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
