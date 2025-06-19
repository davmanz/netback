import csv
import unicodedata
from io import TextIOWrapper

from django.conf import settings

from core.models import Area, Country, Site
from utils.zabbix_manager import ZabbixManager

count_none_country = 0
count_none_site = 0
count_none_area = 0


def normalize_text(text):
    """
    Normaliza texto para evitar problemas con tildes, mayúsculas y espacios.
    """
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text.strip().lower())


def build_area_cache():
    """Carga todos los países, sitios y áreas en caché para búsquedas rápidas."""

    countries = {normalize_text(c.name): c for c in Country.objects.all()}
    sites = {(normalize_text(s.name), s.country_id): s for s in Site.objects.all()}
    areas = {(normalize_text(a.name), a.site_id): a for a in Area.objects.all()}

    return {
        "countries": countries,
        "sites": sites,
        "areas": areas,
    }


def resolve_area_id_cached(classified_fields: dict, cache: dict):
    """
    Determina el área más específica posible usando datos precargados y jerarquía coherente.
    """
    country_name = (classified_fields.get("country") or "").lower().strip()
    site_name = (classified_fields.get("site") or "").lower().strip()
    area_name = (classified_fields.get("area") or "").lower().strip()

    countries = cache["countries"]
    sites = cache["sites"]
    areas = cache["areas"]

    # Buscar país (exacto o "Desconocido")
    country = countries.get(country_name)
    if not country:
        country = countries.get("desconocido")
        if not country:
            return None  # No hay ni siquiera país desconocido

    # Buscar sitio (exacto o "Desconocido" del país)
    site = sites.get((site_name, country.id))
    if not site:
        site = sites.get(("desconocido", country.id))

        if not site:
            return None  # No hay sitio válido

    # Buscar área (exacta o "Desconocido" del sitio)
    area = areas.get((area_name, site.id))

    if not area:
        area = areas.get(("desconocido", site.id))

    return area


class HostClassifier:
    def __init__(self, rules: dict):
        self.rules = rules
        self.area_cache = build_area_cache()

    def classify_host(self, host: dict) -> dict:
        classification = {}
        missing = []

        sources = {
            "hostname": host.get("hostname", "").lower(),
            "tags": (host.get("tags") or "").lower(),
            "groups": [g.lower() for g in host.get("groups", set())],
            "model": host.get("model", "").lower(),
        }

        for field, field_rules in self.rules.items():
            matched = None
            for rule in field_rules:
                value = rule.get("value", "").lower()
                assign = rule.get("assign")
                search_in = rule.get("searchIn", [])

                for source in search_in:
                    if source == "groups" and any(
                        value in g for g in sources["groups"]
                    ):
                        matched = assign
                        break
                    elif source == "tags" and value in sources["tags"]:
                        matched = assign
                        break
                    elif source == "hostname" and value in sources["hostname"]:
                        matched = assign
                        break
                    elif source == "model" and value in sources["model"]:
                        matched = assign
                        break
                if matched:
                    break

            if matched:
                classification[field] = matched
            else:
                classification[field] = "Desconocido"
                missing.append(field)

        # ✅ Añadir resolución de área directamente
        area_obj = resolve_area_id_cached(classification, self.area_cache)

        return {
            "hostname": host.get("hostname"),
            "ip": host.get("ip"),
            "model": host.get("model"),
            "manufacturer": classification.get("manufacturer"),
            "deviceType": classification.get("deviceType"),
            "classification": classification,
            "area": {
                "id": str(area_obj.id) if area_obj else None,
                "name": str(area_obj) if area_obj else None,
            },
            "missing": missing,
        }

    def classify_all(self, hosts: list) -> list:
        return [self.classify_host(host) for host in hosts]

# # Zabbix Integration
def get_hosts_from_zabbix() -> list:

    zabbix_url = settings.ZABBIX_URL
    zabbix_token = settings.ZABBIX_TOKEN

    if not zabbix_url or not zabbix_token:
        raise ValueError("Faltan variables de entorno ZABBIX_URL o ZABBIX_TOKEN.")

    try:
        zm = ZabbixManager(url=zabbix_url, token=zabbix_token)
        zm.connect()
        hosts = zm.get_processed_hosts()
    except Exception as e:
        raise ValueError(f"No se pudo conectar con Zabbix: {str(e)}")

    return hosts
# # CSV Integration
def get_hosts_from_csv(file) -> list:
    """
    Parsea un archivo CSV con hosts y devuelve una lista de diccionarios estandarizados.
    """
    hosts = []
    reader = csv.DictReader(TextIOWrapper(file, encoding="utf-8"))

    for row in reader:
        hosts.append(
            {
                "hostname": row.get("hostname", "").strip(),
                "ip": row.get("ip", "").strip(),
                "groups": set(
                    g.strip().lower() for g in row.get("groups", "").split(";") if g
                ),
                "tags": row.get("tags", "").strip().lower(),
                "model": row.get("model", "").strip(),
            }
        )

    return hosts
