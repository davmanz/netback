from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):
    help = "Crea o actualiza el CrontabSchedule + PeriodicTask para core.tasks.autoBackup"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hour", type=int, default=0, help="Hora (0-23) por defecto 0 (medianoche)"
        )
        parser.add_argument(
            "--minute", type=int, default=0, help="Minuto (0-59) por defecto 0"
        )
        parser.add_argument(
            "--timezone",
            type=str,
            default=getattr(settings, "TIME_ZONE", "UTC"),
            help="Timezone (ej. Europe/Madrid) por defecto settings.TIME_ZONE",
        )
        parser.add_argument(
            "--name",
            type=str,
            default="autoBackup",
            help="Nombre del PeriodicTask (por defecto 'autoBackup')",
        )
        parser.add_argument(
            "--enabled",
            action="store_true",
            default=True,
            help="Habilitar el PeriodicTask creado",
        )
        parser.add_argument(
            "--dry-run", action="store_true", help="Mostrar qué se crearía sin aplicarlo"
        )

    def handle(self, *args, **options):
        hour = options["hour"]
        minute = options["minute"]
        tz = options["timezone"]
        name = options["name"]
        enabled = options.get("enabled", True)
        dry = options.get("dry_run", False)

        minute_s = str(minute)
        hour_s = str(hour)

        self.stdout.write(f"Creando/actualizando CrontabSchedule {hour_s}:{minute_s} ({tz})")

        if dry:
            self.stdout.write("--dry-run activado, no se aplicarán cambios")

        if not dry:
            schedule, created = CrontabSchedule.objects.update_or_create(
                minute=minute_s, hour=hour_s, timezone=tz
            )

            pt, created_pt = PeriodicTask.objects.update_or_create(
                name=name,
                defaults={
                    "task": "core.tasks.autoBackup",
                    "crontab": schedule,
                    "enabled": enabled,
                },
            )

            self.stdout.write(
                f"PeriodicTask '{name}' {'creado' if created_pt else 'actualizado'} (enabled={pt.enabled})"
            )
        else:
            self.stdout.write("dry-run: CrontabSchedule y PeriodicTask no fueron modificados")
