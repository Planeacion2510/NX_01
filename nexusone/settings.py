from dotenv import load_dotenv
import os
from pathlib import Path
import environ

load_dotenv()

# =========================
# BASE DIR
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# ENVIRONMENT VARIABLES
# =========================
env = environ.Env(DEBUG=(bool, False))
env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

SECRET_KEY = env("DJANGO_SECRET_KEY", default="clave-dev")
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
# ✅ En Windows (local) → carpeta OneDrive compartida
# ✅ En Render (Linux) → carpeta /media dentro del proyecto
if os.name == "nt":
    MEDIA_ROOT = Path(r"C:/Users/aux5g/OneDrive/Planeación & Control/Ordenes de Trabajo")
else:
    MEDIA_ROOT = BASE_DIR / "media"

MEDIA_URL = "/media/"

# Crea la carpeta base si no existe (solo si se ejecuta localmente)
os.makedirs(MEDIA_ROOT, exist_ok=True)

# =========================
# DEFAULT AUTO FIELD
# =========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =========================
# SEGURIDAD (solo forzado en producción)
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
    "https://nexusone.onrender.com",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
])
