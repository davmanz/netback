#!/bin/bash
set -euo pipefail

# Funciones de logging con niveles
log_info() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

log_warning() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [WARNING] $1" >&2
}

log_error() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] [ERROR] $1" >&2
}

# Función de limpieza mejorada
cleanup() {
  log_info "🧹 Iniciando limpieza de recursos..."
  
  # Intentar detener procesos en segundo plano si existen
  jobs -p | xargs -r kill -SIGTERM 2>/dev/null || true
  
  # Cerrar conexiones a la base de datos si están abiertas
  if [ -n "${DB_PID:-}" ]; then
    kill -SIGTERM "$DB_PID" 2>/dev/null || true
  fi
  
  log_info "✅ Limpieza completada"
}

# Configuración de traps mejorada
trap 'log_error "❌ Error: Script interrumpido"; cleanup; exit 1' INT TERM
trap 'log_error "❌ Error en la línea $LINENO"; cleanup; exit 1' ERR
trap cleanup EXIT

log_info "🔍 Verificando variables de entorno..."

# Validación completa de variables requeridas al inicio
required_vars=("DB_HOST" "DB_PORT" "SECRET_KEY" "ENCRYPTION_KEY_VAULT")
for var in "${required_vars[@]}"; do
  if [ -z "${!var:-}" ]; then
    log_error "❌ Error: La variable de entorno $var es requerida"
    exit 1
  fi
done

log_info "✅ Variables de entorno validadas correctamente"

log_info "🧠 Verificando si la base de datos ya contiene registros importantes..."

# Verificar si ya existen registros en las tablas clave con mejor manejo de errores
db_check_result=$(python manage.py shell -c "
try:
    from django.db import connections
    from django.db.utils import ProgrammingError
    cursor = connections['default'].cursor()
    
    tables = ['core_usersystem', 'core_networkdevice', 'core_backup']
    has_data = False
    
    for table in tables:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            if count > 0:
                has_data = True
                break
        except ProgrammingError:
            # Tabla no existe, continuar
            continue
    
    print('DATA_EXISTS' if has_data else 'NO_DATA')
except Exception as e:
    print(f'ERROR: {str(e)}')
" 2>/dev/null)

if [ "$db_check_result" = "DATA_EXISTS" ]; then
  log_info "✅ Datos importantes encontrados en la base de datos."
elif [ "$db_check_result" = "NO_DATA" ]; then
  log_warning "⚠️ No se encontraron datos importantes. Ejecutando migraciones..."
  python manage.py makemigrations --noinput
else
  log_error "❌ Error al verificar el estado de la base de datos: $db_check_result"
  exit 1
fi

log_info "📦 Aplicando migraciones a la base de datos..."
python manage.py migrate --noinput

# Inicializar datos
log_info "🔧 Inicializando datos del sistema..."
python manage.py init_data

log_info "🚀 Iniciando servidor Django con Uvicorn..."
exec uvicorn backend.asgi:application --host 0.0.0.0 --port 8000 --log-level info