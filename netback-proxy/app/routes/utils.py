import httpx
from fastapi import APIRouter, Request, Depends, HTTPException
from app.config import settings
from app.dependencies import auth_required

router = APIRouter()

@router.post("/ping/")
async def ping_device(request: Request):
    """Hacer ping a un dispositivo"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/ping/", 
            json=data, 
            headers={"Authorization": f"Bearer {token.split()[-1]}",},
            timeout=10.0)

    return response.json()

@router.post("/classification-rules/", dependencies=[Depends(auth_required)])
async def create_classification_rules(request: Request):
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/classification-rules/",
            json=data,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@router.post("/networkdevice/bulk/from-zabbix/", dependencies=[Depends(auth_required)])
async def classify_from_zabbix(request: Request):
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/networkdevice/bulk/from-zabbix/",
            json=data,
            timeout=30,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

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
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.full_django_api_url}/networkdevice/bulk/save/",
            json=data,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    
    # Agregar manejo de errores para respuestas no-JSON
    try:
        if response.status_code == 200:
            return response.json()
        else:
            # Si hay error HTTP, intentar parsear JSON de error o devolver texto plano
            try:
                error_data = response.json()
                return {"error": error_data, "status_code": response.status_code}
            except:
                # Si no es JSON válido, devolver el texto de la respuesta
                return {
                    "error": f"Backend error: {response.text}", 
                    "status_code": response.status_code
                }
    except Exception as e:
        # Si falla completamente el parseo
        return {
            "error": f"Failed to parse response: {str(e)}", 
            "raw_response": response.text,
            "status_code": response.status_code
        }

@router.get("/classification-rules/", dependencies=[Depends(auth_required)])
async def get_classification_rules(request: Request):
    """Obtener todos los conjuntos de reglas de clasificación"""
    token = request.headers.get("Authorization")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/classification-rules/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@router.put("/classification-rules/{rule_id}/", dependencies=[Depends(auth_required)])
async def update_classification_rules(rule_id: str, request: Request):
    """Actualizar un conjunto de reglas de clasificación"""
    token = request.headers.get("Authorization")
    data = await request.json()

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{settings.full_django_api_url}/classification-rules/{rule_id}/",
            json=data,
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )
    return response.json()

@router.delete("/classification-rules/{rule_id}/", dependencies=[Depends(auth_required)])
async def delete_classification_rules(rule_id: str, request: Request):
    """Eliminar un conjunto de reglas de clasificación"""
    token = request.headers.get("Authorization")

    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{settings.full_django_api_url}/classification-rules/{rule_id}/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"}
        )

    if response.status_code == 204:
        return {"message": "Eliminado correctamente"}
    raise HTTPException(status_code=response.status_code, detail="Error eliminando regla")

@router.get("/zabbix/status/", dependencies=[Depends(auth_required)])
async def check_zabbix_status(request: Request):
    """Evaluar el estado de la conexión con Zabbix"""
    token = request.headers.get("Authorization")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.full_django_api_url}/zabbix/status/",
            headers={"Authorization": f"Bearer {token.split()[-1]}"},
            timeout=30.0  
        )
        
    if response.status_code == 200:
        return response.json()
    raise HTTPException(
        status_code=response.status_code, 
        detail="Error al verificar el estado de Zabbix"
    )

@router.get("/health/")
async def health_service():
    """Verificar si el servicio proxy está activo."""
    return {"status": "ok", "message": "Proxy service is running"}
