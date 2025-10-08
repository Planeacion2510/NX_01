from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings  # ✅ Importar settings
from django.conf.urls.static import static  # ✅ Importar para servir media en DEBUG
from . import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Autenticación
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Administración Django
    path("admin/", admin.site.urls),

    # -------------------------------
    # Apps internas con namespace
    # -------------------------------
    path(
        "administrativa/",
        include(("nexusone.administrativa.urls", "administrativa"), namespace="administrativa")
    ),
]

# ✅ Servir archivos de MEDIA en modo DEBUG (solo en desarrollo)
if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
