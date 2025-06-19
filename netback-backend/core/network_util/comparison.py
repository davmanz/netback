import difflib
from typing import Any, Dict

from core.models import Backup, BackupDiff

from .backup import section_config
from .vlan_parser import parse_vlan_brief


def compare_vlan_briefs(old_vlan_brief, new_vlan_brief, manufacturer) -> Dict[str, Any]:

    old_parsed = parse_vlan_brief(old_vlan_brief, manufacturer)
    new_parsed = parse_vlan_brief(new_vlan_brief, manufacturer)

    if not isinstance(old_parsed, dict) or not isinstance(new_parsed, dict):
        return {"error": f"Error en parsing VLANs para {manufacturer}"}

    old_vlan_ports = old_parsed.get("ports_vlan", {})
    new_vlans = new_parsed.get("vlans", {})
    new_vlan_ports = new_parsed.get("ports_vlan", {})

    ports_vlan = {}

    for vlan in set(old_vlan_ports.keys()).union(new_vlan_ports.keys()):
        old_ports = set(old_vlan_ports.get(vlan, []))
        new_ports = set(new_vlan_ports.get(vlan, []))

        added_ports = list(new_ports - old_ports)
        removed_ports = list(old_ports - new_ports)

        if added_ports or removed_ports:
            ports_vlan[vlan] = {"assigned": added_ports, "removed": removed_ports}

    return {"vlans": new_vlans, "ports_vlan": ports_vlan}


def generate_backup_diff(backupOld, backupNew):
    old_config = backupOld.runningConfig
    new_config = backupNew.runningConfig
    old_vlan_brief = backupOld.vlanBrief
    new_vlan_brief = backupNew.vlanBrief

    manufacturer = backupOld.device.manufacturer.name
    vlan_info = compare_vlan_briefs(old_vlan_brief, new_vlan_brief, manufacturer)
    if "error" in vlan_info:
        return {"success": False, "error": vlan_info["error"]}

    old_sections = section_config(old_config)
    new_sections = section_config(new_config)

    added_sections, removed_sections, modified_sections = [], [], []
    old_dict = {sec[0]: sec[1] for sec in old_sections}
    new_dict = {sec[0]: sec[1] for sec in new_sections}
    all_section_names = sorted(set(old_dict.keys()).union(set(new_dict.keys())))

    for section in all_section_names:
        old_content = old_dict.get(section, [])
        new_content = new_dict.get(section, [])

        if not old_content:
            added_sections.append({section: ["++ " + line for line in new_content]})
            continue

        if not new_content:
            removed_sections.append({section: ["-- " + line for line in old_content]})
            continue

        diff = list(difflib.ndiff(old_content, new_content))
        formatted_diff = []
        for line in diff:
            if line.startswith("- "):
                formatted_diff.append(f"-- {line[2:]}")
            elif line.startswith("+ "):
                formatted_diff.append(f"++ {line[2:]}")
            else:
                formatted_diff.append(line[2:])
        if any(
            line.startswith("--") or line.startswith("++") for line in formatted_diff
        ):
            modified_sections.append({section: formatted_diff})

    try:
        backupDiff = BackupDiff.objects.create(
            device=backupOld.device,
            backupOld=backupOld,
            backupNew=backupNew,
            changes=str(
                {
                    "added": added_sections,
                    "removed": removed_sections,
                    "modified": modified_sections,
                    "vlanInfo": vlan_info,
                }
            ),
            structured_changes={
                "added": added_sections,
                "removed": removed_sections,
                "modified": modified_sections,
                "vlanInfo": vlan_info,
            },
        )
        return {
            "success": True,
            "backupDiffId": str(backupDiff.id),
            "changes": backupDiff.structured_changes,
        }
    except Exception as e:
        return {"success": False, "error": f"Error al crear BackupDiff: {str(e)}"}


def compareBackups(device):
    backups = Backup.objects.filter(device=device).order_by("-backupTime")[:2]
    if len(backups) < 2:
        return {"error": "Not enough backups to compare"}
    return generate_backup_diff(backups[1], backups[0])


def compareSpecificBackups(backupOld, backupNew):
    if backupOld.device != backupNew.device:
        return {"error": "Both backups must belong to the same device"}
    return generate_backup_diff(backupOld, backupNew)
