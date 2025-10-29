from django.apps import AppConfig


class TalentoHumanoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'talento_humano'
    verbose_name = 'Talento Humano'
    
    def ready(self):
        import talento_humano.signals