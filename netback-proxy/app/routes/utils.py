import httpx
import logging
from fastapi import APIRouter, Request, Depends, HTTPException, Response
from app.config import settings
from app.dependencies import auth_required

router = APIRouter()

@router.post("/ping/")
async def ping_device(request: Request):
    """Hacer ping a un dispositivo"""
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/ping/",
            json=data,
            headers=headers,
            cookies=request.cookies,
            timeout=10.0,
        )

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() == "content-length":
            continue
        resp.headers[k] = v
    return resp

@router.post("/classification-rules/", dependencies=[Depends(auth_required)])
async def create_classification_rules(request: Request):
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/classification-rules/",
            json=data,
            headers=headers,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() == "content-length":
            continue
        resp.headers[k] = v
    return resp

@router.post("/networkdevice/bulk/from-zabbix/", dependencies=[Depends(auth_required)])
async def classify_from_zabbix(request: Request):
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.full_django_api_url}/networkdevice/bulk/from-zabbix/",
                json=data,
                timeout=10.0,
                headers=headers,
                cookies=request.cookies,
            )
        resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
        for k, v in response.headers.items():
            if k.lower() == "content-length":
                continue
            resp.headers[k] = v
        return resp
    except httpx.ReadTimeout:
        # Devolver un 504 Gateway Timeout controlado, confirmando que el proxy recibió y procesó la solicitud
        return Response(
            content='{"detail":"Zabbix upstream timeout"}',
            status_code=504,
            media_type="application/json",
        )

@router.post("/networkdevice/bulk/from-csv/", dependencies=[Depends(auth_required)])
async def classify_from_csv(request: Request):
    token = request.headers.get("Authorization")
    form = await request.form()
    files = {"file": (form["file"].filename, await form["file"].read())}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/networkdevice/bulk/from-csv/",
            data={"ruleSetId": form["ruleSetId"]},
            files=files,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@router.post("/networkdevice/bulk/save/", dependencies=[Depends(auth_required)])
async def save_classified_hosts(request: Request):
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/networkdevice/bulk/save/",
            json=data,
            headers=headers,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() == "content-length":
            continue
        resp.headers[k] = v
    return resp

@router.get("/classification-rules/", dependencies=[Depends(auth_required)])
async def get_classification_rules(request: Request):
    """Obtener todos los conjuntos de reglas de clasificación"""
    token = request.headers.get("Authorization")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/classification-rules/",
            headers=headers,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() == "content-length":
            continue
        resp.headers[k] = v
    return resp

@router.put("/classification-rules/{rule_id}/", dependencies=[Depends(auth_required)])
async def update_classification_rules(rule_id: str, request: Request):
    """Actualizar un conjunto de reglas de clasificación"""
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")
    data = await request.json()

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.full_django_api_url}/classification-rules/{rule_id}/",
            json=data,
            headers=headers,
            cookies=request.cookies,
        )
    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() == "content-length":
            continue
        resp.headers[k] = v
    return resp

@router.delete("/classification-rules/{rule_id}/", dependencies=[Depends(auth_required)])
async def delete_classification_rules(rule_id: str, request: Request):
    """Eliminar un conjunto de reglas de clasificación"""
    token = request.headers.get("Authorization")
    xsrf = request.headers.get("X-CSRF-Token")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"
    if xsrf:
        headers["X-CSRF-Token"] = xsrf

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.full_django_api_url}/classification-rules/{rule_id}/",
            headers=headers,
            cookies=request.cookies,
        )

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() == "content-length":
            continue
        resp.headers[k] = v
    return resp

@router.get("/zabbix/status/", dependencies=[Depends(auth_required)])
async def check_zabbix_status(request: Request):
    """Evaluar el estado de la conexión con Zabbix"""
    token = request.headers.get("Authorization")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token.split()[-1]}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/zabbix/status/",
            headers=headers,
            cookies=request.cookies,
            timeout=30.0,
        )

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    for k, v in response.headers.items():
        if k.lower() == "content-length":
            continue
        resp.headers[k] = v
    return resp

@router.get("/health/")
async def health_service():
    """Verificar si el servicio proxy está activo."""
    return {"status": "ok", "message": "Proxy service is running"}


# Catch-all proxy for any /api/... path not explicitly handled above
@router.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy_api(path: str, request: Request):
    """Proxy genérico que reenvía la petición al backend Django y devuelve la respuesta reproduciendo Set-Cookie si existe."""
    logging.info(f"Proxying {request.method} /api/{path} to backend")
    backend_base = settings.full_django_api_url.rstrip("/")
    url = f"{backend_base}/{path}"
    method = request.method.upper()

    # preparar headers y cookies (eliminar Host)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}
    cookies = request.cookies

    # leer body si existe
    try:
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            request_json = await request.json()
            request_content = None
        else:
            request_json = None
            request_content = await request.body()
    except Exception:
        request_json = None
        request_content = await request.body()

    async with httpx.AsyncClient() as client:
        if request_json is not None:
            response = await client.request(method, url, json=request_json, headers=headers, cookies=cookies)
        else:
            response = await client.request(method, url, content=request_content, headers=headers, cookies=cookies)

    resp = Response(content=response.content, status_code=response.status_code, media_type=response.headers.get("content-type", "application/json"))
    # Intentar copiar raw_headers exactamente como vienen del backend (preserva múltiples Set-Cookie)
    try:
        resp.raw_headers = list(response.raw_headers)
    except Exception:
        # Fallback: copiar headers de forma normal
        for k, v in response.headers.items():
            if k.lower() == "content-length":
                continue
            resp.headers[k] = v
    return resp
