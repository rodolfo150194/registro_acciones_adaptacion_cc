import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)
class RegistroConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'registro'

    def ready(self):
        import registro.signals
        from jobs.scheduler import start, obtener_estadisticas_scheduler

        # Iniciar scheduler
        start()

        # Log de estadísticas iniciales
        stats = obtener_estadisticas_scheduler()
        logger.info(f"📊 Scheduler iniciado con {stats.get('total_jobs', 0)} jobs programados")

        # Opcional: Programar todos los indicadores al inicio
        # from jobs.scheduler import programar_tareas_para_todos_los_indicadores
        # programar_tareas_para_todos_los_indicadores()
