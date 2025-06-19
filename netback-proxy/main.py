import uvicorn
import requests
import httpx
import logging
from fastapi import FastAPI, Request, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app_settings = {
    "DJANGO_API_PROTOCOL": os.getenv('DJANGO_API_PROTOCOL', 'http'),
    "DJANGO_API_URL": os.getenv('DJANGO_API_URL'),
    "DJANGO_API_PORT": int(os.getenv('DJANGO_API_PORT')),
    'HOST': os.getenv('FASTAPI_PROXY_URL'),
    'PORT': int(os.getenv('FASTAPI_PROXY_PORT')),
    'DEBUG': os.getenv('FASTAPI_PROXY_URL', 'false').lower() == 'true',
    'ALLOW_ORIGINS': os.getenv('ALLOW_ORIGINS', '*').split(','),
    'ALLOW_CREDENTIALS': os.getenv('ALLOW_CREDENTIALS', 'true').lower() == 'true',
    'ALLOW_METHODS': os.getenv('ALLOW_METHODS', 'GET,POST,PUT,PATCH,DELETE,OPTIONS').split(','),
    'ALLOW_HEADERS': os.getenv('ALLOW_HEADERS', 'Content-Type,Authorization').split(',')
}

# URL base de la API de Django - Obtener desde variable de entorno o usar valor por defecto
DJANGO_API_URL = f'{app_settings["DJANGO_API_PROTOCOL"]}://{app_settings["DJANGO_API_URL"]}:{app_settings["DJANGO_API_PORT"]}/api'

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=app_settings['ALLOW_CREDENTIALS'],
    allow_methods=app_settings['ALLOW_METHODS'],
    allow_headers=app_settings['ALLOW_HEADERS'],
    allow_origins=app_settings['ALLOW_ORIGINS'],

)

#****************************************
# 🛡️ Funciones de Autenticación y Roles
#****************************************
# Login y almacenamiento del token
def auth_required(authorization: str = Header(None)):
    """Validar token y obtener usuario autenticado"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    token = authorization.split(" ")[-1]
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{DJANGO_API_URL}/users/me/", headers=headers)
        response.raise_for_status()
    except requests.RequestException:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    return response.json()

# Gestion de ROL Admin
def admin_required(user=Depends(auth_required)):
    """Validar que el usuario tenga rol de administrador"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado, se requiere rol de administrador")
    return user

#****************************************
# 🔐 Autenticación y Sesión
#****************************************
class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/auth/login/")
async def login(user: UserLogin):
    """Autenticar usuario y obtener token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DJANGO_API_URL}/token/", json=user.dict())

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")

#****************************************
# 👤 Gestión de Usuarios
#****************************************
# Obtener información del usuario autenticado
@app.get("/users/me/")
async def get_current_user(request: Request):
    """Devuelve información del usuario autenticado"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/users/me/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Error obteniendo usuario actual")

#Crear un nuevo usuario (Solo administradores)
@app.post("/users/", dependencies=[Depends(admin_required)])
async def create_user(request: Request):
    """Crear usuario (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DJANGO_API_URL}/users/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    if response.status_code == 201:
        logging.info(f"Usuario creado: {data['username']}")
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Error creando usuario")

# Obtener todos los usuarios
@app.get("/users/", dependencies=[Depends(admin_required)])
async def get_users(request: Request):
    """Obtener lista de usuarios (solo admins)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/users/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Actualizar usuario (Admins pueden editar cualquier usuario, viewers solo el suyo)
@app.put("/users/{user_id}/")
async def update_user(user_id: str, request: Request, user=Depends(admin_required)):
    """Actualizar usuario (usuarios pueden editar su perfil, admins pueden editar a todos)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if user["role"] != "admin" and user["id"] != user_id:
        raise HTTPException(status_code=403, detail="No puedes modificar otros usuarios")

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{DJANGO_API_URL}/users/{user_id}/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Eliminar usuario (Solo administradores)
@app.delete("/users/{user_id}/", dependencies=[Depends(admin_required)])
async def delete_user(user_id: str, request: Request):
    """Eliminar usuario (solo admins)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{DJANGO_API_URL}/users/{user_id}/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    if response.status_code == 204:
        logging.info(f"Usuario eliminado: {user_id}")
        return {"message": "Usuario eliminado exitosamente"}
    raise HTTPException(status_code=response.status_code, detail="Error eliminando usuario")

#****************************************
# 🔌 Gestión de Dispositivos
#****************************************
# Crear un nuevo dispositivo
@app.post("/networkdevice/", dependencies=[Depends(admin_required)])
async def create_device(request: Request):
    """Crear dispositivo (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DJANGO_API_URL}/networkdevice/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Obtener todos los dispositivos
@app.get("/networkdevice/")
async def get_devices(request: Request, user=Depends(auth_required)):
    """Obtener lista de dispositivos"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/networkdevice/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Obtener dispositivoc por ID
@app.get("/networkdevice/{device_id}/")
async def get_device_by_id(device_id: str, request: Request, user=Depends(auth_required)):
    """Obtener un dispositivo por su ID"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/networkdevice/{device_id}/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )

    return response.json()

# Actualizar un dispositivo
@app.patch("/networkdevice/{device_id}/")
async def update_device(device_id: str, request: Request, user=Depends(auth_required)):
    """Actualizar dispositivo (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()
    print(f"Actualizando dispositivo {device_id} con datos: {data}")

    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{DJANGO_API_URL}/networkdevice/{device_id}/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Eliminar un dispositivo
@app.delete("/networkdevice/{device_id}/", dependencies=[Depends(admin_required)])
async def delete_device(device_id: str, request: Request):
    """Eliminar dispositivo (solo admins)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{DJANGO_API_URL}/networkdevice/{device_id}/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return {"message": "Dispositivo eliminado"}

#****************************************
# 🔑 Gestión de Credenciales Vault
#****************************************

# Crear una nueva credencial Vault
@app.post("/vaultcredentials/", dependencies=[Depends(auth_required)])
async def create_vault_credential(request: Request):
    """Crear una nueva credencial Vault"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DJANGO_API_URL}/vaultcredentials/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Obtener todas las credenciales Vault
@app.get("/vaultcredentials/", dependencies=[Depends(auth_required)])
async def get_vault_credentials(request: Request):
    """Obtener lista de credenciales Vault"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/vaultcredentials/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Actualizar una credencial Vault
@app.put("/vaultcredentials/{credential_id}/", dependencies=[Depends(auth_required)])
async def update_vault_credential(credential_id: str, request: Request):
    """Actualizar una credencial Vault"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{DJANGO_API_URL}/vaultcredentials/{credential_id}/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

# Eliminar una credencial Vault
@app.delete("/vaultcredentials/{credential_id}/", dependencies=[Depends(auth_required)])
async def delete_vault_credential(credential_id: str, request: Request):
    """Eliminar una credencial Vault"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{DJANGO_API_URL}/vaultcredentials/{credential_id}/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return {"message": "Credencial eliminada"}

#**********************************************************
# 📍 Gestión de Fabricantes (Manufacturers)
#**********************************************************
@app.get("/manufacturers/", dependencies=[Depends(auth_required)])
async def get_manufacturers(request: Request):
    """Obtener lista de fabricantes (requiere autenticación)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/manufacturers/", headers={"Authorization": f"Bearer {token.split()[-1]}"})
    return response.json()

#**********************************************************
# 📍 Gestión de Tipos de Dispositivos (DeviceType)
#**********************************************************
@app.get("/devicetypes/", dependencies=[Depends(auth_required)])
async def get_device_types(request: Request):
    """Obtener lista de tipos de equipos (requiere autenticación)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/devicetypes/", headers={"Authorization": f"Bearer {token.split()[-1]}"})
    return response.json()

#**********************************************************
# 📂 Manejo de Respaldos
#**********************************************************
# Guardar un nuevo respaldo de un dispositivo
@app.post("/networkdevice/{device_id}/backup/", dependencies=[Depends(auth_required)])
async def backup_device(device_id: str, request: Request):
    """Generar un nuevo respaldo de un dispositivo."""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/networkdevice/{device_id}/backup/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  # Cambiado de 10.0 a 30.0
        )

    return response.json()

# Obtener lista de dispositivos con su último respaldo
@app.get("/backups_last/", dependencies=[Depends(auth_required)])
async def get_last_backups(request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/backups/last/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  # Agregado timeout
        )

    return response.json()

# Obtener historial de respaldos de un dispositivo
@app.get("/networkdevice/{device_id}/backups/", dependencies=[Depends(auth_required)])
async def get_backup_history(device_id: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/networkdevice/{device_id}/backups/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  # Agregado timeout
        )

    return response.json()

# Ver contenido de un respaldo
@app.get("/backup/{backup_id}/", dependencies=[Depends(auth_required)])
async def get_backup(backup_id: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/backup/{backup_id}/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  # Agregado timeout
        )

    return response.json()

# Comparar dos respaldos específicos por su ID
@app.get("/backups/compare/{backupOldId}/{backupNewId}/", dependencies=[Depends(auth_required)])
async def compare_specific_backups(backupOldId: str, backupNewId: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/backups/compare/{backupOldId}/{backupNewId}/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  # Agregado timeout
        )

    return response.json()

# Comparar los dos últimos respaldos de un dispositivo
@app.get("/networkdevice/{device_id}/compare/", dependencies=[Depends(auth_required)])
async def compare_last_backups(device_id: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/networkdevice/{device_id}/compare/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  # Agregado timeout
        )

    return response.json()

#****************************************
# 📍 Gestión de Países
#****************************************
@app.post("/countries/", dependencies=[Depends(auth_required)])
async def create_country(request: Request):
    """Crear un nuevo País (requiere autenticación)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if "name" not in data:
        raise HTTPException(status_code=400, detail="El campo 'name' es obligatorio")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/countries/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )
    
    return response.json()

@app.get("/countries/", dependencies=[Depends(auth_required)])
async def get_countries(request: Request):
    """Obtener lista de Países (requiere autenticación)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/countries/", headers={"Authorization": f"Bearer {token.split()[-1]}"})
    return response.json()

#**********************************************************
# 📍 Gestión de Sitios
#**********************************************************
@app.post("/sites/", dependencies=[Depends(auth_required)])
async def create_site(request: Request):
    """Crear un nuevo Site (requiere autenticación)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if "name" not in data or "country" not in data:
        raise HTTPException(status_code=400, detail="Los campos 'name' y 'country' son obligatorios")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/sites/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )
    
    return response.json()

@app.get("/sites/", dependencies=[Depends(auth_required)])
async def get_sites(request: Request, country_id: str = None):
    """Obtener lista de Sites, opcionalmente filtrados por country_id"""
    token = request.headers.get("Authorization")

    params = {}
    if country_id:
        params["country_id"] = country_id

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/sites/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            params=params
        )
    return response.json()


#**********************************************************
# 📍 Gestión de Áreas
#**********************************************************
@app.post("/areas/", dependencies=[Depends(auth_required)])
async def create_area(request: Request):
    """Crear una nueva Área (requiere autenticación)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if "name" not in data or "site" not in data:
        raise HTTPException(status_code=400, detail="Los campos 'name' y 'site' son obligatorios")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/areas/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )
    
    return response.json()

@app.get("/areas/", dependencies=[Depends(auth_required)])
async def get_areas(request: Request, site_id: str = None, country_id: str = None):
    """Obtener lista de Áreas, filtradas por site_id o country_id"""
    token = request.headers.get("Authorization")

    params = {}
    if site_id:
        params["site_id"] = site_id
    elif country_id:
        params["country_id"] = country_id

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/areas/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            params=params
        )
    return response.json()


#****************************************
# 📂 Gestión de Respaldo Automático
#****************************************
# Actualizar el horario del respaldo
@app.post("/backup-config/schedule/", dependencies=[Depends(admin_required)])
async def update_backup_schedule(request: Request):
    """Actualizar la hora de programación del respaldo automático (Solo Admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/backup-config/schedule/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Error al actualizar la programación del respaldo")

# Obtener el horario del respaldo
@app.get("/backup-config/schedule/", dependencies=[Depends(admin_required)])
async def get_backup_schedule(request: Request):
    """Obtener la hora programada del respaldo automático"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/backup-config/schedule/get/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    
    if response.status_code == 200:
        return response.json()
    
    raise HTTPException(status_code=response.status_code, detail="Error obteniendo la hora programada")

#****************************************
# 📡 Utilidades y Herramientas
#****************************************
@app.post("/ping/")
async def ping_device(request: Request):
    """Hacer ping a un dispositivo"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/ping/", 
            json=data, 
            headers={"Authorization": f"Bearer {token.split()[-1]}",},
            timeout=10.0)

    return response.json()

#****************************************
# Importacion de equipos
#****************************************
@app.post("/classification-rules/", dependencies=[Depends(auth_required)])
async def create_classification_rules(request: Request):
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/classification-rules/",
            json=data,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@app.post("/networkdevice/bulk/from-zabbix/", dependencies=[Depends(auth_required)])
async def classify_from_zabbix(request: Request):
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/networkdevice/bulk/from-zabbix/",
            json=data,
            timeout=30,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@app.post("/networkdevice/bulk/from-csv/", dependencies=[Depends(auth_required)])
async def classify_from_csv(request: Request):
    token = request.headers.get("Authorization")
    form = await request.form()
    files = {"file": (form["file"].filename, await form["file"].read())}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/networkdevice/bulk/from-csv/",
            data={"ruleSetId": form["ruleSetId"]},
            files=files,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@app.post("/networkdevice/bulk/save/", dependencies=[Depends(auth_required)])
async def save_classified_hosts(request: Request):
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/networkdevice/bulk/save/",
            json=data,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

#**********************************************************
# 📂 Reglas de Clasificación (CRUD desde el proxy)
#**********************************************************
@app.get("/classification-rules/", dependencies=[Depends(auth_required)])
async def get_classification_rules(request: Request):
    """Obtener todos los conjuntos de reglas de clasificación"""
    token = request.headers.get("Authorization")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/classification-rules/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@app.put("/classification-rules/{rule_id}/", dependencies=[Depends(auth_required)])
async def update_classification_rules(rule_id: str, request: Request):
    """Actualizar un conjunto de reglas de clasificación"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{DJANGO_API_URL}/classification-rules/{rule_id}/",
            json=data,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@app.delete("/classification-rules/{rule_id}/", dependencies=[Depends(auth_required)])
async def delete_classification_rules(rule_id: str, request: Request):
    """Eliminar un conjunto de reglas de clasificación"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{DJANGO_API_URL}/classification-rules/{rule_id}/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )

    if response.status_code == 204:
        return {"message": "Eliminado correctamente"}
    raise HTTPException(status_code=response.status_code, detail="Error eliminando regla")


#****************************************
# 🔄 Evaluación de Conexión Zabbix 
#****************************************
@app.get("/zabbix/status/", dependencies=[Depends(auth_required)])
async def check_zabbix_status(request: Request):
    """Evaluar el estado de la conexión con Zabbix"""
    token = request.headers.get("Authorization")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{DJANGO_API_URL}/zabbix/status/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  
        )
        
    if response.status_code == 200:
        return response.json()
    raise HTTPException(
        status_code=response.status_code, 
        detail="Error al verificar el estado de Zabbix"
    )

#****************************************
# 🩺 Servicio de Salud del Proxy
#****************************************
@app.get("/health/")
async def health_service():
    """Verificar si el servicio proxy está activo."""
    return {"status": "ok", "message": "Proxy service is running"}
