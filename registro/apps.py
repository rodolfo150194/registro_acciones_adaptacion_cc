from django.apps import AppConfig


class RegistroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'registro'

    def ready(self):
        import registro.signals
        from jobs import scheduler
        scheduler.start()