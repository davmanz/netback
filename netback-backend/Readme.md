# Redback API

## 📌 Descripción
Redback es una API basada en **Django REST Framework** con soporte para autenticación JWT y automatización de backups mediante **Celery** y **Netmiko**.  
Permite la gestión de usuarios, dispositivos de red y respaldos de configuración.

---

## 🚀 **Tecnologías Utilizadas**
- **Django 5.1.6**
- **Django REST Framework**
- **PostgreSQL**
- **Celery + Redis** (para tareas en segundo plano)
- **Netmiko** (para conexiones SSH a dispositivos de red)
- **JWT (SimpleJWT)** (para autenticación segura)

---

## 🔑 **Autenticación**
La API usa **JWT** para la autenticación.

### 🔹 **Obtener Token de Acceso**
`POST /api/token/`

**Cuerpo de la solicitud (`JSON`)**:
```json
{
  "username": "admin",
  "password": "adminpassword"
}
Respuesta exitosa (200 OK):

json
Copiar
Editar
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
🔹 Refrescar Token
POST /api/token/refresh/

Cuerpo de la solicitud (JSON):

json
Copiar
Editar
{
  "refresh": "jwt_refresh_token"
}
Respuesta exitosa (200 OK):

json
Copiar
Editar
{
  "access": "new_jwt_access_token"
}
📌 Endpoints de la API
🟢 Usuarios
🔹 Obtener Lista de Usuarios
GET /api/users/

Requiere rol de Admin.
Retorna la lista de usuarios.
🔹 Crear un Usuario
POST /api/users/create_user/

Solo Admins pueden crear usuarios.
Cuerpo de la solicitud (JSON):

json
Copiar
Editar
{
  "userName": "nuevo_usuario",
  "email": "user@email.com",
  "password": "password123",
  "role": "operator"
}
Respuesta (201 Created):

json
Copiar
Editar
{
  "id": "uuid",
  "userName": "nuevo_usuario",
  "email": "user@email.com",
  "role": "operator",
  "createdAt": "2025-02-18T00:00:00Z"
}
🖥 Dispositivos de Red
🔹 Obtener Lista de Dispositivos
GET /api/networkdevice/

Roles Permitidos: Admin, Operator, Viewer.
🔹 Crear un Dispositivo
POST /api/networkdevice/

Solo los operadores pueden agregar dispositivos.
Cuerpo de la solicitud (JSON):

json
Copiar
Editar
{
  "hostname": "switch-core",
  "ipAddress": "192.168.1.1",
  "model": "Cisco IOS",
  "manufacturer": "Cisco",
  "deviceType": "cisco_ios",
  "customUser": "admin",
  "customPass": "admin123"
}
Respuesta (201 Created):

json
Copiar
Editar
{
  "id": "uuid",
  "hostname": "switch-core",
  "ipAddress": "192.168.1.1",
  "model": "Cisco IOS",
  "manufacturer": "Cisco",
  "createdAt": "2025-02-18T00:00:00Z"
}
🔹 Ejecutar Comando en un Dispositivo
POST /api/networkdevice/{uuid}/command/

Requiere Autenticación.
Cuerpo de la solicitud (JSON):

json
Copiar
Editar
{
  "command": "show running-config"
}
Respuesta (200 OK):

json
Copiar
Editar
{
  "result": "Configuración completa del dispositivo..."
}
🔄 Backups
🔹 Obtener Historial de Backups de un Dispositivo
GET /api/networkdevice/{uuid}/backups/

Respuesta (200 OK):

json
Copiar
Editar
{
  "device": "switch-core",
  "backups": [
    {
      "id": "uuid",
      "backupTime": "2025-02-18T00:00:00Z",
      "checksum": "sha256_hash"
    }
  ]
}
🔹 Crear Backup Manual
POST /api/networkdevice/{uuid}/backup/

Requiere Autenticación.
Respuesta (200 OK):

json
Copiar
Editar
{
  "success": true,
  "backupId": "uuid"
}
🔹 Comparar Últimos 2 Backups de un Dispositivo
GET /api/networkdevice/{uuid}/compare/

Requiere Autenticación.
Respuesta (200 OK):

json
Copiar
Editar
{
  "success": true,
  "backupDiffId": "uuid",
  "changes": {
    "runningConfigDiff": "-- línea eliminada\n++ línea agregada",
    "vlanBriefDiff": "-- VLAN 10 eliminada\n++ VLAN 20 agregada"
  }
}
🔹 Comparar 2 Backups Específicos
GET /api/backups/compare/{backupOldId}/{backupNewId}/

📊 Estados de Backups
🔹 Obtener Estado de los Backups de un Dispositivo
GET /api/networkdevice/{uuid}/status/

Respuesta (200 OK):

json
Copiar
Editar
{
  "device": "switch-core",
  "statuses": [
    {
      "status": "completed",
      "message": "Backup successful.",
      "timestamp": "2025-02-18T01:00:00Z"
    }
  ]
}
⚙️ Automatización con Celery
Se ejecuta automáticamente un backup diario a la 1 AM.
Se configura en celery.py:
python
Copiar
Editar
celery_app.conf.beat_schedule = {
    'daily_backup': {
        'task': 'core.tasks.autoBackup',
        'schedule': crontab(hour=1, minute=0),
    },
}
🔒 Permisos de Usuario
Rol	Acciones Permitidas
Admin	Crear, ver y modificar usuarios, dispositivos y backups
Operator	Crear y administrar dispositivos y backups
Viewer	Solo ver información, sin modificar
🛠 Instalación y Configuración
Clonar el repositorio:

bash
Copiar
Editar
git clone https://github.com/usuario/redback.git
cd redback
Crear y activar entorno virtual:

bash
Copiar
Editar
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
Instalar dependencias:

bash
Copiar
Editar
pip install -r requirements.txt
Configurar base de datos PostgreSQL en .env:

ini
Copiar
Editar
DATABASE_NAME=redback
DATABASE_USER=redback
DATABASE_PASSWORD=redback
DATABASE_HOST=localhost
DATABASE_PORT=5432
Aplicar migraciones:

bash
Copiar
Editar
python manage.py migrate
Ejecutar el servidor:

bash
Copiar
Editar
python manage.py runserver
Iniciar Celery:

bash
Copiar
Editar
celery -A backend worker --loglevel=info
Iniciar Celery Beat (para tareas programadas):

bash
Copiar
Editar
celery -A backend beat --loglevel=info
📩 Contacto
Si necesitas soporte, contáctanos en redback@correo.com.

📌 Desarrollado con Django y Celery para gestión eficiente de respaldos de red.