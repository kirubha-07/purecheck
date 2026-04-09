import threading
import time
import random


_scheduler_lock = threading.Lock()
_scheduler_started = False

LAST_PIPELINE_METADATA = {
    'status': 'idle',
    'last_run_time': None,
    'records_processed': 0,
}

CITIES = [
    'chennai',
    'coimbatore',
    'bangalore',
    'mumbai',
    'delhi',
    'hyderabad',
    'kolkata',
    'pune',
    'madurai',
    'trichy',
]

FOOD_DATA = [
    ('milk', 'detergent'),
    ('oil', 'artificial color'),
    ('rice', 'plastic granules'),
    ('tea', 'synthetic dye'),
    ('spices', 'brick powder'),
    ('sweets', 'starch'),
]

CITY_STATE = {
    'chennai': 'Tamil Nadu',
    'coimbatore': 'Tamil Nadu',
    'bangalore': 'Karnataka',
    'mumbai': 'Maharashtra',
    'delhi': 'Delhi',
    'hyderabad': 'Telangana',
    'kolkata': 'West Bengal',
    'pune': 'Maharashtra',
    'madurai': 'Tamil Nadu',
    'trichy': 'Tamil Nadu',
}


def _normalize_city(city: str) -> str:
    return (city or '').lower().strip()


def run_pipeline():
    print('Pipeline started')

    from django.utils import timezone
    from core.models import Complaint, LiveAlert, RiskScore
    current_month = timezone.now().strftime('%Y-%m')

    city_count = 0
    complaints_inserted = 0
    risks_inserted = 0
    alerts_inserted = 0

    for city in CITIES:
        city_norm = _normalize_city(city)

        # Avoid duplicate generation for the same city-month.
        if RiskScore.objects.filter(city__iexact=city_norm, month=current_month).exists():
            continue

        city_count += 1
        sampled_foods = random.sample(FOOD_DATA, k=random.randint(2, 3))

        city_complaints = []
        for food_item, adulterant in sampled_foods:
            severity = random.randint(2, 5)
            complaint, created = Complaint.objects.get_or_create(
                city=city_norm,
                food_item=food_item,
                adulterant=adulterant,
                source='NEWS',
                defaults={
                    'severity': severity,
                    'state': CITY_STATE.get(city_norm, 'India'),
                    'raw_text': f'Simulated complaint in {city_norm}: {food_item} adulterated with {adulterant}',
                    'data_source_type': 'SIMULATED',
                    'nlp_mode': 'KEYWORD',
                    'nlp_confidence': 0.9,
                },
            )
            if created:
                complaints_inserted += 1
            city_complaints.append(complaint)

        for complaint in city_complaints:
            risk_score = float(random.randint(40, 90))
            _, created_risk = RiskScore.objects.update_or_create(
                city=city_norm,
                food_item=complaint.food_item,
                month=current_month,
                defaults={
                    'risk_score': risk_score,
                    'confidence_score': round(min(0.95, 0.55 + (complaint.severity * 0.08)), 2),
                    'adulterant': complaint.adulterant,
                    'complaint_count': Complaint.objects.filter(
                        city__iexact=city_norm,
                        food_item__iexact=complaint.food_item,
                    ).count(),
                    'severity_avg': float(complaint.severity or 2),
                    'shap_explanation': {
                        'reasoning': 'Simulated multi-city score generation',
                        'features': [],
                    },
                    'score_source': 'RULE_ONLY',
                    'data_source_type': 'SIMULATED',
                },
            )
            if created_risk:
                risks_inserted += 1

            if risk_score > 60:
                risk_level = 'HIGH' if risk_score > 70 else 'MEDIUM'
                _, created_alert = LiveAlert.objects.get_or_create(
                    city=city_norm,
                    food_item=complaint.food_item,
                    created_at__date=timezone.now().date(),
                    defaults={
                        'message': f'{risk_level} RISK: {complaint.food_item} in {city_norm} - Risk Score: {risk_score:.1f}',
                        'risk_level': risk_level,
                        'risk_score': risk_score,
                        'data_source_type': 'SIMULATED',
                    },
                )
                if created_alert:
                    alerts_inserted += 1

    LAST_PIPELINE_METADATA.update(
        {
            'status': 'ok',
            'last_run_time': timezone.now().isoformat(),
            'records_processed': complaints_inserted + risks_inserted,
        }
    )

    print(f'Generated data for {city_count} cities')
    print(f'Total complaints inserted: {complaints_inserted}')
    print(f'Total risks inserted: {risks_inserted}')
    print(f'Inserted {alerts_inserted} alerts')
    print('Pipeline finished')


def start_scheduler():
    global _scheduler_started

    with _scheduler_lock:
        if _scheduler_started:
            return

        def loop():
            while True:
                run_pipeline()
                time.sleep(300)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        _scheduler_started = True
        print('Scheduler started')


def get_last_pipeline_metadata():
    return dict(LAST_PIPELINE_METADATA)


def export_to_csv():
    import csv
    import os
    from datetime import datetime
    from core.models import Complaint, RiskScore

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    powerbi_dir = os.path.join(base_dir, 'powerbi')
    os.makedirs(powerbi_dir, exist_ok=True)

    risk_path = os.path.join(powerbi_dir, 'purecheck_live.csv')
    with open(risk_path, 'w', newline='', encoding='utf-8') as fp:
        writer = csv.writer(fp)
        writer.writerow([
            'city', 'food', 'risk_score', 'month', 'source',
            'state', 'confidence', 'adulterant', 'complaint_count',
            'risk_level', 'last_updated'
        ])
        for rs in RiskScore.objects.all().order_by('-risk_score'):
            risk_level = 'HIGH' if float(rs.risk_score or 0) > 70 else 'MEDIUM' if float(rs.risk_score or 0) > 40 else 'LOW'
            writer.writerow([
                rs.city or '',
                rs.food_item or '',
                round(float(rs.risk_score or 0), 2),
                rs.month or datetime.now().strftime('%Y-%m'),
                'UNKNOWN',
                'India',
                round(float(rs.confidence_score or 0.8), 2),
                rs.adulterant or 'unknown',
                rs.complaint_count or 0,
                risk_level,
                datetime.now().strftime('%Y-%m-%d'),
            ])

    complaints_path = os.path.join(powerbi_dir, 'purecheck_complaints.csv')
    with open(complaints_path, 'w', newline='', encoding='utf-8') as fp:
        writer = csv.writer(fp)
        writer.writerow([
            'city', 'food', 'risk_score', 'month', 'source',
            'state', 'adulterant', 'severity', 'created_date'
        ])
        for complaint in Complaint.objects.all().order_by('-created_at'):
            writer.writerow([
                complaint.city or '',
                complaint.food_item or '',
                '',
                complaint.created_at.strftime('%Y-%m') if complaint.created_at else datetime.now().strftime('%Y-%m'),
                complaint.source or 'UNKNOWN',
                complaint.state or 'India',
                complaint.adulterant or 'unknown',
                complaint.severity or 1,
                complaint.created_at.strftime('%Y-%m-%d') if complaint.created_at else datetime.now().strftime('%Y-%m-%d'),
            ])

    return {
        'status': 'ok',
        'path': powerbi_dir,
    }
