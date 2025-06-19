# Imagen base oficial con Python
FROM python:3.13.3-slim
# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto al contenedor
COPY . .

# Crear usuario no root
RUN groupadd -r netback && useradd -r -g netback netback

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y gcc libffi-dev curl && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Variables de entorno (se cargan desde un archivo .env externo en docker-compose)
ENV PYTHONUNBUFFERED=1

# Usuario para ejecutar la aplicación
USER netback

EXPOSE 8080

# Comando para ejecutar el servidor FastAPI con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

