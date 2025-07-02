import requests
from fastapi import Depends, HTTPException, Header
from .config import settings

def auth_required(authorization: str = Header(None)):
    """Validar token y obtener usuario autenticado"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    token = authorization.split(" ")[-1]
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{settings.full_django_api_url}/users/me/", headers=headers)
        response.raise_for_status()
    except requests.RequestException:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    return response.json()

def admin_required(user=Depends(auth_required)):
    """Validar que el usuario tenga rol de administrador"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado, se requiere rol de administrador")
    return user
