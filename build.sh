#!/usr/bin/env bash
echo "🔧 Forzando Python 3.11.9 en Render..."
pyenv install -s 3.11.9
pyenv global 3.11.9
python --version

# Instalar dependencias
pip install -r requirements.txt

# ✅ EJECUTAR MIGRACIONES (ESTO CREA LA TABLA DE NOTIFICACIONES)
echo "📦 Creando migraciones..."
python manage.py makemigrations

echo "🚀 Ejecutando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
python manage.py collectstatic --noinput

# Crear o actualizar superusuario admin
python manage.py createsuperuser --noinput --username admin --email admin@example.com || true
python manage.py shell -c "
from django.contrib.auth.models import User;
u = User.objects.get(username='admin')
u.is_superuser = True
u.is_staff = True
u.set_password('admin123')
u.save()
"

# Crear usuarios adicionales
python manage.py shell -c "
from django.contrib.auth.models import User;
usuarios = [
    ('Mecanizados', 'Dinnova2510'),
    ('Ensamble', 'Dinnova2510E'),
    ('Despacho', 'Dinnova2510D'),
    ('Produccion', 'Dinnova2510P'),
    ('Almacen', 'Dinnova2510A'),
    ('Gerencia', 'Dinnova2510G'),
    ('TalentoHumano', 'Dinnova2510H'),
];
for nombre, clave in usuarios:
    u, creado = User.objects.get_or_create(username=nombre)
    u.set_password(clave)
    u.is_staff = False
    u.is_superuser = False
    u.save()
print('✅ Usuarios actualizados correctamente.')
"

echo "🚀 Build finalizado correctamente"