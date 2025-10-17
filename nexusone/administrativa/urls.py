from django.urls import path, include

app_name = "administrativa"

urlpatterns = [
    path("ordenes/", include("nexusone.administrativa.ordenes.urls")),
]