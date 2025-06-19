FROM python:3.13.3-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on


# Crear usuario no root
RUN groupadd -r netback && useradd -r -g netback netback

# Instalar dependencias del sistema y limpiar en una sola capa
RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    netcat-openbsd \
    openssh-client \
    curl \
    gcc libpq-dev \
    traceroute \
    iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Cambiar propiedad de los archivos al usuario django
RUN chown -R netback:netback /app

# Crear directorio para archivos estáticos y media
RUN mkdir -p /app/data/keys && chown -R netback:netback /app/data

# Cambiar al usuario no root
USER netback

# Agregar healthcheck
#HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    #CMD curl -f http://localhost:8000/health/ || exit 1

# Exponer puerto
EXPOSE 8000

# Usar script de entrada para generar SECRET_KEY si no se proporciona
COPY entrypoint.sh /app/

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
