import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from jobs.scheduler import programar_siguiente_medicion
from registro.models import ResultadoIndicador

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ResultadoIndicador)
def reprogramar_medicion(sender, instance, **kwargs):
    """Programa la próxima medición cuando se actualiza el indicador."""
    indicador = instance.resultados_indicador.first()
    proxima_medicion = indicador.calcular_proxima_medicion()

    if proxima_medicion:
        logger.info(f"Proxima medicion: {proxima_medicion}")
        programar_siguiente_medicion(indicador, proxima_medicion)
