"""
PureCheck Multi-Agent Analysis Pipeline (Lightweight Implementation)
Implements a 4-agent system for collaborative food adulteration risk analysis.
Uses pure Python without external LLM dependencies for maximum reliability and speed.

Agents:
1. News Research Agent - Gathers intelligence from news sources
2. FSSAI Database Agent - Queries official regulatory database  
3. Risk Analysis Agent - Evaluates risk using ML models
4. Report Generator Agent - Synthesizes findings into actionable reports
"""

from typing import Dict, List
import json
from datetime import datetime, timedelta
from collections import defaultdict
from django.utils import timezone

from agent.scraper import fetch_news_articles, fetch_fssai_complaints
from agent.nlp_extractor import extract_entities
from agent.risk_scorer import calculate_risk_score_with_explanation
from core.models import Complaint, RiskScore, LiveAlert


class NewsResearchAgent:
    """Gathers and analyzes food safety incidents from news sources."""
    
    def __init__(self, cities: List[str]):
        self.cities = cities
        self.name = "News Research Analyst"
    
    def run(self) -> Dict:
        """Gather news intelligence from news sources."""
        print(f"\n[{self.name}] Gathering news intelligence from {len(self.cities)} cities...")
        
        all_articles = []
        incidents = []
        
        for city in self.cities:
            try:
                articles = fetch_news_articles(city)
                all_articles.extend(articles)
            except Exception as e:
                print(f"  [{self.name}] Error fetching news for {city}: {e}")
        
        # Analyze articles with NLP to extract incidents
        for article in all_articles[:10]:  # Limit to top 10 for analysis
            try:
                text = article.get('description') or article.get('title', '')
                entities = extract_entities(text)
                
                if entities['city'] != 'Unknown' and entities['adulterant'] != 'Unknown':
                    incidents.append({
                        'source': 'NEWS',
                        'city': entities['city'],
                        'food_item': entities['food_item'],
                        'adulterant': entities['adulterant'],
                        'severity': entities['severity'],
                        'confidence': entities.get('nlp_confidence', 0.5),
                        'date': article.get('published_at', datetime.now().isoformat()),
                        'title': article.get('title', '')[:100]
                    })
            except Exception as e:
                continue
        
        print(f"  [{self.name}] Identified {len(incidents)} food adulteration incidents")
        return {
            'name': self.name,
            'total_articles': len(all_articles),
            'incidents_identified': len(incidents),
            'incidents': incidents
        }


class FSSAIAgent:
    """Queries and analyzes official FSSAI regulatory database."""
    
    def __init__(self, cities: List[str]):
        self.cities = cities
        self.name = "FSSAI Database Specialist"
    
    def run(self) -> Dict:
        """Query FSSAI database for complaints."""
        print(f"\n[{self.name}] Querying FSSAI database for {len(self.cities)} cities...")
        
        try:
            fssai_complaints = fetch_fssai_complaints()
            
            # Analyze complaints by city and food type
            city_analysis = defaultdict(lambda: {'total': 0, 'foods': {}, 'adulterants': {}})
            
            for complaint in fssai_complaints:
                city = complaint.get('city', 'Unknown')
                food = complaint.get('food_item', 'Unknown')
                adulterant = complaint.get('adulterant', 'Unknown')
                
                city_analysis[city]['total'] += 1
                city_analysis[city]['foods'][food] = city_analysis[city]['foods'].get(food, 0) + 1
                city_analysis[city]['adulterants'][adulterant] = city_analysis[city]['adulterants'].get(adulterant, 0) + 1
            
            # Identify patterns
            patterns = {
                'repeated_offenders': {},
                'high_risk_foods': {},
                'geographic_hotspots': {}
            }
            
            for city, data in city_analysis.items():
                if data['total'] > 2:
                    patterns['geographic_hotspots'][city] = data['total']
                    
                for food, count in data['foods'].items():
                    if count > 2:
                        patterns['high_risk_foods'][food] = patterns['high_risk_foods'].get(food, 0) + count
            
            print(f"  [{self.name}] Analyzed {len(fssai_complaints)} FSSAI complaints")
            print(f"  [{self.name}] Identified patterns: {len(patterns['geographic_hotspots'])} hotspots, "
                  f"{len(patterns['high_risk_foods'])} high-risk foods")
            
            return {
                'name': self.name,
                'total_complaints': len(fssai_complaints),
                'city_analysis': dict(city_analysis),
                'patterns': patterns
            }
        except Exception as e:
            print(f"  [{self.name}] Error querying FSSAI: {e}")
            return {
                'name': self.name,
                'total_complaints': 0,
                'error': str(e)
            }


class RiskAnalysisAgent:
    """Evaluates risk using ML models."""
    
    def __init__(self, cities: List[str]):
        self.cities = cities
        self.name = "AI Risk Analysis Specialist"
    
    def run(self) -> Dict:
        """Calculate risk scores for city-food combinations."""
        print(f"\n[{self.name}] Calculating ML-based risk scores...")
        
        risk_assessments = []
        high_risk_count = 0
        
        for city in self.cities:
            try:
                # Get unique food items for this city
                complaints = Complaint.objects.filter(city__iexact=city).values_list('food_item', flat=True).distinct()
                
                for food_item in complaints:
                    try:
                        # Calculate risk with SHAP explanation
                        result = calculate_risk_score_with_explanation(city, food_item)
                        score = result['risk_score']
                        confidence = result['confidence']
                        
                        assessment = {
                            'city': city,
                            'food_item': food_item,
                            'risk_score': score,
                            'confidence': confidence,
                            'risk_level': 'HIGH' if score > 70 else 'MEDIUM' if score > 40 else 'LOW',
                            'complaint_count': Complaint.objects.filter(
                                city__iexact=city,
                                food_item__iexact=food_item
                            ).count(),
                            'trend': 'INCREASING' if score > 80 else 'STABLE'
                        }
                        
                        if score > 70:
                            high_risk_count += 1
                        
                        risk_assessments.append(assessment)
                    except Exception as e:
                        continue
            except Exception as e:
                continue
        
        # Sort by risk score
        risk_assessments.sort(key=lambda x: x['risk_score'], reverse=True)
        
        print(f"  [{self.name}] Analyzed {len(risk_assessments)} city-food combinations")
        print(f"  [{self.name}] Identified {high_risk_count} HIGH RISK combinations")
        
        return {
            'name': self.name,
            'total_assessments': len(risk_assessments),
            'high_risk_count': high_risk_count,
            'assessments': risk_assessments[:50]  # Top 50
        }


class ReportGeneratorAgent:
    """Synthesizes findings into actionable reports."""
    
    def __init__(self):
        self.name = "Executive Report Synthesizer"
    
    def run(self, news_data: Dict, fssai_data: Dict, risk_data: Dict) -> Dict:
        """Generate comprehensive report from all analysis."""
        print(f"\n[{self.name}] Synthesizing comprehensive report...")
        
        # Build report
        report = f"""# PureCheck Food Adulteration Risk Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

This automated analysis identifies critical food adulteration risks across Indian markets
using a combination of news intelligence, regulatory data, and ML-based predictions.

**Key Findings:**
- News Incidents Identified: {news_data.get('incidents_identified', 0)}
- FSSAI Complaints Analyzed: {fssai_data.get('total_complaints', 0)}
- High-Risk Combinations Detected: {risk_data.get('high_risk_count', 0)}

## 1. News Intelligence Analysis

Total Articles Analyzed: {news_data.get('total_articles', 0)}
Incidents Identified: {news_data.get('incidents_identified', 0)}

### Top Incidents:
"""
        
        for idx, incident in enumerate(news_data.get('incidents', [])[:5], 1):
            report += f"\n{idx}. **{incident['food_item']}** contaminated with {incident['adulterant']} in {incident['city']}\n"
            report += f"   - Severity: {'High' if incident['severity'] >= 4 else 'Medium' if incident['severity'] >= 2 else 'Low'}\n"
            report += f"   - Confidence: {incident['confidence']:.0%}\n"
        
        report += f"\n## 2. FSSAI Regulatory Analysis\n\n"
        report += f"Total Complaints: {fssai_data.get('total_complaints', 0)}\n"
        
        patterns = fssai_data.get('patterns', {})
        if patterns.get('geographic_hotspots'):
            report += f"\n### Geographic Hotspots:\n"
            for city, count in sorted(patterns['geographic_hotspots'].items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"- {city}: {count} complaints\n"
        
        if patterns.get('high_risk_foods'):
            report += f"\n### High-Risk Food Items:\n"
            for food, count in sorted(patterns['high_risk_foods'].items(), key=lambda x: x[1], reverse=True)[:5]:
                report += f"- {food}: {count} incidents\n"
        
        report += f"\n## 3. ML Risk Assessment Results\n\n"
        report += f"High-Risk Combinations: {risk_data.get('high_risk_count', 0)}\n"
        
        report += f"\n### Top 10 Highest Risk City-Food Combinations:\n"
        for idx, assessment in enumerate(risk_data.get('assessments', [])[:10], 1):
            report += f"\n{idx}. **{assessment['food_item']}** in **{assessment['city']}**\n"
            report += f"   - Risk Score: {assessment['risk_score']:.1f}/100\n"
            report += f"   - Confidence: {assessment['confidence']:.0%}\n"
            report += f"   - Risk Level: {assessment['risk_level']}\n"
            report += f"   - Complaints: {assessment['complaint_count']}\n"
            report += f"   - Trend: {assessment['trend']}\n"
        
        report += f"\n## 4. Recommended Actions (Priority Ranked)\n\n"
        
        high_risk = [a for a in risk_data.get('assessments', []) if a['risk_level'] == 'HIGH']
        
        for idx, assessment in enumerate(high_risk[:5], 1):
            report += f"{idx}. **URGENT: {assessment['food_item']} in {assessment['city']}** (Risk: {assessment['risk_score']:.1f})\n"
            report += f"   - Action: Immediate inspection and enforcement\n"
            report += f"   - Timeline: 24-48 hours\n"
            report += f"   - Resources: District FSSAI + regulatory team\n"
        
        report += f"\n## 5. Monitoring Plan\n\n"
        report += "- Daily: Monitor top 10 risk combinations\n"
        report += "- Weekly: Review trend analysis\n"
        report += "- Monthly: Full risk reassessment\n"
        report += "- Quarterly: Strategic review and planning\n"
        
        report += f"\n---\nReport Generated by: PureCheck AI System\n"
        report += f"Next Update: {(datetime.now() + timedelta(hours=6)).strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        print(f"  [{self.name}] Report generated ({len(report)} characters)")
        
        return {
            'name': self.name,
            'report': report,
            'summary': {
                'total_incidents': news_data.get('incidents_identified', 0),
                'fssai_complaints': fssai_data.get('total_complaints', 0),
                'high_risk_combinations': risk_data.get('high_risk_count', 0),
                'generated_at': datetime.now().isoformat()
            }
        }


class FoodAdulterationCrew:
    """
    Multi-agent crew for analyzing food adulteration risks.
    Orchestrates 4 specialized agents to provide comprehensive analysis.
    """
    
    def __init__(self, cities: List[str] = None):
        """Initialize the crew with configuration."""
        self.cities = cities or [
            'Trichy', 'Coimbatore', 'Chennai', 'Madurai', 'Salem',
            'Bangalore', 'Delhi', 'Mumbai', 'Pune', 'Hyderabad'
        ]
        
        # Initialize agents
        self.news_agent = NewsResearchAgent(self.cities)
        self.fssai_agent = FSSAIAgent(self.cities)
        self.risk_agent = RiskAnalysisAgent(self.cities)
        self.report_agent = ReportGeneratorAgent()
    
    def run_analysis(self) -> Dict:
        """
        Execute the crew to run full analysis pipeline.
        
        Returns:
            Dict containing crew results and generated report
        """
        print("\n" + "="*70)
        print("[CrewAI] Starting Food Adulteration Risk Analysis Pipeline")
        print(f"[CrewAI] Analyzing {len(self.cities)} cities")
        print("="*70)
        
        try:
            # Run agents sequentially
            print("\n[CrewAI] Phase 1/4: News Research...")
            news_results = self.news_agent.run()
            
            print("\n[CrewAI] Phase 2/4: FSSAI Analysis...")
            fssai_results = self.fssai_agent.run()
            
            print("\n[CrewAI] Phase 3/4: Risk Analysis...")
            risk_results = self.risk_agent.run()
            
            print("\n[CrewAI] Phase 4/4: Report Generation...")
            report_results = self.report_agent.run(news_results, fssai_results, risk_results)
            
            # Compile final analysis
            final_result = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'agents': 4,
                'cities_analyzed': len(self.cities),
                'news_analysis': news_results,
                'fssai_analysis': fssai_results,
                'risk_analysis': risk_results,
                'report': report_results['report'],
                'summary': report_results['summary']
            }
            
            print("\n" + "="*70)
            print("[CrewAI] Analysis Complete!")
            print("="*70 + "\n")
            
            return final_result
            
        except Exception as e:
            print(f"\n[CrewAI] Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
