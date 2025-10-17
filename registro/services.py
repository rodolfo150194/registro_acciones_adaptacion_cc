import base64
import statistics
import matplotlib
matplotlib.use('Agg')
from datetime import timedelta, datetime
from io import BytesIO
from typing import List, Dict, Any, Optional

import numpy as np
from django.db.models import Avg, Min, Max, StdDev
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from matplotlib import pyplot as plt
from sympy import sympify, Symbol, stats
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from nomencladores.models import TipoMoneda, CategoriaPresupuesto
from registro.models import ResultadoVariable, Accion
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
        # try:
        formula = sympify(formula_string)
        symbols = [Symbol(var.variable_indicador.variable) for var in variables_resultados]
        substitutions = {
            symbol: float(var.valor)
            for var, symbol in zip(variables_resultados, symbols)
        }
        # except ZeroDivisionError:
        #     return 0
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

        # 2. Análisis de dirección óptima (NUEVO)
        insights.extend(InsightGeneratorService._analyze_direction_effectiveness(object_list, indicador))

        # 3. Análisis de tendencias temporales
        insights.extend(InsightGeneratorService._analyze_temporal_trends(object_list, variations, indicador))

        # 4. Análisis de calidad de datos
        insights.extend(InsightGeneratorService._analyze_data_quality(statistics, object_list))

        # 5. Análisis de progreso hacia metas (MEJORADO)
        insights.extend(InsightGeneratorService._analyze_goal_progress(indicador))

        # 6. Análisis de frecuencia de medición
        insights.extend(InsightGeneratorService._analyze_measurement_frequency(object_list, indicador))

        # 7. Recomendaciones estratégicas
        insights.extend(InsightGeneratorService._generate_strategic_recommendations(
            object_list, statistics, variations, indicador
        ))

        # Priorizar insights críticos primero
        insights.sort(key=lambda x: {'critico': 0, 'regular': 1, 'bueno': 2, 'excelente': 3}.get(x['nivel'], 4))

        return insights[:6] # Limitar a 6 insights más relevantes

    @staticmethod
    def _analyze_climate_effectiveness(statistics, variations, indicador):
        """Analiza la efectividad de la acción climática CONSIDERANDO LA META"""
        insights = []
        efectividad = statistics.get('efectividad', {})

        # CRÍTICO: Obtener el progreso de la meta antes de evaluar efectividad
        progreso_meta = indicador.calcular_progreso_meta()
        tiene_meta = progreso_meta is not None
        progreso_pct = progreso_meta.get('progreso_porcentaje', 0) if tiene_meta else 0

        # Caso 1: Alta efectividad
        if efectividad.get('nivel') == 'alta':
            # SUB-CASO 1A: Efectivo Y con buen progreso hacia meta (>60%)
            if tiene_meta and progreso_pct > 60:
                insights.append({
                    'tipo': 'efectividad_alta',
                    'titulo': 'Acción Climática Altamente Efectiva',
                    'descripcion': f"Impacto positivo confirmado con {efectividad.get('descripcion', '').lower()} y {progreso_pct:.1f}% de progreso hacia la meta. Estrategia efectiva y bien encaminada para cumplir objetivos.",
                    'nivel': 'excelente',
                    'icono': 'ki-verify',
                    'accion_recomendada': 'Mantener estrategia y considerar replicar en otros sectores'
                })
            # SUB-CASO 1B: Efectivo PERO con bajo progreso hacia meta (<=60%)
            elif tiene_meta and progreso_pct <= 60:
                insights.append({
                    'tipo': 'efectividad_insuficiente_para_meta',
                    'titulo': 'Mejora Positiva pero Insuficiente para Meta',
                    'descripcion': f"Se observa {efectividad.get('descripcion', '').lower()}, sin embargo el progreso hacia la meta es solo {progreso_pct:.1f}%. La estrategia funciona pero necesita INTENSIFICARSE para alcanzar el objetivo.",
                    'nivel': 'regular',
                    'icono': 'ki-arrow-up',
                    'accion_recomendada': 'Intensificar implementación - aumentar recursos, frecuencia o escala'
                })
            # SUB-CASO 1C: Efectivo sin meta definida
            else:
                insights.append({
                    'tipo': 'efectividad_alta_sin_meta',
                    'titulo': 'Mejora Significativa Detectada',
                    'descripcion': f"Impacto positivo confirmado con {efectividad.get('descripcion', '').lower()}. Considera establecer una meta específica para medir el éxito completo.",
                    'nivel': 'excelente',
                    'icono': 'ki-verify',
                    'accion_recomendada': 'Establecer meta cuantificable'
                })

        # Caso 2: Efectividad negativa
        elif efectividad.get('nivel') == 'negativa':
            insights.append({
                'tipo': 'efectividad_baja',
                'titulo': 'Acción Requiere Reformulación Urgente',
                'descripcion': f"Resultados muestran {efectividad.get('descripcion', '').lower()}. El indicador se mueve en dirección contraria a la deseada. Revisar metodología, presupuesto y estrategia de implementación.",
                'nivel': 'critico',
                'icono': 'ki-shield-cross',
                'accion_recomendada': 'URGENTE: Suspender y revisar estrategia completa'
            })

        # Caso 3: Efectividad media
        elif efectividad.get('nivel') == 'media':
            # SUB-CASO 3A: Media pero con buen progreso
            if tiene_meta and progreso_pct > 70:
                insights.append({
                    'tipo': 'efectividad_media_progreso_bueno',
                    'titulo': 'Progreso Sostenido hacia Meta',
                    'descripcion': f"Efectividad moderada ({efectividad.get('descripcion', '').lower()}) pero con {progreso_pct:.1f}% de progreso. Mantener estrategia actual.",
                    'nivel': 'bueno',
                    'icono': 'ki-check',
                    'accion_recomendada': 'Mantener curso actual'
                })
            # SUB-CASO 3B: Media con bajo progreso
            else:
                insights.append({
                    'tipo': 'efectividad_media',
                    'titulo': 'Potencial de Optimización',
                    'descripcion': f"Efectividad moderada detectada. Analizar factores limitantes para maximizar impacto climático y acelerar progreso.",
                    'nivel': 'regular',
                    'icono': 'ki-arrows-circle',
                    'accion_recomendada': 'Optimizar implementación y aumentar intensidad'
                })

        return insights

    @staticmethod
    def _analyze_direction_effectiveness(object_list, indicador):
        """Analiza si el indicador se está moviendo en la dirección correcta"""
        insights = []

        if len(object_list) < 2:
            return insights

        ultimo = object_list.order_by('-fecha').first()
        penultimo = object_list.order_by('-fecha')[1] if len(object_list) > 1 else None

        if not penultimo:
            return insights

        cambio = ultimo.valor - penultimo.valor
        direccion_actual = 'incremento' if cambio > 0 else 'decremento'

        # Verificar si va en la dirección correcta
        if direccion_actual != indicador.direccion_optima:
            # Calcular cuántos de los últimos resultados van en dirección incorrecta
            ultimos_5 = list(object_list.order_by('-fecha')[:5])
            direccion_incorrecta_count = 0

            for i in range(len(ultimos_5) - 1):
                cambio_i = ultimos_5[i].valor - ultimos_5[i + 1].valor
                dir_i = 'incremento' if cambio_i > 0 else 'decremento'
                if dir_i != indicador.direccion_optima:
                    direccion_incorrecta_count += 1

            if direccion_incorrecta_count >= 3:
                insights.append({
                    'tipo': 'direccion_incorrecta',
                    'titulo': 'Movimiento en Dirección No Deseada',
                    'descripcion': f"El indicador se está moviendo hacia el {direccion_actual}, pero la dirección óptima es {indicador.get_direccion_optima_display()}. Las últimas {direccion_incorrecta_count} de 4 mediciones muestran esta tendencia negativa.",
                    'nivel': 'critico',
                    'icono': 'ki-arrow-circle',
                    'accion_recomendada': 'URGENTE: Revisar y ajustar estrategia de implementación',
                    'datos_adicionales': {
                        'direccion_actual': direccion_actual,
                        'direccion_optima': indicador.direccion_optima,
                        'mediciones_incorrectas': direccion_incorrecta_count
                    }
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
        """Analiza el progreso hacia las metas climáticas con mayor detalle"""
        insights = []
        progreso_meta = indicador.calcular_progreso_meta()

        if not progreso_meta or not indicador.meta_fecha_limite:
            return insights

        progreso_pct = progreso_meta['progreso_porcentaje']
        meta_alcanzada = progreso_meta['meta_alcanzada']
        dias_restantes = (indicador.meta_fecha_limite - timezone.now().date()).days

        # Obtener acción si existe
        accion = getattr(indicador, 'accion', None)
        dias_totales = (indicador.meta_fecha_limite - accion.fecha_inicio).days if accion else None

        # Calcular porcentaje de tiempo transcurrido
        if dias_totales and dias_totales > 0:
            dias_transcurridos = dias_totales - dias_restantes
            pct_tiempo = (dias_transcurridos / dias_totales) * 100
        else:
            pct_tiempo = 0

        # Determinar dirección del indicador para mensajes personalizados
        dir_texto = "reducción" if indicador.direccion_optima == 'decremento' else "incremento"

        # === CASO 1: Meta ya alcanzada ===
        if meta_alcanzada:
            insights.append({
                'tipo': 'meta_alcanzada',
                'titulo': 'Meta Climática Superada',
                'descripcion': f"¡Excelente! Meta de {dir_texto} alcanzada con {progreso_pct:.1f}% de cumplimiento y {dias_restantes} días de anticipación. Considerar establecer objetivos más ambiciosos alineados con NDC 2030.",
                'nivel': 'excelente',
                'icono': 'ki-crown',
                'accion_recomendada': 'Establecer nueva meta más ambiciosa',
                'datos_adicionales': {
                    'dias_anticipacion': dias_restantes,
                    'fecha_meta': indicador.meta_fecha_limite.strftime('%d/%m/%Y'),
                    'direccion': indicador.get_direccion_optima_display()
                }
            })
            return insights

        # === CASO 2: Progreso excelente (>80%) ===
        if progreso_pct > 80:
            tiempo_msg = f" en {dias_restantes} días" if dias_restantes > 0 else ""
            insights.append({
                'tipo': 'meta_cerca',
                'titulo': 'Meta Climática al Alcance',
                'descripcion': f"Progreso destacado del {progreso_pct:.1f}% hacia la meta de {dir_texto}. Mantener esfuerzos actuales para alcanzar meta{tiempo_msg}. Fecha límite: {indicador.meta_fecha_limite.strftime('%d/%m/%Y')}.",
                'nivel': 'excelente',
                'icono': 'ki-medal-star',
                'accion_recomendada': 'Mantener intensidad actual',
                'datos_adicionales': {
                    'progreso': progreso_pct,
                    'dias_restantes': dias_restantes,
                    'fecha_meta': indicador.meta_fecha_limite.strftime('%d/%m/%Y'),
                    'direccion': indicador.get_direccion_optima_display()
                }
            })

        # === CASO 3: Progreso moderado (50-80%) ===
        elif 50 <= progreso_pct <= 80:
            # Comparar progreso vs tiempo
            if pct_tiempo > 0:
                diferencia = progreso_pct - pct_tiempo
                if diferencia > 10:
                    estado = "adelante del cronograma"
                    nivel = "excelente"
                elif diferencia < -10:
                    estado = "retrasado respecto al cronograma"
                    nivel = "regular"
                else:
                    estado = "en línea con el cronograma"
                    nivel = "bueno"
            else:
                estado = "avanzando"
                nivel = "bueno"

            insights.append({
                'tipo': 'meta_progreso_moderado',
                'titulo': f'Progreso Moderado hacia Meta de {dir_texto.title()}',
                'descripcion': f"Progreso del {progreso_pct:.1f}% ({estado}). Quedan {dias_restantes} días hasta {indicador.meta_fecha_limite.strftime('%d/%m/%Y')}. Tiempo transcurrido: {pct_tiempo:.1f}% del plazo total.",
                'nivel': nivel,
                'icono': 'ki-timer',
                'accion_recomendada': 'Mantener monitoreo y evaluar aceleración si es necesario',
                'datos_adicionales': {
                    'progreso': progreso_pct,
                    'tiempo_transcurrido': pct_tiempo,
                    'diferencia': progreso_pct - pct_tiempo if pct_tiempo > 0 else None,
                    'dias_restantes': dias_restantes,
                    'fecha_meta': indicador.meta_fecha_limite.strftime('%d/%m/%Y'),
                    'direccion': indicador.get_direccion_optima_display()
                }
            })

        # === CASO 4: Progreso bajo (30-50%) ===
        elif 30 <= progreso_pct < 50:
            if dias_restantes < 365:  # Menos de 1 año
                urgencia = "alta"
                nivel = "regular"
                accion = "Acelerar implementación de medidas"
            else:
                urgencia = "moderada"
                nivel = "regular"
                accion = "Reforzar estrategias actuales"

            insights.append({
                'tipo': 'meta_progreso_bajo',
                'titulo': f'Progreso Insuficiente en {dir_texto.title()}',
                'descripcion': f"Progreso del {progreso_pct:.1f}% con {dias_restantes} días restantes hasta {indicador.meta_fecha_limite.strftime('%d/%m/%Y')}. Urgencia {urgencia}. Se requiere acelerar el ritmo de {dir_texto} para cumplir la meta.",
                'nivel': nivel,
                'icono': 'ki-information-3',
                'accion_recomendada': accion,
                'datos_adicionales': {
                    'progreso': progreso_pct,
                    'dias_restantes': dias_restantes,
                    'urgencia': urgencia,
                    'fecha_meta': indicador.meta_fecha_limite.strftime('%d/%m/%Y'),
                    'direccion': indicador.get_direccion_optima_display()
                }
            })

        # === CASO 5: Progreso crítico (<30%) ===
        else:  # progreso_pct < 30
            if dias_restantes < 180:  # Menos de 6 meses
                insights.append({
                    'tipo': 'meta_riesgo_alto',
                    'titulo': 'Riesgo Alto de Incumplimiento de Meta',
                    'descripcion': f"CRÍTICO: Solo {progreso_pct:.1f}% de progreso en {dir_texto} con {dias_restantes} días restantes (meta: {indicador.meta_fecha_limite.strftime('%d/%m/%Y')}). Se requiere intervención inmediata y replanteo estratégico.",
                    'nivel': 'critico',
                    'icono': 'ki-shield-cross',
                    'accion_recomendada': 'ACCIÓN URGENTE: Convocar comité de crisis y revisar estrategia',
                    'datos_adicionales': {
                        'progreso': progreso_pct,
                        'dias_restantes': dias_restantes,
                        'brecha': 100 - progreso_pct,
                        'fecha_meta': indicador.meta_fecha_limite.strftime('%d/%m/%Y'),
                        'direccion': indicador.get_direccion_optima_display()
                    }
                })
            elif dias_restantes < 365:  # Menos de 1 año
                insights.append({
                    'tipo': 'meta_riesgo_medio',
                    'titulo': 'Riesgo de Incumplimiento de Meta',
                    'descripcion': f"Progreso del {progreso_pct:.1f}% en {dir_texto} con {dias_restantes} días hasta {indicador.meta_fecha_limite.strftime('%d/%m/%Y')}. Intensificar acciones urgentemente para evitar incumplimiento.",
                    'nivel': 'critico',
                    'icono': 'ki-shield-tick',
                    'accion_recomendada': 'Intensificar acciones y aumentar recursos',
                    'datos_adicionales': {
                        'progreso': progreso_pct,
                        'dias_restantes': dias_restantes,
                        'brecha': 100 - progreso_pct,
                        'fecha_meta': indicador.meta_fecha_limite.strftime('%d/%m/%Y'),
                        'direccion': indicador.get_direccion_optima_display()
                    }
                })
            else:  # Más de 1 año
                insights.append({
                    'tipo': 'meta_atencion',
                    'titulo': 'Progreso Requiere Atención',
                    'descripcion': f"Progreso del {progreso_pct:.1f}% en {dir_texto}. Aunque quedan {dias_restantes} días hasta {indicador.meta_fecha_limite.strftime('%d/%m/%Y')}, el ritmo actual puede no ser suficiente. Evaluar estrategia.",
                    'nivel': 'regular',
                    'icono': 'ki-information-2',
                    'accion_recomendada': 'Evaluar y ajustar estrategia',
                    'datos_adicionales': {
                        'progreso': progreso_pct,
                        'dias_restantes': dias_restantes,
                        'fecha_meta': indicador.meta_fecha_limite.strftime('%d/%m/%Y'),
                        'direccion': indicador.get_direccion_optima_display()
                    }
                })

        # === INSIGHT ADICIONAL: Velocidad requerida ===
        if not meta_alcanzada and dias_restantes > 0:
            ultimo_resultado = indicador.resultados.order_by('-fecha').first()
            if ultimo_resultado:
                valor_actual = ultimo_resultado.valor
                meta_valor = indicador.meta_valor
                distancia = abs(meta_valor - valor_actual)
                velocidad_requerida = (distancia / dias_restantes) * 30  # Por mes

                # Calcular velocidad actual
                resultados = list(indicador.resultados.order_by('-fecha')[:3])
                if len(resultados) >= 2:
                    dias_diff = (resultados[0].fecha - resultados[-1].fecha).days
                    if dias_diff > 0:
                        cambio = abs(resultados[0].valor - resultados[-1].valor)
                        velocidad_actual = (cambio / dias_diff) * 30

                        if velocidad_actual < velocidad_requerida * 0.7:
                            insights.append({
                                'tipo': 'velocidad_insuficiente',
                                'titulo': 'Ritmo de Cambio Insuficiente',
                                'descripcion': f"Velocidad actual: {velocidad_actual:.2f} unidades/mes. Velocidad requerida para meta: {velocidad_requerida:.2f} unidades/mes. Necesitas aumentar el ritmo en {((velocidad_requerida / velocidad_actual - 1) * 100):.0f}%.",
                                'nivel': 'regular',
                                'icono': 'ki-speedometer',
                                'accion_recomendada': 'Aumentar intensidad de las intervenciones',
                                'datos_adicionales': {
                                    'velocidad_actual': round(velocidad_actual, 2),
                                    'velocidad_requerida': round(velocidad_requerida, 2),
                                    'direccion': indicador.get_direccion_optima_display()
                                }
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
                    'icono': 'ki-chart-line-star',
                    'accion_recomendada': 'Análisis de mejores prácticas históricas'
                })

        return insights

    @staticmethod
    def generate_executive_summary(object_list, statistics, variations, indicador):
        """Genera resumen ejecutivo del indicador"""
        if not object_list.exists():
            return "Sin datos suficientes para generar resumen."

        ultimo_resultado = object_list.last()
        efectividad = statistics.get('efectividad', {})
        progreso_meta = indicador.calcular_progreso_meta()

        # Construir mensaje principal
        if progreso_meta and progreso_meta.get('meta_alcanzada'):
            mensaje = f"Meta alcanzada exitosamente con {progreso_meta['progreso_porcentaje']:.1f}% de cumplimiento."
        elif progreso_meta:
            mensaje = f"Progreso del {progreso_meta['progreso_porcentaje']:.1f}% hacia la meta."
        else:
            mensaje = f"Valor actual: {ultimo_resultado.valor:.2f} {indicador.unidad_medida.nombre if indicador.unidad_medida else ''}."

        # Agregar contexto de efectividad
        if efectividad.get('nivel') == 'alta':
            mensaje += f" {efectividad.get('descripcion', '')}."
        elif efectividad.get('nivel') == 'negativa':
            mensaje += " Se requiere revisión urgente de la estrategia."

        # Recomendación principal
        velocidad = statistics.get('velocidad_mensual', 0)
        if abs(velocidad) > 5:
            if velocidad > 0 and indicador.direccion_optima == 'incremento':
                recomendacion = "Mantener momentum positivo actual."
            elif velocidad < 0 and indicador.direccion_optima == 'decremento':
                recomendacion = "Mantener momentum positivo actual."
            else:
                recomendacion = "Ajustar estrategia para corregir tendencia."
        elif progreso_meta and progreso_meta['progreso_porcentaje'] < 50:
            recomendacion = "Intensificar acciones para alcanzar la meta."
        else:
            recomendacion = "Continuar con estrategia actual."

        return {
            'mensaje_principal': mensaje,
            'efectividad': efectividad.get('nivel', 'N/A'),
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


class PresupuestoAnalyticsService:
    """Servicio para análisis avanzado de presupuestos"""

    @staticmethod
    def calculate_budget_health_score(accion) -> int:
        """Calcula un score de salud presupuestaria (0-100)"""
        score = 0
        presupuestos = accion.presupuestos_planificados.all()

        if not presupuestos.exists():
            return 0

        # 1. Análisis de ejecución (40 puntos)
        tasas_ejecucion = []
        for pp in presupuestos:
            tasa = pp.get_porcentaje_monto_ejecutado
            tasas_ejecucion.append(tasa)

        if tasas_ejecucion:
            tasa_promedio = sum(tasas_ejecucion) / len(tasas_ejecucion)
            if tasa_promedio >= 80:
                score += 40
            elif tasa_promedio >= 60:
                score += 30
            elif tasa_promedio >= 40:
                score += 20
            elif tasa_promedio >= 20:
                score += 10

        # 2. Puntualidad en ejecución (30 puntos)
        puntuales = 0
        total_con_vigencia = 0
        for pp in presupuestos:
            if hasattr(pp, 'fecha_fin_vigencia') and pp.fecha_fin_vigencia:
                total_con_vigencia += 1
                if pp.dias_restantes_vigencia and pp.dias_restantes_vigencia > 0:
                    puntuales += 1

        if total_con_vigencia > 0:
            porcentaje_puntual = (puntuales / total_con_vigencia) * 100
            if porcentaje_puntual >= 90:
                score += 30
            elif porcentaje_puntual >= 70:
                score += 20
            elif porcentaje_puntual >= 50:
                score += 10
        else:
            score += 15  # Puntuación media si no hay vigencias definidas

        # 3. Diversificación de fuentes (30 puntos)
        fuentes_unicas = presupuestos.values('fuente_financiamiento').distinct().count()
        if fuentes_unicas >= 4:
            score += 30
        elif fuentes_unicas >= 3:
            score += 20
        elif fuentes_unicas >= 2:
            score += 10

        return min(100, score)

    @staticmethod
    def detect_budget_anomalies(accion) -> List[Dict[str, Any]]:
        """Detecta anomalías en la ejecución presupuestaria"""
        anomalias = []

        for pp in accion.presupuestos_planificados.all():
            porcentaje_ejecutado = pp.get_porcentaje_monto_ejecutado

            # Sobre-ejecución
            if porcentaje_ejecutado > 110:
                anomalias.append({
                    'presupuesto': pp,
                    'tipo': 'sobreejecucion',
                    'nivel': 'critico',
                    'nivel_color': 'danger',
                    'icono': 'ki-shield-cross',
                    'titulo': f'Sobre-ejecución en {pp.tipo_presupuesto.nombre}',
                    'mensaje': f'Presupuesto excedido en {porcentaje_ejecutado - 100:.1f}%',
                    'accion_recomendada': 'Revisar aprobaciones y ajustar presupuesto inmediatamente'
                })
            elif porcentaje_ejecutado > 100:
                anomalias.append({
                    'presupuesto': pp,
                    'tipo': 'sobreejecucion_leve',
                    'nivel': 'alto',
                    'nivel_color': 'warning',
                    'icono': 'ki-information-5',
                    'titulo': f'Ejecución al límite en {pp.tipo_presupuesto.nombre}',
                    'mensaje': f'Presupuesto ejecutado al {porcentaje_ejecutado:.1f}%',
                    'accion_recomendada': 'Monitorear de cerca futuras ejecuciones'
                })

            # Sub-ejecución crónica
            if porcentaje_ejecutado < 30 and pp.presupuestos_ejecutados.count() >= 2:
                anomalias.append({
                    'presupuesto': pp,
                    'tipo': 'subejecucion',
                    'nivel': 'medio',
                    'nivel_color': 'info',
                    'icono': 'ki-arrow-down',
                    'titulo': f'Baja ejecución en {pp.tipo_presupuesto.nombre}',
                    'mensaje': f'Solo {porcentaje_ejecutado:.1f}% ejecutado con múltiples desembolsos',
                    'accion_recomendada': 'Evaluar necesidad real del presupuesto o acelerar ejecución'
                })

            # Verificar vigencia
            if hasattr(pp, 'dias_restantes_vigencia') and pp.dias_restantes_vigencia is not None:
                if pp.dias_restantes_vigencia < 30 and porcentaje_ejecutado < 80:
                    anomalias.append({
                        'presupuesto': pp,
                        'tipo': 'vencimiento_cercano',
                        'nivel': 'alto',
                        'nivel_color': 'warning',
                        'icono': 'ki-calendar-tick',
                        'titulo': f'Vigencia próxima a vencer: {pp.tipo_presupuesto.nombre}',
                        'mensaje': f'Quedan {pp.dias_restantes_vigencia} días y solo {porcentaje_ejecutado:.1f}% ejecutado',
                        'accion_recomendada': 'Acelerar ejecución o solicitar extensión de vigencia'
                    })
                elif pp.dias_restantes_vigencia < 0:
                    anomalias.append({
                        'presupuesto': pp,
                        'tipo': 'vencido',
                        'nivel': 'critico',
                        'nivel_color': 'danger',
                        'icono': 'ki-cross-circle',
                        'titulo': f'Presupuesto vencido: {pp.tipo_presupuesto.nombre}',
                        'mensaje': f'Vigencia expirada hace {abs(pp.dias_restantes_vigencia)} días',
                        'accion_recomendada': 'Regularizar situación o cancelar presupuesto'
                    })

            # Anomalías en velocidad de ejecución
            velocidad = pp.velocidad_ejecucion_mensual if hasattr(pp, 'velocidad_ejecucion_mensual') else 0
            if velocidad > 0:
                meses_para_completar = pp.get_monto_restante / velocidad
                if meses_para_completar > 12:
                    anomalias.append({
                        'presupuesto': pp,
                        'tipo': 'ejecucion_lenta',
                        'nivel': 'medio',
                        'nivel_color': 'info',
                        'icono': 'ki-timer',
                        'titulo': f'Ejecución lenta en {pp.tipo_presupuesto.nombre}',
                        'mensaje': f'A este ritmo tomará {meses_para_completar:.1f} meses completar',
                        'accion_recomendada': 'Revisar planificación y obstáculos en ejecución'
                    })

        return anomalias

    @staticmethod
    def calculate_execution_summary(accion) -> Dict[str, Any]:
        """Calcula resumen ejecutivo de ejecución presupuestaria"""
        resumen = {
            'total_planificado': [],
            'total_ejecutado': [],
            'saldo_disponible': [],
            'velocidad_mensual': []
        }

        # Agrupar por moneda
        for moneda in TipoMoneda.objects.filter(estado=True):
            presupuestos = accion.presupuestos_planificados.filter(tipo_moneda=moneda)

            if presupuestos.exists():
                total_plan = sum(pp.monto for pp in presupuestos)
                total_ejec = sum(pp.get_monto_total_ejecutado for pp in presupuestos)
                saldo = total_plan - total_ejec

                # Calcular velocidad mensual promedio
                velocidades = []
                for pp in presupuestos:
                    if hasattr(pp, 'velocidad_ejecucion_mensual'):
                        vel = pp.velocidad_ejecucion_mensual
                        if vel > 0:
                            velocidades.append(vel)

                vel_promedio = sum(velocidades) / len(velocidades) if velocidades else 0

                resumen['total_planificado'].append({
                    'moneda': moneda.nombre,
                    'moneda_simbolo': moneda.simbolo or '$',
                    'monto_total': total_plan
                })

                resumen['total_ejecutado'].append({
                    'moneda': moneda.nombre,
                    'moneda_simbolo': moneda.simbolo or '$',
                    'monto_total': total_ejec,
                    'porcentaje': (total_ejec / total_plan * 100) if total_plan > 0 else 0
                })

                resumen['saldo_disponible'].append({
                    'moneda': moneda.nombre,
                    'moneda_simbolo': moneda.simbolo or '$',
                    'monto_total': saldo
                })

                resumen['velocidad_mensual'].append({
                    'moneda': moneda.nombre,
                    'moneda_simbolo': moneda.simbolo or '$',
                    'velocidad': vel_promedio
                })

        return resumen


class PresupuestoForecastService:
    """Servicio para proyecciones presupuestarias"""

    @staticmethod
    def forecast_budget_completion(accion) -> Optional[Dict[str, Any]]:
        """Proyecta cuándo se completará el presupuesto"""
        presupuestos = accion.presupuestos_planificados.all()

        if not presupuestos.exists():
            return None

        proyecciones_por_moneda = []

        for moneda in TipoMoneda.objects.filter(estado=True):
            presupuestos_moneda = presupuestos.filter(tipo_moneda=moneda)

            if not presupuestos_moneda.exists():
                continue

            # Calcular velocidad promedio de ejecución
            velocidades = []
            for pp in presupuestos_moneda:
                ejecutados = pp.presupuestos_ejecutados.all().order_by('fecha_inicio')

                if ejecutados.count() >= 2:
                    primer_ejecutado = ejecutados.first()
                    ultimo_ejecutado = ejecutados.last()

                    dias_transcurridos = (ultimo_ejecutado.fecha_fin - primer_ejecutado.fecha_inicio).days
                    if dias_transcurridos > 0:
                        meses = dias_transcurridos / 30.44
                        monto_total = sum(e.monto for e in ejecutados)
                        velocidad = monto_total / meses
                        velocidades.append(velocidad)

            if velocidades:
                velocidad_promedio = sum(velocidades) / len(velocidades)
                monto_restante = sum(pp.get_monto_restante for pp in presupuestos_moneda)

                if velocidad_promedio > 0:
                    meses_estimados = monto_restante / velocidad_promedio
                    fecha_estimada = timezone.now().date() + timedelta(days=int(meses_estimados * 30.44))

                    # Determinar tendencia
                    if len(velocidades) >= 2:
                        velocidad_reciente = velocidades[-1]
                        velocidad_anterior = sum(velocidades[:-1]) / len(velocidades[:-1])
                        tendencia = 'acelerada' if velocidad_reciente > velocidad_anterior * 1.1 else 'normal'
                    else:
                        tendencia = 'normal'

                    # Evaluar riesgo de retraso
                    riesgo_retraso = False
                    mensaje_riesgo = ''

                    if hasattr(accion, 'fecha_fin') and accion.fecha_fin:
                        dias_hasta_fin = (accion.fecha_fin - timezone.now().date()).days
                        dias_estimados = meses_estimados * 30.44

                        if dias_estimados > dias_hasta_fin:
                            riesgo_retraso = True
                            dias_exceso = int(dias_estimados - dias_hasta_fin)
                            mensaje_riesgo = f'La proyección excede la fecha límite en {dias_exceso} días'

                    proyecciones_por_moneda.append({
                        'moneda': moneda.nombre,
                        'meses_estimados': round(meses_estimados, 1),
                        'fecha_estimada': fecha_estimada,
                        'velocidad_mensual': velocidad_promedio,
                        'tendencia': tendencia,
                        'riesgo_retraso': riesgo_retraso,
                        'mensaje_riesgo': mensaje_riesgo
                    })

        return proyecciones_por_moneda[0] if proyecciones_por_moneda else None

    @staticmethod
    def recommend_budget_adjustments(accion) -> List[Dict[str, Any]]:
        """Recomienda ajustes presupuestarios basados en ejecución histórica"""
        recomendaciones = []

        for pp in accion.presupuestos_planificados.all():
            tasa_ejecucion = pp.get_porcentaje_monto_ejecutado

            # Calcular días transcurridos desde fecha de inicio de acción
            if accion.fecha_inicio:
                dias_transcurridos = (timezone.now().date() - accion.fecha_inicio).days
            else:
                dias_transcurridos = 180  # Default

            # Recomendación de reasignación por baja ejecución
            if tasa_ejecucion < 50 and dias_transcurridos > 180:
                monto_sugerido = pp.get_monto_restante * 0.5
                recomendaciones.append({
                    'presupuesto': pp,
                    'tipo': 'reasignacion',
                    'tipo_color': 'warning',
                    'icono': 'ki-arrows-circle',
                    'titulo': f'Reasignación sugerida: {pp.tipo_presupuesto.nombre}',
                    'descripcion': f'Con solo {tasa_ejecucion:.1f}% ejecutado en {dias_transcurridos} días, '
                                   f'considerar reasignar parte del presupuesto a otras categorías con mayor demanda.',
                    'monto_sugerido': monto_sugerido,
                    'accion': 'Reasignar 50% del saldo a categorías con sobre-ejecución'
                })

            # Recomendación de ampliación por alta demanda
            elif tasa_ejecucion > 90 and pp.get_monto_restante > 0:
                monto_sugerido = pp.monto * 0.2  # 20% adicional
                recomendaciones.append({
                    'presupuesto': pp,
                    'tipo': 'ampliacion',
                    'tipo_color': 'success',
                    'icono': 'ki-arrow-up',
                    'titulo': f'Ampliación recomendada: {pp.tipo_presupuesto.nombre}',
                    'descripcion': f'Con {tasa_ejecucion:.1f}% ejecutado, la alta demanda sugiere '
                                   f'necesidad de recursos adicionales para mantener el ritmo.',
                    'monto_sugerido': monto_sugerido,
                    'accion': f'Ampliar presupuesto en 20% ({pp.tipo_moneda.simbolo}{monto_sugerido:,.2f})'
                })

            # Recomendación de revisión por sobre-ejecución
            elif tasa_ejecucion > 100:
                recomendaciones.append({
                    'presupuesto': pp,
                    'tipo': 'revision',
                    'tipo_color': 'danger',
                    'icono': 'ki-shield-cross',
                    'titulo': f'Revisión urgente: {pp.tipo_presupuesto.nombre}',
                    'descripcion': f'Sobre-ejecución de {tasa_ejecucion - 100:.1f}% requiere '
                                   f'análisis de causas y regularización presupuestaria.',
                    'monto_sugerido': pp.get_monto_total_ejecutado - pp.monto,
                    'accion': 'Auditar desembolsos y ajustar presupuesto planificado'
                })

            # Recomendación de aceleración
            elif tasa_ejecucion < 40 and dias_transcurridos > 120:
                recomendaciones.append({
                    'presupuesto': pp,
                    'tipo': 'aceleracion',
                    'tipo_color': 'info',
                    'icono': 'ki-rocket',
                    'titulo': f'Acelerar ejecución: {pp.tipo_presupuesto.nombre}',
                    'descripcion': f'Ritmo de ejecución lento ({tasa_ejecucion:.1f}% en {dias_transcurridos} días). '
                                   f'Identificar y remover obstáculos.',
                    'accion': 'Revisar procesos de aprobación y desembolso'
                })

        return recomendaciones


class PresupuestoVisualizationService:
    """Servicio para preparar datos de visualizaciones"""

    @staticmethod
    def generate_waterfall_data(accion, moneda=None) -> Dict[str, Any]:
        """Genera datos para gráfico de cascada"""
        data = {
            'categorias': [],
            'valores': []
        }

        if moneda:
            presupuestos = accion.presupuestos_planificados.filter(tipo_moneda=moneda)
        else:
            # Usar primera moneda disponible
            presupuestos = accion.presupuestos_planificados.all()

        if not presupuestos.exists():
            return data

        # Presupuesto planificado total
        total_planificado = sum(pp.monto for pp in presupuestos)
        data['categorias'].append('Planificado')
        data['valores'].append(float(total_planificado))

        # Ejecución por categoría (negativo para mostrar salida)
        categorias = CategoriaPresupuesto.objects.all()
        for categoria in categorias:
            presupuestos_cat = presupuestos.filter(categoria=categoria)
            if presupuestos_cat.exists():
                monto_ejecutado = sum(pp.get_monto_total_ejecutado for pp in presupuestos_cat)
                if monto_ejecutado > 0:
                    data['categorias'].append(categoria.nombre)
                    data['valores'].append(-float(monto_ejecutado))

        # Saldo restante
        saldo = sum(pp.get_monto_restante for pp in presupuestos)
        data['categorias'].append('Restante')
        data['valores'].append(float(saldo))

        return data

    @staticmethod
    def generate_category_chart_data(accion, moneda=None) -> Dict[str, Any]:
        """Genera datos para gráfico de categorías"""
        data = {
            'labels': [],
            'series': []
        }

        if moneda:
            presupuestos = accion.presupuestos_planificados.filter(tipo_moneda=moneda)
        else:
            presupuestos = accion.presupuestos_planificados.all()

        categorias = CategoriaPresupuesto.objects.all()
        for categoria in categorias:
            presupuestos_cat = presupuestos.filter(categoria=categoria)
            if presupuestos_cat.exists():
                total_ejecutado = sum(pp.get_monto_total_ejecutado for pp in presupuestos_cat)
                if total_ejecutado > 0:
                    data['labels'].append(categoria.nombre)
                    data['series'].append(float(total_ejecutado))

        return data

    @staticmethod
    def generate_burn_rate_data(accion, moneda=None) -> Dict[str, Any]:
        """Genera datos para gráfico de burn rate"""
        data = {
            'fechas': [],
            'ejecutado': [],
            'planificado': []
        }

        if moneda:
            presupuestos = accion.presupuestos_planificados.filter(tipo_moneda=moneda)
        else:
            presupuestos = accion.presupuestos_planificados.all()

        if not presupuestos.exists():
            return data

        total_planificado = sum(pp.monto for pp in presupuestos)

        # Recopilar todas las ejecuciones
        todas_ejecuciones = []
        for pp in presupuestos:
            for ejecutado in pp.presupuestos_ejecutados.all():
                todas_ejecuciones.append({
                    'fecha': ejecutado.fecha_fin,
                    'monto': ejecutado.monto
                })

        # Ordenar por fecha
        todas_ejecuciones.sort(key=lambda x: x['fecha'])

        # Calcular acumulados
        acumulado = 0
        for ejecucion in todas_ejecuciones:
            acumulado += ejecucion['monto']
            data['fechas'].append(ejecucion['fecha'].strftime('%d/%m/%Y'))
            data['ejecutado'].append(float(acumulado))

        # Línea de planificado (constante)
        data['planificado'] = [float(total_planificado)] * len(data['fechas'])

        return data


class PresupuestoBenchmarkService:
    """Servicio para comparación y benchmarking presupuestario"""

    @staticmethod
    def compare_budget_efficiency(accion) -> Optional[Dict[str, Any]]:
        """Compara eficiencia presupuestaria con otras acciones del sector"""
        sector = accion.sector
        acciones_sector = Accion.objects.filter(sector=sector, publicado=True).exclude(id=accion.id)

        if acciones_sector.count() < 3:
            return None  # No hay suficientes acciones para comparar

        eficiencias = []

        # Calcular eficiencia de la acción actual
        eficiencia_actual = PresupuestoBenchmarkService._calculate_efficiency(accion)
        eficiencias.append({
            'accion': accion,
            'eficiencia': eficiencia_actual,
            'es_actual': True
        })

        # Calcular eficiencias de otras acciones
        for acc in acciones_sector:
            eficiencia = PresupuestoBenchmarkService._calculate_efficiency(acc)
            if eficiencia > 0:
                eficiencias.append({
                    'accion': acc,
                    'eficiencia': eficiencia,
                    'es_actual': False
                })

        # Ordenar por eficiencia
        eficiencias.sort(key=lambda x: x['eficiencia'], reverse=True)

        # Encontrar posición
        posicion = next((i + 1 for i, e in enumerate(eficiencias) if e['es_actual']), None)

        if posicion is None:
            return None

        # Calcular estadísticas
        valores_eficiencia = [e['eficiencia'] for e in eficiencias if not e['es_actual']]
        eficiencia_promedio_sector = sum(valores_eficiencia) / len(valores_eficiencia) if valores_eficiencia else 0
        percentil = ((len(eficiencias) - posicion) / len(eficiencias)) * 100

        # Preparar datos para gráfico
        series_data = []
        labels = []
        for i, e in enumerate(eficiencias[:10]):  # Top 10
            labels.append(f"Acción {e['accion'].id}" if not e['es_actual'] else "Tu Acción")
            series_data.append(e['eficiencia'])

        return {
            'posicion': posicion,
            'total': len(eficiencias),
            'percentil': round(percentil, 1),
            'eficiencia': eficiencia_actual,
            'eficiencia_promedio_sector': round(eficiencia_promedio_sector, 1),
            'series_data': series_data,
            'labels': labels
        }

    @staticmethod
    def _calculate_efficiency(accion) -> float:
        """Calcula score de eficiencia presupuestaria"""
        presupuestos = accion.presupuestos_planificados.all()

        if not presupuestos.exists():
            return 0

        score = 0

        # Factor 1: Tasa de ejecución (0-40 puntos)
        tasas = [pp.get_porcentaje_monto_ejecutado for pp in presupuestos]
        tasa_promedio = sum(tasas) / len(tasas)

        if 70 <= tasa_promedio <= 95:
            score += 40  # Rango óptimo
        elif 60 <= tasa_promedio < 70 or 95 < tasa_promedio <= 100:
            score += 30
        elif 50 <= tasa_promedio < 60:
            score += 20
        else:
            score += 10

        # Factor 2: Consistencia (0-30 puntos)
        if len(tasas) > 1:
            desviacion = stats.stdev(tasas)
            if desviacion < 10:
                score += 30
            elif desviacion < 20:
                score += 20
            elif desviacion < 30:
                score += 10

        # Factor 3: Impacto en indicadores (0-30 puntos)
        indicadores_mejorando = 0
        total_indicadores = accion.indicadores.count()

        if total_indicadores > 0:
            for indicador in accion.indicadores.all():
                variacion = indicador.variacion_valor
                if variacion and variacion.get('interpretacion_cambio_total') == 'positivo':
                    indicadores_mejorando += 1

            porcentaje_mejora = (indicadores_mejorando / total_indicadores) * 100
            if porcentaje_mejora >= 80:
                score += 30
            elif porcentaje_mejora >= 60:
                score += 20
            elif porcentaje_mejora >= 40:
                score += 10

        return min(100, score)


class PresupuestoIndicadorAnalyzer:
    """Analiza relación entre presupuesto e indicadores"""

    @staticmethod
    def calculate_cost_effectiveness(accion) -> List[Dict[str, Any]]:
        """Calcula costo-efectividad por indicador"""
        resultados = []

        # Calcular presupuesto total
        presupuesto_total = 0
        for pp in accion.presupuestos_planificados.all():
            presupuesto_total += pp.get_monto_total_ejecutado

        if presupuesto_total == 0 or accion.indicadores.count() == 0:
            return resultados

        # Presupuesto asignado por indicador (distribución equitativa)
        presupuesto_por_indicador = presupuesto_total / accion.indicadores.count()

        for indicador in accion.indicadores.all():
            variacion = indicador.variacion_valor

            if variacion and variacion.get('variacion_numerica') is not None:
                mejora = variacion['variacion_numerica']

                # Calcular costo por unidad de mejora
                if mejora != 0:
                    costo_por_unidad = presupuesto_por_indicador / abs(mejora)
                else:
                    costo_por_unidad = presupuesto_por_indicador

                # Calcular score de efectividad
                if mejora > 0 and indicador.direccion_optima == 'incremento':
                    score = min(100, (abs(mejora) / presupuesto_por_indicador) * 10000)
                elif mejora < 0 and indicador.direccion_optima == 'decremento':
                    score = min(100, (abs(mejora) / presupuesto_por_indicador) * 10000)
                else:
                    score = 0

                resultados.append({
                    'indicador': indicador,
                    'presupuesto_asignado': presupuesto_por_indicador,
                    'mejora': mejora,
                    'costo_por_unidad': costo_por_unidad,
                    'score_efectividad': score
                })

        return resultados


class ReportePDFService:
    """Servicio para generar diferentes tipos de reportes PDF"""

    def __init__(self, indicador, accion):
        self.indicador = indicador
        self.accion = accion
        self.resultados = indicador.resultados.all().order_by('fecha')
        self.font_config = FontConfiguration()

    def generar_reporte_completo(self):
        """Genera reporte completo con todas las secciones"""
        context = self._preparar_contexto_completo()
        html_string = render_to_string('reportes/reporte_completo.html', context)
        return self._generar_pdf(html_string)

    def generar_reporte_ejecutivo(self):
        """Genera reporte ejecutivo resumido"""
        context = self._preparar_contexto_ejecutivo()
        html_string = render_to_string('reportes/reporte_ejecutivo.html', context)
        return self._generar_pdf(html_string)

    def generar_reporte_estadistico(self):
        """Genera reporte enfocado en estadísticas"""
        context = self._preparar_contexto_estadistico()
        html_string = render_to_string('reportes/reporte_estadistico.html', context)
        return self._generar_pdf(html_string)

    def generar_reporte_comparativo(self):
        """Genera reporte comparativo con otros indicadores"""
        context = self._preparar_contexto_comparativo()
        html_string = render_to_string('reportes/reporte_comparativo.html', context)
        return self._generar_pdf(html_string)

    def _preparar_contexto_completo(self):
        """Prepara contexto para reporte completo"""
        # Calcular estadísticas
        statistics_calculator = StatisticsCalculatorService()
        variation_calculator = VariationCalculatorService()
        insight_generator = InsightGeneratorService()

        advanced_stats = statistics_calculator.calculate_advanced_statistics(
            self.resultados, self.indicador
        )
        variations = variation_calculator.calculate_variations(
            self.resultados, self.indicador
        )
        insights = insight_generator.generate_insights(
            self.resultados, advanced_stats, variations, self.indicador
        )

        # Generar gráficos
        graficos = {
            'tendencia': self._generar_grafico_tendencia(),
            'distribucion': self._generar_grafico_distribucion(),
            'progreso_meta': self._generar_grafico_meta() if self.indicador.meta_valor else None,
        }

        return {
            'indicador': self.indicador,
            'accion': self.accion,
            'resultados': self.resultados,
            'estadisticas': advanced_stats,
            'variaciones': variations,
            'insights': insights,
            'graficos': graficos,
            'fecha_generacion': datetime.now(),
            'total_mediciones': self.resultados.count(),
            'meta_progress': self.indicador.calcular_progreso_meta(),
        }

    def _preparar_contexto_ejecutivo(self):
        """Prepara contexto resumido para ejecutivos"""
        statistics_calculator = StatisticsCalculatorService()
        advanced_stats = statistics_calculator.calculate_advanced_statistics(
            self.resultados, self.indicador
        )

        ultimo_resultado = self.resultados.last()
        primer_resultado = self.resultados.first()

        # KPIs principales
        kpis = {
            'valor_actual': ultimo_resultado.valor if ultimo_resultado else 0,
            'variacion_total': ((ultimo_resultado.valor - primer_resultado.valor) / primer_resultado.valor * 100)
            if ultimo_resultado and primer_resultado and primer_resultado.valor != 0 else 0,
            'promedio': advanced_stats.get('promedio', 0),
            'tendencia': 'Positiva' if advanced_stats.get('velocidad_mensual', 0) > 0 else 'Negativa',
            'efectividad': advanced_stats.get('efectividad', {}).get('nivel', 'N/A'),
        }

        return {
            'indicador': self.indicador,
            'accion': self.accion,
            'kpis': kpis,
            'grafico_tendencia': self._generar_grafico_tendencia(),
            'fecha_generacion': datetime.now(),
            'meta_progress': self.indicador.calcular_progreso_meta(),
        }

    def _preparar_contexto_estadistico(self):
        """Prepara contexto con análisis estadístico detallado"""
        statistics_calculator = StatisticsCalculatorService()
        advanced_stats = statistics_calculator.calculate_advanced_statistics(
            self.resultados, self.indicador
        )

        # Tabla de datos
        tabla_datos = []
        for resultado in self.resultados:
            tabla_datos.append({
                'fecha': resultado.fecha,
                'valor': resultado.valor,
                'observacion': resultado.observacion or '-'
            })

        return {
            'indicador': self.indicador,
            'accion': self.accion,
            'estadisticas': advanced_stats,
            'tabla_datos': tabla_datos,
            'graficos': {
                'tendencia': self._generar_grafico_tendencia(),
                'distribucion': self._generar_grafico_distribucion(),
                'boxplot': self._generar_boxplot(),
            },
            'fecha_generacion': datetime.now(),
        }

    def _preparar_contexto_comparativo(self):
        """Prepara contexto para comparación con otros indicadores"""
        otros_indicadores = self.accion.indicadores.exclude(id=self.indicador.id)

        comparaciones = []
        for otro in otros_indicadores:
            resultados_otro = otro.resultados.all()
            if resultados_otro.exists():
                statistics_calculator = StatisticsCalculatorService()
                stats_otro = statistics_calculator.calculate_advanced_statistics(
                    resultados_otro, otro
                )

                comparaciones.append({
                    'nombre': otro.nombre,
                    'ultimo_valor': resultados_otro.last().valor if resultados_otro.last() else 0,
                    'promedio': stats_otro.get('promedio', 0),
                    'num_mediciones': resultados_otro.count(),
                })

        return {
            'indicador': self.indicador,
            'accion': self.accion,
            'comparaciones': comparaciones,
            'grafico_comparativo': self._generar_grafico_comparativo(otros_indicadores),
            'fecha_generacion': datetime.now(),
        }

    def _generar_grafico_tendencia(self):
        """Genera gráfico de tendencia con matplotlib"""
        if not self.resultados.exists():
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        fechas = [r.fecha for r in self.resultados]
        valores = [r.valor for r in self.resultados]

        # Gráfico de línea
        ax.plot(fechas, valores, marker='o', linewidth=2, markersize=8, color='#1B84FF')

        # Regresión lineal
        x_numeric = np.arange(len(fechas))
        z = np.polyfit(x_numeric, valores, 1)
        p = np.poly1d(z)
        ax.plot(fechas, p(x_numeric), "--", linewidth=2, color='#10b981', alpha=0.7, label='Tendencia')

        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel(f'{self.indicador.unidad_medida.nombre if self.indicador.unidad_medida else "Valor"}',
                      fontsize=12)
        ax.set_title(f'Tendencia - {self.indicador.nombre}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _generar_grafico_distribucion(self):
        """Genera histograma de distribución"""
        if self.resultados.count() < 5:
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        valores = [r.valor for r in self.resultados]

        ax.hist(valores, bins=10, color='#1B84FF', alpha=0.7, edgecolor='black')

        # Líneas de cuartiles
        q1, q2, q3 = np.percentile(valores, [25, 50, 75])
        ax.axvline(q1, color='red', linestyle='--', linewidth=2, label=f'Q1: {q1:.2f}')
        ax.axvline(q2, color='green', linestyle='--', linewidth=2, label=f'Mediana: {q2:.2f}')
        ax.axvline(q3, color='orange', linestyle='--', linewidth=2, label=f'Q3: {q3:.2f}')

        ax.set_xlabel(f'{self.indicador.unidad_medida.nombre if self.indicador.unidad_medida else "Valor"}',
                      fontsize=12)
        ax.set_ylabel('Frecuencia', fontsize=12)
        ax.set_title(f'Distribución de Valores - {self.indicador.nombre}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _generar_boxplot(self):
        """Genera gráfico de caja (boxplot)"""
        if self.resultados.count() < 5:
            return None

        fig, ax = plt.subplots(figsize=(8, 6))

        valores = [r.valor for r in self.resultados]

        bp = ax.boxplot([valores], vert=True, patch_artist=True)
        bp['boxes'][0].set_facecolor('#1B84FF')
        bp['boxes'][0].set_alpha(0.7)

        ax.set_ylabel(f'{self.indicador.unidad_medida.nombre if self.indicador.unidad_medida else "Valor"}',
                      fontsize=12)
        ax.set_title(f'Análisis de Caja - {self.indicador.nombre}', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _generar_grafico_meta(self):
        """Genera gráfico de progreso hacia meta"""
        if not self.indicador.meta_valor or not self.resultados.exists():
            return None

        fig, ax = plt.subplots(figsize=(10, 6))

        fechas = [r.fecha for r in self.resultados]
        valores = [r.valor for r in self.resultados]
        meta = [self.indicador.meta_valor] * len(fechas)

        ax.plot(fechas, valores, marker='o', linewidth=2, markersize=8, color='#1B84FF', label='Valor Real')
        ax.plot(fechas, meta, '--', linewidth=2, color='#ef4444', label=f'Meta: {self.indicador.meta_valor}')

        ax.fill_between(fechas, valores, meta, where=np.array(valores) >= np.array(meta),
                        alpha=0.3, color='green', label='Sobre la meta')
        ax.fill_between(fechas, valores, meta, where=np.array(valores) < np.array(meta),
                        alpha=0.3, color='red', label='Bajo la meta')

        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel(f'{self.indicador.unidad_medida.nombre if self.indicador.unidad_medida else "Valor"}',
                      fontsize=12)
        ax.set_title(f'Progreso hacia Meta - {self.indicador.nombre}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _generar_grafico_comparativo(self, otros_indicadores):
        """Genera gráfico comparativo con otros indicadores"""
        if not otros_indicadores.exists():
            return None

        fig, ax = plt.subplots(figsize=(12, 6))

        nombres = [self.indicador.nombre[:20]]
        valores = [self.resultados.last().valor if self.resultados.last() else 0]

        for otro in otros_indicadores[:5]:  # Máximo 5 para claridad
            resultados_otro = otro.resultados.all()
            if resultados_otro.exists():
                nombres.append(otro.nombre[:20])
                valores.append(resultados_otro.last().valor)

        colors = ['#1B84FF'] + ['#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'][:len(nombres) - 1]

        bars = ax.bar(nombres, valores, color=colors, alpha=0.7, edgecolor='black')

        # Añadir valores sobre las barras
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height:.2f}',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')

        ax.set_ylabel('Último Valor', fontsize=12)
        ax.set_title('Comparación de Indicadores', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        return self._fig_to_base64(fig)

    def _fig_to_base64(self, fig):
        """Convierte figura matplotlib a base64"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return f'data:image/png;base64,{image_base64}'

    def _generar_pdf(self, html_string):
        """Genera PDF desde HTML usando WeasyPrint"""
        css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
            body {
                font-family: Arial, sans-serif;
                font-size: 11pt;
                line-height: 1.6;
            }
            h1 { color: #1B84FF; font-size: 24pt; }
            h2 { color: #333; font-size: 18pt; margin-top: 20pt; }
            h3 { color: #555; font-size: 14pt; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 10pt 0;
            }
            th {
                background-color: #1B84FF;
                color: white;
                padding: 8pt;
                text-align: left;
            }
            td {
                border: 1pt solid #ddd;
                padding: 8pt;
            }
            .kpi-box {
                background: #f0f0f0;
                padding: 10pt;
                margin: 10pt 0;
                border-left: 4pt solid #1B84FF;
            }
            .insight {
                background: #fff3cd;
                padding: 10pt;
                margin: 10pt 0;
                border-left: 4pt solid #f59e0b;
            }
            img {
                max-width: 100%;
                height: auto;
            }
        ''', font_config=self.font_config)

        pdf_file = HTML(string=html_string).write_pdf(
            stylesheets=[css],
            font_config=self.font_config
        )

        return pdf_file