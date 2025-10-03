from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from django_celery_beat.models import CrontabSchedule, PeriodicTask

from .models import BackupSchedule
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BackupSchedule)
def sync_autobackup_schedule(sender, instance, created, **kwargs):
    """Sincroniza BackupSchedule con django-celery-beat (CrontabSchedule + PeriodicTask).

    Es idempotente y usa update_or_create para evitar duplicados.
    """
    try:
        hour = instance.scheduled_time.hour
        minute = instance.scheduled_time.minute
    except Exception:
        logger.exception("BackupSchedule tiene scheduled_time inválido")
        return

    tz = getattr(settings, "TIME_ZONE", "UTC")

    # CrontabSchedule stores minute/hour as strings (supports lists/steps)
    schedule, _ = CrontabSchedule.objects.update_or_create(
        minute=str(minute),
        hour=str(hour),
        timezone=tz,
    )

    PeriodicTask.objects.update_or_create(
        name="autoBackup",
        defaults={
            "task": "core.tasks.autoBackup",
            "crontab": schedule,
            "enabled": getattr(instance, "enabled", True),
        },
    )


@receiver(post_delete, sender=BackupSchedule)
def remove_autobackup_schedule(sender, instance, **kwargs):
    try:
        pt = PeriodicTask.objects.get(name="autoBackup")
        # Preferir desactivar en lugar de eliminar para conservar historial
        pt.enabled = False
        pt.save()
    except PeriodicTask.DoesNotExist:
        pass
