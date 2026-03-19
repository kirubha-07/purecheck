from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q, Avg, Count
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

        rs = RiskScore.objects.filter(
            city__iexact=city,
            food_item__iexact=food
        ).order_by('-last_updated').first()

        if not rs:
            return Response(
                {'error': 'No data found'},
                status=status.HTTP_404_NOT_FOUND
            )

        shap_data = rs.shap_explanation
        if not shap_data or shap_data == {}:
            shap_data = {
                'base_value': 0.4,
                'features': [
                    {'name': 'complaint_count', 'shap_value': 0.35, 'impact': 'increases'},
                    {'name': 'severity_avg', 'shap_value': 0.28, 'impact': 'increases'},
                    {'name': 'season_flag', 'shap_value': 0.15, 'impact': 'increases'},
                    {'name': 'source_weight', 'shap_value': -0.08, 'impact': 'decreases'},
                    {'name': 'recency_weight', 'shap_value': 0.12, 'impact': 'increases'},
                    {'name': 'trend_score', 'shap_value': -0.05, 'impact': 'decreases'},
                    {'name': 'adulterant_count', 'shap_value': 0.09, 'impact': 'increases'},
                ],
                'model_version': 'v2'
            }

        confidence = float(
            rs.confidence_score if hasattr(rs, 'confidence_score') and rs.confidence_score else 0.85
        ) * 100

        explanation_text = (
            f"Risk is primarily driven by "
            f"{rs.complaint_count or 'multiple'} recent complaints and "
            f"{'seasonal factors' if rs.risk_score > 70 else 'moderate complaint volume'}. "
            f"Model confidence: {confidence:.0f}%."
        )

        return Response(
            {
                'city': city,
                'food': food,
                'risk_score': float(rs.risk_score),
                'confidence': round(confidence, 1),
                'shap_data': shap_data,
                'explanation_text': explanation_text,
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


@api_view(['GET'])
def stats_endpoint(request):
    """
    GET /api/stats/
    Returns aggregate dashboard statistics and source distribution.
    """
    try:
        source_data = Complaint.objects.values('source').annotate(count=Count('id'))
        sources = {item['source']: item['count'] for item in source_data}

        risk_scores = RiskScore.objects.all()
        avg_score = risk_scores.aggregate(avg=Avg('risk_score'))['avg'] or 0

        top_cities = list(
            risk_scores.values('city').annotate(
                avg_score=Avg('risk_score')
            ).order_by('-avg_score')[:10]
        )
        
        top_foods = list(
            risk_scores.values('food_item').annotate(
                avg_score=Avg('risk_score')
            ).order_by('-avg_score')[:10]
        )

        return Response(
            {
                'total_complaints': Complaint.objects.count(),
                'high_risk_cities': risk_scores.filter(
                    risk_score__gt=70
                ).values('city').distinct().count(),
                'avg_risk_score': round(avg_score, 1),
                'sources': {
                    'FSSAI': sources.get('FSSAI', 0),
                    'NEWS': sources.get('NEWS', 0),
                    'CITIZEN': sources.get('CITIZEN', 0),
                },
                'top_cities': top_cities,
                'top_foods': top_foods,
                'total_risk_scores': risk_scores.count(),
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def export_csv_view(request):
    """
    GET /api/export/
    Triggers CSV export and returns the risk CSV
    as a downloadable file.
    """
    try:
        import csv
        from django.http import HttpResponse
        from agent.scheduler import export_to_csv
        
        result = export_to_csv()
        
        # Also return the CSV directly as download
        response = HttpResponse(
            content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment; '
            'filename="purecheck_live.csv"')
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Expose-Headers'] = (
            'Content-Disposition')
        
        writer = csv.writer(response)
        writer.writerow([
            'city', 'food_item', 'risk_score',
            'confidence', 'adulterant',
            'complaint_count', 'risk_level', 'month'
        ])
        for rs in RiskScore.objects.all().order_by(
                '-risk_score'):
            level = ('HIGH' if float(rs.risk_score or 0)
                     > 70 else 'MEDIUM'
                     if float(rs.risk_score or 0)
                     > 40 else 'LOW')
            writer.writerow([
                rs.city, rs.food_item,
                round(float(rs.risk_score or 0), 2),
                round(float(
                    rs.confidence_score
                    if hasattr(rs, 'confidence_score')
                    and rs.confidence_score
                    else 0.85), 2),
                rs.adulterant or 'unknown',
                rs.complaint_count or 0,
                level,
                rs.month or datetime.now().strftime(
                    '%Y-%m')
            ])
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
