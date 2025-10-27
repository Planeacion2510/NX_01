#!/bin/bash
# ============================================================================
# NEXUSONE - Deploy Simple (Versión alternativa ligera)
# ============================================================================

set -e

echo "🚀 Iniciando deploy..."

# Ejecutar migraciones inteligentes
python scripts/check_db.py

# Collectstatic
echo "📦 Recolectando estáticos..."
python manage.py collectstatic --noinput --clear 2>&1 | grep -v "Found another file" || true

echo "✅ Deploy completado"
echo "🚀 Iniciando servidor..."

# Iniciar Gunicorn
exec gunicorn nexusone.wsgi:application --bind 0.0.0.0:${PORT:-10000}