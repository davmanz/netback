# --- Etapa 1: Builder ---
# Usamos una imagen completa para instalar dependencias y compilar paquetes.
FROM python:3.13.3-slim as builder

# Establecer variables de entorno para un build limpio
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Instalar solo las dependencias de compilación necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear un entorno virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar e instalar requerimientos
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Etapa 2: Final ---
# Empezamos de nuevo con una imagen limpia
FROM python:3.13.3-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear usuario no root
RUN groupadd -r netback && useradd -r -g netback netback

# Instalar solo las dependencias de ejecución (curl para el healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual desde la etapa builder
COPY --from=builder /opt/venv /opt/venv

# Copiar el código de la aplicación
WORKDIR /app
COPY . .
RUN chown -R netback:netback /app

# Activar el entorno virtual y establecer usuario
ENV PATH="/opt/venv/bin:$PATH"
USER netback

# Exponer puerto y ejecutar
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
