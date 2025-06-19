# Imagen base liviana con Python
FROM python:3.13.3-slim

ENV DOCKERIZE_VERSION=v0.9.3

# Establece el directorio de trabajo
WORKDIR /app

# Crear usuario no root
RUN groupadd -r netback && useradd -r -g netback netback

# Evita mensajes interactivos (como de psycopg2)
# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Instala dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    wget \
    && wget -O - https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz | tar xzf - -C /usr/local/bin \
    && apt-get autoremove -yqq --purge wget \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala las dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

USER netback
# Copia todo el código del proyecto
COPY . .

# Exponer puertos si es necesario
EXPOSE 8000
