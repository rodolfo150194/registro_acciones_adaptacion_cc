from auditlog.models import AuditlogHistoryField
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models
from django.utils import timezone

from config.settings import MEDIA_URL, STATIC_URL
from nomencladores.models import Cargo, Entidad
from registro.models import Accion
from seguridad.validators import validate_image_size


class Notificacion(models.Model):
    TIPOS = (
        ('S', 'Seguridad'),
        ('M', 'Mensaje'),
        ('P', 'Proceso')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacion')
    message = models.CharField(max_length=255)
    type = models.CharField(max_length=1, choices=TIPOS)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    link = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return self.mensaje

    # calcula el tiempo exacto desde la creacion de la notificacion ya sea minutos horas dias
    @property
    def get_tiempo_desde_creacion(self):
        tiempo = timezone.now() - self.created_at
        if tiempo.days > 0:
            return f'{tiempo.days} días'
        elif tiempo.seconds // 3600 > 0:
            return f'{tiempo.seconds // 3600} horas'
        elif tiempo.seconds // 60 > 0:
            return f'{tiempo.seconds // 60} minutos'
        else:
            return 'Hace unos segundos'


class Perfil(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?\d{7,15}$',
        message="El número de teléfono debe estar en el formato: '+5357899472'. Entre 7 y 15 dígitos permitidos."
    )

    SEXO = (('F', 'Femenino'), ('M', 'Masculino'), ('', '---------'))

    history = AuditlogHistoryField()
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', verbose_name='Usuario')
    nombre = models.CharField(verbose_name='Nombre', max_length=150, null=True, blank=True)
    apellidos = models.CharField(verbose_name='Apellidos', max_length=500, null=True, blank=True)
    edad = models.IntegerField(verbose_name='Edad', null=True, blank=True,validators=[
        MinValueValidator(18, message="Debe tener al menos 18 años."),
        MaxValueValidator(120, message="Edad no válida.")
    ])
    sexo = models.CharField(max_length=1, choices=SEXO, default='', null=True, blank=True)
    correo = models.EmailField(verbose_name='Correo', max_length=150, null=True, blank=True, unique=True)
    telefono = models.CharField(verbose_name='Teléfono', max_length=20, null=True, blank=True,
                                validators=[phone_regex], help_text='De ser posible teléfono coorporativo.')
    cargo = models.ForeignKey(Cargo, verbose_name='Cargo que ocupa', on_delete=models.SET_NULL, null=True, blank=True)
    entidad = models.ForeignKey(Entidad, verbose_name='Entidad responsable', on_delete=models.SET_NULL, null=True,
                                blank=True)

    foto = models.ImageField(verbose_name='Foto', upload_to='perfil/', null=True, blank=True,
                             validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),validate_image_size

    ],
    help_text='Formatos soportados: JPG, JPEG, PNG')

    def __str__(self):
        return f"{self.nombre} {self.apellidos}".strip()

    def get_foto(self):
        if self.foto:
            return '{}{}'.format(MEDIA_URL, self.foto)

        else:
            return '{}{}'.format(STATIC_URL, 'assets/media/user_empty.png')





    @property
    def acciones(self):
        acciones = Accion.objects.filter(user=self.user)
        return acciones