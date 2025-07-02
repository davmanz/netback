import httpx
from fastapi import APIRouter, Request, Depends
from app.config import settings
from app.dependencies import auth_required, admin_required

router = APIRouter()

@router.post("/networkdevice/", dependencies=[Depends(admin_required)])
async def create_device(request: Request):
    """Crear dispositivo (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.full_django_api_url}/networkdevice/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.get("/networkdevice/")
async def get_devices(request: Request, user=Depends(auth_required)):
    """Obtener lista de dispositivos"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.full_django_api_url}/networkdevice/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.get("/networkdevice/{device_id}/")
async def get_device_by_id(device_id: str, request: Request, user=Depends(auth_required)):
    """Obtener un dispositivo por su ID"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/networkdevice/{device_id}/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )

    return response.json()

@router.patch("/networkdevice/{device_id}/")
async def update_device(device_id: str, request: Request, user=Depends(auth_required)):
    """Actualizar dispositivo (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()
    print(f"Actualizando dispositivo {device_id} con datos: {data}")

    async with httpx.AsyncClient() as client:
        response = await client.patch(f"{settings.full_django_api_url}/networkdevice/{device_id}/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.delete("/networkdevice/{device_id}/", dependencies=[Depends(admin_required)])
async def delete_device(device_id: str, request: Request):
    """Eliminar dispositivo (solo admins)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{settings.full_django_api_url}/networkdevice/{device_id}/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return {"message": "Dispositivo eliminado"}
