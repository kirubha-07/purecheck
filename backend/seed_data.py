import os
import django
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Complaint, RiskScore, LiveAlert

print("Creating dummy data...")

# Cities and food items
cities = ['Trichy', 'Coimbatore', 'Chennai', 'Madurai', 'Salem']
foods = ['milk', 'rice', 'oil', 'turmeric', 'ghee', 'sweets', 'paneer']
adulterants = ['detergent', 'starch', 'synthetic color', 'chalk powder', 'water']

# Create Complaints
for i, city in enumerate(cities):
    for j, food in enumerate(foods[:3]):
        adulterant = adulterants[j % len(adulterants)]
        Complaint.objects.create(
            source='NEWS' if i % 2 == 0 else 'FSSAI',
            city=city,
            state='Tamil Nadu',
            food_item=food,
            adulterant=adulterant,
            severity=(i + j) % 5 + 1,
            raw_text=f"Sample complaint about {adulterant} found in {food} from {city}"
        )
        print(f"✓ Created complaint: {food} in {city}")

# Create RiskScores
current_month = timezone.now().strftime('%Y-%m')
risk_scores = [85, 72, 68, 45, 38, 55, 62]
for i, city in enumerate(cities):
    for j, food in enumerate(foods):
        risk_score = risk_scores[(i * len(foods) + j) % len(risk_scores)]
        RiskScore.objects.get_or_create(
            city=city,
            food_item=food,
            month=current_month,
            defaults={
                'risk_score': float(risk_score),
                'adulterant': adulterants[j % len(adulterants)],
                'complaint_count': (i + j) % 10 + 1,
            }
        )
        print(f"✓ Created risk score: {food} in {city} = {risk_score}")

# Create LiveAlerts
for i, city in enumerate(cities):
    for j, food in enumerate(foods[:2]):
        risk_level = ['HIGH', 'MEDIUM', 'LOW'][i % 3]
        LiveAlert.objects.create(
            city=city,
            food_item=food,
            message=f'{risk_level} RISK: {food} adulteration detected in {city}',
            risk_level=risk_level
        )
        print(f"✓ Created alert: {food} in {city} - {risk_level}")

print("\n✅ Dummy data created successfully!")
