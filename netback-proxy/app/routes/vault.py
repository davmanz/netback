import httpx
from fastapi import APIRouter, Request, Depends
from app.config import settings
from app.dependencies import auth_required

router = APIRouter()

@router.post("/vaultcredentials/", dependencies=[Depends(auth_required)])
async def create_vault_credential(request: Request):
    """Crear una nueva credencial Vault"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.full_django_api_url}/vaultcredentials/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.get("/vaultcredentials/", dependencies=[Depends(auth_required)])
async def get_vault_credentials(request: Request):
    """Obtener lista de credenciales Vault"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.full_django_api_url}/vaultcredentials/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.put("/vaultcredentials/{credential_id}/", dependencies=[Depends(auth_required)])
async def update_vault_credential(credential_id: str, request: Request):
    """Actualizar una credencial Vault"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{settings.full_django_api_url}/vaultcredentials/{credential_id}/", json=data, headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return response.json()

@router.delete("/vaultcredentials/{credential_id}/", dependencies=[Depends(auth_required)])
async def delete_vault_credential(credential_id: str, request: Request):
    """Eliminar una credencial Vault"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{settings.full_django_api_url}/vaultcredentials/{credential_id}/", headers={"Authorization": f"Bearer {token.split()[-1]}"})

    return {"message": "Credencial eliminada"}
