import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from app.config import settings
from app.dependencies import auth_required

router = APIRouter()

@router.get("/manufacturers/", dependencies=[Depends(auth_required)])
async def get_manufacturers(request: Request):
    """Obtener lista de fabricantes (requiere autenticación)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.full_django_api_url}/manufacturers/", headers={"Authorization": f"Bearer {token.split()[-1]}"})
    return response.json()

@router.get("/devicetypes/", dependencies=[Depends(auth_required)])
async def get_device_types(request: Request):
    """Obtener lista de tipos de equipos (requiere autenticación)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.full_django_api_url}/devicetypes/", headers={"Authorization": f"Bearer {token.split()[-1]}"})
    return response.json()

@router.post("/countries/", dependencies=[Depends(auth_required)])
async def create_country(request: Request):
    """Crear un nuevo País (requiere autenticación)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if "name" not in data:
        raise HTTPException(status_code=400, detail="El campo 'name' es obligatorio")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/countries/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )
    
    return response.json()

@router.get("/countries/", dependencies=[Depends(auth_required)])
async def get_countries(request: Request):
    """Obtener lista de Países (requiere autenticación)"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.full_django_api_url}/countries/", headers={"Authorization": f"Bearer {token.split()[-1]}"})
    return response.json()

@router.post("/sites/", dependencies=[Depends(auth_required)])
async def create_site(request: Request):
    """Crear un nuevo Site (requiere autenticación)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if "name" not in data or "country" not in data:
        raise HTTPException(status_code=400, detail="Los campos 'name' y 'country' son obligatorios")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/sites/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )
    
    return response.json()

@router.get("/sites/", dependencies=[Depends(auth_required)])
async def get_sites(request: Request, country_id: str = None):
    """Obtener lista de Sites, opcionalmente filtrados por country_id"""
    token = request.headers.get("Authorization")

    params = {}
    if country_id:
        params["country_id"] = country_id

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/sites/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            params=params
        )
    return response.json()

@router.post("/areas/", dependencies=[Depends(auth_required)])
async def create_area(request: Request):
    """Crear una nueva Área (requiere autenticación)"""
    token = request.headers.get("Authorization")
    data = await request.json()

    if "name" not in data or "site" not in data:
        raise HTTPException(status_code=400, detail="Los campos 'name' y 'site' son obligatorios")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/areas/",
            headers={"Authorization": f"Bearer {token.split()[-1]}", "Content-Type": "application/json"},
            json=data
        )
    
    return response.json()

@router.get("/areas/", dependencies=[Depends(auth_required)])
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
            f"{settings.full_django_api_url}/areas/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            params=params
        )
    return response.json()
