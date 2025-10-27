# nexusone/produccion/apps.py
from django.apps import AppConfig


class ProduccionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nexusone.produccion'
    verbose_name = 'Producción'