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

    logger.info("🔄 Celery ejecutó autoBackup()")

    schedule = BackupSchedule.objects.first()
    if not schedule:
        logger.warning("❌ No hay hora programada en la BD")
        return {"error": "No se ha configurado una hora para el respaldo automático"}

    # Obtener la hora programada con la zona horaria correcta
    current_time = localtime(now()).time()
    scheduled_time = schedule.scheduled_time

    if (
        current_time.hour == scheduled_time.hour
        and current_time.minute == scheduled_time.minute
    ):
        logger.info("✅ Ejecutando respaldos")
        resultado = execute_backup_process()
        logger.info(f"📂 Resultado de los backups: {resultado}")
        return {"message": "Backups ejecutados."}

    return {"message": "No es la hora programada aún."}


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
