from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from nomencladores.models import NomencladorAbstract
from registro.models import Accion, Indicador, PresupuestoPlanificado


# Create your models here.
class TipoNotificacion(NomencladorAbstract):
    """Tipos de notificación disponibles"""
    history = AuditlogHistoryField()
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código único")
    icono = models.CharField(max_length=50, null=True, blank=True, verbose_name="Icono")
    color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Color")

    class Meta:
        verbose_name = "Tipo de Notificación"
        verbose_name_plural = "Tipos de Notificación"

    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    """Modelo para gestionar notificaciones de mediciones de indicadores"""
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    history = AuditlogHistoryField()

    # Relaciones
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones', verbose_name="Usuario")
    indicador = models.ForeignKey(Indicador,on_delete=models.CASCADE, related_name='notificaciones',  verbose_name="Indicador",  null=True,  blank=True)
    accion = models.ForeignKey(Accion,on_delete=models.CASCADE,related_name='notificaciones',verbose_name="Acción",null=True,blank=True)
    presupuesto = models.ForeignKey(PresupuestoPlanificado,on_delete=models.CASCADE,related_name='notificaciones',verbose_name="Presupuesto",null=True,blank=True)
    tipo_notificacion = models.ForeignKey( TipoNotificacion,on_delete=models.PROTECT,verbose_name="Tipo de notificación", null=True, blank=True)
    titulo = models.CharField(max_length=200, verbose_name="Título")
    mensaje = models.TextField(verbose_name="Mensaje")
    enlace = models.CharField( max_length=500,null=True,blank=True,verbose_name="Enlace a la acción")
    leida = models.BooleanField(default='False', verbose_name="Es leida")
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media', verbose_name="Prioridad", null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_leida = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de lectura")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion', '-prioridad']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['fecha_creacion', 'leida']),
            models.Index(fields=['indicador', 'leida']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

    def marcar_como_leida(self):
        """Marca la notificación como leída"""
        if self.leida == False:
            self.leida = True
            self.fecha_leida = timezone.now()
            self.save(update_fields=['leida', 'fecha_leida'])



    @property
    def icono_prioridad(self):
        """Retorna el icono según la prioridad"""
        iconos = {
            'baja': 'ki-information',
            'media': 'ki-notification',
            'alta': 'ki-warning',
            'urgente': 'ki-shield-cross'
        }
        return iconos.get(self.prioridad, 'ki-notification')

    @property
    def color_prioridad(self):
        """Retorna el color según la prioridad"""
        colores = {
            'baja': 'info',
            'media': 'primary',
            'alta': 'warning',
            'urgente': 'danger'
        }
        return colores.get(self.prioridad, 'primary')

    @property
    def get_tiempo_desde_creacion(self):
        tiempo = timezone.now() - self.fecha_creacion
        if tiempo.days > 0:
            return f'{tiempo.days} días'
        elif tiempo.seconds // 3600 > 0:
            return f'{tiempo.seconds // 3600} horas'
        elif tiempo.seconds // 60 > 0:
            return f'{tiempo.seconds // 60} minutos'
        else:
            return 'Hace unos segundos'


class ConfiguracionNotificacion(models.Model):
    usuario = models.OneToOneField(User,on_delete=models.CASCADE, related_name='config_notificaciones',  verbose_name="Usuario")
    notificar_meta_cercana = models.BooleanField( default=True, verbose_name="Notificar cuando una meta está cerca")
    notificar_meta_vencida = models.BooleanField( default=True, verbose_name="Notificar metas vencidas")
    notificar_resultado_anomalo = models.BooleanField( default=True,  verbose_name="Notificar resultados anómalos")
    recibir_emails = models.BooleanField( default=True, verbose_name="Recibir notificaciones por email")
    email_alternativo = models.EmailField( null=True,  blank=True,  verbose_name="Email alternativo", help_text="Email adicional para recibir notificaciones")

    # Horarios de envío
    hora_envio_preferida = models.TimeField(  default='09:00:00',  verbose_name="Hora preferida de envío",  help_text="Hora del día para recibir notificaciones")

    # Control
    activo = models.BooleanField( default=True,verbose_name="Sistema de notificaciones activo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Notificación"
        verbose_name_plural = "Configuraciones de Notificaciones"

    def __str__(self):
        return f"Config. notificaciones - {self.usuario.username}"


# Registrar modelos en auditlog
auditlog.register(TipoNotificacion)
auditlog.register(Notificacion)
auditlog.register(ConfiguracionNotificacion)