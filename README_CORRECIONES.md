# README_CORRECIONES.md

## 📌 Resumen ejecutivo

Auditoría completa del stack **Netback** (Backend Django + Celery, Proxy FastAPI, Frontend React/Nginx y Docker Compose).  
Este documento resume **hallazgos**, su **criticidad**, **archivos afectados** y **acciones concretas** para corregirlos.

---

## 🔴 Prioridad ALTA

### 1) Bug al crear/actualizar `NetworkDevice` (la validación no detiene el guardado)
- **Síntoma:** En `perform_create`/`perform_update` se retorna `Response(...)`. DRF **ignora** ese retorno y el objeto puede guardarse aunque haya error.
- **Impacto:** Riesgo de datos inválidos en BD.
- **Archivos:** `netback-backend/core/views.py`, `netback-backend/core/serializers.py`
- **Acción:** Dejar la validación en el **serializer** (que lanza `serializers.ValidationError`) y mantener `serializer.save()` en el viewset.

```python
# views.py
from rest_framework import viewsets

class NetworkDeviceViewSet(viewsets.ModelViewSet):
    ...
    def perform_create(self, serializer):
        serializer.save()  # Validación vive en el serializer

    def perform_update(self, serializer):
        serializer.save()
```

> Si se desea validar en el viewset, **levantar** `serializers.ValidationError` en lugar de retornar `Response`.

---

### 2) Atributo mal escrito rompe comandos remotos
- **Síntoma:** Se usa `device.VaultCredential` (V mayúscula) en lugar de `device.vaultCredential`. Lanza `AttributeError`.
- **Impacto:** Falla la ejecución de comandos (Netmiko).
- **Archivo:** `netback-backend/core/network_util/executor.py`
- **Acción:** Usar el nombre correcto y validar credenciales.

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

    with ConnectHandler(**connection) as conn:
        return conn.send_command(command)
```

---

### 3) `BackupStatusTracker.last_status` usa valores fuera de las *choices*
- **Síntoma:** Se asigna `success_no_changes`/`success_with_changes`, pero las choices del modelo son `success | unchanged | error`.
- **Impacto:** Inconsistencia y posibles datos inválidos.
- **Archivos:**  
  - Modelo: `netback-backend/core/models.py`  
  - Lógica: `netback-backend/core/network_util/backup.py`
- **Acción:** Usar exactamente `success`, `unchanged` o `error`.

```python
# backup.py (fragmento)
if Backup.objects.filter(device=device, checksum=checksum).exists():
    tracker.success_count = 0
    tracker.error_count = 0
    tracker.no_change_count += 1
    tracker.last_status = "unchanged"  # ✅
    tracker.save()
    return {"success": True, "message": "No Changes. Backup not created."}

# Cuando hay nuevo backup
tracker.no_change_count = 0
tracker.error_count = 0
tracker.success_count += 1
tracker.last_status = "success"  # ✅
tracker.save()
```

---

### 4) *autoBackup* con Celery Beat no se está programando
- **Síntoma:** En Docker se usa `DatabaseScheduler` de `django_celery_beat`, pero no existe la `PeriodicTask` correspondiente. El `beat_schedule` en código no aplica con ese scheduler.
- **Impacto:** `autoBackup` no se ejecuta automáticamente.
- **Archivos:** `netback-backend/backend/celery.py`, `docker-compose.yml` (servicio `celery-beat`)
- **Acción (elige una):**
  1) **Mantener DatabaseScheduler** y crear una `PeriodicTask` para `core.tasks.autoBackup` (vía admin o comando de management).  
  2) **No** usar `django_celery_beat` y dejar que el `beat_schedule` de código gobierne.

```python
# Ejemplo (comando de management)
from django_celery_beat.models import CrontabSchedule, PeriodicTask

sched, _ = CrontabSchedule.objects.get_or_create(
    minute='*', hour='*', day_of_week='*', day_of_month='*', month_of_year='*'
)

PeriodicTask.objects.get_or_create(
    name='autoBackup-every-minute',
    task='core.tasks.autoBackup',
    crontab=sched,
)
```

---

### 5) Volumen `app:/app` en Docker Compose vacía el código del backend
- **Síntoma:** `app:/app` en `backend`/`celery`/`celery-beat` **enmascara** el código de la imagen.
- **Impacto:** El contenedor queda sin `manage.py` ni código.
- **Archivo:** `docker-compose.yml`
- **Acción:** Eliminar ese volumen o montar solo rutas de datos.

```yaml
# Recomendado (ejemplo)
volumes:
  - ./netback-backend/data:/app/data
```

---

### 6) Healthcheck del Proxy (FastAPI) inexistente
- **Síntoma:** `docker-compose` chequea `http://localhost:8080/health/`, pero el proxy no expone esa ruta.
- **Impacto:** Healthcheck falla aunque el servicio esté arriba.
- **Archivos:** `netback-proxy/main.py`, `docker-compose.yml`
- **Acción:** Agregar endpoint `/health/` o ajustar el healthcheck a una ruta existente.

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health/")
def health():
    return {"status": "ok"}
```

---

## 🟠 Prioridad MEDIA

### 7) Zona horaria inválida
- **Síntoma:** `TIME_ZONE = "America/Chile"` (no válido IANA).
- **Impacto:** Errores sutiles en tiempos/cron.
- **Archivo:** `netback-backend/backend/settings.py`
- **Acción:** Usar `America/Santiago` (o variable de entorno válida).

```python
TIME_ZONE = config("TIME_ZONE", default="America/Santiago")
```

---

### 8) CORS y `ALLOWED_HOSTS`
- **Síntoma:** `ALLOWED_HOSTS=['*']` (solo aceptable en dev). `CORS_ALLOWED_ORIGINS` incluye `http://localhost:3000`, pero el frontend puede servir en `http://localhost` vía Nginx.
- **Impacto:** Superficie de ataque mayor y CORS incongruente.
- **Archivos:** `netback-backend/backend/settings.py`, `netback-frontend/nginx.conf`
- **Acción:** Restringir `ALLOWED_HOSTS` (p. ej. `['netback-backend', 'localhost']`). Ajustar orígenes CORS reales.  
  > Si el frontend _no_ llama directo al backend (usa proxy `/api`), puedes reducir CORS.

---

### 9) `DEBUG` en FastAPI mal mapeado
- **Síntoma:** `DEBUG` se deriva de `FASTAPI_PROXY_URL` (typo).
- **Impacto:** Modo debug activado/desactivado incorrectamente.
- **Archivo:** `netback-proxy/app/config.py`
- **Acción:** Introducir `FASTAPI_PROXY_DEBUG` y usarlo.

```python
import os

DEBUG: bool = os.getenv('FASTAPI_PROXY_DEBUG', 'false').lower() == 'true'
```

> Con `allow_credentials=True`, **no** usar `'*'` en `allow_origins`; definir orígenes explícitos.

---

### 10) `SiteSerializer` y `AreaSerializer`: acceso `.id` sobre PK crudos
- **Síntoma:** En `validate`, `data.get("country").id`/`data.get("site").id` pueden ser UUIDs, no instancias.
- **Impacto:** `AttributeError` en validación.
- **Archivo:** `netback-backend/core/serializers.py`
- **Acción:** Confiar en `PrimaryKeyRelatedField` y remover esa validación, o normalizar PKs antes.

```python
class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ["id", "name", "country"]
    # Validación de relaciones: delegar al Model/DB
```

---

### 11) Zabbix Manager: no usar `exit()` en librerías
- **Síntoma:** `exit()` en `connect()` puede matar workers/servicios.
- **Impacto:** Caída inesperada de procesos.
- **Archivo:** `netback-backend/utils/zabbix_manager.py`
- **Acción:** Registrar y **re-lanzar** la excepción para que el caller la maneje.

```python
except Exception as e:
    print(f"❌ Failed to connect to Zabbix API: {e}")
    raise
```

---

### 12) `entrypoint.sh`: gunicorn vs uvicorn
- **Síntoma:** Dockerfile define `CMD gunicorn ...`, pero `ENTRYPOINT` ejecuta `uvicorn`. La `CMD` se ignora.
- **Impacto:** Configuración confusa; difícil reproducir issues.
- **Archivos:** `netback-backend/Dockerfile`, `netback-backend/entrypoint.sh`
- **Acción:** Unificar: o solo Gunicorn o solo Uvicorn. Si usas Uvicorn, elimina la `CMD` de Gunicorn.

---

## 🟡 Prioridad BAJA / Mejores prácticas

### 13) Seguridad Nginx / CSP
- **Síntoma:** `Content-Security-Policy` permite `'unsafe-inline'`.
- **Impacto:** Mayor riesgo XSS.
- **Archivo:** `netback-frontend/nginx.conf`
- **Acción:** Endurecer CSP (si el bundle lo permite), p. ej.:  
  `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'`

---

### 14) Rate limiting muy conservador
- **Archivo:** `netback-frontend/nginx.conf`
- **Acción:** Ajustar a algo como **10 r/s** (depende del tráfico esperado).

---

### 15) Encriptación de `customPass`
- **Síntoma:** `NetworkDevice.customPass` en texto claro.
- **Impacto:** Riesgo de exposición de credenciales.
- **Archivos:** `netback-backend/core/models.py`, `utils/env.py`
- **Acción:** Cifrar en reposo (reusar `Fernet` como en `VaultCredential`).

---

### 16) Tipos Netmiko
- **Acción:** Validar que `manufacturer.netmiko_type` sea un tipo soportado (`cisco_ios`, `huawei`, etc.), no `generic`.

---

### 17) Healthcheck del backend
- **Acción:** Usar un endpoint real en el healthcheck.

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
    interval: 30s
    timeout: 10s
    retries: 3
```

---

## 🗂️ Lista de archivos involucrados

- **Backend (Django)**
  - `netback-backend/backend/settings.py` → **FIX** zona horaria, `ALLOWED_HOSTS`, CORS
  - `netback-backend/backend/urls.py` → Rutas (incluye health/JWT)
  - `netback-backend/core/views.py` → **FIX** validaciones en `NetworkDeviceViewSet`; ver nota de permisos
  - `netback-backend/core/serializers.py` → **FIX** validación `SiteSerializer`/`AreaSerializer`
  - `netback-backend/core/models.py` → **FIX** uso de choices en `BackupStatusTracker`
  - `netback-backend/core/network_util/executor.py` → **FIX** `vaultCredential` (lowercase) y validación de credenciales
  - `netback-backend/core/network_util/backup.py` → **FIX** `last_status` y manejo de credenciales ausentes
  - `netback-backend/core/network_util/comparison.py` → OK
  - `netback-backend/core/tasks.py`, `backend/celery.py` → **FIX** estrategia de Beat (DB vs código)
  - `netback-backend/utils/zabbix_manager.py` → **FIX** evitar `exit()`
  - `netback-backend/entrypoint.sh` → **FIX** coherencia runner (Uvicorn/Gunicorn)

- **Proxy (FastAPI)**
  - `netback-proxy/app/config.py` → **FIX** `DEBUG` y orígenes CORS explícitos
  - `netback-proxy/main.py` → **ADD** `/health/`
  - `netback-proxy/app/dependencies.py` → OK
  - `netback-proxy/app/routes/auth.py` → OK

- **Frontend (Nginx/React)**
  - `netback-frontend/nginx.conf` → **TUNE** CSP, rate limiting, cache headers
  - `netback-frontend/Dockerfile` → OK (multi-stage con pnpm)

- **Orquestación**
  - `docker-compose.yml` → **FIX** volumen `app:/app`, healthchecks, puertos

---

## 🔐 Nota sobre permisos en `UserSystemViewSet`

Actualmente, un usuario no admin podría pasar `IsAuthenticated` en `update`/`partial_update` y **editar a otros** si no hay control por objeto.

- **Archivo:** `netback-backend/core/views.py`
- **Acción:** Limitar que no-admins solo editen **su propio** usuario.

```python
from rest_framework import status
from rest_framework.response import Response

def update(self, request, *args, **kwargs):
    if request.user.role != 'admin' and str(request.user.id) != kwargs.get('pk'):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
    return super().update(request, *args, **kwargs)
```

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
9. **Opcional:** Cifrar `customPass` con `Fernet`.
10. **Opcional:** Endurecer CSP y aumentar rate en Nginx.

---

## 🧪 Pruebas mínimas tras cambios

- **Backend:** `pytest`/`manage.py test` (si aplica) + `curl /api/health/` → **200**.
- **Proxy:** `curl :8080/health/` → `{ "status": "ok" }`.
- **Celery:** Ver logs de `celery-beat` y `celery` ejecutando `autoBackup` en el minuto esperado.
- **Frontend:** Navegar SPA y verificar llamadas `/api/*` a través del proxy.

---

## Observaciones finales

La base del sistema es sólida. Los tres defectos críticos detectados afectaban **persistencia segura**, **ejecución remota** y **programación de tareas**. Con las correcciones propuestas, la plataforma queda más **robusta**, **segura** y **predecible** en operación.
