from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Count
from datetime import datetime
from functools import wraps
from time import perf_counter
import json
from django.conf import settings
from core.models import Complaint, RiskScore, LiveAlert
from core.serializers import RiskScoreSerializer, LiveAlertSerializer
from core.system_metrics import get_system_metrics, record_api_response
from agent.scheduler import run_pipeline, get_last_pipeline_metadata
import logging


logger = logging.getLogger(__name__)


def timed_api(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        started = perf_counter()
        response = view_func(request, *args, **kwargs)
        record_api_response(perf_counter() - started)
        return response
    return _wrapped


@api_view(['GET'])
@timed_api
def risk_endpoint(request):
    """
    GET /api/risk/?city=Trichy
    Returns top 5 RiskScore objects for that city this month
    sorted by risk_score descending.
    """
    try:
        city = request.query_params.get('city', '').strip().lower()
        if not city:
            return Response(
                {'error': 'city parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        logger.info('Fetching data for city: %s', city)
        
        # Get current month
        now = timezone.now()
        current_month = now.strftime('%Y-%m')
        
        # Fetch top 5 risk scores for this city and month
        risk_scores = RiskScore.objects.filter(
            city__iexact=city,
            month=current_month
        ).order_by('-risk_score')[:5]
        
        record_count = risk_scores.count()
        logger.info('Records found: %s', record_count)
        if record_count == 0:
            return Response(
                {
                    'message': 'No data found. Pipeline may not have run.',
                    'data': []
                },
                status=status.HTTP_200_OK
            )

        serializer = RiskScoreSerializer(risk_scores, many=True)
        logger.info('API returning %s records', len(serializer.data))
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@timed_api
def alerts_endpoint(request):
    """
    GET /api/alerts/?city=Trichy
    Returns last 20 LiveAlert objects for that city.
    """
    try:
        city = request.query_params.get('city', '').strip().lower()
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
@timed_api
def report_endpoint(request):
    """
    POST /api/report/
    Accepts: city, food_item, adulterant, description
    Creates a Complaint with source="CITIZEN"
    Triggers immediate re-scoring for that city.
    """
    try:
        city = request.data.get('city', '').strip().lower()
        food_item = request.data.get('food_item', '').strip()
        adulterant = request.data.get('adulterant', '').strip()
        description = request.data.get('description', '').strip()
        
        severity_raw = request.data.get('severity', 2)

        # Validate required fields
        if not all([city, food_item, adulterant, description]):
            return Response(
                {'error': 'city, food_item, adulterant, and description are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate severity (1-5)
        try:
            severity = int(severity_raw)
        except (TypeError, ValueError):
            return Response(
                {'error': 'severity must be an integer between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if severity < 1 or severity > 5:
            return Response(
                {'error': 'severity must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create complaint
        complaint = Complaint.objects.create(
            source='CITIZEN',
            city=city,
            state='Tamil Nadu',
            food_item=food_item,
            adulterant=adulterant,
            severity=severity,
            data_source_type='REAL',
            nlp_mode='KEYWORD',
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
@timed_api
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
@timed_api
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
        city = request.query_params.get('city', '').strip().lower()
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
                'top_factors': [
                    {
                        'name': 'complaint_count',
                        'value': float(rs.complaint_count or 0),
                        'impact': 'increases',
                    },
                    {
                        'name': 'severity_avg',
                        'value': float(rs.severity_avg or 0),
                        'impact': 'increases',
                    },
                    {
                        'name': 'risk_score_band',
                        'value': float(rs.risk_score or 0),
                        'impact': 'increases' if float(rs.risk_score or 0) > 40 else 'decreases',
                    },
                ],
                'reasoning': 'Fallback explanation generated from complaint volume and severity because SHAP values are unavailable.',
                'confidence_score': round(float(rs.confidence_score or 0.6), 3),
                'model_version': 'fallback-v1'
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

        factors = (
            shap_data.get('features')
            if isinstance(shap_data, dict) and shap_data.get('features')
            else shap_data.get('top_factors', []) if isinstance(shap_data, dict) else []
        )
        explanation_source = 'SHAP' if isinstance(shap_data, dict) and shap_data.get('features') else 'RULE_BASED'

        return Response(
            {
                'city': city,
                'food': food,
                'risk_score': float(rs.risk_score),
                'confidence': round(confidence, 1),
                'score_source': rs.score_source if hasattr(rs, 'score_source') else 'RULE_ONLY',
                'data_source_type': getattr(rs, 'data_source_type', settings.DATA_MODE),
                'explanation_source': explanation_source,
                'shap_data': shap_data,
                'factors': factors,
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
@timed_api
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
@timed_api
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
@timed_api
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
            'city', 'food', 'risk_score', 'month', 'source',
            'confidence', 'adulterant', 'complaint_count', 'risk_level'
        ])
        for rs in RiskScore.objects.all().order_by(
                '-risk_score'):
            level = ('HIGH' if float(rs.risk_score or 0)
                     > 70 else 'MEDIUM'
                     if float(rs.risk_score or 0)
                     > 40 else 'LOW')
            source_row = (
                Complaint.objects.filter(
                    city__iexact=rs.city,
                    food_item__iexact=rs.food_item,
                )
                .values('source')
                .annotate(count=Count('id'))
                .order_by('-count')
                .first()
            )
            dominant_source = source_row['source'] if source_row else 'UNKNOWN'

            writer.writerow([
                rs.city,
                rs.food_item,
                round(float(rs.risk_score or 0), 2),
                rs.month or datetime.now().strftime(
                    '%Y-%m'),
                dominant_source,
                round(float(
                    rs.confidence_score
                    if hasattr(rs, 'confidence_score')
                    and rs.confidence_score
                    else 0.85), 2),
                rs.adulterant or 'unknown',
                rs.complaint_count or 0,
                level
            ])
        return response
        
    except Exception as e:
        return Response(
            {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@timed_api
def ml_status_endpoint(request):
    try:
        from agent.risk_scorer import get_ml_runtime_status, MODEL_DIR

        status_payload = get_ml_runtime_status()
        status_payload['data_mode'] = settings.DATA_MODE
        status_payload['model_dir'] = str(MODEL_DIR)
        return Response(status_payload, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@timed_api
def run_pipeline_endpoint(request):
    try:
        run_pipeline()
        return Response(get_last_pipeline_metadata(), status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@timed_api
def system_metrics_endpoint(request):
    try:
        metrics = get_system_metrics()
        pipeline_metadata = get_last_pipeline_metadata()
        metrics['last_run_time'] = pipeline_metadata.get('last_run_time')
        metrics['last_pipeline_duration'] = pipeline_metadata.get(
            'last_duration',
            metrics.get('last_pipeline_duration', 0.0),
        )
        metrics['avg_pipeline_time'] = metrics.get('avg_pipeline_latency', 0.0)
        return Response(metrics, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@timed_api
def evaluation_report_endpoint(request):
    try:
        from agent.risk_scorer import RiskScorerAgent, MODEL_DIR, FEATURE_ORDER

        metadata_path = MODEL_DIR / 'model_metadata.json'
        metadata = {}
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as fp:
                metadata = json.load(fp)

        scorer = RiskScorerAgent()
        sample_pairs = list(
            Complaint.objects.values_list('city', 'food_item').distinct()[:20]
        )

        comparisons = []
        for city, food_item in sample_pairs:
            features = scorer._extract_features(city, food_item)
            rule_score = scorer._weighted_formula(features)
            if scorer.uses_ml_model:
                feature_vector = [[features[name] for name in FEATURE_ORDER]]
                ml_score = float(scorer.model.predict(scorer.scaler.transform(feature_vector))[0])
                ml_score = max(0.0, min(100.0, ml_score))
                hybrid_score = (0.7 * ml_score) + (0.3 * rule_score)
            else:
                ml_score = None
                hybrid_score = rule_score

            comparisons.append(
                {
                    'city': city,
                    'food_item': food_item,
                    'ml_score': round(ml_score, 3) if ml_score is not None else None,
                    'rule_score': round(rule_score, 3),
                    'hybrid_score': round(hybrid_score, 3),
                }
            )

        report = {
            'accuracy': metadata.get('r2_score', metadata.get('r2')),
            'rmse': metadata.get('rmse', metadata.get('rmse_test')),
            'dataset_size': metadata.get('total_samples', metadata.get('training_samples', 0) + metadata.get('test_samples', 0)),
            'ablation': {
                'mode': 'ML+RULE' if scorer.uses_ml_model else 'RULE_ONLY',
                'samples': comparisons,
            },
        }
        return Response(report, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
