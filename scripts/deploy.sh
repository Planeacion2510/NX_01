#!/bin/bash
# ============================================================================
# NEXUSONE ERP - Script de Deploy Inteligente
# ============================================================================
# Este script detecta automáticamente el estado de la base de datos y aplica
# la estrategia correcta de migraciones.
#
# Estrategias:
# - empty: BD nueva → migrate normal
# - needs_sync: Tablas existen sin registro → migrate --fake-initial
# - synced: BD con migraciones → migrate normal
# ============================================================================

set -e  # Salir si hay error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logs
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo ""
echo "============================================================"
echo "🚀 NEXUSONE ERP - DEPLOY"
echo "============================================================"
echo ""

# ============================================================================
# PASO 1: VERIFICAR REQUISITOS
# ============================================================================
log_info "Verificando requisitos..."

if [ ! -f "manage.py" ]; then
    log_error "manage.py no encontrado. ¿Estás en la raíz del proyecto?"
    exit 1
fi

log_success "Requisitos verificados"

# ============================================================================
# PASO 2: VERIFICAR CONEXIÓN A BASE DE DATOS
# ============================================================================
log_info "Verificando conexión a base de datos..."

python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexusone.settings')
django.setup()

try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Conexión exitosa")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    exit(1)
END

if [ $? -ne 0 ]; then
    log_error "No se pudo conectar a la base de datos"
    exit 1
fi

log_success "Conexión a BD establecida"

# ============================================================================
# PASO 3: DETECTAR ESTADO Y EJECUTAR MIGRACIONES
# ============================================================================
log_info "Detectando estado de la base de datos y aplicando migraciones..."
echo ""

# Ejecutar el script Python que hace la verificación inteligente
python scripts/check_db.py

if [ $? -ne 0 ]; then
    log_error "Error al ejecutar migraciones"
    exit 1
fi

log_success "Migraciones aplicadas correctamente"

# ============================================================================
# PASO 4: CREAR SUPERUSUARIO (Si no existe)
# ============================================================================
log_info "Verificando superusuario..."

python << END
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nexusone.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(is_superuser=True).exists():
    print("⚠️  No existe superusuario")
    
    # Obtener credenciales de variables de entorno
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@nexusone.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    
    if password == 'admin123':
        print("⚠️  Usando contraseña por defecto. Define DJANGO_SUPERUSER_PASSWORD")
    
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"✅ Superusuario '{username}' creado")
    except Exception as e:
        print(f"⚠️  No se pudo crear superusuario: {e}")
else:
    print("✅ Superusuario ya existe")
END

# ============================================================================
# PASO 5: RECOLECTAR ARCHIVOS ESTÁTICOS
# ============================================================================
log_info "Recolectando archivos estáticos..."

python manage.py collectstatic --noinput --clear > /dev/null 2>&1

if [ $? -eq 0 ]; then
    log_success "Archivos estáticos recolectados"
else
    log_warning "Error al recolectar estáticos (continuando...)"
fi

# ============================================================================
# PASO 6: VERIFICACIÓN FINAL
# ============================================================================
log_info "Ejecutando verificaciones finales..."

python manage.py check --deploy > /dev/null 2>&1

if [ $? -eq 0 ]; then
    log_success "Verificaciones completadas"
else
    log_warning "Algunas verificaciones fallaron (no crítico)"
fi

# ============================================================================
# RESUMEN
# ============================================================================
echo ""
echo "============================================================"
log_success "DEPLOY COMPLETADO EXITOSAMENTE"
echo "============================================================"
echo ""
log_info "Base de datos: Migraciones aplicadas"
log_info "Estáticos: Recolectados"
log_info "Estado: Listo para producción"
echo ""
echo "============================================================"
echo "🚀 INICIANDO SERVIDOR..."
echo "============================================================"
echo ""

# ============================================================================
# PASO 7: INICIAR GUNICORN
# ============================================================================
exec gunicorn nexusone.wsgi:application \
    --bind 0.0.0.0:${PORT:-10000} \
    --workers ${WEB_CONCURRENCY:-2} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
