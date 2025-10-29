# nexusone/talento_humano/apps.py

from django.apps import AppConfig


class TalentoHumanoConfig(AppConfig):
    """
    Configuración de la aplicación Talento Humano.
    Gestiona empleados, contratos, nómina, capacitación, SST y más.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nexusone.talento_humano'
    verbose_name = 'Talento Humano'
    
    def ready(self):
        """
        Método que se ejecuta cuando la aplicación está lista.
        Aquí se importan las señales.
        """
        try:
            import nexusone.talento_humano.signals  # noqa
        except ImportError:
            pass