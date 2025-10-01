# --- Etapa 1: Builder ---
# Usamos una imagen completa para instalar dependencias, descargar herramientas y compilar paquetes.
FROM python:3.13.3-slim as builder

# Versión de Dockerize
ENV DOCKERIZE_VERSION=v0.9.3

# Establecer variables de entorno para un build limpio
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Instalar dependencias de compilación y descargar dockerize
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    wget \
    && wget -O - https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz | tar xzf - -C /usr/local/bin \
    && apt-get autoremove -yqq --purge wget \
    && rm -rf /var/lib/apt/lists/*

# Crear un entorno virtual para mantener las dependencias aisladas
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar e instalar requerimientos en el entorno virtual
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 2: Final ---
# Empezamos de nuevo con una imagen slim limpia para la ejecución
FROM python:3.13.3-slim

# Establecer variables de entorno de ejecución
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear usuario no root para mayor seguridad
RUN groupadd -r netback && useradd -r -g netback netback

# Instalar solo las dependencias de *ejecución*
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar dockerize y el entorno virtual desde la etapa builder
COPY --from=builder /usr/local/bin/dockerize /usr/local/bin/dockerize
COPY --from=builder /opt/venv /opt/venv

# Copiar el código de la aplicación
WORKDIR /app
COPY . .

# Cambiar propiedad de los archivos y activar venv
RUN chown -R netback:netback /app
ENV PATH="/opt/venv/bin:$PATH"
USER netback

# El CMD y ENTRYPOINT se definen en docker-compose.yml
EXPOSE 8000
