# Netback — Backend (Django REST API)

API REST para **gestión de dispositivos de red y respaldos**. Incluye autenticación **JWT**, ejecución de comandos vía **Netmiko**, tareas en segundo plano con **Celery**/**Redis** y persistencia en **PostgreSQL**.

---

## 🧭 ¿Qué hace?
- **Usuarios y roles**: _admin_, _operator_, _viewer_.
- **Inventario**: fabricantes, tipos de dispositivo, países, sitios, áreas y dispositivos.
- **Respaldos**: obtención de `running-config` y `vlan brief`, deduplicación por _checksum_, historial y **comparación estructurada** entre respaldos.
- **Automatización**: _scheduler_ diario/con hora configurable con **Celery**.
- **Diagnóstico**: ejecución de comandos y **ping** desde el servidor.
- **Integración Zabbix**: clasificación/ingesta de hosts por reglas.

---

## 🏗️ Stack & Dependencias
- **Python 3.13**, **Django 5**, **Django REST Framework**
- **JWT (SimpleJWT)**
- **PostgreSQL** (psycopg2-binary)
- **Celery 5** + **Redis** (django-celery-beat / django-celery-results)
- **Netmiko** (con `ntc_templates`)
- **cryptography.Fernet** para cifrar credenciales en _VaultCredential_

> Ver `requirements.txt` para el detalle de librerías.

---

## 🔌 Endpoints principales
Ruta base: `/api/`

- **Auth**
  - `POST /api/token/` — obtener `access` y `refresh`
  - `POST /api/token/refresh/` — renovar `access`
  - `GET  /api/users/me/` — perfil del usuario autenticado

- **Usuarios** (`/api/users/` — _admin_ requerido para crear/eliminar)

- **Ubicación**
  - `countries`, `sites`, `areas` — filtros por `?country_id=` / `?site_id=`

- **Dispositivos** (`/api/networkdevice/`)
  - `GET` (_viewer_+), `POST` (_operator_+), `PUT/PATCH/DELETE` (_admin_)
  - Acciones:
    - `POST /api/networkdevice/{uuid}/command/` — ejecutar comando Netmiko
    - `POST /api/networkdevice/{uuid}/backup/` — forzar respaldo
    - `GET  /api/networkdevice/{uuid}/backups/` — historial
    - `GET  /api/networkdevice/{uuid}/compare/` — comparar 2 últimos
    - `GET  /api/backups/compare/{old}/{new}/` — comparar por IDs

- **Backups**
  - `GET  /api/backups/last/` — último backup por dispositivo

- **Estado y salud**
  - `GET  /api/networkdevice/{uuid}/status/` — estados de backup
  - `GET  /api/health/` — _healthcheck_ del backend (público)

- **Zabbix & Clasificación** (solo _admin_)
  - `POST /api/networkdevice/bulk/from-zabbix/` — clasificar hosts desde Zabbix
  - `POST /api/networkdevice/bulk/from-csv/` — clasificar desde CSV
  - `POST /api/networkdevice/bulk/save/` — persistir clasificados
  - `GET  /api/zabbix/status/` — ping + conectividad a API Zabbix

- **Programación de backups** (solo _admin_)
  - `POST /api/backup-config/schedule/` — setear hora `HH:MM`
  - `GET  /api/backup-config/schedule/get/` — obtener hora vigente

---

## 🗃️ Modelos clave
- `UserSystem` (usuario, `role`)
- `VaultCredential` (usuario/clave cifrados con **Fernet**)
- `Manufacturer` (comandos y `netmiko_type`)
- `DeviceType`, `Country`, `Site`, `Area`
- `NetworkDevice` (hostname, IP, fabricante, tipo, credencial)
- `Backup` (runningConfig, vlanBrief, checksum)
- `BackupDiff` (dif estructurado por secciones y VLAN)
- `BackupStatus` (eventos in_progress/completed/failed)
- `BackupSchedule` (hora programada)
- `BackupStatusTracker` (`success|unchanged|error`, contadores)

---

## 🧰 Tareas y Scheduler (Celery)
- Tarea periódica: `core.tasks.autoBackup` — ejecuta respaldos cuando la hora actual coincide con `BackupSchedule`.
- _Beat_: puedes usar **DatabaseScheduler** (via `django_celery_beat`) o el `beat_schedule` definido en `backend/celery.py` (si no usas DatabaseScheduler).

> Si usas DatabaseScheduler, crea una **PeriodicTask** por admin/command para llamar `core.tasks.autoBackup` cada minuto.

---

## ⚙️ Variables de entorno (ejemplo)
```
# Django / Seguridad
SECRET_KEY=...
TIME_ZONE=America/Santiago
ALLOWED_HOSTS=netback-backend,localhost

# Base de datos
POSTGRES_DB=netback
POSTGRES_USER=netback
POSTGRES_PASSWORD=netback
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Celery / Redis
CELERY_BROKER_URL=redis://redis:6379/0

# Zabbix
ZABBIX_URL=https://zabbix.example.com
ZABBIX_TOKEN=xxxxx

# Cifrado credenciales VaultCredential
ENCRYPTION_KEY_VAULT=<clave_fernet_base64>

# CORS (si aplica)
CORS_ALLOWED_ORIGINS=http://localhost
```

---

## ▶️ Cómo ejecutar
### Docker Compose (recomendado)
1) Crear archivo `.env` en `netback-env/` (ver ejemplo arriba).
2) Levantar servicios desde la raíz del repo:
```bash
docker compose up -d --build
```
Servicios: `postgres`, `redis`, `backend`, `celery`, `celery-beat`, `proxy`, `frontend`.

### Local (desarrollo)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(cat ../netback-env/.env | xargs)
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
# Celery
celery -A backend worker --loglevel=info
celery -A backend beat --loglevel=info  # si usas beat en código, omite DatabaseScheduler
```

---

## 🔍 Healthchecks / Diagnóstico
- Backend: `GET /api/health/`
- Ping dispositivo: `POST /api/ping/` body: `{ "ip": "8.8.8.8" }`
- Últimos backups: `GET /api/backups/last/`
- Comparaciones: `GET /api/networkdevice/{uuid}/compare/`

---

## 🔐 Permisos & Seguridad
- **Roles**:
  - _admin_: CRUD completo, configura horarios y Zabbix.
  - _operator_: crear dispositivos y ejecutar backups manuales.
  - _viewer_: solo lectura.
- **JWT** obligatorio salvo `/api/health/`.
- **Credenciales**:
  - Preferir `VaultCredential` (cifrado **Fernet** mediante `ENCRYPTION_KEY_VAULT`).
  - Evitar `customPass` en texto plano (si se usa, considerar cifrarlo).

---

## 🗂️ Estructura de proyecto (parcial)
```
netback-backend/
├─ backend/
│  ├─ settings.py
│  ├─ urls.py
│  ├─ celery.py
├─ core/
│  ├─ models.py
│  ├─ views.py
│  ├─ serializers.py
│  ├─ tasks.py
│  └─ network_util/
│     ├─ backup.py
│     ├─ comparison.py
│     ├─ executor.py
│     └─ vlan_parser.py
├─ utils/
│  ├─ env.py
│  └─ zabbix_manager.py
├─ entrypoint.sh
├─ Dockerfile
└─ requirements.txt
```

---

## 🧪 Tests
- Ubicación de tests: `core/test_suite/` (evita colisiones con paquetes globales llamados `tests`).
- Ejecutar todos los tests:
  - `python manage.py test core.test_suite -v 2`
- Ejecutar por módulo:
  - `python manage.py test core.test_suite.test_models_crud -v 2`
  - `python manage.py test core.test_suite.test_endpoints_signals -v 2`
  - `python manage.py test core.test_suite.test_ping -v 2`
  - `python manage.py test core.test_suite.test_autobackup_schedule -v 2`
- Atajos opcionales (re-export):
  - `python manage.py test core.tests_crud`
  - `python manage.py test core.tests_endpoints`
- Nota: Evita `python manage.py test core` si tu entorno tiene instalado un paquete llamado "tests", ya que interfiere con el discovery estándar de unittest.

---

## 📒 Notas relevantes
- **Zona horaria** válida: `America/Santiago`.
- Si usas **django_celery_beat** como scheduler, asegúrate de crear la `PeriodicTask` correspondiente.
- El servicio `proxy` expone `/api/*` hacia este backend (no es necesario habilitar CORS si todo el tráfico viene por el proxy y Nginx del frontend).

---

## Licencia
Proyecto interno Netback. Uso restringido.