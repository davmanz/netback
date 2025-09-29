import hashlib

from django.utils import timezone
from netmiko import ConnectHandler

from core.models import Backup, BackupStatusTracker

from .vlan_parser import parse_vlan_brief


def section_config(config):
    """Divide la configuración en bloques estructurados basados en títulos de secciones."""
    sections = []
    current_section = None
    section_lines = []

    for line in config.splitlines():
        if line.strip():
            if not line.startswith(" "):  # Nueva sección detectada
                if current_section:  # Guardar la sección anterior
                    sections.append((current_section, section_lines))
                current_section = line.strip()
                section_lines = []
            section_lines.append(line)

    if current_section:  # Guardar la última sección
        sections.append((current_section, section_lines))

    return sections


def backupDevice(device):
    commands = device.get_commands()
    results = {}

    connection = {
        "device_type": device.manufacturer.netmiko_type or "generic",
        "host": device.ipAddress,
        "username": device.customUser or device.vaultCredential.username,
        "password": device.customPass or device.vaultCredential.get_plain_password(),
    }

    # Obtener o crear el tracker
    tracker, _ = BackupStatusTracker.objects.get_or_create(device=device)

    try:
        with ConnectHandler(**connection) as net_connect:
            results["runningConfig"] = net_connect.send_command(
                commands["runningConfig"]
            )
            results["vlanBrief"] = net_connect.send_command(commands["vlanBrief"])

        parsed_vlan = parse_vlan_brief(results["vlanBrief"], device.manufacturer.name)

        data_hash = f'{results["runningConfig"]}{results["vlanBrief"]}'

        checksum = hashlib.sha256(data_hash.encode()).hexdigest()

        if Backup.objects.filter(device=device, checksum=checksum).exists():
            tracker.success_count = 0
            tracker.error_count = 0
            tracker.no_change_count += 1
            tracker.last_status = "unchanged"
            tracker.save()
            return {"success": True, "message": "No Changes. Backup not created."}

        backup = Backup.objects.create(
            device=device,
            backupTime=timezone.now(),
            runningConfig=results["runningConfig"],
            vlanBrief=results["vlanBrief"],
            checksum=checksum,
        )

        tracker.no_change_count = 0
        tracker.error_count = 0
        tracker.success_count += 1
        tracker.last_status = "success"
        tracker.save()

        return {"success": True, "backupId": backup.id, "parsed_vlan": parsed_vlan}

    except Exception as e:
        tracker.success_count = 0
        tracker.no_change_count = 0
        tracker.error_count += 1
        tracker.last_status = "error"
        tracker.save()
        return {"success": False, "error": str(e)}
