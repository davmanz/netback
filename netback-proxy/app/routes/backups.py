import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from app.config import settings
from app.dependencies import auth_required, admin_required

router = APIRouter()

@router.post("/networkdevice/{device_id}/backup/", dependencies=[Depends(auth_required)])
async def backup_device(device_id: str, request: Request):
    """Generar un nuevo respaldo de un dispositivo."""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/networkdevice/{device_id}/backup/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0
        )

    return response.json()

@router.get("/backups_last/", dependencies=[Depends(auth_required)])
async def get_last_backups(request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/backups/last/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0
        )

    return response.json()

@router.get("/networkdevice/{device_id}/backups/", dependencies=[Depends(auth_required)])
async def get_backup_history(device_id: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/networkdevice/{device_id}/backups/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0
        )

    return response.json()

@router.get("/backup/{backup_id}/", dependencies=[Depends(auth_required)])
async def get_backup(backup_id: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/backup/{backup_id}/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0
        )

    return response.json()

@router.get("/backups/compare/{backupOldId}/{backupNewId}/", dependencies=[Depends(auth_required)])
async def compare_specific_backups(backupOldId: str, backupNewId: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/backups/compare/{backupOldId}/{backupNewId}/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0
        )

    return response.json()

@router.get("/networkdevice/{device_id}/compare/", dependencies=[Depends(auth_required)])
async def compare_last_backups(device_id: str, request: Request):
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/networkdevice/{device_id}/compare/", 
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0
        )

    return response.json()

@router.post("/backup-config/schedule/", dependencies=[Depends(admin_required)])
async def update_backup_schedule(request: Request):
    """Actualizar la hora de programación del respaldo automático (Solo Admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/backup-config/schedule/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Error al actualizar la programación del respaldo")

@router.get("/backup-config/schedule/", dependencies=[Depends(admin_required)])
async def get_backup_schedule(request: Request):
    """Obtener la hora programada del respaldo automático"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/backup-config/schedule/get/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    
    if response.status_code == 200:
        return response.json()
    
    raise HTTPException(status_code=response.status_code, detail="Error obteniendo la hora programada")
