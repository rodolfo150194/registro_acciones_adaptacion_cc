import datetime
import pathlib

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import F, Avg
from django.utils.timezone import now

from .utils import data_chart_line
from nomencladores.models import *


def get_upload_path(instance, filename):
    # Obtener el nombre de la clase del objeto relacionado
    related_model_name = instance.__class__.__name__.lower()
    upload_path = f'documentos_subidos/{related_model_name}/{now().year}/{now().month}/{now().day}/{filename}'

    return upload_path


class Documento(models.Model):
    nombre = models.CharField(max_length=500, verbose_name="Nombre", null=True, blank=True)
    documento = models.FileField(verbose_name="Documento", upload_to=get_upload_path, null=True, blank=True)
    fecha = models.DateTimeField('Fecha de subida', auto_now=True)

    def __str__(self):
        return self.nombre

    def get_extension(self):
        path = pathlib.Path(self.documento.url)
        return path.suffix


class Cobeneficio(models.Model):
    history = AuditlogHistoryField()
    nombre = models.CharField(max_length=500, verbose_name="Nombre", null=True, blank=True)
    descripcion = models.CharField(max_length=500, verbose_name="Descripción", null=True, blank=True)
    cumplimiento = models.BooleanField(default=False, verbose_name="Cumplimiento", null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)


class ResultadoIndicador(models.Model):
    history = AuditlogHistoryField()
    fuente_dato = models.CharField(max_length=500, verbose_name="Fuente del dato", null=True, blank=True)
    variable_indicador = models.ManyToManyField(VariableIndicador, verbose_name="Variables", related_name="variables",
                                                blank=True,
                                                through="ResultadoVariable")
    valor = models.FloatField(null=True, blank=True)
    observacion = models.CharField(max_length=500, verbose_name="Observaciones o comentarios", null=True, blank=True)
    fecha = models.DateField(unique=True)



class ResultadoVariable(models.Model):
    history = AuditlogHistoryField()
    resultado = models.ForeignKey(ResultadoIndicador, verbose_name='Resultado', on_delete=models.CASCADE, null=True,
                                  blank=True)
    variable_indicador = models.ForeignKey(VariableIndicador, verbose_name='Variable', on_delete=models.CASCADE,
                                           null=True, blank=True)
    valor = models.FloatField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now=True)



class Indicador(models.Model):
    DIRECCION_CHOICES = [
        ('incremento', 'A mayor valor, mejor resultado'),
        ('decremento', 'A menor valor, mejor resultado'),
    ]

    history = AuditlogHistoryField()
    nombre = models.CharField(verbose_name='Nombre', max_length=500)
    tipo_indicador = models.ForeignKey(TipoIndicador, verbose_name='Tipo de indicador', on_delete=models.CASCADE)
    descripcion = models.CharField(verbose_name='Descripcion del indicador', max_length=500, null=True, blank=True)
    fuente_indicador = models.CharField(verbose_name='Fuente del indicador', max_length=500, null=True, blank=True)
    formula = models.CharField(verbose_name='Fórmula o Método de calculo', max_length=500, help_text='Ecuación para medir el indicador, escriba las variables y los operadores con precaución. Ejemplo (cant_animal*factor_emision)/1000')
    unidad_medida = models.ForeignKey(UnidadMedidaIndicador, on_delete=models.CASCADE)
    enfoqueIPCC = models.ForeignKey(EnfoqueIPCC, verbose_name='Enfoque IPCC', on_delete=models.CASCADE,
                                    null=True, blank=True)
    objetivos_relacionados = models.ManyToManyField(ObjetivosDesarrolloSostenible, blank=True,
                                                    related_name="objetivos_relacionados",
                                                    verbose_name="Objetivos de Desarrollo Sostenible relacionados")
    frecuencia_medicion = models.ForeignKey(FrecuenciaMedicion, verbose_name="Frecuencia de la medicion",
                                            on_delete=models.CASCADE, null=True, blank=True)
    variable_indicador = models.ManyToManyField(VariableIndicador, verbose_name="Dato del indicador",
                                                related_name="variables_indicador")
    resultados = models.ManyToManyField(ResultadoIndicador, verbose_name="Resultados del indicador",
                                        related_name="resultados_indicador", blank=True)
    ultima_medicion = models.DateTimeField(null=True, blank=True)
    direccion_optima = models.CharField(
        max_length=20,
        choices=DIRECCION_CHOICES,
        verbose_name='Dirección óptima del indicador',
        null=True,
        blank=True,
        help_text='Define si el indicador mejora al aumentar o disminuir su valor'
    )

    # Meta específica para este indicador
    meta_valor = models.FloatField(
        verbose_name='Valor meta a alcanzar',
        null=True,
        blank=True,
        help_text='Valor objetivo que se desea alcanzar con este indicador'
    )

    meta_fecha_limite = models.DateField(
        verbose_name='Fecha límite para alcanzar la meta',
        null=True,
        blank=True
    )
    valor_baseline = models.FloatField(
        verbose_name='Valor base',
        null=True,
        blank=True,
        help_text='Valor inicial o de referencia antes de implementar acciones'
    )


    def __str__(self):
        return self.nombre + ' - ' + self.tipo_indicador.nombre

    @property
    def variacion_valor(self):
        """
        Retorna la variación numérica y porcentual del valor entre el primer y el último resultado.
        """
        primer_resultado = self.resultados.order_by('fecha').first()
        ultimo_resultado = self.resultados.order_by('-fecha').first()

        if primer_resultado and ultimo_resultado:
            variacion_numerica = ultimo_resultado.valor - primer_resultado.valor
            if primer_resultado.valor != 0:
                variacion_porcentual = (variacion_numerica / primer_resultado.valor) * 100
            else:
                variacion_porcentual = 0
        else:
            variacion_numerica = variacion_porcentual = None


        return {
            'variacion_numerica': variacion_numerica,
            'variacion_porcentual': variacion_porcentual,
            'primer_resultado': primer_resultado,
            'ultimo_resultado': ultimo_resultado
        }



    @property
    def mayor_valor(self):
        return self.resultados.annotate(valor_abs=F('valor')).filter(valor__gt=0).order_by('-valor_abs').first()

    @property
    def menor_valor(self):
        return self.resultados.annotate(valor_abs=F('valor')).order_by('valor_abs').first()

    @property
    def promedio_valor(self):
        return self.resultados.aggregate(promedio=Avg('valor'))['promedio']

    @property
    def get_grafico(self):
        data_line = {
            'valores': {
                'name': 'Valor',
                'data': []
            },
            'labels': []
        }
        for re in self.resultados.all():
            data_line['valores']['data'].append(round(re.valor, 2))
            data_line['labels'].append(re.fecha.strftime("%d-%m-%Y"))

        chart_data_line = data_chart_line(data_line, self)
        return chart_data_line

    def calcular_proxima_medicion(self):
        """Calcula la próxima medición basada en la última medición registrada"""
        if not self.frecuencia_medicion:
            return None

        # Buscar la última medición real en los resultados
        ultimo_resultado = self.resultados.order_by('-fecha').first()
        if not ultimo_resultado:
            return None

        from dateutil.relativedelta import relativedelta

        # Calcular basándose en la última medición real
        ultima_fecha = ultimo_resultado.fecha

        if 'mensual' in self.frecuencia_medicion.nombre.lower():
            return ultima_fecha + relativedelta(months=1)
        elif 'trimestral' in self.frecuencia_medicion.unidad.lower():
            return ultima_fecha + relativedelta(months=3)
        elif 'semestral' in self.frecuencia_medicion.nombre.lower():
            return ultima_fecha + relativedelta(months=6)
        elif 'anual' in self.frecuencia_medicion.nombre.lower():
            return ultima_fecha + relativedelta(years=1)
        elif 'semanal' in self.frecuencia_medicion.nombre.lower():
            return ultima_fecha + relativedelta(weeks=1)
        else:
            # Por defecto, usar días si no se reconoce la frecuencia
            return ultima_fecha + relativedelta(days=30)

    def interpretar_cambio(self, valor_anterior, valor_actual):
        """Interpreta si un cambio es positivo o negativo según la dirección óptima"""
        if valor_anterior is None or valor_actual is None:
            return 'neutral'

        diferencia = valor_actual - valor_anterior

        if diferencia == 0:
            return 'neutral'
        elif self.direccion_optima == 'incremento':
            return 'positivo' if diferencia > 0 else 'negativo'
        else:  # decremento
            return 'positivo' if diferencia < 0 else 'negativo'

    def calcular_progreso_meta(self):
        """Calcula el progreso hacia la meta considerando la dirección óptima"""
        if not self.meta_valor:
            return None

        ultimo_resultado = self.resultados.order_by('-fecha').first()
        if not ultimo_resultado:
            return None

        valor_actual = ultimo_resultado.valor
        baseline = self.valor_baseline or 0

        if self.direccion_optima == 'incremento':
            # Para indicadores que deben incrementar
            if self.meta_valor <= baseline:
                return None  # Meta mal configurada

            progreso = ((valor_actual - baseline) / (self.meta_valor - baseline)) * 100
        else:
            # Para indicadores que deben decrementar
            if self.meta_valor >= baseline:
                return None  # Meta mal configurada

            progreso = ((baseline - valor_actual) / (baseline - self.meta_valor)) * 100

        return {
            'progreso_porcentaje': max(0, min(100, progreso)),
            'valor_actual': valor_actual,
            'meta_valor': self.meta_valor,
            'baseline': baseline,
            'meta_alcanzada': (
                valor_actual >= self.meta_valor if self.direccion_optima == 'incremento'
                else valor_actual <= self.meta_valor
            )
        }

    def get_ultimo_valor(self):
        # Último resultado asociado al indicador
        ultimo_resultado = self.resultados.order_by("-fecha").first()

        if not ultimo_resultado:
            return self.valor_baseline

        return round(ultimo_resultado.valor,2)

    def get_users(self):
        acciones = self.accion_set.all()
        usuarios = User.objects.filter(accion__in=acciones).distinct()
        return usuarios


class ResultadoAccion(models.Model):
    history = AuditlogHistoryField()
    descripcion = models.TextField(verbose_name="Descripcion del resultado de la acción")
    fecha = models.DateField(auto_now=True)

    def __str__(self):
        return self.descripcion


class Presupuesto(models.Model):
    history = AuditlogHistoryField()
    tipo_presupuesto = models.ForeignKey(TipoPresupuesto, verbose_name='Tipo presupuesto', on_delete=models.CASCADE)
    tipo_moneda = models.ForeignKey(TipoMoneda, verbose_name='Tipo de moneda', on_delete=models.CASCADE)
    monto = models.FloatField(verbose_name='Monto')

    class Meta:
        abstract = True

    @property
    def format_monto(self):
        return intcomma(self.monto)



class PresupuestoEjecutado(models.Model):
    history = AuditlogHistoryField()
    monto = models.FloatField(verbose_name='Monto')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio', null=True, blank=True)
    fecha_fin = models.DateField(verbose_name='Fecha de finalización', null=True, blank=True)
    observacion = models.CharField(verbose_name='Observación', max_length=500, null=True, blank=True)

    @property
    def get_porciento_ejecutado(self):
        presupuesto_planificado = self.presupuestos_ejecutados.first()
        return (self.monto / presupuesto_planificado.monto) * 100

    @property
    def cantidad_dias_periodo(self):
        diferencia = relativedelta(self.fecha_fin, self.fecha_inicio)
        meses_diferencia = diferencia.years * 365 + diferencia.days
        return meses_diferencia



class PresupuestoPlanificado(Presupuesto):
    history = AuditlogHistoryField()
    fuente_financiamiento = models.CharField(verbose_name='Fuente del financiamiento', max_length=500)
    estado_presupuesto = models.ForeignKey(EstadoPresupuesto, verbose_name='Estado del presupuesto',
                                           on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaPresupuesto, verbose_name='Categoría',
                                  on_delete=models.CASCADE, null=True, blank=True)
    presupuestos_ejecutados = models.ManyToManyField(PresupuestoEjecutado, verbose_name="Presupuestos ejecutados",
                                                     related_name="presupuestos_ejecutados", blank=True)

    def __str__(self):
        return self.tipo_presupuesto.nombre + ' - ' + self.estado_presupuesto.nombre + ' - ' + str(
            self.monto) + ' - ' + self.tipo_moneda.nombre

    @property
    def get_monto_restante(self):
        total_ejecutado = sum(p.monto for p in self.presupuestos_ejecutados.all())
        return self.monto - total_ejecutado

    @property
    def get_porcentaje_monto_ejecutado(self):
        porciento_total_ejecutado = sum(p.get_porciento_ejecutado for p in self.presupuestos_ejecutados.all())
        return porciento_total_ejecutado

    @property
    def get_monto_total_ejecutado(self):
        total_ejecutado = sum(p.monto for p in self.presupuestos_ejecutados.all())
        return total_ejecutado

    # @property
    # def format_monto(self):
    #     return "${:,.2f}".format(self.monto).replace(",", "X").replace(".", ",").replace("X", ".")


class Accion(models.Model):
    history = AuditlogHistoryField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_accion = models.ForeignKey(TipoAccion, verbose_name='Tipo Accion', on_delete=models.CASCADE)
    nombre = models.CharField(verbose_name='Nombre', max_length=150)
    objetivo = models.CharField(verbose_name='Objetivo', max_length=500, null=True, blank=True)
    descripcion = models.CharField(verbose_name='Descripcion de la acción', max_length=500, null=True, blank=True)
    sector = models.ForeignKey(Sector, verbose_name='Sector', on_delete=models.CASCADE)
    escenario = models.ForeignKey(Escenario, verbose_name='Escenario', on_delete=models.CASCADE, null=True, blank=True)
    alcance = models.ForeignKey(Alcance, verbose_name='Alcance', on_delete=models.CASCADE, null=True, blank=True)
    escala = models.ForeignKey(Escala, verbose_name='Escala o niveles', on_delete=models.CASCADE, null=True, blank=True)
    lugar_intervencion = models.CharField(verbose_name='Lugar de intervención', max_length=500, null=True, blank=True)
    provincias = models.ManyToManyField(Provincia, verbose_name='Provincia', blank=True, null=True)
    municipios = models.ManyToManyField(Municipio, verbose_name='Municipios', blank=True, null=True)
    meta = models.CharField(verbose_name='Meta climática', max_length=500, null=True, blank=True)
    publicado = models.BooleanField(default=False, verbose_name="Publicado", null=True, blank=True)

    fecha_inicio = models.DateField(verbose_name='Fecha de inicio', null=True, blank=True)
    fecha_fin = models.DateField(verbose_name='Fecha de finalización', null=True, blank=True)
    estado_accion = models.ForeignKey(EstadoAccion, verbose_name='Estado', null=True, blank=True,
                                      on_delete=models.CASCADE)
    entidad_responsable = models.ForeignKey(Entidad, verbose_name='Institución o Entidad responsable',
                                            related_name='entidad_responsable',
                                            on_delete=models.CASCADE, null=True, blank=True)
    programa_apoyo = models.ForeignKey(ProgramaApoyo, verbose_name='Programa de Apoyo',
                                       related_name='programa_apoyo',
                                       on_delete=models.CASCADE, null=True, blank=True)
    programa_productivo = models.ForeignKey(ProgramaProductivo, verbose_name='Programa Productivo',
                                            related_name='programa_productivo',
                                            on_delete=models.CASCADE, null=True, blank=True)
    otras_entidades = models.ManyToManyField(Entidad, verbose_name='Otras entidades involucradad',
                                             related_name='otras_entidades', blank=True)

    presupuestos_planificados = models.ManyToManyField(PresupuestoPlanificado, verbose_name="Presupuestos planificados",
                                                       related_name="presupuestos_planificados", blank=True)
    indicadores = models.ManyToManyField(Indicador, verbose_name="Indicadores", related_name="indicadores", blank=True)
    cobeneficios = models.ManyToManyField(Cobeneficio, verbose_name="Cobeneficios", related_name="cobeneficios",
                                          blank=True)
    documentos = models.ManyToManyField(Documento, verbose_name="Documentos relacionados",
                                        related_name="documentos_accion", blank=True)
    resultados_accion = models.ManyToManyField(ResultadoAccion, verbose_name="Resultados de la accción",
                                               related_name="resultados_accion", blank=True)

    def __str__(self):
        return self.nombre

    @property
    def calcular_dias_desde_inicio(self):
        dias = datetime.date.today() - self.fecha_inicio
        return dias.days

    @property
    def presupuesto_total(self):
        presupuesto_total_por_monedas = []

        for tm in TipoMoneda.objects.filter(estado=True):
            monto_total = 0
            monto_ejecutado = 0
            monto_restante = 0
            for pp in self.presupuestos_planificados.filter(tipo_moneda=tm):
                monto_total += pp.monto
            presupuesto_total_por_monedas.append({'moneda': tm.nombre, 'monto_total': monto_total})

        return presupuesto_total_por_monedas

    @property
    def total_indicatores(self):
        return self.indicadores.count()

    # obtener la primera letra del nombre
    @property
    def get_primera_letra(self):
        return self.nombre[0]



auditlog.register(Accion)
auditlog.register(Indicador)
auditlog.register(PresupuestoPlanificado)
auditlog.register(PresupuestoEjecutado)
auditlog.register(ResultadoAccion)
auditlog.register(ResultadoIndicador)
auditlog.register(Documento)
auditlog.register(Cobeneficio)
auditlog.register(ResultadoVariable)
