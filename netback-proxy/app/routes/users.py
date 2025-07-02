import httpx
import logging
from fastapi import APIRouter, Request, Depends, HTTPException
from app.config import settings
from app.dependencies import admin_required

router = APIRouter()

@router.get("/users/me/")
async def get_current_user(request: Request):
    """Devuelve información del usuario autenticado"""
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/users/me/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Error obteniendo usuario actual")

@router.post("/users/", dependencies=[Depends(admin_required)])
async def create_user(request: Request):
    """Crear usuario (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.full_django_api_url}/users/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    if response.status_code == 201:
        logging.info(f"Usuario creado: {data['username']}")
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Error creando usuario")

@router.get("/users/", dependencies=[Depends(admin_required)])
async def get_users(request: Request):
    """Obtener lista de usuarios (solo admins)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.full_django_api_url}/users/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.put("/users/{user_id}/")
async def update_user(user_id: str, request: Request, user=Depends(admin_required)):
    """Actualizar usuario (usuarios pueden editar su perfil, admins pueden editar a todos)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if user["role"] != "admin" and user["id"] != user_id:
        raise HTTPException(status_code=403, detail="No puedes modificar otros usuarios")

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{settings.full_django_api_url}/users/{user_id}/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.delete("/users/{user_id}/", dependencies=[Depends(admin_required)])
async def delete_user(user_id: str, request: Request):
    """Eliminar usuario (solo admins)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{settings.full_django_api_url}/users/{user_id}/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    if response.status_code == 204:
        logging.info(f"Usuario eliminado: {user_id}")
        return {"message": "Usuario eliminado exitosamente"}
    raise HTTPException(status_code=response.status_code, detail="Error eliminando usuario")
