import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

celery_app = Celery("backend")
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()


celery_app.conf.beat_schedule = {
    "check_backup_time": {
        "task": "core.tasks.autoBackup",
        "schedule": crontab(minute="*"),  # Se ejecuta cada minuto
    },
}
