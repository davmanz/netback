import httpx
import logging
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.config import settings

router = APIRouter()

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/auth/login/")
async def login(user: UserLogin):
    """Autenticar usuario y obtener token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{settings.full_django_api_url}/token/", json=user.dict())

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=401, detail="Credenciales incorrectas")
