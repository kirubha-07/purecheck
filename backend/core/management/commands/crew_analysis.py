from django.core.management.base import BaseCommand
from agent.crew_pipeline_v2 import FoodAdulterationCrew


class Command(BaseCommand):
    help = 'Run the multi-agent analysis pipeline for food adulteration risks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cities',
            type=str,
            default='',
            help='Comma-separated list of cities to analyze (default: all configured cities)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='markdown',
            choices=['json', 'markdown', 'text'],
            help='Output format for the report'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('\nStarting Multi-Agent Food Adulteration Analysis Pipeline...\n')
        )
        
        # Get cities
        cities = None
        if options['cities']:
            cities = [city.strip() for city in options['cities'].split(',')]
            self.stdout.write(f"Analyzing cities: {', '.join(cities)}\n")
        
        # Initialize and run crew
        crew = FoodAdulterationCrew(cities=cities)
        result = crew.run_analysis()
        
        # Display results
        if result['status'] == 'success':
            self.stdout.write(self.style.SUCCESS('\nAnalysis completed successfully!\n'))
            
            if options['format'] == 'markdown':
                # Display the markdown report
                self.stdout.write(result['report'])
            elif options['format'] == 'json':
                import json
                # Create JSON output with report included
                json_output = {
                    'status': result['status'],
                    'timestamp': result['timestamp'],
                    'summary': result['summary'],
                    'high_risk_combinations': result['risk_analysis'].get('high_risk_count', 0),
                    'top_risks': result['risk_analysis'].get('assessments', [])[:10]
                }
                self.stdout.write(json.dumps(json_output, indent=2))
            else:
                # Text summary
                self.stdout.write(f"News Incidents: {result['summary'].get('total_incidents', 0)}")
                self.stdout.write(f"FSSAI Complaints: {result['summary'].get('fssai_complaints', 0)}")
                self.stdout.write(f"High Risk Combinations: {result['summary'].get('high_risk_combinations', 0)}")
        else:
            self.stdout.write(
                self.style.ERROR(f"\nAnalysis failed: {result.get('error', 'Unknown error')}")
            )
