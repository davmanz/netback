# README_CORRECIONES.md

## 📌 Resumen ejecutivo

Auditoría completa del stack **Netback** (Backend Django + Celery, Proxy FastAPI, Frontend React/Nginx y Docker Compose).
Este documento resume **hallazgos**, su **criticidad**, **archivos afectados** y **acciones concretas** para corregirlos, **incluyendo implementaciones sugeridas** para referencia futura.

---

## 🔴 Prioridad ALTA
(CORREGIDO)
### 1) Bug al crear/actualizar `NetworkDevice` (la validación no detiene el guardado)
- **Síntoma:** En `perform_create`/`perform_update` se retorna `Response(...)`. DRF **ignora** ese retorno y el objeto puede guardarse aunque haya error.
- **Impacto:** Riesgo de datos inválidos en BD.
- **Archivos implicados:**
  - `netback-backend/core/views.py`
  - `netback-backend/core/serializers.py`
- **Corrección implementada:** La validación debe residir en el **serializer** (lanzando `serializers.ValidationError` ante datos inválidos). Los métodos
  `perform_create` y `perform_update` del `ModelViewSet` deben limitarse a llamar `serializer.save()` para que DRF maneje las excepciones de validación.

**`netback-backend/core/views.py` (asegurar que se vea así):**
```python
from rest_framework import viewsets

class NetworkDeviceViewSet(viewsets.ModelViewSet):
    # ... queryset, serializer_class, permission_classes

    def perform_create(self, serializer):
        # La validación se realiza en el serializer
        serializer.save()

    def perform_update(self, serializer):
        # La validación se realiza en el serializer
        serializer.save()
```

**`netback-backend/core/serializers.py` (ejemplo de validación en serializer):**
```python
from rest_framework import serializers
from core.models import NetworkDevice

class NetworkDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDevice
        fields = "__all__"  # o los campos específicos

    def validate(self, data):
        # Ejemplo: asegurar IP única
        ip_address = data.get("ipAddress")
        if ip_address and NetworkDevice.objects.filter(ipAddress=ip_address).exists():
            raise serializers.ValidationError({"ipAddress": "Ya existe un dispositivo con esta dirección IP."})
        return data
```

> **Nota:** Si alguna validación solo puede hacerse en el viewset, **levantar** `serializers.ValidationError` en lugar de retornar `Response`.

---
(CORREGIDO)
### 2) Atributo mal escrito rompe comandos remotos
- **Síntoma:** Se usa `device.VaultCredential` (V mayúscula) en lugar de `device.vaultCredential`. Lanza `AttributeError`.
- **Impacto:** Falla la ejecución de comandos (Netmiko).
- **Archivos implicados:**
  - `netback-backend/core/network_util/executor.py`
- **Corrección implementada:** Corregir el nombre del atributo a `device.vaultCredential` (con **v** minúscula) y validar credenciales antes de conectar.

**`netback-backend/core/network_util/executor.py` (asegurar que se vea así):**
```python
from netmiko import ConnectHandler

def executeCommandOnDevice(device, command):
    # Validación de credenciales
    if not (device.customUser and device.customPass) and not device.vaultCredential:
        return "No credentials found for this device"

    connection = {
        "device_type": device.manufacturer.netmiko_type or "cisco_ios",
        "host": device.ipAddress,
        "username": device.customUser or device.vaultCredential.username,
        "password": device.customPass or device.vaultCredential.get_plain_password(),
    }

    try:
        with ConnectHandler(**connection) as conn:
            return conn.send_command(command)
    except Exception as e:
        # Manejo de errores de conexión o de ejecución del comando
        return f"Error ejecutando comando en {device.ipAddress}: {e}"
```

---
(CORREGIDO)
### 3) `BackupStatusTracker.last_status` usa valores fuera de las *choices*
- **Síntoma:** Se asigna `success_no_changes`/`success_with_changes`, pero las choices del modelo son `success | unchanged | error`.
- **Impacto:** Inconsistencia y posibles datos inválidos.
- **Archivos implicados:**
  - `netback-backend/core/models.py`
  - `netback-backend/core/network_util/backup.py`
- **Corrección implementada:** Asegurar que `last_status` use **solo** `success`, `unchanged` o `error`.

**`netback-backend/core/models.py` (asegurar que las choices estén definidas):**
```python
from django.db import models

class BackupStatusTracker(models.Model):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("unchanged", "Unchanged"),
        ("error", "Error"),
    ]
    # ... otros campos
    last_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unchanged")
    # ...
```

**`netback-backend/core/network_util/backup.py` (fragmento corregido):**
```python
from core.models import Backup, BackupStatusTracker

def perform_backup_logic(device):
    # ... lógica para determinar si hay cambios o no
    checksum = "some_checksum"  # ejemplo

    tracker, _ = BackupStatusTracker.objects.get_or_create(device=device)

    if Backup.objects.filter(device=device, checksum=checksum).exists():
        tracker.success_count = 0
        tracker.error_count = 0
        tracker.no_change_count += 1
        tracker.last_status = "unchanged"  # ✅
        tracker.save()
        return {"success": True, "message": "No Changes. Backup not created."}
    else:
        # Lógica para crear un nuevo backup
        # ...
        tracker.no_change_count = 0
        tracker.error_count = 0
        tracker.success_count += 1
        tracker.last_status = "success"  # ✅
        tracker.save()
        return {"success": True, "message": "New backup created."}
```

---

### 4) *autoBackup* con Celery Beat no se está programando
- **Síntoma:** En Docker se usa `DatabaseScheduler` de `django_celery_beat`, pero no existe la `PeriodicTask` correspondiente. El `beat_schedule` en código no
  aplica con ese scheduler.
- **Impacto:** `autoBackup` no se ejecuta automáticamente.
- **Archivos implicados:**
  - `netback-backend/backend/celery.py`
  - `docker-compose.yml` (servicio `celery-beat`)
- **Corrección implementada:** Mantener `DatabaseScheduler` y **crear** la `PeriodicTask` para `core.tasks.autoBackup` mediante un comando de management o script de init.

**`netback-backend/backend/celery.py` (usar DatabaseScheduler):**
```python
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

app = Celery("backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Scheduler django-celery-beat
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
```

**Comando de Management (ejecutar una vez):**
```python
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from django.utils import timezone

# Ejecutar cada minuto (ajustar según necesidad)
sched, _ = CrontabSchedule.objects.get_or_create(
    minute="*", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"
)

PeriodicTask.objects.get_or_create(
    name="autoBackup-every-minute",
    task="core.tasks.autoBackup",
    crontab=sched,
    defaults={
        "enabled": True,
        "args": "[]",
        "kwargs": "{}",
        "expires": None,
        "start_time": timezone.now(),
    },
)
print("PeriodicTask 'autoBackup-every-minute' asegurada.")
```

**`docker-compose.yml` (servicio `celery-beat`):**
```yaml
services:
  celery-beat:
    build:
      context: ./netback-backend
      dockerfile: Dockerfile
    command: celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    env_file:
      - ./.env
    depends_on:
      - db
```

> **Nota:** Ejecuta la creación de la `PeriodicTask` **después** de migrar la base de datos.

---

### 5) Volumen `app:/app` en Docker Compose vacía el código del backend
- **Síntoma:** `app:/app` en `backend`/`celery`/`celery-beat` **enmascara** el código de la imagen.
- **Impacto:** El contenedor queda sin `manage.py` ni código.
- **Archivos implicados:**
  - `docker-compose.yml`
- **Corrección implementada:** Eliminar el volumen problemático. Si se necesita persistencia, montar rutas **granulares** (p. ej., `/app/data`).

**`docker-compose.yml` (ejemplo sin `app:/app`):**
```yaml
services:
  backend:
    build:
      context: ./netback-backend
      dockerfile: Dockerfile
    command: /usr/local/bin/gunicorn backend.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - ./netback-backend/data:/app/data  # si se necesita persistir datos específicos
    env_file:
      - ./.env
    depends_on:
      - db
    ports:
      - "8000:8000"

  celery:
    build:
      context: ./netback-backend
      dockerfile: Dockerfile
    command: celery -A backend worker -l info
    volumes:
      - ./netback-backend/data:/app/data
    env_file:
      - ./.env
    depends_on:
      - db

  celery-beat:
    build:
      context: ./netback-backend
      dockerfile: Dockerfile
    command: celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    volumes:
      - ./netback-backend/data:/app/data
    env_file:
      - ./.env
    depends_on:
      - db
```

> **Importante:** Asegúrate de que el `Dockerfile` del backend copie todo el código a `/app` dentro de la imagen.

---

### 6) Healthcheck del Proxy (FastAPI) inexistente
- **Síntoma:** `docker-compose` chequea `http://localhost:8080/health/`, pero el proxy no expone esa ruta.
- **Impacto:** Healthcheck falla aunque el servicio esté arriba.
- **Archivos implicados:**
  - `netback-proxy/main.py`
  - `docker-compose.yml`
- **Corrección implementada:** Añadir endpoint `/health/` en el proxy y apuntar el `healthcheck` a esa ruta.

**`netback-proxy/main.py` (añadir endpoint):**
```python
from fastapi import FastAPI

app = FastAPI()

# ... otros endpoints

@app.get("/health/")
def health():
    return {"status": "ok"}
```

**`docker-compose.yml` (healthcheck para `proxy`):**
```yaml
services:
  proxy:
    build:
      context: ./netback-proxy
      dockerfile: Dockerfile
    command: uvicorn main:app --host 0.0.0.0 --port 8080
    ports:
      - "8080:8080"
    env_file:
      - ./.env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    depends_on:
      - backend
```

---

## 🟠 Prioridad MEDIA

### 7) Zona horaria inválida
- **Síntoma:** `TIME_ZONE = "America/Chile"` (no válido IANA).
- **Impacto:** Errores sutiles en tiempos/cron.
- **Archivo implicado:** `netback-backend/backend/settings.py`
- **Corrección implementada:** Usar un valor IANA válido (p. ej., `America/Santiago`) o tomarlo de variable de entorno.

**`netback-backend/backend/settings.py` (asegurar que se vea así):**
```python
from decouple import config
# ...
# TIME_ZONE = "America/Chile"  # ❌
TIME_ZONE = config("TIME_ZONE", default="America/Santiago")  # ✅
USE_TZ = True
```

---

### 8) CORS y `ALLOWED_HOSTS`
- **Síntoma:** `ALLOWED_HOSTS=['*']` (solo aceptable en dev). `CORS_ALLOWED_ORIGINS` incluye `http://localhost:3000`, pero el frontend puede servir en
  `http://localhost` vía Nginx.
- **Impacto:** Superficie de ataque mayor y CORS incongruente.
- **Archivos implicados:**
  - `netback-backend/backend/settings.py`
  - `netback-frontend/nginx.conf`
- **Corrección implementada:** Restringir `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` a valores específicos y seguros.

**`netback-backend/backend/settings.py` (ejemplo seguro):**
```python
from decouple import config

# Restringir ALLOWED_HOSTS (coma-separado)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# CORS (ajustar a tu despliegue)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost",
    "http://127.0.0.1",
    "https://yourfrontenddomain.com",
]
CORS_ALLOW_CREDENTIALS = True  # si usas cookies o auth headers
```

> **Nota:** Si el frontend no llama directo al backend (usa proxy `/api`), puedes reducir CORS.

---

### 9) `DEBUG` en FastAPI mal mapeado
- **Síntoma:** `DEBUG` se deriva de `FASTAPI_PROXY_URL` (typo).
- **Impacto:** Modo debug activado/desactivado incorrectamente.
- **Archivo implicado:** `netback-proxy/app/config.py`
- **Corrección implementada:** Usar variable de entorno dedicada `FASTAPI_PROXY_DEBUG`.

**`netback-proxy/app/config.py` (asegurar que se vea así):**
```python
import os

DEBUG: bool = os.getenv("FASTAPI_PROXY_DEBUG", "false").lower() == "true"  # ✅
```

Ejemplo de CORS en FastAPI:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000"],  # orígenes explícitos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
> Con `allow_credentials=True`, **no** usar `"*"` en `allow_origins`.

---

### 10) `SiteSerializer` y `AreaSerializer`: acceso `.id` sobre PK crudos
- **Síntoma:** En `validate`, `data.get("country").id`/`data.get("site").id` pueden ser UUIDs, no instancias → `AttributeError`.
- **Impacto:** Errores en validación.
- **Archivo implicado:** `netback-backend/core/serializers.py`
- **Corrección implementada:** Confiar en `PrimaryKeyRelatedField` y eliminar validaciones manuales que acceden a `.id`.

**`netback-backend/core/serializers.py` (ejemplo):**
```python
from rest_framework import serializers
from core.models import Site, Area

class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ["id", "name", "country"]  # 'country' se valida como PK por defecto

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ["id", "name", "site"]  # 'site' se valida como PK por defecto
```

> Para representaciones distintas, usar `SlugRelatedField`/`HyperlinkedRelatedField` según necesidad.

---

### 11) Zabbix Manager: no usar `exit()` en librerías
- **Síntoma:** `exit()` en `connect()` puede matar workers/servicios.
- **Impacto:** Caída inesperada de procesos.
- **Archivo implicado:** `netback-backend/utils/zabbix_manager.py`
- **Corrección implementada:** Registrar el error y **re-lanzar** la excepción.

**`netback-backend/utils/zabbix_manager.py` (fragmento):**
```python
from pyzabbix import ZabbixAPI

class ZabbixManager:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.zapi = None

    def connect(self):
        try:
            self.zapi = ZabbixAPI(self.url)
            self.zapi.login(self.user, self.password)
            print(f"✅ Conectado a Zabbix API en {self.url}")
            return True
        except Exception as e:
            print(f"❌ Error al conectar a Zabbix API en {self.url}: {e}")
            raise  # ✅ Re-lanzar para que el caller lo maneje
```

---

### 12) `entrypoint.sh`: gunicorn vs uvicorn
- **Síntoma:** `Dockerfile` define `CMD gunicorn ...`, pero `ENTRYPOINT` ejecuta `uvicorn` (o viceversa), ignorando la `CMD`.
- **Impacto:** Configuración confusa; difícil reproducir issues.
- **Archivos implicados:**
  - `netback-backend/Dockerfile`
  - `netback-backend/entrypoint.sh`
- **Corrección implementada:** Unificar runner (asumimos **Gunicorn** para Django).

**`netback-backend/Dockerfile` (ejemplo con Gunicorn):**
```dockerfile
# ... otras instrucciones
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app/
EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**`netback-backend/entrypoint.sh` (ejemplo):**
```bash
#!/bin/bash
set -e

python manage.py migrate --noinput

# (Opcional) Crear superusuario si no existe
# python manage.py createsuperuser --noinput || true

exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000
```

> Si prefieres Uvicorn/ASGI, adapta ambos archivos de forma coherente.

---

## 🟡 Prioridad BAJA / Mejores prácticas

### 13) Seguridad Nginx / CSP
- **Síntoma:** `Content-Security-Policy` permite `'unsafe-inline'` → riesgo XSS.
- **Impacto:** Mayor superficie de ataque.
- **Archivo implicado:** `netback-frontend/nginx.conf`
- **Corrección implementada:** Endurecer CSP, eliminando `'unsafe-inline'` cuando sea posible y restringiendo fuentes.

**`netback-frontend/nginx.conf` (fragmento):**
```nginx
server {
    listen 80;
    server_name localhost;

    # ...

    add_header Content-Security-Policy "
        default-src 'self';
        script-src 'self' https://trusted-cdn.com;
        style-src 'self' 'unsafe-inline';  # intentar eliminar 'unsafe-inline' si el bundle lo permite
        img-src 'self' data:;
        font-src 'self';
        connect-src 'self' http://localhost:8080;
        frame-ancestors 'none';
        form-action 'self';
        base-uri 'self';
    ";
}
```

> Ajusta la política a las necesidades reales del frontend.

---

### 14) Rate limiting muy conservador
- **Síntoma:** Configuración restrictiva o inexistente.
- **Impacto:** Bloqueo de usuarios legítimos o falta de protección ante abuso.
- **Archivo implicado:** `netback-frontend/nginx.conf`
- **Corrección implementada:** Ajustar `limit_req_zone` a un valor razonable (p. ej., **10 r/s**) con ráfagas.

**`netback-frontend/nginx.conf` (fragmento):**
```nginx
http {
    # ...
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;

    server {
        listen 80;
        server_name localhost;

        location / {
            limit_req zone=mylimit burst=20 nodelay;
            # ...
        }

        location /api/ {
            limit_req zone=mylimit burst=10 nodelay;
            # ...
        }
    }
}
```

---

### 15) Encriptación de `customPass`
- **Síntoma:** `NetworkDevice.customPass` en texto claro.
- **Impacto:** Riesgo de exposición de credenciales.
- **Archivos implicados:**
  - `netback-backend/core/models.py`
  - `netback-backend/utils/env.py`
- **Corrección implementada:** Cifrado en reposo con `Fernet` (similar a `VaultCredential`). Requiere **migración de datos**.

**`netback-backend/core/models.py` (ejemplo con campo cifrado):**
```python
from django.db import models
from cryptography.fernet import Fernet
from decouple import config

FERNET_KEY = config("FERNET_KEY").encode()  # NO hardcodear en prod
cipher_suite = Fernet(FERNET_KEY)

class EncryptedCharField(models.CharField):
    def get_prep_value(self, value):
        if value is not None:
            return cipher_suite.encrypt(value.encode()).decode()
        return value

    def from_db_value(self, value, expression, connection):
        if value is not None:
            try:
                return cipher_suite.decrypt(value.encode()).decode()
            except Exception:
                # Manejar valores antiguos o clave cambiada
                return value
        return value

class NetworkDevice(models.Model):
    # ...
    customUser = models.CharField(max_length=255, blank=True, null=True)
    customPass = EncryptedCharField(max_length=255, blank=True, null=True)  # ✅ cifrado
    # ...
```

> **Consideraciones:** `FERNET_KEY` debe ser una clave segura (32 bytes, base64). Gestionarla como **secreto** en entorno.

---

### 16) Tipos Netmiko
- **Síntoma:** `manufacturer.netmiko_type` podría contener valores no soportados.
- **Impacto:** Errores en conexión.
- **Archivos implicados:**
  - `netback-backend/core/models.py` (Manufacturer/NetworkDevice)
  - `netback-backend/core/serializers.py`
  - `netback-backend/core/network_util/executor.py`
- **Corrección implementada:** Validar `netmiko_type` contra una lista soportada.

**`netback-backend/core/models.py` (validación ejemplo):**
```python
from django.db import models
from django.core.exceptions import ValidationError

SUPPORTED_NETMIKO_TYPES = [
    "cisco_ios", "cisco_xe", "cisco_xr", "cisco_nxos", "cisco_asa",
    "huawei", "hp_procurve", "juniper", "arista_eos", "mikrotik_routeros",
    # ... añade los que necesites
]

class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    netmiko_type = models.CharField(
        max_length=50, blank=True, null=True,
        choices=[(t, t) for t in SUPPORTED_NETMIKO_TYPES],
        help_text="Tipo Netmiko (e.g., cisco_ios, huawei)"
    )

    def clean(self):
        if self.netmiko_type and self.netmiko_type not in SUPPORTED_NETMIKO_TYPES:
            raise ValidationError({"netmiko_type": f"Tipo Netmiko '{self.netmiko_type}' no soportado."})
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
```

**`netback-backend/core/serializers.py` (validación en serializer):**
```python
from rest_framework import serializers
from core.models import Manufacturer, SUPPORTED_NETMIKO_TYPES

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = "__all__"

    def validate_netmiko_type(self, value):
        if value and value not in SUPPORTED_NETMIKO_TYPES:
            raise serializers.ValidationError(
                f"Tipo Netmiko '{value}' no soportado. Válidos: {', '.join(SUPPORTED_NETMIKO_TYPES)}"
            )
        return value
```

---

### 17) Healthcheck del backend
- **Síntoma:** `backend` en `docker-compose` sin healthcheck real.
- **Impacto:** Docker podría marcar como healthy sin que Django funcione.
- **Archivos implicados:**
  - `docker-compose.yml`
  - `netback-backend/backend/urls.py`
  - `netback-backend/backend/views.py`
- **Corrección implementada:** Añadir endpoint `/api/health/` y usarlo en el healthcheck.

**`netback-backend/backend/views.py`:**
```python
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})
```

**`netback-backend/backend/urls.py`:**
```python
from django.contrib import admin
from django.urls import path, include
from backend.views import health_check

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
    path("api/health/", health_check),  # ✅
]
```

**`docker-compose.yml` (healthcheck para `backend`):**
```yaml
services:
  backend:
    # ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    depends_on:
      - db
```

---

## 🔐 Nota sobre permisos en `UserSystemViewSet`

Un usuario no admin podría pasar `IsAuthenticated` en `update`/`partial_update` y **editar a otros** si no hay control por objeto.

- **Archivo implicado:** `netback-backend/core/views.py`
- **Corrección implementada:** Limitar que los no-admin **solo** editen su propio usuario.

**`netback-backend/core/views.py` (fragmento para `UserSystemViewSet`):**
```python
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserSystemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    # ... queryset, serializer_class

    def update(self, request, *args, **kwargs):
        user_id_to_modify = kwargs.get("pk")
        if not getattr(request.user, "is_staff", False) and str(request.user.id) != str(user_id_to_modify):
            return Response({"detail": "No tienes permiso para editar este usuario."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        user_id_to_modify = kwargs.get("pk")
        if not getattr(request.user, "is_staff", False) and str(request.user.id) != str(user_id_to_modify):
            return Response({"detail": "No tienes permiso para editar este usuario."}, status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)
```

> Si usas un campo `role` personalizado, reemplaza `is_staff` por la condición equivalente (p. ej., `request.user.role == "admin"`).

---

## ✅ Checklist de acciones

1. Corregir `executor.py` (`vaultCredential`) y revalidar ejecución de comandos.
2. Alinear `BackupStatusTracker` y estados en `backup.py` (`success`/`unchanged`/`error`).
3. Quitar validaciones en `perform_create/update` y delegarlas al serializer.
4. Definir estrategia única para Celery Beat (DBScheduler + PeriodicTask **o** `beat_schedule` en código).
5. Eliminar `app:/app` en `docker-compose.yml` (o reemplazar por `/app/data`).
6. Añadir `/health/` al proxy y ajustar healthchecks.
7. Corregir `TIME_ZONE` y revisar `ALLOWED_HOSTS`/CORS.
8. Simplificar `SiteSerializer`/`AreaSerializer`.
9. **Opcional:** Cifrar `customPass` con `Fernet` (requiere migración).
10. **Opcional:** Endurecer CSP y ajustar rate limiting en Nginx.

---

## 🧪 Pruebas mínimas tras cambios

- **Backend:** `pytest`/`manage.py test` (si aplica) + `curl /api/health/` → **200**.
- **Proxy:** `curl :8080/health/` → `{ "status": "ok" }`.
- **Celery:** Logs de `celery-beat` y `celery` ejecutando `autoBackup` en la frecuencia esperada.
- **Frontend:** Navegar SPA y verificar llamadas `/api/*` a través del proxy.

---

## Observaciones finales

La base del sistema es sólida. Los tres defectos críticos detectados afectaban **persistencia segura**, **ejecución remota** y **programación de tareas**.
Con las correcciones propuestas, la plataforma queda más **robusta**, **segura** y **predecible** en operación.
