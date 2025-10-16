from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from . import views
import os

urlpatterns = [
    # Página principal
    path("", views.home, name="home"),

    # Autenticación
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Administración de Django
    path("admin/", admin.site.urls),

    # Apps internas
    path(
        "administrativa/",
        include(("nexusone.administrativa.urls", "administrativa"), namespace="administrativa")
    ),

    # Servir PDFs desde la carpeta Ordenes
    re_path(
        r'^Ordenes/(?P<path>.*)$',
        serve,
        {'document_root': os.path.join(settings.MEDIA_ROOT, 'Ordenes')},
        name='ordenes_files'
    ),
]

# Servir archivos media (opcional)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
