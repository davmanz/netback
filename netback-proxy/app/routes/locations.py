import httpx
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, Response
from app.config import settings
from app.dependencies import auth_required

router = APIRouter()

@router.get("/manufacturers/", dependencies=[Depends(auth_required)])
async def get_manufacturers(request: Request):
    """Obtener lista de fabricantes (requiere autenticación)"""
    token = request.headers.get("Authorization")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/manufacturers/",
            headers=headers,
            cookies=request.cookies,
        )

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.get("/devicetypes/", dependencies=[Depends(auth_required)])
async def get_device_types(request: Request):
    """Obtener lista de tipos de equipos (requiere autenticación)"""
    token = request.headers.get("Authorization")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/devicetypes/",
            headers=headers,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.post("/countries/", dependencies=[Depends(auth_required)])
async def create_country(request: Request):
    """Crear un nuevo País (requiere autenticación)"""
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    if "name" not in data:
        raise HTTPException(status_code=400, detail="El campo 'name' es obligatorio")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/countries/",
            headers=headers,
            json=data,
            cookies=request.cookies,
        )

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.get("/countries/", dependencies=[Depends(auth_required)])
async def get_countries(request: Request):
    """Obtener lista de Países (requiere autenticación)"""
    token = request.headers.get("Authorization")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/countries/",
            headers=headers,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.post("/sites/", dependencies=[Depends(auth_required)])
async def create_site(request: Request):
    """Crear un nuevo Site (requiere autenticación)"""
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    if "name" not in data or "country" not in data:
        raise HTTPException(status_code=400, detail="Los campos 'name' y 'country' son obligatorios")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/sites/",
            headers=headers,
            json=data,
            cookies=request.cookies,
        )

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.get("/sites/", dependencies=[Depends(auth_required)])
async def get_sites(request: Request, country_id: Optional[str] = None):
    """Obtener lista de Sites, opcionalmente filtrados por country_id"""
    token = request.headers.get("Authorization")

    params = {}
    if country_id:
        params["country_id"] = country_id

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/sites/",
            headers=headers,
            params=params,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

# PATCH endpoints para updates parciales
@router.patch("/countries/{country_id}/", dependencies=[Depends(auth_required)])
async def patch_country(country_id: str, request: Request):
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.full_django_api_url}/countries/{country_id}/",
            headers=headers,
            json=data,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.patch("/sites/{site_id}/", dependencies=[Depends(auth_required)])
async def patch_site(site_id: str, request: Request):
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.full_django_api_url}/sites/{site_id}/",
            headers=headers,
            json=data,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.patch("/areas/{area_id}/", dependencies=[Depends(auth_required)])
async def patch_area(area_id: str, request: Request):
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{settings.full_django_api_url}/areas/{area_id}/",
            headers=headers,
            json=data,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.post("/areas/", dependencies=[Depends(auth_required)])
async def create_area(request: Request):
    """Crear una nueva Área (requiere autenticación)"""
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    if "name" not in data or "site" not in data:
        raise HTTPException(status_code=400, detail="Los campos 'name' y 'site' son obligatorios")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/areas/",
            headers=headers,
            json=data,
            cookies=request.cookies,
        )

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp

@router.get("/areas/", dependencies=[Depends(auth_required)])
async def get_areas(request: Request, site_id: Optional[str] = None, country_id: Optional[str] = None):
    """Obtener lista de Áreas, filtradas por site_id o country_id"""
    token = request.headers.get("Authorization")

    params = {}
    if site_id:
        params["site_id"] = site_id
    elif country_id:
        params["country_id"] = country_id

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/areas/",
            headers=headers,
            params=params,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() in ("content-length",):
            continue
        resp.headers[k] = v
    return resp
