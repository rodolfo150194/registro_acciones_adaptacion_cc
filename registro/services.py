import statistics

import numpy as np
from django.db.models import Avg, Min, Max, StdDev
from django.urls import reverse
from django.utils import timezone
from sympy import sympify, Symbol

from registro.models import ResultadoVariable
from registro.utils import data_chart_line


class BreadcrumbBuilder:
    """Constructor de breadcrumbs (Single Responsibility)"""

    @staticmethod
    def build_indicador_list_breadcrumbs():
        return [
            {'name': 'Inicio', 'url': reverse('registro:home'), 'icon': 'ki-home'},
            {'name': 'Acciones', 'url': reverse('registro:lista_accion'), 'icon': None},
            {'name': 'Indicadores', 'url': None, 'icon': None},
        ]

    @staticmethod
    def build_indicador_create_breadcrumbs(id_accion):
        return [
            {'name': 'Inicio', 'url': reverse('registro:home'), 'icon': 'ki-home'},
            {'name': 'Acciones', 'url': reverse('registro:lista_accion'), 'icon': None},
            {'name': 'Indicadores', 'url': reverse('registro:lista_indicador', args=[id_accion]), 'icon': None},
            {'name': 'Nuevo Indicador', 'url': None, 'icon': None},
        ]

    @staticmethod
    def build_indicador_update_breadcrumbs(id_accion):
        return [
            {'name': 'Inicio', 'url': reverse('registro:home'), 'icon': 'ki-home'},
            {'name': 'Acciones', 'url': reverse('registro:lista_accion'), 'icon': None},
            {'name': 'Indicadores', 'url': reverse('registro:lista_indicador', args=[id_accion]), 'icon': None},
            {'name': 'Indicador', 'url': None, 'icon': None},
        ]

    @staticmethod
    def build_comportamiento_indicador_breadcrumbs(id_accion, id_indicador):
        return [
            {'name': 'Inicio', 'url': reverse('registro:home'), 'icon': 'ki-home'},
            {'name': 'Acciones', 'url': reverse('registro:lista_accion'), 'icon': None},
            {'name': 'Indicadores', 'url': reverse('registro:lista_indicador', args=[id_accion]), 'icon': None},
            {'name': 'Indicador', 'url': reverse('registro:editar_indicador', args=[id_accion, id_indicador]), 'icon': None},
            {'name': 'Comportamiento', 'url': None, 'icon': None},
        ]



# ============================================================================
# SERVICES - Aplicando Single Responsibility Principle
# ============================================================================

class StatisticsCalculatorService:
    """Servicio para cálculos estadísticos avanzados de indicadores climáticos"""

    @staticmethod
    def calculate_advanced_statistics(object_list, indicador):
        """Calcula estadísticas avanzadas para el indicador"""
        if not object_list.exists():
            return {}

        valores = [float(obj.valor) for obj in object_list]

        # Estadísticas básicas
        stats = object_list.aggregate(
            promedio=Avg('valor'),
            minimo=Min('valor'),
            maximo=Max('valor'),
            desviacion=StdDev('valor')
        )

        # Coeficiente de variación
        coef_variacion = (stats['desviacion'] / stats['promedio'] * 100) if stats['promedio'] != 0 else 0

        # Nivel de consistencia
        if coef_variacion < 10:
            consistencia_nivel = "Muy Alta"
        elif coef_variacion < 20:
            consistencia_nivel = "Alta"
        elif coef_variacion < 30:
            consistencia_nivel = "Media"
        else:
            consistencia_nivel = "Baja"

        # Velocidad de cambio mensual
        velocidad_mensual = StatisticsCalculatorService._calculate_monthly_velocity(object_list)

        # Velocidades por período (para gráfico)
        velocidades_mensuales, periodos_velocidad = StatisticsCalculatorService._calculate_period_velocities(
            object_list)

        # Análisis de efectividad climática
        efectividad = StatisticsCalculatorService._analyze_climate_effectiveness(object_list, indicador)

        # Percentiles
        percentiles = StatisticsCalculatorService._calculate_percentiles(valores)

        return {
            'promedio': stats['promedio'],
            'minimo': stats['minimo'],
            'maximo': stats['maximo'],
            'desviacion': stats['desviacion'],
            'coef_variacion': coef_variacion,
            'consistencia_nivel': consistencia_nivel,
            'velocidad_mensual': velocidad_mensual,
            'velocidades_mensuales': velocidades_mensuales,
            'periodos_velocidad': periodos_velocidad,
            'efectividad': efectividad,
            'rango': stats['maximo'] - stats['minimo'],
            **percentiles
        }

    @staticmethod
    def _calculate_monthly_velocity(object_list):
        """Calcula la velocidad promedio de cambio mensual"""
        if object_list.count() < 2:
            return 0

        resultados_ordenados = object_list.order_by('fecha')
        primer_resultado = resultados_ordenados.first()
        ultimo_resultado = resultados_ordenados.last()

        diferencia_dias = (ultimo_resultado.fecha - primer_resultado.fecha).days
        if diferencia_dias == 0:
            return 0

        diferencia_meses = diferencia_dias / 30.44  # Promedio de días por mes
        cambio_total = ultimo_resultado.valor - primer_resultado.valor

        return cambio_total / diferencia_meses if diferencia_meses > 0 else 0

    @staticmethod
    def _calculate_period_velocities(object_list):
        """Calcula velocidades de cambio por períodos específicos"""
        if object_list.count() < 3:
            return [], []

        resultados = list(object_list.order_by('fecha'))
        velocidades = []
        periodos = []

        for i in range(1, len(resultados)):
            resultado_anterior = resultados[i - 1]
            resultado_actual = resultados[i]

            dias_diferencia = (resultado_actual.fecha - resultado_anterior.fecha).days
            if dias_diferencia > 0:
                cambio = resultado_actual.valor - resultado_anterior.valor
                velocidad_diaria = cambio / dias_diferencia
                velocidad_mensual = velocidad_diaria * 30.44

                velocidades.append(round(velocidad_mensual, 2))
                periodos.append(
                    f"{resultado_anterior.fecha.strftime('%m/%y')}-{resultado_actual.fecha.strftime('%m/%y')}")

        return velocidades, periodos

    @staticmethod
    def _analyze_climate_effectiveness(object_list, indicador):
        """Analiza la efectividad específica para indicadores climáticos"""
        if object_list.count() < 2:
            return {'nivel': 'insuficiente', 'descripcion': 'Datos insuficientes'}

        primer_valor = object_list.order_by('fecha').first().valor
        ultimo_valor = object_list.order_by('fecha').last().valor

        # Calcular cambio según la dirección óptima del indicador
        if indicador.direccion_optima == 'incremento':
            cambio_efectivo = ultimo_valor - primer_valor
            mejora = cambio_efectivo > 0
        else:  # decremento
            cambio_efectivo = primer_valor - ultimo_valor
            mejora = cambio_efectivo > 0

        # Calcular porcentaje de cambio
        if primer_valor != 0:
            porcentaje_cambio = abs(cambio_efectivo / primer_valor) * 100
        else:
            porcentaje_cambio = 0

        # Determinar nivel de efectividad
        if mejora and porcentaje_cambio > 20:
            return {
                'nivel': 'alta',
                'descripcion': f'Mejora significativa del {porcentaje_cambio:.1f}%',
                'impacto_climatico': 'Alto'
            }
        elif mejora and porcentaje_cambio > 5:
            return {
                'nivel': 'media',
                'descripcion': f'Mejora moderada del {porcentaje_cambio:.1f}%',
                'impacto_climatico': 'Medio'
            }
        elif mejora:
            return {
                'nivel': 'baja',
                'descripcion': f'Mejora leve del {porcentaje_cambio:.1f}%',
                'impacto_climatico': 'Bajo'
            }
        else:
            return {
                'nivel': 'negativa',
                'descripcion': f'Empeoramiento del {porcentaje_cambio:.1f}%',
                'impacto_climatico': 'Negativo'
            }

    @staticmethod
    def _calculate_percentiles(valores):
        """Calcula percentiles útiles para análisis"""
        if len(valores) < 4:
            return {}

        return {
            'percentil_25': np.percentile(valores, 25),
            'percentil_50': np.percentile(valores, 50),  # Mediana
            'percentil_75': np.percentile(valores, 75),
            'percentil_90': np.percentile(valores, 90)
        }

    @staticmethod
    def calculate_trend_strength(object_list):
        """Calcula la fuerza de la tendencia usando correlación"""
        if object_list.count() < 3:
            return {'fuerza': 0, 'descripcion': 'Insuficientes datos'}

        # Crear series temporal
        fechas_numericas = []
        valores = []

        for i, resultado in enumerate(object_list.order_by('fecha')):
            fechas_numericas.append(i)
            valores.append(float(resultado.valor))

        # Calcular correlación de Pearson
        try:
            correlation = np.corrcoef(fechas_numericas, valores)[0, 1]
            fuerza_absoluta = abs(correlation)

            if fuerza_absoluta > 0.8:
                descripcion = "Tendencia muy fuerte"
            elif fuerza_absoluta > 0.6:
                descripcion = "Tendencia fuerte"
            elif fuerza_absoluta > 0.4:
                descripcion = "Tendencia moderada"
            elif fuerza_absoluta > 0.2:
                descripcion = "Tendencia débil"
            else:
                descripcion = "Sin tendencia clara"

            return {
                'fuerza': correlation,
                'fuerza_absoluta': fuerza_absoluta,
                'descripcion': descripcion,
                'direccion': 'ascendente' if correlation > 0 else 'descendente'
            }
        except:
            return {'fuerza': 0, 'descripcion': 'Error en cálculo'}

    @staticmethod
    def calculate_seasonal_analysis(object_list):
        """Analiza patrones estacionales si hay suficientes datos"""
        if object_list.count() < 12:
            return None

        # Agrupar por trimestre
        quarterly_data = {1: [], 2: [], 3: [], 4: []}

        for resultado in object_list:
            quarter = (resultado.fecha.month - 1) // 3 + 1
            quarterly_data[quarter].append(resultado.valor)

        # Calcular promedios trimestrales
        quarterly_averages = {}
        for quarter, values in quarterly_data.items():
            if values:
                quarterly_averages[quarter] = sum(values) / len(values)

        if len(quarterly_averages) >= 3:
            best_quarter = max(quarterly_averages, key=quarterly_averages.get)
            worst_quarter = min(quarterly_averages, key=quarterly_averages.get)

            quarter_names = {1: 'Q1 (Ene-Mar)', 2: 'Q2 (Abr-Jun)', 3: 'Q3 (Jul-Sep)', 4: 'Q4 (Oct-Dic)'}

            return {
                'mejor_trimestre': quarter_names[best_quarter],
                'peor_trimestre': quarter_names[worst_quarter],
                'promedios_trimestrales': {quarter_names[q]: avg for q, avg in quarterly_averages.items()}
            }

        return None



class VariationCalculatorService:
    """Servicio para calcular variaciones entre resultados"""

    @staticmethod
    def calculate_variations(object_list, indicador):
        """Calcula todas las variaciones entre resultados"""
        variacion = 0
        variacion_anterior_ultimo_resultado = 0
        variacion_porcentual = 0
        variacion_porcentual_resultado_anterior = 0
        interpretacion_cambio_total = 'neutral'
        interpretacion_cambio_reciente = 'neutral'

        valor_ultimos_resultados = object_list.order_by('-fecha')[:2]

        if len(object_list) >= 2:
            primer_resultado = object_list.first()
            ultimo_resultado = object_list.last()

            # Variación total
            variacion = round(ultimo_resultado.valor - primer_resultado.valor, 2)

            # Variación porcentual total
            if primer_resultado.valor != 0:
                variacion_porcentual = round(
                    ((ultimo_resultado.valor - primer_resultado.valor) /
                     abs(primer_resultado.valor)) * 100, 2
                )

            # Interpretar cambio total
            interpretacion_cambio_total = indicador.interpretar_cambio(
                primer_resultado.valor, ultimo_resultado.valor
            )

            # Variación entre últimos dos resultados
            if len(valor_ultimos_resultados) >= 2:
                resultado_actual = valor_ultimos_resultados[0]
                resultado_anterior = valor_ultimos_resultados[1]

                variacion_anterior_ultimo_resultado = round(
                    resultado_actual.valor - resultado_anterior.valor, 2
                )

                # Variación porcentual entre últimos dos resultados
                if resultado_anterior.valor != 0:
                    variacion_porcentual_resultado_anterior = round(
                        ((resultado_actual.valor - resultado_anterior.valor) /
                         abs(resultado_anterior.valor)) * 100, 2
                    )

                # Interpretar cambio reciente
                interpretacion_cambio_reciente = indicador.interpretar_cambio(
                    resultado_anterior.valor, resultado_actual.valor
                )

        return {
            'variacion': variacion,
            'variacion_porcentual': variacion_porcentual,
            'variacion_anterior_ultimo_resultado': variacion_anterior_ultimo_resultado,
            'variacion_porcentual_resultado_anterior': variacion_porcentual_resultado_anterior,
            'interpretacion_cambio_total': interpretacion_cambio_total,
            'interpretacion_cambio_reciente': interpretacion_cambio_reciente,
            'ultimo_resultado': object_list.last() if object_list else None,
            'anterior_ultimo_resultado': valor_ultimos_resultados[1] if len(valor_ultimos_resultados) >= 2 else None,
        }



class ResultadoIndicadorService:
    """Servicio para manejar lógica de negocio de resultados de indicadores"""

    def __init__(self, formula_calculator=None):
        self.formula_calculator = formula_calculator or FormulaCalculatorService()

    def save_resultado_with_calculation(self, form_resultado_indicador, formset_variables,
                                        indicador, resultado_obj):
        """Guarda el resultado y calcula el valor usando la fórmula"""
        variables_resultados = []

        # Limpiar variables anteriores si es edición
        if resultado_obj.pk:
            resultado_obj.resultadovariable_set.all().delete()

        # Guardar valores de las variables
        for form in formset_variables:
            v = ResultadoVariable()
            v.resultado = resultado_obj
            v.variable_indicador_id = form.cleaned_data['variable_indicador_id']
            v.valor = form.cleaned_data['valor']
            v.fecha = form_resultado_indicador.cleaned_data['fecha']
            v.save()
            variables_resultados.append(v)

        # Calcular resultado usando el servicio de cálculo
        result = self.formula_calculator.calculate_formula_result(
            indicador.formula, variables_resultados
        )

        # Actualizar resultado
        resultado_obj.valor = round(result, 2)
        resultado_obj.save()

        # Actualizar última medición del indicador
        indicador.ultima_medicion = form_resultado_indicador.cleaned_data['fecha']
        indicador.save()

        # Añadir al indicador si es nuevo
        if resultado_obj not in indicador.resultados.all():
            indicador.resultados.add(resultado_obj)


class FormulaCalculatorService:
    """Servicio para calcular fórmulas usando sympy"""

    @staticmethod
    def calculate_formula_result(formula_string, variables_resultados):
        """Calcula el resultado de una fórmula con variables"""
        formula = sympify(formula_string)
        symbols = [Symbol(var.variable_indicador.variable) for var in variables_resultados]
        substitutions = {
            symbol: float(var.valor)
            for var, symbol in zip(variables_resultados, symbols)
        }

        return formula.subs(substitutions)
class InsightGeneratorService:
    """Servicio para generar insights automáticos"""

    @staticmethod
    def generate_insights(object_list, statistics, variations, indicador):
        """Genera insights específicos para indicadores climáticos"""
        insights = []

        if not object_list.exists():
            return insights

        # 1. Análisis de efectividad climática
        insights.extend(InsightGeneratorService._analyze_climate_effectiveness(statistics, variations, indicador))

        # 2. Análisis de tendencias temporales
        insights.extend(InsightGeneratorService._analyze_temporal_trends(object_list, variations, indicador))

        # 3. Análisis de calidad de datos
        insights.extend(InsightGeneratorService._analyze_data_quality(statistics, object_list))

        # 4. Análisis de progreso hacia metas
        insights.extend(InsightGeneratorService._analyze_goal_progress(indicador))

        # 5. Análisis de frecuencia de medición
        insights.extend(InsightGeneratorService._analyze_measurement_frequency(object_list, indicador))

        # 6. Recomendaciones estratégicas
        insights.extend(InsightGeneratorService._generate_strategic_recommendations(
            object_list, statistics, variations, indicador
        ))

        return insights[:5]  # Limitar a 5 insights más relevantes

    @staticmethod
    def _analyze_climate_effectiveness(statistics, variations, indicador):
        """Analiza la efectividad de la acción climática"""
        insights = []
        efectividad = statistics.get('efectividad', {})

        if efectividad.get('nivel') == 'alta':
            insights.append({
                'tipo': 'efectividad_alta',
                'titulo': 'Acción Climática Altamente Efectiva',
                'descripcion': f"Impacto positivo confirmado con {efectividad.get('descripcion', '').lower()}. Considera replicar esta estrategia en otros sectores.",
                'nivel': 'excelente',
                'icono': 'ki-verify',
                'accion_recomendada': 'Expandir implementación'
            })
        elif efectividad.get('nivel') == 'negativa':
            insights.append({
                'tipo': 'efectividad_baja',
                'titulo': 'Acción Requiere Reformulación',
                'descripcion': f"Resultados sugieren impacto negativo. Revisar metodología, presupuesto y estrategia de implementación.",
                'nivel': 'critico',
                'icono': 'ki-shield-cross',
                'accion_recomendada': 'Revisar estrategia inmediatamente'
            })
        elif efectividad.get('nivel') == 'media':
            insights.append({
                'tipo': 'efectividad_media',
                'titulo': 'Potencial de Optimización',
                'descripcion': f"Efectividad moderada detectada. Analizar factores limitantes para maximizar impacto climático.",
                'nivel': 'bueno',
                'icono': 'ki-arrows-circle',
                'accion_recomendada': 'Optimizar implementación'
            })

        return insights

    @staticmethod
    def _analyze_temporal_trends(object_list, variations, indicador):
        """Analiza tendencias temporales y patrones estacionales"""
        insights = []

        # Análisis de aceleración/desaceleración
        if len(object_list) >= 3:
            ultimos_3 = list(object_list.order_by('-fecha')[:3])
            if len(ultimos_3) == 3:
                cambio_reciente = ultimos_3[0].valor - ultimos_3[1].valor
                cambio_anterior = ultimos_3[1].valor - ultimos_3[2].valor

                if indicador.direccion_optima == 'decremento':
                    cambio_reciente *= -1
                    cambio_anterior *= -1

                if cambio_reciente > cambio_anterior * 1.5:
                    insights.append({
                        'tipo': 'aceleracion',
                        'titulo': 'Aceleración Positiva Detectada',
                        'descripcion': "La mejora se está acelerando en las últimas mediciones. Mantener las estrategias actuales.",
                        'nivel': 'excelente',
                        'icono': 'ki-arrow-up-right',
                        'accion_recomendada': 'Mantener estrategia actual'
                    })
                elif cambio_reciente < cambio_anterior * 0.5:
                    insights.append({
                        'tipo': 'desaceleracion',
                        'titulo': 'Desaceleración en el Progreso',
                        'descripcion': "El ritmo de mejora está disminuyendo. Considerar refuerzo de medidas o nuevas estrategias.",
                        'nivel': 'regular',
                        'icono': 'ki-arrow-down-right',
                        'accion_recomendada': 'Reforzar medidas'
                    })

        # Análisis de estacionalidad (si hay suficientes datos)
        if len(object_list) >= 12:
            insights.extend(InsightGeneratorService._detect_seasonal_patterns(object_list))

        return insights

    @staticmethod
    def _detect_seasonal_patterns(object_list):
        """Detecta patrones estacionales en los datos"""
        insights = []

        # Agrupar por mes
        monthly_data = {}
        for result in object_list:
            month = result.fecha.month
            if month not in monthly_data:
                monthly_data[month] = []
            monthly_data[month].append(result.valor)

        # Calcular promedios mensuales
        monthly_averages = {month: sum(values) / len(values) for month, values in monthly_data.items()}

        if len(monthly_averages) >= 6:  # Al menos 6 meses de datos
            best_month = max(monthly_averages, key=monthly_averages.get)
            worst_month = min(monthly_averages, key=monthly_averages.get)

            month_names = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }

            insights.append({
                'tipo': 'estacionalidad',
                'titulo': 'Patrón Estacional Identificado',
                'descripcion': f"Mejor rendimiento en {month_names[best_month]}, menor en {month_names[worst_month]}. Planificar intervenciones según estacionalidad.",
                'nivel': 'bueno',
                'icono': 'ki-calendar',
                'accion_recomendada': 'Ajustar calendario de acciones'
            })

        return insights

    @staticmethod
    def _analyze_data_quality(statistics, object_list):
        """Analiza la calidad y consistencia de los datos"""
        insights = []
        coef_var = statistics.get('coef_variacion', 0)

        if coef_var < 10:
            insights.append({
                'tipo': 'calidad_excelente',
                'titulo': 'Datos de Alta Calidad',
                'descripcion': f"Variabilidad muy baja ({coef_var:.1f}%). Proceso de monitoreo robusto y confiable.",
                'nivel': 'excelente',
                'icono': 'ki-verify',
                'accion_recomendada': 'Mantener protocolo actual'
            })
        elif coef_var > 30:
            insights.append({
                'tipo': 'calidad_mejorable',
                'titulo': 'Revisar Protocolo de Medición',
                'descripcion': f"Alta variabilidad ({coef_var:.1f}%) sugiere inconsistencias. Estandarizar métodos de medición.",
                'nivel': 'regular',
                'icono': 'ki-information',
                'accion_recomendada': 'Mejorar protocolo de medición'
            })

        # Análisis de frecuencia de mediciones
        if len(object_list) >= 2:
            fechas = [r.fecha for r in object_list.order_by('fecha')]
            intervalos = [(fechas[i] - fechas[i - 1]).days for i in range(1, len(fechas))]
            promedio_intervalo = sum(intervalos) / len(intervalos)

            if promedio_intervalo > 90:  # Más de 3 meses entre mediciones
                insights.append({
                    'tipo': 'frecuencia_baja',
                    'titulo': 'Aumentar Frecuencia de Monitoreo',
                    'descripcion': f"Intervalos promedio de {promedio_intervalo:.0f} días. Mayor frecuencia mejoraría detección temprana de cambios.",
                    'nivel': 'regular',
                    'icono': 'ki-timer',
                    'accion_recomendada': 'Incrementar frecuencia de medición'
                })

        return insights

    @staticmethod
    def _analyze_goal_progress(indicador):
        """Analiza el progreso hacia las metas climáticas"""
        insights = []
        progreso_meta = indicador.calcular_progreso_meta()

        if progreso_meta:
            progreso_pct = progreso_meta['progreso_porcentaje']

            if progreso_meta['meta_alcanzada']:
                insights.append({
                    'tipo': 'meta_alcanzada',
                    'titulo': '🎯 Meta Climática Superada',
                    'descripcion': f"Meta alcanzada exitosamente ({progreso_pct:.1f}%). Considerar establecer objetivos más ambiciosos para 2030.",
                    'nivel': 'excelente',
                    'icono': 'ki-crown',
                    'accion_recomendada': 'Establecer nueva meta más ambiciosa'
                })
            elif progreso_pct > 80:
                dias_restantes = (
                            indicador.meta_fecha_limite - timezone.now().date()).days if indicador.meta_fecha_limite else None
                tiempo_msg = f" en {dias_restantes} días" if dias_restantes and dias_restantes > 0 else ""

                insights.append({
                    'tipo': 'meta_cerca',
                    'titulo': 'Meta Climática al Alcance',
                    'descripcion': f"Progreso del {progreso_pct:.1f}%. Mantener esfuerzos actuales para alcanzar meta{tiempo_msg}.",
                    'nivel': 'excelente',
                    'icono': 'ki-medal-star',
                    'accion_recomendada': 'Mantener intensidad actual'
                })
            elif progreso_pct < 30 and indicador.meta_fecha_limite:
                dias_restantes = (indicador.meta_fecha_limite - timezone.now().date()).days
                if dias_restantes < 180:  # Menos de 6 meses
                    insights.append({
                        'tipo': 'meta_riesgo',
                        'titulo': 'Riesgo de Incumplimiento de Meta',
                        'descripcion': f"Solo {progreso_pct:.1f}% de progreso con {dias_restantes} días restantes. Intensificar acciones urgentemente.",
                        'nivel': 'critico',
                        'icono': 'ki-shield-cross',
                        'accion_recomendada': 'Intensificar acciones inmediatamente'
                    })

        return insights

    @staticmethod
    def _analyze_measurement_frequency(object_list, indicador):
        """Analiza la frecuencia y puntualidad de las mediciones"""
        insights = []

        if not indicador.frecuencia_medicion:
            return insights

        # Verificar si las mediciones están al día
        proxima_medicion = indicador.calcular_proxima_medicion()
        if proxima_medicion:
            dias_desde_ultima = (timezone.now() - object_list.last().fecha).days

            if dias_desde_ultima > 30:  # Más de un mes sin medir
                insights.append({
                    'tipo': 'medicion_atrasada',
                    'titulo': 'Medición Pendiente',
                    'descripcion': f"Han pasado {dias_desde_ultima} días desde la última medición. El monitoreo continuo es crucial para la acción climática.",
                    'nivel': 'regular',
                    'icono': 'ki-calendar-tick',
                    'accion_recomendada': 'Programar medición inmediata'
                })

        return insights

    @staticmethod
    def _generate_strategic_recommendations(object_list, statistics, variations, indicador):
        """Genera recomendaciones estratégicas basadas en el análisis completo"""
        insights = []

        # Recomendación basada en velocidad de cambio
        velocidad = statistics.get('velocidad_mensual', 0)
        if abs(velocidad) > 5:  # Cambio rápido
            direccion = "positiva" if velocidad > 0 else "negativa"
            insights.append({
                'tipo': 'velocidad_cambio',
                'titulo': f'Cambio Acelerado {direccion.title()}',
                'descripcion': f"Velocidad de {abs(velocidad):.1f} unidades/mes. {'Capitalizar momentum' if velocidad > 0 else 'Intervenir para corregir rumbo'}.",
                'nivel': 'excelente' if velocidad > 0 else 'regular',
                'icono': 'ki-rocket' if velocidad > 0 else 'ki-arrows-circle',
                'accion_recomendada': 'Capitalizar momentum' if velocidad > 0 else 'Corregir estrategia'
            })

        # Análisis de volatilidad para planificación
        if statistics.get('coef_variacion', 0) > 25:
            insights.append({
                'tipo': 'alta_volatilidad',
                'titulo': 'Indicador con Alta Volatilidad',
                'descripcion': "Resultados variables sugieren factores externos influyentes. Identificar y controlar variables de confusión.",
                'nivel': 'regular',
                'icono': 'ki-chart-line-up',
                'accion_recomendada': 'Análisis de factores externos'
            })

        # Recomendación de benchmark
        if len(object_list) >= 6:
            valor_actual = object_list.last().valor
            percentil_75 = statistics.get('percentil_75', valor_actual)

            if valor_actual < percentil_75 * 0.8:  # Por debajo del 80% del percentil 75
                insights.append({
                    'tipo': 'benchmark',
                    'titulo': 'Oportunidad de Mejora Identificada',
                    'descripcion': f"Rendimiento actual por debajo del potencial histórico. Revisar mejores prácticas de períodos exitosos.",
                    'nivel': 'bueno',
                    'icono': 'ki-chart-simple',
                    'accion_recomendada': 'Analizar períodos de mejor rendimiento'
                })

        return insights

    @staticmethod
    def generate_executive_summary(object_list, statistics, variations, indicador):
        """Genera un resumen ejecutivo para tomadores de decisiones"""
        if not object_list.exists():
            return None

        ultimo_valor = object_list.last().valor
        variacion_total = variations.get('variacion_porcentual', 0)
        efectividad = statistics.get('efectividad', {}).get('nivel', 'desconocida')

        # Determinar estado general
        if efectividad == 'alta' and variacion_total > 10:
            estado = "EXCELENTE"
            color = "success"
            recomendacion = "Mantener y escalar estrategia actual"
        elif efectividad == 'media' or (efectividad == 'alta' and abs(variacion_total) < 10):
            estado = "BUENO"
            color = "primary"
            recomendacion = "Optimizar para maximizar impacto"
        elif efectividad == 'baja' or variacion_total < -10:
            estado = "REQUIERE ATENCIÓN"
            color = "warning"
            recomendacion = "Revisar y reformular estrategia"
        else:
            estado = "CRÍTICO"
            color = "danger"
            recomendacion = "Intervención urgente necesaria"

        return {
            'estado_general': estado,
            'color': color,
            'valor_actual': ultimo_valor,
            'variacion_total': variacion_total,
            'efectividad': efectividad,
            'recomendacion_principal': recomendacion,
            'fecha_ultima_medicion': object_list.last().fecha,
            'total_mediciones': object_list.count()
        }

    @staticmethod
    def generate_climate_impact_score(object_list, statistics, variations, indicador):
        """Calcula un score de impacto climático (0-100)"""
        if not object_list.exists():
            return 0

        score = 0

        # Componente de efectividad (40% del score)
        efectividad = statistics.get('efectividad', {}).get('nivel', 'baja')
        if efectividad == 'alta':
            score += 40
        elif efectividad == 'media':
            score += 25
        elif efectividad == 'baja':
            score += 10

        # Componente de tendencia (30% del score)
        if variations.get('interpretacion_cambio_total') == 'positivo':
            score += 30
        elif variations.get('interpretacion_cambio_reciente') == 'positivo':
            score += 15

        # Componente de consistencia (20% del score)
        coef_var = statistics.get('coef_variacion', 100)
        if coef_var < 15:
            score += 20
        elif coef_var < 30:
            score += 10

        # Componente de progreso hacia meta (10% del score)
        progreso_meta = indicador.calcular_progreso_meta()
        if progreso_meta:
            if progreso_meta['meta_alcanzada']:
                score += 10
            elif progreso_meta['progreso_porcentaje'] > 70:
                score += 7
            elif progreso_meta['progreso_porcentaje'] > 40:
                score += 5

        return min(100, max(0, score))


class ChartDataService:
    """Servicio para preparar datos de gráficos"""

    @staticmethod
    def prepare_chart_data(object_list, indicador):
        """Prepara los datos para el gráfico de línea"""
        data_line = {
            'valores': {
                'name': 'Valor',
                'data': []
            },
            'labels': []
        }

        for result in object_list:
            data_line['valores']['data'].append(round(result.valor, 2))
            data_line['labels'].append(result.fecha.strftime("%d-%m-%Y"))

        # Asumiendo que data_chart_line es una función externa
        return data_chart_line(data_line, indicador)


class RankingCalculatorService:
    """Servicio para calcular ranking de indicadores"""

    @staticmethod
    def calculate_ranking(indicador_actual, todos_indicadores):
        """Calcula el ranking del indicador actual entre todos los indicadores"""
        if not todos_indicadores.exists():
            return None

        # Calcular scores para todos los indicadores
        indicadores_con_scores = []

        for indicador in todos_indicadores:
            resultados = indicador.resultados.all().order_by('fecha')
            if not resultados.exists():
                continue

            # Calcular score basado en varios factores
            score = RankingCalculatorService._calculate_indicator_score(indicador, resultados)
            indicadores_con_scores.append({
                'indicador': indicador,
                'score': score,
                'ultimo_valor': resultados.last().valor if resultados else 0
            })

        # Ordenar por score (de mayor a menor)
        indicadores_con_scores.sort(key=lambda x: x['score'], reverse=True)

        # Encontrar posición del indicador actual
        posicion = next((i + 1 for i, item in enumerate(indicadores_con_scores)
                         if item['indicador'].id == indicador_actual.id), None)

        if posicion is None:
            return None

        # Calcular percentil
        total_indicadores = len(indicadores_con_scores)
        percentil = ((total_indicadores - posicion) / total_indicadores) * 100

        # Obtener estadísticas del ranking
        scores = [item['score'] for item in indicadores_con_scores]
        score_promedio = sum(scores) / len(scores) if scores else 0
        mejor_score = max(scores) if scores else 0
        score_actual = next((item['score'] for item in indicadores_con_scores
                             if item['indicador'].id == indicador_actual.id), 0)

        # Determinar nivel de desempeño
        nivel_desempeño = RankingCalculatorService._get_performance_level(percentil)

        return {
            'posicion': posicion,
            'total_indicadores': total_indicadores,
            'percentil': round(percentil, 1),
            'score_actual': round(score_actual, 1),
            'score_promedio': round(score_promedio, 1),
            'mejor_score': round(mejor_score, 1),
            'nivel_desempeño': nivel_desempeño
        }

    @staticmethod
    def _calculate_indicator_score(indicador, resultados):
        """Calcula un score compuesto para el indicador"""
        if not resultados:
            return 0

        # 1. Progreso hacia meta (30%)
        progreso_meta = indicador.calcular_progreso_meta() or {}
        score_meta = progreso_meta.get('progreso_porcentaje', 0) * 0.3 if progreso_meta else 0

        # 2. Consistencia de mediciones (25%)
        valores = [r.valor for r in resultados]
        if len(valores) > 1:
            promedio = sum(valores) / len(valores)
            desviacion = (sum((v - promedio) ** 2 for v in valores) / len(valores)) ** 0.5
            coef_variacion = (desviacion / promedio * 100) if promedio != 0 else 0
            score_consistencia = max(0, 100 - coef_variacion) * 0.25
        else:
            score_consistencia = 50 * 0.25  # Valor por defecto si hay pocas mediciones

        # 3. Tendencia reciente (25%)
        if len(valores) >= 2:
            ultimo_valor = valores[-1]
            anterior_valor = valores[-2]
            if indicador.direccion_optima == 'incremento':
                tendencia = 100 if ultimo_valor > anterior_valor else 0
            else:
                tendencia = 100 if ultimo_valor < anterior_valor else 0
            score_tendencia = tendencia * 0.25
        else:
            score_tendencia = 50 * 0.25

        # 4. Frecuencia de medición (20%)
        # Verificar si se están siguiendo las frecuencias establecidas
        if indicador.frecuencia_medicion:
            # Simplificado - en una implementación real se verificarían las fechas
            score_frecuencia = 80 * 0.2  # Valor por defecto
        else:
            score_frecuencia = 50 * 0.2

        return score_meta + score_consistencia + score_tendencia + score_frecuencia

    @staticmethod
    def _get_performance_level(percentil):
        """Determina el nivel de desempeño basado en el percentil"""
        if percentil >= 90:
            return {'nivel': 'excelente', 'descripcion': 'Top 10%', 'color': 'success'}
        elif percentil >= 75:
            return {'nivel': 'muy-bueno', 'descripcion': 'Top 25%', 'color': 'primary'}
        elif percentil >= 50:
            return {'nivel': 'bueno', 'descripcion': 'Top 50%', 'color': 'info'}
        elif percentil >= 25:
            return {'nivel': 'regular', 'descripcion': 'Necesita mejora', 'color': 'warning'}
        else:
            return {'nivel': 'bajo', 'descripcion': 'Requiere atención', 'color': 'danger'}


class MetaProgressService:
    """Servicio para calcular progreso hacia metas climáticas"""

    @staticmethod
    def calculate_detailed_progress(indicador):
        """Calcula progreso detallado hacia la meta"""
        progreso_basico = indicador.calcular_progreso_meta()
        if not progreso_basico:
            return None

        ultimo_resultado = indicador.resultados.order_by('-fecha').first()
        if not ultimo_resultado:
            return None

        # Cálculos adicionales
        valor_actual = ultimo_resultado.valor
        meta_valor = progreso_basico['meta_valor']
        baseline = progreso_basico['baseline']

        # Distancia a la meta
        if indicador.direccion_optima == 'incremento':
            distancia_meta = max(0, meta_valor - valor_actual)
            porcentaje_faltante = (distancia_meta / meta_valor) * 100 if meta_valor != 0 else 0
        else:
            distancia_meta = max(0, valor_actual - meta_valor)
            porcentaje_faltante = (distancia_meta / baseline) * 100 if baseline != 0 else 0

        # Estimación de tiempo para alcanzar meta
        tiempo_estimado = MetaProgressService._estimate_time_to_goal(indicador, valor_actual, meta_valor)

        # Nivel de riesgo de no cumplimiento
        riesgo = MetaProgressService._assess_risk_level(indicador, progreso_basico['progreso_porcentaje'],
                                                        tiempo_estimado)

        return {
            **progreso_basico,
            'distancia_meta': round(distancia_meta, 2),
            'porcentaje_faltante': round(porcentaje_faltante, 2),
            'tiempo_estimado': tiempo_estimado,
            'nivel_riesgo': riesgo,
            'unidad_medida': indicador.unidad_medida.nombre if indicador.unidad_medida else '',
            'direccion': indicador.get_direccion_optima_display()
        }

    @staticmethod
    def _estimate_time_to_goal(indicador, valor_actual, meta_valor):
        """Estima tiempo para alcanzar la meta basado en tendencia actual"""
        resultados = indicador.resultados.order_by('fecha')

        if resultados.count() < 3:
            return None

        # Calcular velocidad promedio mensual de los últimos 3 resultados
        ultimos_3 = list(resultados.order_by('-fecha')[:3])

        diferencias_temporales = []
        cambios = []

        for i in range(len(ultimos_3) - 1):
            fecha_actual = ultimos_3[i].fecha
            fecha_anterior = ultimos_3[i + 1].fecha
            dias_diff = (fecha_actual - fecha_anterior).days

            if dias_diff > 0:
                cambio = ultimos_3[i].valor - ultimos_3[i + 1].valor
                cambio_mensual = (cambio / dias_diff) * 30
                cambios.append(cambio_mensual)

        if not cambios:
            return None

        velocidad_promedio_mensual = sum(cambios) / len(cambios)

        if velocidad_promedio_mensual == 0:
            return None

        # Calcular meses necesarios
        if indicador.direccion_optima == 'incremento':
            diferencia_necesaria = meta_valor - valor_actual
            if velocidad_promedio_mensual <= 0:
                return None  # Tendencia contraria
        else:
            diferencia_necesaria = valor_actual - meta_valor
            if velocidad_promedio_mensual >= 0:
                return None  # Tendencia contraria
            velocidad_promedio_mensual = abs(velocidad_promedio_mensual)

        if diferencia_necesaria <= 0:
            return {'meses': 0, 'descripcion': 'Meta ya alcanzada'}

        meses_estimados = diferencia_necesaria / velocidad_promedio_mensual

        return {
            'meses': round(meses_estimados, 1),
            'descripcion': f'Aproximadamente {round(meses_estimados)} meses al ritmo actual'
        }

    @staticmethod
    def _assess_risk_level(indicador, progreso_porcentaje, tiempo_estimado):
        """Evalúa el nivel de riesgo de no cumplir la meta"""
        if not indicador.meta_fecha_limite:
            return {'nivel': 'sin_limite', 'descripcion': 'Sin fecha límite definida'}

        from datetime import date
        dias_restantes = (indicador.meta_fecha_limite - date.today()).days
        meses_restantes = dias_restantes / 30

        if progreso_porcentaje >= 100:
            return {'nivel': 'cumplida', 'descripcion': 'Meta ya cumplida', 'color': 'success'}

        if tiempo_estimado and tiempo_estimado.get('meses'):
            meses_necesarios = tiempo_estimado['meses']

            if meses_necesarios <= meses_restantes * 0.8:  # 80% del tiempo disponible
                return {'nivel': 'bajo', 'descripcion': 'Buen ritmo para cumplir meta', 'color': 'success'}
            elif meses_necesarios <= meses_restantes:
                return {'nivel': 'medio', 'descripcion': 'Ritmo justo para cumplir meta', 'color': 'warning'}
            else:
                return {'nivel': 'alto', 'descripcion': 'Riesgo de no cumplir meta', 'color': 'danger'}

        # Si no se puede estimar tiempo, usar solo progreso
        if progreso_porcentaje >= 75:
            return {'nivel': 'bajo', 'descripcion': 'Progreso satisfactorio', 'color': 'success'}
        elif progreso_porcentaje >= 50:
            return {'nivel': 'medio', 'descripcion': 'Progreso moderado', 'color': 'warning'}
        else:
            return {'nivel': 'alto', 'descripcion': 'Progreso insuficiente', 'color': 'danger'}


class ClimateInsightAnalyzer:
    """Analizador especializado para insights climáticos específicos"""

    @staticmethod
    def analyze_emission_reduction_effectiveness(object_list, indicador):
        """Análisis específico para indicadores de reducción de emisiones"""
        if 'emision' not in indicador.nombre.lower() and 'co2' not in indicador.nombre.lower():
            return []

        insights = []
        if len(object_list) >= 2:
            total_reduction = object_list.first().valor - object_list.last().valor
            if total_reduction > 0:
                insights.append({
                    'tipo': 'reduccion_emisiones',
                    'titulo': 'Reducción de Emisiones Confirmada',
                    'descripcion': f"Reducción total de {total_reduction:.2f} {indicador.unidad_medida.nombre}. Contribución positiva al objetivo climático nacional.",
                    'nivel': 'excelente',
                    'icono': 'ki-abstract-14'
                })

        return insights

    @staticmethod
    def analyze_adaptation_resilience(object_list, indicador):
        """Análisis específico para indicadores de adaptación"""
        if 'adaptacion' not in indicador.nombre.lower() and 'resiliencia' not in indicador.nombre.lower():
            return []

        insights = []
        # Lógica específica para indicadores de adaptación
        # ...

        return insights