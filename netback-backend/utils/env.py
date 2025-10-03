from cryptography.fernet import Fernet
from django.conf import settings


def get_encryption_cipher():
    key = getattr(settings, "ENCRYPTION_KEY_VAULT", None)
    if not key:
        raise ValueError("❌ ENCRYPTION_KEY_VAULT no está definida en settings.py o en las variables de entorno.")
    return Fernet(key.encode())

def get_fernet():
    """Devuelve un objeto Fernet o None si no hay clave válida.

    Esta función es tolerante: no lanza excepción si la clave no está presente o
    está mal formada; en su lugar devuelve None para que el código que la use
    pueda decidir el comportamiento en tiempo de ejecución.
    """
    key = getattr(settings, "ENCRYPTION_KEY_VAULT", None)
    if not key:
        return None
    try:
        # Aceptar tanto str como bytes
        key_bytes = key.encode() if isinstance(key, str) else key
        return Fernet(key_bytes)
    except Exception:
        return None


def get_zabbix_url():
    url = getattr(settings, "ZABBIX_URL", None)
    if not url:
        raise ValueError("❌ ZABBIX_URL no está definida.")
    return url

def get_zabbix_token():
    token = getattr(settings, "ZABBIX_TOKEN", None)
    if not token:
        raise ValueError("❌ ZABBIX_TOKEN no está definido.")
    return token
