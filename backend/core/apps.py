from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """Start the scheduler when Django app is ready."""
        # Disabled automatic startup for now - use management command instead
        # try:
        #     from agent.scheduler import start_scheduler
        #     start_scheduler()
        # except Exception as e:
        #     print(f"Warning: Could not start scheduler: {e}")
