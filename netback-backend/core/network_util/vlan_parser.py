import re


# 📌 Parsing de VLANs
def parse_vlan_brief(vlan_brief, manufacturer):
    """
    Parsea la información de VLANs basada en el fabricante.
    """

    if manufacturer == "Cisco":
        return parse_vlan_cisco(vlan_brief)
    elif manufacturer == "Huawei":
        return parse_vlan_huawei(vlan_brief)
    elif manufacturer in ["HP", "Dell", "Extreme", "Arista"]:
        return parse_vlan_generic(vlan_brief)
    else:
        # ✅ Si la marca no es reconocida, asegurar que se devuelve un diccionario válido
        return {
            "vlans": {},
            "ports_vlan": {},
            "error": f"Parsing no soportado para {manufacturer}",
        }


# 📌 Parsing para Cisco (show vlan brief)
def parse_vlan_cisco(vlan_brief):
    vlan_dict = {}
    vlan_names = {}
    current_vlan = None

    for line in vlan_brief.splitlines():
        line = line.strip()

        if (
            not line
            or line.startswith("VLAN")
            or line.startswith("----")
            or "act/unsup" in line
        ):
            continue

        match = re.match(r"^(\d+)\s+(\S+)\s+(active)\s+(.+)?", line)
        if match:
            vlan_id, vlan_name, status, interfaces = match.groups()
            vlan_names[vlan_id] = vlan_name
            vlan_dict[vlan_id] = (
                interfaces.replace("+", "").strip().split(", ") if interfaces else []
            )
            current_vlan = vlan_id
            continue

        if current_vlan and re.match(r"^\s+Gi\d+/\d+/\d+", line):
            vlan_dict[current_vlan].extend(line.replace("+", "").strip().split(", "))

    return {"vlans": vlan_names, "ports_vlan": vlan_dict}


# 📌 Parsing para Huawei (display vlan)
def parse_vlan_huawei(vlan_brief):
    vlan_dict = {}
    vlan_names = {}

    lines = vlan_brief.splitlines()
    current_vlan = None

    for line in lines:
        line = line.strip()

        match = re.match(r"^VLAN ID:\s*(\d+)", line)
        if match:
            current_vlan = match.group(1)
            vlan_dict[current_vlan] = []
            continue

        match = re.match(r"^Name\s*:\s*(\S+)", line)
        if match and current_vlan:
            vlan_names[current_vlan] = match.group(1)

        # ✅ Ajuste aquí para soportar "Ports:" además de "Untagged ports:"
        match = re.match(r"^(Untagged ports|Ports):\s*(.+)", line)
        if match and current_vlan:
            vlan_dict[current_vlan].extend(match.group(2).split())

    return {"vlans": vlan_names, "ports_vlan": vlan_dict}


# 📌 Parsing genérico para HP, Dell, Extreme y Arista
def parse_vlan_generic(vlan_brief):
    vlan_dict = {}
    vlan_names = {}

    lines = vlan_brief.splitlines()
    current_vlan = None

    for line in lines:
        line = line.strip()

        match = re.match(r"^(\d+)\s+(\S+)", line)
        if match:
            vlan_id, vlan_name = match.groups()
            vlan_names[vlan_id] = vlan_name
            vlan_dict[vlan_id] = []
            current_vlan = vlan_id
            continue

        if current_vlan and re.match(r"^\s+(eth\d+/\d+)", line):
            vlan_dict[current_vlan].append(line.strip())

    return {"vlans": vlan_names, "ports_vlan": vlan_dict}
