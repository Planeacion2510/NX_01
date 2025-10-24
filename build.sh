
#!/usr/bin/env bash
echo "🔧 Forzando Python 3.11.9 en Render..."
pyenv install -s 3.11.9
pyenv global 3.11.9
python --version

# 🧩 Instalar dependencias del proyecto
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# ⚠️ No ejecutar migraciones aquí (la base aún no está activa en el build)
# python manage.py makemigrations
# python manage.py migrate --noinput

# 🧱 Compilar archivos estáticos
echo "🎨 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# 👤 Crear o actualizar superusuario admin (solo si no existe)
echo "👤 Configurando usuario administrador..."
python manage.py shell -c "
from django.contrib.auth.models import User;
u, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com'});
u.is_superuser = True
u.is_staff = True
u.set_password('admin123')
u.save()
"

# 👥 Crear usuarios predefinidos
echo "👥 Creando usuarios de sistema..."
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
    u, _ = User.objects.get_or_create(username=nombre)
    u.set_password(clave)
    u.is_staff = False
    u.is_superuser = False
    u.save()
print('✅ Usuarios actualizados correctamente.')
"

echo "🚀 Build completado correctamente. Las migraciones se aplicarán al iniciar el servicio."
