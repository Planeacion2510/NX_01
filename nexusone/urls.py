from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
import os

urlpatterns = [
    # Administración de Django
    path("admin/", admin.site.urls),

    # Autenticación
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Página principal
    path("", views.home, name="home"),

    # Apps internas
    path("administrativa/", include("nexusone.administrativa.urls")),

    # Servir archivos desde carpeta Ordenes (para descargas directas)
    re_path(
        r'^Ordenes/(?P<path>.*)$',
        serve,
        {'document_root': os.path.join(settings.MEDIA_ROOT, 'Ordenes')},
        name='ordenes_files'
    ),
]

# Servir archivos media en todos los entornos
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Servir archivos estáticos solo en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)