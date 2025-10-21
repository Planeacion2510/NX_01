from dotenv import load_dotenv
import os
from pathlib import Path
import environ

# =========================
# CARGAR VARIABLES DE ENTORNO
# =========================
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Configurar entorno
env = environ.Env(DEBUG=(bool, False))

# Archivos .env
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

# =========================
# CONFIGURACIÓN BÁSICA
# =========================
SECRET_KEY = env("DJANGO_SECRET_KEY", default="clave-dev-insegura")
DEBUG = env.bool("DEBUG", default=False)

# =========================
# HOSTS PERMITIDOS
# =========================
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[
    "127.0.0.1",
    "localhost",
    "nx-01.onrender.com",
])

# =========================
# APLICACIONES INSTALADAS
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps del proyecto
    "nexusone",
    "nexusone.administrativa",
    "nexusone.administrativa.ordenes",
    "nexusone.administrativa.inventario",
    "nexusone.administrativa.compras",
]
# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =========================
# URLS Y WSGI
# =========================
ROOT_URLCONF = "nexusone.urls"
WSGI_APPLICATION = "nexusone.wsgi.application"

# =========================
# TEMPLATES
# =========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "nexusone" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# =========================
# BASE DE DATOS
# =========================
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# =========================
# VALIDADORES DE CONTRASEÑA
# =========================
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# =========================
# LOGIN / LOGOUT
# =========================
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

# =========================
# INTERNACIONALIZACIÓN
# =========================
LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True

# =========================
# ARCHIVOS ESTÁTICOS
# =========================
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "nexusone" / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =========================
# 📂 ARCHIVOS DE USUARIO (MEDIA)
# =========================
# Detección de entorno
IS_RENDER = os.getenv("RENDER", False)

if IS_RENDER:
    # 🌐 Producción en Render - Disco persistente montado en /data
    MEDIA_ROOT = Path("/data")
    MEDIA_URL = "/media/"
else:
    # 💻 Desarrollo local
    MEDIA_ROOT = BASE_DIR / "media"
    MEDIA_URL = "/media/"

# NO crear carpeta aquí - se creará cuando se necesite en las vistas

# =========================
# DEFAULT AUTO FIELD
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# SEGURIDAD (solo en producción)
# =========================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# =========================
# CSRF TRUSTED ORIGINS
# =========================
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[
    "https://nx-01.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
])
# ============================================
# CONFIGURACIÓN DE ARCHIVOS MEDIA
# ============================================
import os

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Tamaño máximo de archivo (25 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 26214400  # 25 MB