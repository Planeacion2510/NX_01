from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

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
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

