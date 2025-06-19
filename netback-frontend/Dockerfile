# Al inicio del Dockerfile
ARG NODE_VERSION=22
ARG PNPM_VERSION=latest

# Etapa 1: Construcción
FROM node:${NODE_VERSION}-slim AS builder

WORKDIR /app

# Actualizar npm e instalar corepack de forma más robusta
RUN npm install -g npm@latest && \
    npm install -g corepack && \
    corepack enable && \
    corepack prepare pnpm@${PNPM_VERSION} --activate

# Copiar solo los archivos necesarios para instalar dependencias
COPY pnpm-lock.yaml ./
COPY package.json ./

# Instalar dependencias
RUN pnpm install --frozen-lockfile
RUN pnpm add \
    workbox-precaching \
    workbox-core \
    workbox-routing \
    workbox-strategies \
    workbox-expiration

# Copiar el resto del código fuente
COPY . .

# Ejecutar build para producción
RUN pnpm run build

# Etapa 2: Servir los archivos con Nginx
FROM nginx:stable-alpine

# Crear los directorios necesarios para evitar el error client_temp
RUN mkdir -p /var/cache/nginx/client_temp && \
    chown -R nginx:nginx /var/cache/nginx

# Copiar el build de React desde la etapa anterior
COPY --from=builder /app/build /usr/share/nginx/html

# Copiar configuración de Nginx personalizada
COPY ./nginx.conf /etc/nginx/nginx.conf

# Usar el usuario seguro de nginx
# USER nginx

# Exponer puerto
EXPOSE 80

# Mantener Nginx en primer plano
CMD ["nginx", "-g", "daemon off;"]

# Healthcheck para saber si ya está listo
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1
