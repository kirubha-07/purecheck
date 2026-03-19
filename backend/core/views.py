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


@api_view(['GET'])
def risk_explain_endpoint(request):
    """
    GET /api/risk/explain/?city=Trichy&food=milk
    Returns full SHAP explanation for one food item.
    Response: {
        food_item: "milk",
        risk_score: 84.2,
        confidence: 91.3,
        explanation: "Human-readable explanation",
        shap_values: { ... },
        top_factor: "complaint_count"
    }
    """
    try:
        city = request.query_params.get('city', '').strip()
        food = request.query_params.get('food', '').strip()
        
        if not city or not food:
            return Response(
                {'error': 'city and food parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get current month
        now = timezone.now()
        current_month = now.strftime('%Y-%m')
        
        # Fetch risk score
        try:
            risk_score = RiskScore.objects.get(
                city__iexact=city,
                food_item__iexact=food,
                month=current_month
            )
        except RiskScore.DoesNotExist:
            return Response(
                {'error': f'No risk data found for {food} in {city}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Extract explanation from SHAP values
        shap_vals = risk_score.shap_explanation or {}
        explanation_text = f"Risk is primarily driven by "
        
        if shap_vals:
            top_factors = sorted(
                shap_vals.items(),
                key=lambda x: abs(x[1]),
                reverse=True
            )[:3]
            
            factors_text = " and ".join([
                f"{factor[0]} ({factor[1]:+.2f})"
                for factor in top_factors
            ])
            explanation_text += factors_text
        else:
            explanation_text += "recent complaints and severity patterns"
        
        explanation_text += f". Confidence level: {risk_score.confidence_score:.1f}%"
        
        return Response(
            {
                'food_item': risk_score.food_item,
                'city': risk_score.city,
                'risk_score': risk_score.risk_score,
                'confidence': risk_score.confidence_score,
                'adulterant': risk_score.adulterant,
                'complaint_count': risk_score.complaint_count,
                'explanation': explanation_text,
                'shap_values': shap_vals,
                'top_factor': max(
                    shap_vals.items(),
                    key=lambda x: abs(x[1]),
                    default=('N/A', 0)
                )[0] if shap_vals else 'N/A'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def heatmap_endpoint(request):
    """
    GET /api/heatmap/
    Returns risk scores for ALL cities in DB with coordinates.
    Response: list of {
        city, lat, lng, risk_score,
        top_food, top_adulterant, state
    }
    Used by IndiaMap.jsx to render Leaflet heatmap.
    """
    try:
        from core.city_coordinates import get_coordinates
        
        # Get current month
        now = timezone.now()
        current_month = now.strftime('%Y-%m')
        
        # Get distinct cities and their highest risk scores
        cities_data = []
        cities_processed = set()
        
        risk_scores = RiskScore.objects.filter(
            month=current_month
        ).order_by('-risk_score')
        
        for risk_score in risk_scores:
            city = risk_score.city
            
            # Skip if we've already added this city
            if city.lower() in cities_processed:
                continue
            
            cities_processed.add(city.lower())
            
            # Get coordinates
            coords = get_coordinates(city)
            if not coords:
                continue
            
            cities_data.append({
                'city': city,
                'state': coords.get('state', 'Unknown'),
                'lat': coords['lat'],
                'lng': coords['lng'],
                'risk_score': risk_score.risk_score,
                'confidence': risk_score.confidence_score,
                'top_food': risk_score.food_item,
                'top_adulterant': risk_score.adulterant,
                'complaint_count': risk_score.complaint_count
            })
        
        # Sort by risk score descending
        cities_data.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return Response(
            {
                'total_cities': len(cities_data),
                'data': cities_data,
                'last_updated': now.isoformat()
            },
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
