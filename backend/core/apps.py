from django.apps import AppConfig
import logging
import os
import sys
import threading


logger = logging.getLogger(__name__)
_scheduler_boot_lock = threading.Lock()
_scheduler_booted = False


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
    def ready(self):
        """Run startup checks when Django app is ready."""
        global _scheduler_booted

        # Start scheduler only for runserver process, never for migrate/shell/test commands.
        if 'runserver' not in sys.argv:
            return

        try:
            from agent.risk_scorer import get_ml_runtime_status

            status = get_ml_runtime_status()
            logger.info(
                "[Startup] ML status -> mode=%s model_loaded=%s shap_enabled=%s",
                status['mode'],
                status['model_loaded'],
                status['shap_enabled'],
            )
        except Exception as exc:
            logger.warning("[Startup] Could not evaluate ML status: %s", exc)

        # Prevent duplicate scheduler startup under Django autoreload parent process.
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return

        with _scheduler_boot_lock:
            if _scheduler_booted:
                return
            _scheduler_booted = True

        def _start_scheduler_thread():
            try:
                from agent.scheduler import start_scheduler
                start_scheduler()
            except Exception as exc:
                logger.warning("[Startup] Could not start scheduler: %s", exc)

        threading.Thread(
            target=_start_scheduler_thread,
            name='purecheck-scheduler-bootstrap',
            daemon=True,
        ).start()
