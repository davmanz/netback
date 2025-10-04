import httpx
import logging
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Response
from pydantic import BaseModel
from app.config import settings
from app.utils.cookie_utils import parse_httpx_cookies_to_response

router = APIRouter()


def _set_or_delete_cookie(resp: Response, name: str, value: str, *, httponly: bool = False, secure: bool = False, samesite: str = "Lax", path: str = "/", max_age: Optional[int] = None):
    """Normaliza el valor de cookie (quita comillas si existen) y elimina la cookie si el valor queda vacío.

    Esto evita que se envíen valores con comillas dobles como '""' en los Set-Cookie.
    """
    if value is None:
        value = ""
    # quitar comillas envolventes si las hay
    if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
        value = value[1:-1]
    # strip whitespace
    value = value.strip()

    # Si el valor es vacío, eliminar la cookie (emitir Set-Cookie de borrado)
    if value == "":
        # Construir header Set-Cookie sin comillas para borrar la cookie
        expire = "Thu, 01 Jan 1970 00:00:00 GMT"
        # name= (vacio) para asegurar eliminación
        parts = [f"{name}=", f"Expires={expire}", "Max-Age=0", f"Path={path}", f"SameSite={samesite}"]
        if secure:
            parts.append("Secure")
        if httponly:
            parts.append("HttpOnly")
        header_value = "; ".join(parts)
        # Añadir encabezado Set-Cookie explícito sin usar resp.delete_cookie
        resp.headers.append("set-cookie", header_value)
        return

    # Caso normal: establecer cookie
    if max_age is not None:
        resp.set_cookie(key=name, value=value, httponly=httponly, secure=secure, samesite=samesite, path=path, max_age=max_age)
    else:
        resp.set_cookie(key=name, value=value, httponly=httponly, secure=secure, samesite=samesite, path=path)


class UserLogin(BaseModel):
    username: str
    password: str


@router.post("/auth/login/")
async def login(user: UserLogin):
    """Autenticar usuario y obtener token delegando al backend y reenviando headers (incluyendo Set-Cookie)."""
    async with httpx.AsyncClient() as client:
        backend_resp = await client.post(f"{settings.full_django_api_url}/token/", json=user.dict())

    # Si backend retornó 200, construimos una Response que incluye
    # body y todas las cabeceras originales (en particular Set-Cookie).
    if backend_resp.status_code == 200:
        # Crear respuesta FastAPI con mismo contenido y media_type
        resp = Response(content=backend_resp.content, status_code=backend_resp.status_code,
                        media_type=backend_resp.headers.get("content-type", "application/json"))

        # Copiar headers normales (excepto content-length)
        for k, v in backend_resp.headers.items():
            if k.lower() == "content-length":
                continue
            if k.lower() == "set-cookie":
                # omitimos; manejaremos cookies de forma explícita
                continue
            resp.headers[k] = v

        # Parsear cookies desde la respuesta del backend y añadirlas a la Response
        parse_httpx_cookies_to_response(
            backend_resp,
            resp,
            refresh_name=getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh"),
            xsrf_name=getattr(settings, "CSRF_COOKIE_NAME", "XSRF-TOKEN"),
            refresh_opts={
                "secure": getattr(settings, "JWT_REFRESH_COOKIE_SECURE", False),
                "samesite": getattr(settings, "JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
                "path": getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/"),
                "max_age": getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            },
            xsrf_opts={
                "secure": getattr(settings, "CSRF_COOKIE_SECURE", False),
                "samesite": getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax"),
                "path": "/",
                "max_age": getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            },
        )

        return resp

    raise HTTPException(status_code=backend_resp.status_code, detail=backend_resp.text)


@router.post("/token/refresh/")
@router.post("/api/token/refresh/")
async def refresh_token(request: Request):
    """Refrescar access token delegando al backend. Lee cookies del request y las reenvía.
    Responde con el body del backend y propaga cualquier Set-Cookie retornada.
    """
    # Leer body si existe
    try:
        body = await request.json()
    except Exception:
        body = None

    async with httpx.AsyncClient() as client:
        # reenviar cookies del request al backend
        response = await client.post(
            f"{settings.full_django_api_url}/token/refresh/",
            json=(body or {}),
            cookies=request.cookies,
        )

    if response.status_code == 200:
        resp = Response(content=response.content, status_code=response.status_code,
                        media_type=response.headers.get("content-type", "application/json"))
        for k, v in response.headers.items():
            if k.lower() == "content-length":
                continue
            if k.lower() == "set-cookie":
                continue
            resp.headers[k] = v

        # Parsear cookies desde la respuesta del backend y añadirlas a la Response
        parse_httpx_cookies_to_response(
            response,
            resp,
            refresh_name=getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh"),
            xsrf_name=getattr(settings, "CSRF_COOKIE_NAME", "XSRF-TOKEN"),
            refresh_opts={
                "secure": getattr(settings, "JWT_REFRESH_COOKIE_SECURE", False),
                "samesite": getattr(settings, "JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
                "path": getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/"),
                "max_age": getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            },
            xsrf_opts={
                "secure": getattr(settings, "CSRF_COOKIE_SECURE", False),
                "samesite": getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax"),
                "path": "/",
                "max_age": getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            },
        )

        return resp

    raise HTTPException(status_code=response.status_code, detail=response.text)


@router.post("/token/logout/")
@router.post("/api/token/logout/")
async def logout(request: Request):
    """Delegar logout al backend y propagar la eliminación de cookie (Set-Cookie delete)."""
    try:
        body = await request.json()
    except Exception:
        body = None

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/token/logout/",
            json=(body or {}),
            cookies=request.cookies,
        )

    if response.status_code in (200, 204):
        resp = Response(content=response.content, status_code=response.status_code,
                        media_type=response.headers.get("content-type", "application/json"))
        for k, v in response.headers.items():
            if k.lower() == "content-length":
                continue
            if k.lower() == "set-cookie":
                continue
            resp.headers[k] = v

        # Parsear cookies desde la respuesta del backend y añadirlas a la Response
        parse_httpx_cookies_to_response(
            response,
            resp,
            refresh_name=getattr(settings, "JWT_REFRESH_COOKIE_NAME", "refresh"),
            xsrf_name=getattr(settings, "CSRF_COOKIE_NAME", "XSRF-TOKEN"),
            refresh_opts={
                "secure": getattr(settings, "JWT_REFRESH_COOKIE_SECURE", False),
                "samesite": getattr(settings, "JWT_REFRESH_COOKIE_SAMESITE", "Lax"),
                "path": getattr(settings, "JWT_REFRESH_COOKIE_PATH", "/"),
                "max_age": getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            },
            xsrf_opts={
                "secure": getattr(settings, "CSRF_COOKIE_SECURE", False),
                "samesite": getattr(settings, "CSRF_COOKIE_SAMESITE", "Lax"),
                "path": "/",
                "max_age": getattr(settings, "JWT_REFRESH_COOKIE_MAX_AGE", 604800),
            },
        )

        return resp

    raise HTTPException(status_code=response.status_code, detail=response.text)
