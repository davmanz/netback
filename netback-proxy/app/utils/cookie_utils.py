import re
from typing import Optional, Dict, Any
from fastapi import Response


def _set_or_delete_cookie(resp: Response, name: str, value: str, *, httponly: bool = False, secure: bool = False, samesite: str = "Lax", path: str = "/", max_age: Optional[int] = None):
    """Normaliza valor de cookie y borra o establece en la Response.

    - Quita comillas envolventes si las hubiera.
    - Si value es vacío, emite un Set-Cookie de borrado sin comillas.
    - Si value no es vacío, usa resp.set_cookie con los flags.
    """
    if value is None:
        value = ""
    # quitar comillas envolventes si las hay
    if len(value) >= 2 and ((value[0] == '"' and value[-1] == '"') or (value[0] == "'" and value[-1] == "'")):
        value = value[1:-1]
    value = value.strip()

    if value == "":
        expire = "Thu, 01 Jan 1970 00:00:00 GMT"
        parts = [f"{name}=", f"Expires={expire}", "Max-Age=0", f"Path={path}", f"SameSite={samesite}"]
        if secure:
            parts.append("Secure")
        if httponly:
            parts.append("HttpOnly")
        header_value = "; ".join(parts)
        resp.headers.append("set-cookie", header_value)
        return

    if max_age is not None:
        resp.set_cookie(key=name, value=value, httponly=httponly, secure=secure, samesite=samesite, path=path, max_age=max_age)
    else:
        resp.set_cookie(key=name, value=value, httponly=httponly, secure=secure, samesite=samesite, path=path)


def parse_httpx_cookies_to_response(httpx_resp, resp: Response, *, refresh_name: str = "refresh", xsrf_name: str = "XSRF-TOKEN", refresh_opts: Optional[Dict[str, Any]] = None, xsrf_opts: Optional[Dict[str, Any]] = None):
    """Extrae cookies de un httpx.Response y las añade a una fastapi.Response.

    Usa preferentemente httpx_resp.cookies.jar; si no está disponible hace un fallback
    buscando en el header 'set-cookie' mediante regex para refresh y xsrf.
    """
    refresh_opts = refresh_opts or {}
    xsrf_opts = xsrf_opts or {}

    try:
        jar = getattr(httpx_resp.cookies, "jar", None)
        if jar:
            for name, morsel in jar.items():
                cookie_name = morsel.name
                cookie_value = morsel.value
                if cookie_name == refresh_name:
                    _set_or_delete_cookie(resp, cookie_name, cookie_value, httponly=True, **refresh_opts)
                else:
                    _set_or_delete_cookie(resp, cookie_name, cookie_value, httponly=False, **xsrf_opts)
            return
    except Exception:
        # ignore and fallback to header parsing
        pass

    # Fallback: parsear header 'set-cookie' buscando names específicos
    sc = httpx_resp.headers.get("set-cookie")
    if not sc:
        return

    # Buscar refresh
    m = re.search(r"(?i)\b" + re.escape(refresh_name) + r"=([^;\s]+)", sc)
    if m:
        _set_or_delete_cookie(resp, refresh_name, m.group(1), httponly=True, **(refresh_opts or {}))

    # Buscar XSRF
    m2 = re.search(r"(?i)\b" + re.escape(xsrf_name) + r"=([^;\s]+)", sc)
    if m2:
        _set_or_delete_cookie(resp, xsrf_name, m2.group(1), httponly=False, **(xsrf_opts or {}))
