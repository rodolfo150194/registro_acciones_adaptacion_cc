from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from datetime import timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class NotificationPriority:
    """Niveles de prioridad de notificaciones"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'


class NotificationService:
    """Servicio para gestionar notificaciones del sistema"""

    def __init__(self):
        self.notifications = []

    def create_notification(self, user, title: str, message: str,
                            priority: str = NotificationPriority.MEDIUM,
                            action_url: str = None, icon: str = 'ki-notification'):
        """Crea una nueva notificación"""
        notification = {
            'user': user,
            'title': title,
            'message': message,
            'priority': priority,
            'action_url': action_url,
            'icon': icon,
            'created_at': timezone.now(),
            'read': False
        }
        self.notifications.append(notification)
        return notification

    def send_email_notification(self, user, subject: str, message: str):
        """Envía notificación por email"""
        try:
            send_mail(
                subject=f'[Sistema de Adaptación] {subject}',
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f'Email enviado a {user.email}')
            return True
        except Exception as e:
            logger.error(f'Error enviando email: {str(e)}')
            return False


class IndicadorAlertService:
    """Servicio para generar alertas de indicadores"""

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def check_indicadores_sin_medicion(self, dias_umbral: int = 90) -> List[Dict]:
        """Detecta indicadores sin mediciones recientes"""
        from registro.models import Accion

        alertas = []
        fecha_limite = timezone.now().date() - timedelta(days=dias_umbral)

        # Obtener acciones publicadas
        acciones = Accion.objects.filter(publicado=True)

        for accion in acciones:
            for indicador in accion.indicadores.all():
                resultados = indicador.resultados.all().order_by('-fecha')

                if not resultados.exists():
                    # Sin mediciones nunca
                    alertas.append({
                        'indicador': indicador,
                        'accion': accion,
                        'tipo': 'sin_mediciones',
                        'prioridad': NotificationPriority.HIGH,
                        'mensaje': f'El indicador "{indicador.nombre}" no tiene mediciones registradas',
                        'dias_sin_medir': 'Nunca'
                    })
                else:
                    ultima_medicion = resultados.first()
                    dias_sin_medir = (timezone.now().date() - ultima_medicion.fecha).days

                    if ultima_medicion.fecha < fecha_limite:
                        # Determinar prioridad según días sin medir
                        if dias_sin_medir > 180:
                            prioridad = NotificationPriority.CRITICAL
                        elif dias_sin_medir > 120:
                            prioridad = NotificationPriority.HIGH
                        else:
                            prioridad = NotificationPriority.MEDIUM

                        alertas.append({
                            'indicador': indicador,
                            'accion': accion,
                            'tipo': 'medicion_atrasada',
                            'prioridad': prioridad,
                            'mensaje': f'Hace {dias_sin_medir} días sin medir "{indicador.nombre}"',
                            'dias_sin_medir': dias_sin_medir
                        })

        return alertas

    def check_metas_en_riesgo(self, umbral_dias: int = 30) -> List[Dict]:
        """Detecta metas en riesgo de no cumplirse"""
        from registro.models import Accion

        alertas = []
        hoy = timezone.now().date()

        acciones = Accion.objects.filter(publicado=True)

        for accion in acciones:
            for indicador in accion.indicadores.filter(
                    meta_valor__isnull=False,
                    meta_fecha_limite__isnull=False
            ):
                # Verificar si la meta está próxima a vencer
                dias_restantes = (indicador.meta_fecha_limite - hoy).days

                if dias_restantes < 0:
                    # Meta vencida
                    progreso = indicador.calcular_progreso_meta()
                    if progreso and not progreso['meta_alcanzada']:
                        alertas.append({
                            'indicador': indicador,
                            'accion': accion,
                            'tipo': 'meta_vencida',
                            'prioridad': NotificationPriority.CRITICAL,
                            'mensaje': f'Meta vencida sin cumplir: "{indicador.nombre}"',
                            'progreso': progreso['progreso_porcentaje'],
                            'dias_restantes': dias_restantes
                        })
                elif 0 <= dias_restantes <= umbral_dias:
                    # Meta próxima a vencer
                    progreso = indicador.calcular_progreso_meta()

                    if progreso:
                        porcentaje = progreso['progreso_porcentaje']

                        # Calcular si el progreso está atrasado
                        dias_totales = (
                                indicador.meta_fecha_limite -
                                accion.fecha_inicio
                        ).days
                        dias_transcurridos = (hoy - accion.fecha_inicio).days
                        progreso_esperado = (
                            dias_transcurridos / dias_totales * 100
                            if dias_totales > 0 else 0
                        )

                        if porcentaje < (progreso_esperado - 20):
                            # Progreso significativamente atrasado
                            prioridad = (
                                NotificationPriority.CRITICAL if dias_restantes <= 7
                                else NotificationPriority.HIGH
                            )

                            alertas.append({
                                'indicador': indicador,
                                'accion': accion,
                                'tipo': 'meta_en_riesgo',
                                'prioridad': prioridad,
                                'mensaje': f'Meta en riesgo: "{indicador.nombre}" '
                                           f'(Progreso: {porcentaje:.1f}%, '
                                           f'Esperado: {progreso_esperado:.1f}%)',
                                'progreso': porcentaje,
                                'progreso_esperado': progreso_esperado,
                                'dias_restantes': dias_restantes
                            })

        return alertas

    def check_tendencias_negativas(self, min_mediciones: int = 3) -> List[Dict]:
        """Detecta tendencias negativas consecutivas"""
        from registro.models import Accion

        alertas = []
        acciones = Accion.objects.filter(publicado=True)

        for accion in acciones:
            for indicador in accion.indicadores.all():
                resultados = list(
                    indicador.resultados.all().order_by('-fecha')[:min_mediciones]
                )

                if len(resultados) < min_mediciones:
                    continue

                # Verificar si hay tendencia negativa
                valores = [r.valor for r in reversed(resultados)]

                if indicador.direccion_optima == 'incremento':
                    # Debería aumentar, pero está disminuyendo
                    if all(valores[i] > valores[i + 1]
                           for i in range(len(valores) - 1)):
                        alertas.append({
                            'indicador': indicador,
                            'accion': accion,
                            'tipo': 'tendencia_negativa',
                            'prioridad': NotificationPriority.HIGH,
                            'mensaje': f'Tendencia descendente en "{indicador.nombre}" '
                                       f'(últimas {min_mediciones} mediciones)',
                            'valores': valores
                        })
                elif indicador.direccion_optima == 'decremento':
                    # Debería disminuir, pero está aumentando
                    if all(valores[i] < valores[i + 1]
                           for i in range(len(valores) - 1)):
                        alertas.append({
                            'indicador': indicador,
                            'accion': accion,
                            'tipo': 'tendencia_negativa',
                            'prioridad': NotificationPriority.HIGH,
                            'mensaje': f'Tendencia ascendente no deseada en '
                                       f'"{indicador.nombre}" '
                                       f'(últimas {min_mediciones} mediciones)',
                            'valores': valores
                        })

        return alertas

    def generar_todas_alertas(self) -> Dict:
        """Genera todas las alertas disponibles"""
        return {
            'sin_medicion': self.check_indicadores_sin_medicion(),
            'metas_en_riesgo': self.check_metas_en_riesgo(),
            'tendencias_negativas': self.check_tendencias_negativas()
        }


class PresupuestoAlertService:
    """Servicio para alertas de presupuesto"""

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def check_ejecucion_presupuestaria(self, umbral_bajo: float = 30) -> List[Dict]:
        """Detecta presupuestos con baja ejecución"""
        from registro.models import Accion

        alertas = []

        for accion in Accion.objects.filter(publicado=True):
            for presupuesto in accion.presupuestos_planificados.all():
                ejecutado = presupuesto.presupuestos_ejecutados.aggregate(
                    total=Sum('monto')
                )['total'] or 0

                porcentaje_ejecutado = (
                    ejecutado / presupuesto.monto * 100
                    if presupuesto.monto > 0 else 0
                )

                # Calcular tiempo transcurrido de la acción
                hoy = timezone.now().date()
                dias_totales = (accion.fecha_fin - accion.fecha_inicio).days
                dias_transcurridos = (hoy - accion.fecha_inicio).days
                porcentaje_tiempo = (
                    dias_transcurridos / dias_totales * 100
                    if dias_totales > 0 else 0
                )

                # Alerta si la ejecución está muy por debajo del tiempo
                if porcentaje_ejecutado < (porcentaje_tiempo - 20) and porcentaje_tiempo > 25:
                    prioridad = (
                        NotificationPriority.CRITICAL
                        if porcentaje_ejecutado < umbral_bajo
                        else NotificationPriority.HIGH
                    )

                    alertas.append({
                        'accion': accion,
                        'presupuesto': presupuesto,
                        'tipo': 'ejecucion_baja',
                        'prioridad': prioridad,
                        'mensaje': f'Baja ejecución presupuestaria en "{accion.nombre}" '
                                   f'({porcentaje_ejecutado:.1f}% ejecutado, '
                                   f'{porcentaje_tiempo:.1f}% del tiempo transcurrido)',
                        'porcentaje_ejecutado': porcentaje_ejecutado,
                        'porcentaje_tiempo': porcentaje_tiempo
                    })

        return alertas

    def check_presupuesto_agotado(self, umbral: float = 95) -> List[Dict]:
        """Detecta presupuestos próximos a agotarse"""
        from registro.models import Accion

        alertas = []

        for accion in Accion.objects.filter(publicado=True):
            for presupuesto in accion.presupuestos_planificados.all():
                ejecutado = presupuesto.presupuestos_ejecutados.aggregate(
                    total=Sum('monto')
                )['total'] or 0

                porcentaje_ejecutado = (
                    ejecutado / presupuesto.monto * 100
                    if presupuesto.monto > 0 else 0
                )

                if porcentaje_ejecutado >= umbral and porcentaje_ejecutado < 100:
                    alertas.append({
                        'accion': accion,
                        'presupuesto': presupuesto,
                        'tipo': 'presupuesto_agotandose',
                        'prioridad': NotificationPriority.HIGH,
                        'mensaje': f'Presupuesto próximo a agotarse en "{accion.nombre}" '
                                   f'({porcentaje_ejecutado:.1f}% ejecutado)',
                        'porcentaje_ejecutado': porcentaje_ejecutado
                    })
                elif porcentaje_ejecutado >= 100:
                    alertas.append({
                        'accion': accion,
                        'presupuesto': presupuesto,
                        'tipo': 'presupuesto_agotado',
                        'prioridad': NotificationPriority.CRITICAL,
                        'mensaje': f'Presupuesto agotado en "{accion.nombre}"',
                        'porcentaje_ejecutado': porcentaje_ejecutado
                    })

        return alertas

    def generar_todas_alertas(self) -> Dict:
        """Genera todas las alertas de presupuesto"""
        return {
            'ejecucion_baja': self.check_ejecucion_presupuestaria(),
            'presupuesto_agotado': self.check_presupuesto_agotado()
        }


class NotificationDispatcher:
    """Despachador de notificaciones a usuarios"""

    def __init__(self):
        self.notification_service = NotificationService()
        self.indicador_alert_service = IndicadorAlertService(self.notification_service)
        self.presupuesto_alert_service = PresupuestoAlertService(self.notification_service)

    def dispatch_daily_alerts(self):
        """Despacha alertas diarias a todos los usuarios"""
        logger.info('Iniciando despacho de alertas diarias')

        # Obtener todas las alertas
        alertas_indicadores = self.indicador_alert_service.generar_todas_alertas()
        alertas_presupuesto = self.presupuesto_alert_service.generar_todas_alertas()

        # Agrupar alertas por usuario
        usuarios_alertas = {}

        # Procesar alertas de indicadores
        for tipo, alertas in alertas_indicadores.items():
            for alerta in alertas:
                user = alerta['accion'].user
                if user not in usuarios_alertas:
                    usuarios_alertas[user] = []
                usuarios_alertas[user].append(alerta)

        # Procesar alertas de presupuesto
        for tipo, alertas in alertas_presupuesto.items():
            for alerta in alertas:
                user = alerta['accion'].user
                if user not in usuarios_alertas:
                    usuarios_alertas[user] = []
                usuarios_alertas[user].append(alerta)

        # Enviar notificaciones a cada usuario
        for user, alertas in usuarios_alertas.items():
            self._send_user_alert_email(user, alertas)

        logger.info(f'Alertas enviadas a {len(usuarios_alertas)} usuarios')
        return len(usuarios_alertas)

    def _send_user_alert_email(self, user, alertas: List[Dict]):
        """Envía email con resumen de alertas a un usuario"""
        if not alertas:
            return

        # Contar alertas por prioridad
        criticas = sum(1 for a in alertas if a['prioridad'] == NotificationPriority.CRITICAL)
        altas = sum(1 for a in alertas if a['prioridad'] == NotificationPriority.HIGH)
        medias = sum(1 for a in alertas if a['prioridad'] == NotificationPriority.MEDIUM)

        # Construir mensaje
        subject = f'Resumen de Alertas - {timezone.now().date().strftime("%d/%m/%Y")}'

        message = f"""
            Hola {user.get_full_name() or user.username},
            
            Este es tu resumen diario de alertas del Sistema de Adaptación al Cambio Climático.
            
            RESUMEN:
            - {criticas} alertas CRÍTICAS
            - {altas} alertas de PRIORIDAD ALTA
            - {medias} alertas de PRIORIDAD MEDIA
            
            DETALLE DE ALERTAS:

            """
        # Ordenar por prioridad
        prioridad_orden = {
            NotificationPriority.CRITICAL: 0,
            NotificationPriority.HIGH: 1,
            NotificationPriority.MEDIUM: 2,
            NotificationPriority.LOW: 3
        }
        alertas_ordenadas = sorted(alertas, key=lambda x: prioridad_orden[x['prioridad']])

        for i, alerta in enumerate(alertas_ordenadas, 1):
            prioridad_texto = alerta['prioridad'].upper()
            accion = alerta.get('accion')
            if accion:
                message += f"{i}. [{prioridad_texto}] {alerta['mensaje']}\n"
                message += f"   Acción: {accion.nombre}\n\n"

        message += """
            Por favor, revisa el sistema para más detalles y toma las acciones necesarias.
            
            ---
            Sistema de Monitoreo y Evaluación de Acciones de Adaptación
            """

        # Enviar email
        self.notification_service.send_email_notification(user, subject, message)

    def get_user_notifications(self, user, only_unread: bool = True) -> List[Dict]:
        """Obtiene notificaciones de un usuario específico"""
        # Obtener alertas actuales del usuario
        from registro.models import Accion

        alertas_indicadores = self.indicador_alert_service.generar_todas_alertas()
        alertas_presupuesto = self.presupuesto_alert_service.generar_todas_alertas()

        user_notifications = []

        # Filtrar alertas del usuario - Indicadores
        for tipo, alertas in alertas_indicadores.items():
            for alerta in alertas:
                if alerta['accion'].user == user:
                    user_notifications.append({
                        'id': f"ind_{tipo}_{alerta['indicador'].id}",
                        'title': f"Alerta: {alerta['indicador'].nombre}",
                        'message': alerta['mensaje'],
                        'priority': alerta['prioridad'],
                        'created_at': timezone.now(),
                        'read': False,
                        'url': f"/accion/{alerta['accion'].id}/indicadores/{alerta['indicador'].id}/resultado/comportamiento/"
                    })

        # Filtrar alertas del usuario - Presupuestos
        for tipo, alertas in alertas_presupuesto.items():
            for alerta in alertas:
                if alerta['accion'].user == user:
                    user_notifications.append({
                        'id': f"pres_{alerta['presupuesto'].id}",
                        'title': f"Alerta Presupuestaria: {alerta['accion'].nombre}",
                        'message': alerta['mensaje'],
                        'priority': alerta['prioridad'],
                        'created_at': timezone.now(),
                        'read': False,
                        'url': f"/accion/{alerta['accion'].id}/presupuesto/lista/"
                    })

        return user_notifications