from django.core.management.base import BaseCommand
from django.conf import settings
from agent.scheduler import run_pipeline


class Command(BaseCommand):
    help = 'Manually run the food adulteration detection pipeline'

    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run pipeline once and exit'
        )

    def handle(self, *args, **options):
        if options['once']:
            self.stdout.write(self.style.SUCCESS('Running pipeline once...'))
            run_pipeline()
            self.stdout.write(self.style.SUCCESS('Pipeline completed!'))
        else:
            # Start the scheduler
            from agent.scheduler import start_scheduler
            self.stdout.write(self.style.SUCCESS(f'Starting background scheduler (runs every {settings.PIPELINE_INTERVAL_MINUTES} minutes)...'))
            try:
                start_scheduler()
                # Keep the process alive
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Scheduler stopped'))
