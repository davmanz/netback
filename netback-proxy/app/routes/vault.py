import httpx
from fastapi import APIRouter, Request, Depends, Response
from app.config import settings
from app.dependencies import auth_required

router = APIRouter()

@router.post("/vaultcredentials/", dependencies=[Depends(auth_required)])
async def create_vault_credential(request: Request):
    """Crear una nueva credencial Vault"""
    token = request.headers.get("Authorization")
    data = await request.json()
    xsrf = request.headers.get("X-CSRF-Token")

    headers = {"Authorization": f"Bearer {token.split()[-1]}"}
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/vaultcredentials/",
            json=data,
            headers=headers,
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

@router.get("/vaultcredentials/", dependencies=[Depends(auth_required)])
async def get_vault_credentials(request: Request):
    """Obtener lista de credenciales Vault"""
    token = request.headers.get("Authorization")
    # GET no requiere CSRF, pero reenviamos cookies igualmente

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/vaultcredentials/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

@router.put("/vaultcredentials/{credential_id}/", dependencies=[Depends(auth_required)])
async def update_vault_credential(credential_id: str, request: Request):
    """Actualizar una credencial Vault"""
    token = request.headers.get("Authorization")
    data = await request.json()
    xsrf = request.headers.get("X-CSRF-Token")

    headers = {"Authorization": f"Bearer {token.split()[-1]}"}
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.full_django_api_url}/vaultcredentials/{credential_id}/",
            json=data,
            headers=headers,
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

@router.delete("/vaultcredentials/{credential_id}/", dependencies=[Depends(auth_required)])
async def delete_vault_credential(credential_id: str, request: Request):
    """Eliminar una credencial Vault"""
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")

    headers = {"Authorization": f"Bearer {token.split()[-1]}"}
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.full_django_api_url}/vaultcredentials/{credential_id}/",
            headers=headers,
            cookies=request.cookies,
        )

    # Propagar status code y body del backend (si 204, body vacío)
    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )
