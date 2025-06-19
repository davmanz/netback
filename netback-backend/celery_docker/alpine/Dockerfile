FROM python:3.13.3-alpine

ENV DOCKERIZE_VERSION=v0.9.3 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app

# Crear usuario no root
RUN addgroup -S netback && adduser -S netback -G netback

# Instalar dependencias necesarias para Celery + Django
RUN apk add --no-cache gcc musl-dev libffi-dev postgresql-dev curl \
    && curl -L https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    | tar xz -C /usr/local/bin

# Copiar solo los requirements mínimos para Celery
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Montar código del backend al contenedor
COPY . .

USER netback
