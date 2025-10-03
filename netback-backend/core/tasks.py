import logging
from concurrent.futures import ThreadPoolExecutor

from celery import shared_task
from django.utils.timezone import localtime, now

from .models import BackupSchedule, BackupStatus, NetworkDevice
from .network_util.backup import backupDevice

logger = logging.getLogger(__name__)


@shared_task
def autoBackup():
    """Ejecuta el respaldo automático según la hora configurada en BackupSchedule"""
    # Esta tarea debe ser programada desde django-celery-beat (PeriodicTask / CrontabSchedule)
    # y ejecutarse exactamente en la hora/minuto deseados. Antes la lógica verificaba
    # la hora en la BD; al delegar la programación a django-celery-beat eliminamos esa
    # comprobación frágil y permitimos que Beat dispare esta tarea en el momento correcto.

    logger.info("🔄 Celery ejecutó autoBackup() (invocado por celery-beat)")

    try:
        resultado = execute_backup_process()
        logger.info(f"📂 Resultado de los backups: {resultado}")
        return {"message": "Backups ejecutados.", "result": resultado}
    except Exception as e:
        logger.exception("❌ Error ejecutando backups automáticos")
        return {"error": str(e)}


def execute_backup_process():
    """Ejecuta los respaldos en todos los dispositivos"""

    logger.info("🚀 Ejecutando backups en dispositivos")

    devices = NetworkDevice.objects.all()

    if not devices:
        logger.warning("⚠ No hay dispositivos registrados para respaldar")
        return {"error": "No hay dispositivos para respaldar"}

    def backup_wrapper(device):
        logger.info(f"🔹 Iniciando backup para {device.hostname} ({device.ipAddress})")

        BackupStatus.objects.create(
            device=device, status="in_progress", message="Backup started."
        )
        result = backupDevice(device)

        BackupStatus.objects.create(
            device=device,
            status="completed" if result["success"] else "failed",
            message="Backup successful." if result["success"] else result["error"],
        )

        logger.info(f"✔ Backup finalizado para {device.hostname}: {result}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(backup_wrapper, devices)

    return {
        "success": True,
        "message": f"Backups completed for {len(devices)} devices.",
    }
