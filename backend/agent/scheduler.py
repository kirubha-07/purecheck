import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from django.db.models import Q

from agent.scraper import fetch_news_articles, fetch_fssai_complaints
from agent.nlp_extractor import extract_entities
from agent.risk_scorer import calculate_risk_score_with_explanation
from core.models import Complaint, RiskScore, LiveAlert


scheduler = BackgroundScheduler()
scheduler_started = False


def run_pipeline():
    """
    Main pipeline job that runs every 6 hours.
    Fetch -> Extract -> Score -> Alert
    """
    try:
        print("\n" + "="*60)
        print(f"[Scheduler] Pipeline started at {datetime.now()}")
        print("="*60)
        
        # Top 10 Indian cities to monitor
        cities = [
            'Trichy', 'Coimbatore', 'Chennai', 'Madurai', 'Salem',
            'Bangalore', 'Delhi', 'Mumbai', 'Pune', 'Hyderabad'
        ]
        
        # Step 1: Scrape data
        print("\n[Pipeline] Step 1: Scraping data...")
        all_articles = []
        for city in cities:
            articles = fetch_news_articles(city)
            all_articles.extend(articles)
        
        fssai_complaints = fetch_fssai_complaints()
        print(f"[Pipeline] Scraped {len(all_articles)} news articles and {len(fssai_complaints)} FSSAI complaints")
        
        # Step 2: Extract entities and create Complaints
        print("\n[Pipeline] Step 2: Extracting entities...")
        new_complaints = []
        
        for article in all_articles:
            try:
                entities = extract_entities(article['description'] or article['title'])
                
                # Check if complaint already exists
                if not Complaint.objects.filter(
                    city__iexact=entities['city'],
                    food_item__iexact=entities['food_item'],
                    adulterant__iexact=entities['adulterant'],
                    created_at__gte=timezone.now() - timezone.timedelta(hours=6)
                ).exists():
                    
                    complaint = Complaint.objects.create(
                        source='NEWS',
                        city=entities['city'],
                        state='Tamil Nadu',
                        food_item=entities['food_item'],
                        adulterant=entities['adulterant'],
                        severity=entities['severity'],
                        nlp_confidence=entities.get('nlp_confidence', 0.5),
                        raw_text=article.get('description', article.get('title', ''))[:1000]
                    )
                    new_complaints.append(complaint)
            except Exception as e:
                print(f"[Pipeline] Error extracting from article: {e}")
        
        for complaint_data in fssai_complaints:
            try:
                # Extract entities from FSSAI complaint text
                entities = extract_entities(complaint_data.get('raw_text', ''))
                
                if not Complaint.objects.filter(
                    city__iexact=complaint_data['city'],
                    food_item__iexact=complaint_data['food_item'],
                    created_at__gte=timezone.now() - timezone.timedelta(hours=6)
                ).exists():
                    
                    # Get NLP confidence from entity extraction
                    nlp_conf = entities.get('nlp_confidence', 0.8)  # FSSAI data is generally high confidence
                    
                    complaint = Complaint.objects.create(
                        source='FSSAI',
                        city=complaint_data['city'],
                        state='Tamil Nadu',
                        food_item=complaint_data['food_item'],
                        adulterant=complaint_data['adulterant'],
                        severity=complaint_data['severity'],
                        nlp_confidence=nlp_conf,
                        raw_text=complaint_data['raw_text']
                    )
                    new_complaints.append(complaint)
            except Exception as e:
                print(f"[Pipeline] Error processing FSSAI complaint: {e}")
        
        print(f"[Pipeline] Created {len(new_complaints)} new complaints")
        
        # Step 3: Calculate risk scores
        print("\n[Pipeline] Step 3: Calculating risk scores...")
        current_month = timezone.now().strftime('%Y-%m')
        alerts_created = 0
        
        for city in cities:
            try:
                # Find unique food items for this city
                food_items = set(
                    Complaint.objects.filter(
                        city__iexact=city
                    ).values_list('food_item', flat=True)
                )
                
                for food_item in food_items:
                    try:
                        # Calculate risk with SHAP explanation
                        result = calculate_risk_score_with_explanation(city, food_item)
                        score = result['risk_score']
                        confidence = result['confidence']
                        shap_explanation = result['shap_explanation']
                        
                        # Update or create RiskScore
                        risk_obj, created = RiskScore.objects.update_or_create(
                            city=city,
                            food_item=food_item,
                            month=current_month,
                            defaults={
                                'risk_score': score,
                                'confidence_score': confidence,
                                'shap_explanation': shap_explanation or {},
                                'adulterant': extract_entities(food_item)['adulterant'],
                                'complaint_count': Complaint.objects.filter(
                                    city__iexact=city,
                                    food_item__iexact=food_item
                                ).count()
                            }
                        )
                        
                        # Create alert if risk is high
                        if score > 70:
                            alert, alert_created = LiveAlert.objects.get_or_create(
                                city=city,
                                food_item=food_item,
                                created_at__date=timezone.now().date(),
                                defaults={
                                    'message': f'HIGH RISK: {food_item} in {city} - Risk Score: {score:.1f}',
                                    'risk_level': 'HIGH'
                                }
                            )
                            if alert_created:
                                alerts_created += 1
                                print(f"[Pipeline] [HIGH RISK ALERT] {food_item} in {city} ({score:.1f})")
                                
                                # Send to WebSocket
                                try:
                                    send_alert_to_websocket(city, alert)
                                except Exception as e:
                                    print(f"[Pipeline] Error sending WebSocket alert: {e}")
                        
                        elif score > 40:
                            alert, alert_created = LiveAlert.objects.get_or_create(
                                city=city,
                                food_item=food_item,
                                created_at__date=timezone.now().date(),
                                defaults={
                                    'message': f'MEDIUM RISK: {food_item} in {city} - Risk Score: {score:.1f}',
                                    'risk_level': 'MEDIUM'
                                }
                            )
                            if alert_created:
                                alerts_created += 1
                    
                    except Exception as e:
                        print(f"[Pipeline] Error calculating score for {food_item} in {city}: {e}")
            
            except Exception as e:
                print(f"[Pipeline] Error processing city {city}: {e}")
        
        print(f"[Pipeline] Created {alerts_created} new alerts")
        
        print("\n" + "="*60)
        print(f"[Scheduler] Pipeline completed successfully at {datetime.now()}")
        print("="*60 + "\n")
    
    except Exception as e:
        print(f"\n[Scheduler] CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()


def send_alert_to_websocket(city: str, alert: LiveAlert):
    """
    Send alert to WebSocket consumers via channel layer.
    Requires channels/async setup.
    """
    try:
        from channels.layers import get_channel_layer
        import asyncio
        
        channel_layer = get_channel_layer()
        room_group_name = f'alerts_{city.lower()}'
        
        message = {
            'id': alert.id,
            'message': alert.message,
            'city': alert.city,
            'food_item': alert.food_item,
            'risk_level': alert.risk_level,
            'created_at': alert.created_at.isoformat(),
        }
        
        asyncio.ensure_future(
            channel_layer.group_send(
                room_group_name,
                {
                    'type': 'alert_message',
                    'message': message
                }
            )
        )
    except Exception as e:
        print(f"[Pipeline] Could not send WebSocket alert: {e}")


def start_scheduler():
    """Start the background scheduler."""
    global scheduler_started
    
    if scheduler_started:
        return
    
    try:
        # Add job to run every 6 hours
        scheduler.add_job(
            run_pipeline,
            'interval',
            hours=6,
            id='food_adulteration_pipeline',
            replace_existing=True
        )
        
        if not scheduler.running:
            scheduler.start()
            scheduler_started = True
            print("[Scheduler] Background scheduler started")
            
            # Run once immediately on startup
            print("[Scheduler] Running initial pipeline on startup...")
            run_pipeline()
    
    except Exception as e:
        print(f"[Scheduler] Error starting scheduler: {e}")


def stop_scheduler():
    """Stop the background scheduler."""
    global scheduler_started
    
    if scheduler.running:
        scheduler.shutdown()
        scheduler_started = False
        print("[Scheduler] Background scheduler stopped")
