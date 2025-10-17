import datetime
import logging
from typing import Optional

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

from config import settings

# scheduler = BackgroundScheduler()
# Configuración de logging
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURACIÓN DEL SCHEDULER CON PERSISTENCIA
# ============================================================================

executors = {
    'default': ThreadPoolExecutor(10)
}

job_defaults = {
    'coalesce': True,  # Combina ejecuciones perdidas
    'max_instances': 1,  # Solo una instancia del job a la vez
    'misfire_grace_time': 3600  # 1 hora de tolerancia para jobs perdidos
}

scheduler = BackgroundScheduler()

# def programar_tareas_para_todos_los_indicadores():
#     from registro.models import Indicador
#     """Programa las mediciones y notificaciones para todos los indicadores activos"""
#     for indicador in Indicador.objects.all():
#         programar_siguiente_medicion(indicador)
def programar_tareas_para_todos_los_indicadores():
    """
    Programa las mediciones y notificaciones para todos los indicadores activos.
    Útil para inicialización del sistema o reprogramación masiva.
    """
    from registro.models import Indicador

    logger.info("Iniciando programación masiva de indicadores...")
    indicadores_programados = 0
    indicadores_omitidos = 0

    for indicador in Indicador.objects.all():
        try:
            proxima_medicion = indicador.calcular_proxima_medicion()
            if proxima_medicion:
                programar_siguiente_medicion(indicador, proxima_medicion)
                indicadores_programados += 1
            else:
                indicadores_omitidos += 1
                logger.warning(
                    f"Indicador {indicador.id} omitido - sin frecuencia o resultados"
                )
        except Exception as e:
            logger.error(
                f"Error programando indicador {indicador.id}: {str(e)}",
                exc_info=True
            )

    logger.info(
        f"Programación completada: {indicadores_programados} exitosos, "
        f"{indicadores_omitidos} omitidos"
    )

# def programar_siguiente_medicion(indicador, proxima_fecha):
#     """Programa la próxima medición y la notificación previa según la frecuencia definida."""
#     # notificacion_previa_fecha = proxima_fecha - datetime.timedelta(days=1)
#     # if notificacion_previa_fecha > datetime.datetime.now():
#     scheduler.add_job(
#         enviar_notificacion,
#         "date",
#         run_date=proxima_fecha,
#         id=f"notificacion_{indicador.id}",
#         replace_existing=True,
#         args=[indicador]
#     )
#
#     # Medición programada
#     scheduler.add_job(
#         verificar_medicion,
#         "date",
#         run_date=proxima_fecha,
#         id=f"medicion_{indicador.id}",
#         replace_existing=True,
#         args=[indicador]
#     )
#
#     print(f"✅ Medición programada para {indicador.nombre} el {proxima_fecha}")
def programar_siguiente_medicion(indicador, proxima_fecha):
    """
    Programa la próxima medición y las notificaciones previas según la frecuencia definida.

    Args:
        indicador: Instancia del modelo Indicador
        proxima_fecha: datetime de la próxima medición
    """
    if not proxima_fecha:
        logger.warning(f"No se puede programar indicador {indicador.id} sin fecha")
        return

    ahora = timezone.now()

    # Validar que la fecha sea futura
    if proxima_fecha <= ahora:
        logger.warning(
            f"Fecha de medición {proxima_fecha} ya pasó para medir el indicador {indicador.id}"
        )
        # Opcionalmente, reprogramar para el siguiente período
        return

    try:
        # ============ NOTIFICACIÓN PREVIA (1 DÍA ANTES) ============
        notificacion_previa_fecha = proxima_fecha - datetime.timedelta(days=1)

        if notificacion_previa_fecha > ahora:
            scheduler.add_job(
                enviar_notificacion_previa,
                "date",
                run_date=notificacion_previa_fecha,
                id=f"notificacion_previa_{indicador.id}",
                replace_existing=True,
                args=[indicador, proxima_fecha]
            )
            logger.info(
                f"📅 Notificación previa programada para {indicador.nombre} "
                f"el {notificacion_previa_fecha.strftime('%Y-%m-%d %H:%M')}"
            )
        else:
            logger.debug(
                f"Notificación previa omitida para {indicador.id} - "
                f"fecha muy cercana o pasada"
            )

        # ============ VERIFICACIÓN EN LA FECHA DE MEDICIÓN ============
        scheduler.add_job(
            verificar_medicion,
            "date",
            run_date=proxima_fecha,
            id=f"medicion_{indicador.id}",
            replace_existing=True,
            args=[indicador]
        )

        logger.info(
            f"✅ Medición programada para {indicador.nombre} "
            f"el {proxima_fecha.strftime('%Y-%m-%d %H:%M')}"
        )

    except Exception as e:
        logger.error(
            f"Error al programar medición para indicador {indicador.id}: {str(e)}",
            exc_info=True
        )


def enviar_notificacion_previa(indicador, fecha_medicion):
    """
    Envía notificación recordatoria 1 día antes de la medición.

    Args:
        indicador: Instancia del modelo Indicador
        fecha_medicion: datetime de cuándo es la medición
    """
    from notificaciones.models import Notificacion

    try:
        fecha_formateada = fecha_medicion.strftime('%d/%m/%Y')
        mensaje = (
            f"📊 Recordatorio: Mañana ({fecha_formateada}) debes registrar "
            f"la medición del indicador '{indicador.nombre}'."
        )

        usuarios = indicador.get_users()
        if not usuarios.exists():
            logger.warning(
                f"No hay usuarios asignados al indicador {indicador.id}"
            )
            return

        notificaciones_creadas = 0
        for user in usuarios:
            Notificacion.objects.create(
                user=user,
                titulo="📅 Medición Programada Mañana",
                mensaje=mensaje,
                indicador=indicador,
                enlace=reverse(
                    'registro:registrar_resultado_indicador',
                    args=[indicador.get_accion().id, indicador.id]
                )
            )
            notificaciones_creadas += 1

        logger.info(
            f"📧 {notificaciones_creadas} notificaciones previas enviadas "
            f"para indicador {indicador.nombre}"
        )

    except Exception as e:
        logger.error(
            f"Error enviando notificación previa para indicador {indicador.id}: {str(e)}",
            exc_info=True
        )


def enviar_notificacion_urgente(indicador):
    """
    Envía notificación urgente cuando NO se ha registrado la medición.

    Args:
        indicador: Instancia del modelo Indicador
    """
    from notificaciones.models import Notificacion

    try:
        mensaje = (
            f"⚠️ URGENTE: El indicador '{indicador.nombre}' no tiene medición registrada. "
            f"Por favor, completa el registro lo antes posible para mantener "
            f"el seguimiento actualizado."
        )

        usuarios = indicador.get_users()
        notificaciones_creadas = 0

        for user in usuarios:
            Notificacion.objects.create(
                user=user,
                titulo="🚨 Medición Pendiente - Acción Requerida",
                mensaje=mensaje,
                indicador=indicador,
                enlace=reverse(
                    'registro:registrar_resultado_indicador',
                    args=[indicador.get_accion().id, indicador.id]
                )
            )
            notificaciones_creadas += 1

        logger.warning(
            f"🚨 {notificaciones_creadas} notificaciones urgentes enviadas "
            f"para indicador {indicador.nombre}"
        )

    except Exception as e:
        logger.error(
            f"Error enviando notificación urgente para indicador {indicador.id}: {str(e)}",
            exc_info=True
        )

def enviar_notificacion(indicador):
    from notificaciones.models import Notificacion
    mensaje = f"⚠ ¡Recuerda! Mañana es la medición para el indicador {indicador.nombre}."

    for user in indicador.get_users():
        Notificacion.objects.create(user=user, titulo="Aviso previo de medición de indicador", mensaje=mensaje,
                                    indicador=indicador, enlace=reverse('registro:lista_resultado_indicador',
                                                                        args=[indicador.get_accion().id, indicador]))

    print(f"⚠ RECORDATORIO: Mañana es la medición del indicador {indicador.nombre}.")


# def verificar_medicion(indicador):
#     from notificaciones.models import Notificacion
#     """Verifica si el indicador debe actualizarse y notifica si es necesario."""
#     now_time = datetime.datetime.now()
#     proxima_medicion = indicador.calcular_proxima_medicion()
#
#     if proxima_medicion and now_time > proxima_medicion:
#         if not hay_resultado_reciente(indicador):
#
#             mensaje = f"⚠ URGENTE: El indicador {indicador.nombre} sigue sin medición. ¡Por favor, regístrelo!"
#             for user in indicador.get_users():
#                 Notificacion.objects.create(user=user, titulo="URGENTE", mensaje=mensaje,
#                                             indicador=indicador, enlace=reverse('registro:lista_resultado_indicador',
#                                                                                 args=[indicador.get_accion().id,
#                                                                                       indicador]))
#
#             print(f"⚠ URGENTE: El indicador {indicador.nombre} sigue sin medición. ¡Registra un nuevo resultado!")
#
#
# def hay_resultado_reciente(indicador):
#     """Verifica si hay un resultado registrado después de la última fecha de medición."""
#     return indicador.resultadoindicador_set.filter(fecha__gte=indicador.calcular_proxima_medicion()).exists()
def verificar_medicion(indicador):
    """
    Verifica si el indicador debe actualizarse y notifica si es necesario.

    Args:
        indicador: Instancia del modelo Indicador
    """
    try:
        ahora = timezone.now()
        proxima_medicion = indicador.calcular_proxima_medicion()

        if not proxima_medicion:
            logger.warning(
                f"No se puede verificar indicador {indicador.id} sin próxima medición"
            )
            return

        # Verificar si ya pasó la fecha de medición
        if ahora >= proxima_medicion:
            if not hay_resultado_reciente(indicador, proxima_medicion):
                # No hay resultado registrado - enviar notificación urgente
                enviar_notificacion_urgente(indicador)
                logger.warning(
                    f"⚠️ Indicador {indicador.nombre} sin medición - "
                    f"notificación urgente enviada"
                )
            else:
                # Hay resultado - reprogramar siguiente medición
                siguiente_medicion = indicador.calcular_proxima_medicion()
                if siguiente_medicion:
                    programar_siguiente_medicion(indicador, siguiente_medicion)
                    logger.info(
                        f"✅ Medición registrada para {indicador.nombre} - "
                        f"reprogramando siguiente"
                    )

    except Exception as e:
        logger.error(
            f"Error verificando medición para indicador {indicador.id}: {str(e)}",
            exc_info=True
        )


def hay_resultado_reciente(indicador, fecha_referencia: Optional[datetime.datetime] = None) -> bool:
    """
    Verifica si hay un resultado registrado después de la fecha de referencia.

    Args:
        indicador: Instancia del modelo Indicador
        fecha_referencia: datetime de referencia (por defecto: próxima medición)

    Returns:
        bool: True si hay resultado reciente, False en caso contrario
    """
    try:
        if fecha_referencia is None:
            fecha_referencia = indicador.calcular_proxima_medicion()

        if not fecha_referencia:
            return False

        # Buscar resultados posteriores a la fecha de referencia
        # con margen de tolerancia de 1 día antes
        fecha_minima = fecha_referencia - datetime.timedelta(days=1)

        existe = indicador.resultados.filter(
            fecha__gte=fecha_minima
        ).exists()

        return existe

    except Exception as e:
        logger.error(
            f"Error verificando resultados recientes para indicador {indicador.id}: {str(e)}",
            exc_info=True
        )
        return False


def start():
    """
    Inicia el scheduler en segundo plano.
    Debe llamarse al arrancar la aplicación Django (en AppConfig.ready()).
    """
    if not scheduler.running:
        try:
            scheduler.start()
            logger.info("🚀 Scheduler iniciado correctamente")

            # Programar tarea de limpieza de jobs vencidos (diaria)
            scheduler.add_job(
                limpiar_jobs_vencidos,
                'cron',
                hour=3,  # 3 AM
                id='limpieza_jobs',
                replace_existing=True
            )

            # Opcional: Reprogramar todos los indicadores al inicio
            # programar_tareas_para_todos_los_indicadores()

        except Exception as e:
            logger.error(f"Error iniciando scheduler: {str(e)}", exc_info=True)
    else:
        logger.warning("Scheduler ya está en ejecución")


def stop():
    """
    Detiene el scheduler de forma segura.
    Útil para tests o shutdown de la aplicación.
    """
    if scheduler.running:
        try:
            scheduler.shutdown(wait=True)
            logger.info("🛑 Scheduler detenido correctamente")
        except Exception as e:
            logger.error(f"Error deteniendo scheduler: {str(e)}", exc_info=True)


def limpiar_jobs_vencidos():
    """
    Elimina jobs que ya se ejecutaron y no son necesarios.
    Se ejecuta automáticamente cada día a las 3 AM.
    """
    try:
        jobs_eliminados = 0
        ahora = timezone.now()

        for job in scheduler.get_jobs():
            # Eliminar jobs de fecha pasada (tipo 'date')
            if hasattr(job.trigger, 'run_date'):
                if job.trigger.run_date < ahora:
                    scheduler.remove_job(job.id)
                    jobs_eliminados += 1

        if jobs_eliminados > 0:
            logger.info(f"🧹 {jobs_eliminados} jobs vencidos eliminados")

    except Exception as e:
        logger.error(f"Error limpiando jobs: {str(e)}", exc_info=True)


def obtener_estadisticas_scheduler():
    """
    Retorna estadísticas del scheduler para debugging/monitoring.

    Returns:
        dict: Estadísticas del scheduler
    """
    try:
        jobs = scheduler.get_jobs()

        estadisticas = {
            'running': scheduler.running,
            'total_jobs': len(jobs),
            'jobs_por_tipo': {
                'notificacion_previa': 0,
                'medicion': 0,
                'otros': 0
            },
            'proximos_jobs': []
        }

        ahora = timezone.now()

        for job in jobs:
            # Clasificar por tipo
            if 'notificacion_previa' in job.id:
                estadisticas['jobs_por_tipo']['notificacion_previa'] += 1
            elif 'medicion' in job.id:
                estadisticas['jobs_por_tipo']['medicion'] += 1
            else:
                estadisticas['jobs_por_tipo']['otros'] += 1

            # Próximos 5 jobs
            if hasattr(job, 'next_run_time') and job.next_run_time:
                if len(estadisticas['proximos_jobs']) < 5:
                    estadisticas['proximos_jobs'].append({
                        'id': job.id,
                        'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'tiempo_restante': str(job.next_run_time - ahora)
                    })

        return estadisticas

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}", exc_info=True)
        return {'error': str(e)}


# ============================================================================
# FUNCIONES AUXILIARES PARA TESTING
# ============================================================================

def forzar_verificacion_indicador(indicador_id: int):
    """
    Fuerza la verificación de un indicador específico (para debugging/testing).

    Args:
        indicador_id: ID del indicador a verificar
    """
    from registro.models import Indicador

    try:
        indicador = Indicador.objects.get(id=indicador_id)
        verificar_medicion(indicador)
        logger.info(f"Verificación forzada para indicador {indicador_id}")
    except Indicador.DoesNotExist:
        logger.error(f"Indicador {indicador_id} no encontrado")
    except Exception as e:
        logger.error(f"Error en verificación forzada: {str(e)}", exc_info=True)
