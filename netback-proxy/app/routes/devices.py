import httpx
from fastapi import APIRouter, Request, Depends, Response
from app.config import settings
from app.dependencies import auth_required, admin_required

router = APIRouter()

@router.post("/networkdevice/", dependencies=[Depends(admin_required)])
async def create_device(request: Request):
    """Crear dispositivo (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    xsrf = request.headers.get("X-CSRF-Token")
    headers = {"Authorization": f"Bearer {token.split()[-1]}"}
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/networkdevice/",
            json=data,
            headers=headers,
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

@router.get("/networkdevice/")
async def get_devices(request: Request, user=Depends(auth_required)):
    """Obtener lista de dispositivos"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/networkdevice/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

@router.get("/networkdevice/{device_id}/")
async def get_device_by_id(device_id: str, request: Request, user=Depends(auth_required)):
    """Obtener un dispositivo por su ID"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/networkdevice/{device_id}/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

@router.patch("/networkdevice/{device_id}/")
async def update_device(device_id: str, request: Request, user=Depends(auth_required)):
    """Actualizar dispositivo (solo admins)"""
    token = request.headers.get("Authorization")
    data = await request.json()
    print(f"Actualizando dispositivo {device_id} con datos: {data}")

    xsrf = request.headers.get("X-CSRF-Token")
    headers = {"Authorization": f"Bearer {token.split()[-1]}"}
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.full_django_api_url}/networkdevice/{device_id}/",
            json=data,
            headers=headers,
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )

@router.delete("/networkdevice/{device_id}/", dependencies=[Depends(admin_required)])
async def delete_device(device_id: str, request: Request):
    """Eliminar dispositivo (solo admins)"""
    token = request.headers.get("Authorization")

    xsrf = request.headers.get("X-CSRF-Token")
    headers = {"Authorization": f"Bearer {token.split()[-1]}"}
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.full_django_api_url}/networkdevice/{device_id}/",
            headers=headers,
            cookies=request.cookies,
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/json"),
    )
