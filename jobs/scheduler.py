import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import now

scheduler = BackgroundScheduler()


def programar_tareas_para_todos_los_indicadores():
    from registro.models import Indicador
    """Programa las mediciones y notificaciones para todos los indicadores activos"""
    for indicador in Indicador.objects.all():
        programar_siguiente_medicion(indicador)


def programar_siguiente_medicion(indicador, proxima_fecha):
    """Programa la próxima medición y la notificación previa según la frecuencia definida."""
    # notificacion_previa_fecha = proxima_fecha - datetime.timedelta(days=1)
    # if notificacion_previa_fecha > datetime.datetime.now():
    scheduler.add_job(
        enviar_notificacion,
        "date",
        run_date=proxima_fecha,
        id=f"notificacion_{indicador.id}",
        replace_existing=True,
        args=[indicador]
    )

    # Medición programada
    scheduler.add_job(
        verificar_medicion,
        "date",
        run_date=proxima_fecha,
        id=f"medicion_{indicador.id}",
        replace_existing=True,
        args=[indicador]
    )

    print(f"✅ Medición programada para {indicador.nombre} el {proxima_fecha}")


def enviar_notificacion(indicador):
    from notificaciones.models import Notificacion
    mensaje = f"⚠ ¡Recuerda! Mañana es la medición para el indicador {indicador.nombre}."

    for user in indicador.get_users():
        Notificacion.objects.create(user=user, titulo="Aviso previo de medición de indicador", mensaje=mensaje,
                                    indicador=indicador, enlace=reverse('registro:lista_resultado_indicador',
                                                                        args=[indicador.get_accion().id, indicador]))

    print(f"⚠ RECORDATORIO: Mañana es la medición del indicador {indicador.nombre}.")


def verificar_medicion(indicador):
    from notificaciones.models import Notificacion
    """Verifica si el indicador debe actualizarse y notifica si es necesario."""
    now_time = datetime.datetime.now()
    proxima_medicion = indicador.calcular_proxima_medicion()

    if proxima_medicion and now_time > proxima_medicion:
        if not hay_resultado_reciente(indicador):

            mensaje = f"⚠ URGENTE: El indicador {indicador.nombre} sigue sin medición. ¡Por favor, regístrelo!"
            for user in indicador.get_users():
                Notificacion.objects.create(user=user, titulo="URGENTE", mensaje=mensaje,
                                            indicador=indicador, enlace=reverse('registro:lista_resultado_indicador',
                                                                                args=[indicador.get_accion().id,
                                                                                      indicador]))

            print(f"⚠ URGENTE: El indicador {indicador.nombre} sigue sin medición. ¡Registra un nuevo resultado!")


def hay_resultado_reciente(indicador):
    """Verifica si hay un resultado registrado después de la última fecha de medición."""
    return indicador.resultadoindicador_set.filter(fecha__gte=indicador.calcular_proxima_medicion()).exists()


def start():
    scheduler.start()
