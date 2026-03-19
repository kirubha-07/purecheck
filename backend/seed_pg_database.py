import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Complaint, RiskScore, LiveAlert
import random
from datetime import datetime

cities = ['Trichy', 'Coimbatore', 'Chennai', 'Madurai',
          'Salem', 'Mumbai', 'Delhi', 'Bangalore',
          'Hyderabad', 'Kolkata']
foods = ['milk', 'oil', 'rice', 'ghee', 'chilli',
         'turmeric', 'paneer', 'sweets', 'vegetables']
adulterants = ['detergent', 'water', 'starch',
               'synthetic color', 'chalk powder',
               'pesticide', 'urea', 'metanil yellow']
sources = ['FSSAI', 'NEWS', 'CITIZEN']

print("Starting database seeding...")
complaint_count = 0
for city in cities:
    for food in foods:
        for _ in range(random.randint(3, 8)):
            Complaint.objects.create(
                source=random.choice(sources),
                city=city,
                state='Tamil Nadu' if city in ['Trichy','Coimbatore','Chennai','Madurai','Salem'] else 'Other',
                food_item=food,
                adulterant=random.choice(adulterants),
                severity=random.randint(1, 5),
                raw_text=f'{food} adulteration reported in {city}'
            )
            complaint_count += 1

print(f"✓ Created {complaint_count} complaints")

risk_count = 0
for city in cities:
    for food in foods:
        risk_obj, created = RiskScore.objects.get_or_create(
            city=city,
            food_item=food,
            month='2026-03',
            defaults={
                'risk_score': round(random.uniform(30, 99), 2),
                'confidence_score': round(random.uniform(0.70, 0.95), 2),
                'adulterant': random.choice(adulterants),
                'complaint_count': random.randint(3, 20),
                'severity_avg': round(random.uniform(1.0, 5.0), 2),
                'shap_explanation': {
                    'complaint_count': round(random.uniform(0.1, 0.5), 3),
                    'severity_avg': round(random.uniform(0.1, 0.4), 3),
                    'season_flag': round(random.uniform(0.05, 0.2), 3),
                    'source_weight': round(random.uniform(0.02, 0.1), 3),
                    'recency_weight': round(random.uniform(0.02, 0.1), 3),
                }
            }
        )
        if created:
            risk_count += 1

print(f"✓ Created {risk_count} risk scores")
print(f"✓ Total Complaints: {Complaint.objects.count()}")
print(f"✓ Total RiskScores: {RiskScore.objects.count()}")
print("✓ Seeding complete!")
