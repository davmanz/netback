import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, users, devices, vault, locations, backups, utils

# Configurar logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
    allow_origins=settings.ALLOW_ORIGINS,
)

# Incluir routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(devices.router)
app.include_router(vault.router)
app.include_router(locations.router)
app.include_router(backups.router)
app.include_router(utils.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )