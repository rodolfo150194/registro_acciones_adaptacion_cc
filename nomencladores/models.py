from django.db import models

# Create your models here.
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db import models
from datetime import timedelta

from parler.models import TranslatableModel, TranslatedFields

# Create your models here.

SEXO = (
    ('1', 'FEMENINO'),
    ('2', 'MASCULINO'),
)


class NomencladorAbstract(models.Model):
    nombre = models.CharField(verbose_name='Nombre', max_length=500, null=True, blank=True)

    class Meta:
        abstract = True


class Provincia(NomencladorAbstract):
    hc_keys = models.CharField(max_length=5)
    codigo = models.CharField(max_length=2, verbose_name='Código')
    sigla = models.CharField(max_length=3, verbose_name='Sigla')

    def __str__(self):
        return self.nombre + ' ~ ' + self.sigla



class Municipio(NomencladorAbstract):
    provincia = models.ForeignKey(Provincia, verbose_name='Provincia', on_delete=models.PROTECT)
    codigo = models.CharField(verbose_name='Código', max_length=5)

    def __str__(self):
        return self.nombre



class TipoEntidad(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class Cargo(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class Entidad(NomencladorAbstract):
    history = AuditlogHistoryField()
    direccion = models.CharField(verbose_name='Direccion', max_length=500, null=True, blank=True)
    correo = models.EmailField(verbose_name='Correo', max_length=150, null=True, blank=True)
    # tipo_entidad = models.ForeignKey(TipoEntidad, on_delete=models.CASCADE, null=True, blank=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Sector(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    def get_presupuesto_total(self):
        presupuesto_total_por_monedas = []
        for tm in TipoMoneda.objects.all():
            monto_total = 0
            for a in self.accion_set.all():
                for pp in a.presupuestos_planificados.filter(tipo_moneda=tm):
                    monto_total += pp.monto

            presupuesto_total_por_monedas.append({'moneda': tm, 'total': monto_total})

        return presupuesto_total_por_monedas


class TipoAccion(NomencladorAbstract):
    history = AuditlogHistoryField()
    info_tooltip = models.CharField(max_length=500, verbose_name="Tooltip", null=True, blank=True)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


class TipoIndicador(NomencladorAbstract):
    history = AuditlogHistoryField()
    info_tooltip = models.CharField(max_length=500, verbose_name="Tooltip", null=True, blank=True)
    orden = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Escala(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class Alcance(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


# class LugarIntervencion(NomencladorAbstract):
#     history = AuditlogHistoryField()
#
#     def __str__(self):
#         return self.nombre


class TipoMoneda(NomencladorAbstract):
    history = AuditlogHistoryField()
    info_tooltip = models.CharField(max_length=500, verbose_name="Tooltip", null=True, blank=True)
    orden = models.IntegerField(default=0, null=True, blank=True)
    estado = models.BooleanField(default=True, verbose_name='¿Está activo?',null=True, blank=True)

    def __str__(self):
        return self.nombre


class TipoPresupuesto(NomencladorAbstract):
    history = AuditlogHistoryField()
    info_tooltip = models.CharField(max_length=500, verbose_name="Tooltip", null=True, blank=True)
    orden = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.nombre


class Escenario(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class CategoriaPresupuesto(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class EstadoAccion(NomencladorAbstract):
    history = AuditlogHistoryField()
    orden = models.IntegerField(verbose_name='Orden lógico', default=0)

    def __str__(self):
        return self.nombre


class EstadoPresupuesto(NomencladorAbstract):
    history = AuditlogHistoryField()
    orden = models.IntegerField(verbose_name='Orden lógico')

    def __str__(self):
        return self.nombre


class ProgramaProductivo(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class ProgramaApoyo(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class UnidadMedidaIndicador(NomencladorAbstract):
    history = AuditlogHistoryField()
    sigla = models.CharField(verbose_name='Sigla', max_length=150)

    def __str__(self):
        return self.nombre


class EnfoqueIPCC(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class ObjetivosDesarrolloSostenible(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class AmenazaClimatica(NomencladorAbstract):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre


class FrecuenciaMedicion(NomencladorAbstract):
    UNIDADES = [
        ("minutos", "Minutos"),
        ("horas", "Horas"),
        ("dias", "Días"),
        ("semanas", "Semanas"),
        ("meses", "Meses"),
        ("años", "Años"),
    ]

    cantidad = models.PositiveIntegerField(verbose_name="Cantidad de tiempo")
    unidad = models.CharField(verbose_name="Unidad de tiempo", max_length=10, choices=UNIDADES)
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nombre

    def __str__(self):
        return f"{self.nombre} ({self.cantidad} {self.get_unidad_display()})"


    def calcular_timedelta(self):

        unidad_mapping = {
            "dias": timedelta(days=self.cantidad),
            "semanas": timedelta(weeks=self.cantidad),
            "meses": timedelta(days=self.cantidad * 30),
            "años": timedelta(days=self.cantidad * 365),
            "horas": timedelta(hours=self.cantidad),
            "minutos": timedelta(minutes=self.cantidad),
        }
        return unidad_mapping.get(self.unidad, timedelta(days=0))


class VariableIndicador(NomencladorAbstract):
    history = AuditlogHistoryField()
    variable = models.CharField('Variable', max_length=100, null=True)

    def __str__(self):
        return self.nombre





auditlog.register(TipoEntidad)
auditlog.register(Cargo)
auditlog.register(Entidad)
auditlog.register(Sector)
auditlog.register(TipoAccion)
auditlog.register(TipoIndicador)
auditlog.register(Escala)
auditlog.register(Alcance)
auditlog.register(TipoMoneda)
auditlog.register(TipoPresupuesto)
auditlog.register(Escenario)
auditlog.register(EstadoAccion)
auditlog.register(EstadoPresupuesto)
auditlog.register(ProgramaProductivo)
auditlog.register(ProgramaApoyo)
auditlog.register(UnidadMedidaIndicador)
auditlog.register(EnfoqueIPCC)
auditlog.register(ObjetivosDesarrolloSostenible)
auditlog.register(AmenazaClimatica)
auditlog.register(FrecuenciaMedicion)
auditlog.register(VariableIndicador)
auditlog.register(CategoriaPresupuesto)
