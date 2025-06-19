from cryptography.fernet import Fernet
from django.conf import settings


def get_encryption_cipher():
    key = getattr(settings, "ENCRYPTION_KEY_VAULT", None)
    if not key:
        raise ValueError("❌ ENCRYPTION_KEY_VAULT no está definida en settings.py o en las variables de entorno.")
    return Fernet(key.encode())


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
