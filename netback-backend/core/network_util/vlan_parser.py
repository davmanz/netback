import re
import json
import os


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


# 📌 Parsing para Huawei (display vlan) - VERSIÓN MEJORADA
def parse_vlan_huawei(vlan_brief):
    """
    Parsea la salida de 'display vlan' de Huawei que presenta la información
    en dos tablas separadas (puertos y descripciones).
    """
    ports_by_vlan = {}
    names_by_vlan = {}
    lines = vlan_brief.splitlines()

    in_ports_table = False
    in_description_table = False
    current_vlan_id = None

    for line in lines:
        if "VID  Type    Ports" in line:
            in_ports_table = True
            in_description_table = False
            continue
        if "VID  Status  Property" in line:
            in_ports_table = False
            in_description_table = True
            continue

        if in_ports_table:
            match = re.match(r"^\s*(\*?\d+)\s+\w+\s+(.*)", line)
            if match:
                current_vlan_id, ports_str = match.groups()
                current_vlan_id = current_vlan_id.replace('*', '')
                ports_by_vlan[current_vlan_id] = ports_str.strip().split()
            elif current_vlan_id and line.startswith("                "):
                ports_by_vlan.setdefault(current_vlan_id, []).extend(line.strip().split())

        if in_description_table:
            match = re.match(r"^\s*(\d+)\s+.*\s+(\S+)$", line)
            if match:
                vlan_id, description = match.groups()
                names_by_vlan[vlan_id] = description

    cleaned_ports = {}
    for vlan_id, ports in ports_by_vlan.items():
        cleaned_list = [re.sub(r"^(UT:|TG:)", "", port).strip() for port in ports]
        cleaned_list = [re.sub(r"\([UD]\)$", "", port).strip() for port in cleaned_list]
        cleaned_ports[vlan_id] = cleaned_list

    final_vlans = {}
    for vlan_id in cleaned_ports:
        final_vlans[vlan_id] = names_by_vlan.get(vlan_id, f"VLAN_{vlan_id}")

    return {"vlans": final_vlans, "ports_vlan": cleaned_ports}


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


# --- FUNCIÓN DE PRUEBA LOCAL ---
def test_parsers_from_files():
    """
    Función de prueba local que carga la configuración desde archivos de texto,
    ejecuta los parsers y muestra el resultado de forma legible.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cisco_file = os.path.join(current_dir, "config-cisco.txt")
    huawei_file = os.path.join(current_dir, "config_huawei.txt")

    print("--- INICIANDO PRUEBAS LOCALES DEL PARSER ---")

    print("\n--- Probando parser de Cisco ---")
    try:
        with open(cisco_file, "r") as f:
            cisco_data = f.read()
        parsed_cisco = parse_vlan_cisco(cisco_data)
        print(json.dumps(parsed_cisco, indent=2))
        print("✅ Parser de Cisco ejecutado con éxito.")
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo de prueba: {cisco_file}")
    except Exception as e:
        print(f"❌ ERROR: Ocurrió un error al parsear la configuración de Cisco: {e}")

    print("\n--- Probando parser de Huawei ---")
    try:
        with open(huawei_file, "r") as f:
            huawei_data = f.read()
        parsed_huawei = parse_vlan_huawei(huawei_data)
        print(json.dumps(parsed_huawei, indent=2))
        print("✅ Parser de Huawei ejecutado con éxito.")
    except FileNotFoundError:
        print(f"❌ ERROR: No se encontró el archivo de prueba: {huawei_file}")
    except Exception as e:
        print(f"❌ ERROR: Ocurrió un error al parsear la configuración de Huawei: {e}")

    print("\n--- PRUEBAS LOCALES FINALIZADAS ---")


if __name__ == "__main__":
    test_parsers_from_files()
