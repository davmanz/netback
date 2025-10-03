# --- Etapa 1: Builder ---
# Usamos una imagen completa para instalar dependencias y compilar paquetes.
FROM python:3.12.11-slim AS builder

# Establecer variables de entorno para un build limpio
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Instalar solo las dependencias de compilación necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear un entorno virtual para mantener las dependencias aisladas
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copiar e instalar requerimientos en el entorno virtual
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


# --- Etapa 2: Final ---
# Empezamos de nuevo con una imagen slim limpia para la ejecución
FROM python:3.12.11-slim

# Establecer variables de entorno de ejecución
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Crear usuario no root para mayor seguridad
RUN groupadd -r netback && useradd -r -g netback netback

# Instalar solo las dependencias de *ejecución* (mucho más pequeñas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual con los paquetes ya instalados desde la etapa builder
COPY --from=builder /opt/venv /opt/venv

# Copiar el código de la aplicación
WORKDIR /app
COPY . .

# Cambiar propiedad de los archivos al usuario no root
RUN chown -R netback:netback /app
# Copiar entrypoint y asegurar permisos mientras somos root
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh && chown netback:netback /app/entrypoint.sh

# Activar el entorno virtual y cambiar al usuario no root
ENV PATH="/opt/venv/bin:$PATH"
USER netback

# Exponer puerto y definir el punto de entrada
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]