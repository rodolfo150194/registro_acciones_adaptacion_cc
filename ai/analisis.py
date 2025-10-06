import google.generativeai as genai
from django.conf import settings
from django.db.models import Avg, Max, Min
import json


class GeminiAnalisisIndicadores:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analizar_indicador_individual(self, indicador):
        """
        Analiza un indicador individual de adaptación

        Args:
            indicador: Instancia del modelo Indicador

        Returns:
            dict con el análisis generado
        """
        # Preparar datos del indicador
        datos = self._preparar_datos_indicador(indicador)
        prompt = self._construir_prompt_individual(datos)

        try:
            response = self.model.generate_content(prompt)
            return {
                'exito': True,
                'indicador_id': indicador.id,
                'indicador_nombre': indicador.nombre,
                'analisis': response.text,
                'datos_analizados': datos
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'indicador_id': indicador.id
            }

    def analizar_indicadores_accion(self, accion):
        """
        Analiza todos los indicadores asociados a una acción

        Args:
            accion: Instancia del modelo Accion

        Returns:
            dict con análisis consolidado
        """
        indicadores = accion.indicadores.all()

        if not indicadores.exists():
            return {
                'exito': False,
                'error': 'La acción no tiene indicadores asociados'
            }

        # Preparar resumen de todos los indicadores
        resumen_indicadores = []
        for ind in indicadores:
            datos = self._preparar_datos_indicador(ind)
            resumen_indicadores.append(datos)

        prompt = self._construir_prompt_accion(accion, resumen_indicadores)

        try:
            response = self.model.generate_content(prompt)
            return {
                'exito': True,
                'accion_id': accion.id,
                'accion_nombre': accion.nombre,
                'total_indicadores': len(resumen_indicadores),
                'analisis_consolidado': response.text,
                'indicadores_analizados': [ind.nombre for ind in indicadores]
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e),
                'accion_id': accion.id
            }

    def generar_reporte_progreso_meta(self, indicador):
        """
        Genera un reporte específico sobre el progreso hacia la meta

        Args:
            indicador: Instancia del modelo Indicador

        Returns:
            dict con análisis de progreso
        """
        if not indicador.meta_valor:
            return {
                'exito': False,
                'error': 'El indicador no tiene meta definida'
            }

        progreso = indicador.calcular_progreso_meta()
        datos = self._preparar_datos_indicador(indicador)

        prompt = f"""
        Analiza el progreso hacia la meta del siguiente indicador de adaptación al cambio climático:

        INFORMACIÓN DEL INDICADOR:
        - Nombre: {indicador.nombre}
        - Tipo: {indicador.tipo_indicador.nombre}
        - Dirección óptima: {indicador.get_direccion_optima_display()}
        - Unidad de medida: {indicador.unidad_medida.sigla}

        DATOS DE META:
        - Valor baseline: {indicador.valor_baseline or 'No definido'}
        - Meta a alcanzar: {indicador.meta_valor}
        - Fecha límite: {indicador.meta_fecha_limite or 'No definida'}
        - Valor actual: {datos['ultimo_valor']}
        - Progreso: {progreso['progreso_porcentaje']:.2f}%
        - Meta alcanzada: {'Sí' if progreso['meta_alcanzada'] else 'No'}

        HISTORIAL DE VALORES:
        {self._formatear_historial_valores(datos['historial_valores'])}

        Por favor proporciona:
        1. Evaluación del progreso actual hacia la meta
        2. Análisis de la tendencia y proyección
        3. Riesgos identificados para alcanzar la meta
        4. Recomendaciones específicas para acelerar el progreso
        5. Acciones correctivas si el progreso es insuficiente
        """

        try:
            response = self.model.generate_content(prompt)
            return {
                'exito': True,
                'indicador_id': indicador.id,
                'progreso': progreso,
                'analisis_meta': response.text
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

    def comparar_indicadores_sector(self, sector):
        """
        Compara indicadores de acciones dentro de un sector

        Args:
            sector: Instancia del modelo Sector

        Returns:
            dict con análisis comparativo
        """
        acciones = sector.accion_set.filter(publicado=True)

        if not acciones.exists():
            return {
                'exito': False,
                'error': 'El sector no tiene acciones publicadas'
            }

        # Recopilar todos los indicadores del sector
        todos_indicadores = []
        for accion in acciones:
            for indicador in accion.indicadores.all():
                datos = self._preparar_datos_indicador(indicador)
                datos['accion_nombre'] = accion.nombre
                todos_indicadores.append(datos)

        if not todos_indicadores:
            return {
                'exito': False,
                'error': 'No se encontraron indicadores en las acciones del sector'
            }

        prompt = f"""
        Analiza comparativamente los indicadores de adaptación del sector {sector.nombre}:

        TOTAL DE ACCIONES: {acciones.count()}
        TOTAL DE INDICADORES: {len(todos_indicadores)}

        RESUMEN DE INDICADORES:
        {self._formatear_resumen_indicadores(todos_indicadores)}

        Por favor proporciona:
        1. Análisis del desempeño general del sector
        2. Identificación de acciones con mejor desempeño
        3. Identificación de acciones que requieren atención
        4. Patrones o tendencias comunes
        5. Recomendaciones estratégicas para el sector
        6. Áreas de oportunidad y mejora
        """

        try:
            response = self.model.generate_content(prompt)
            return {
                'exito': True,
                'sector_id': sector.id,
                'sector_nombre': sector.nombre,
                'total_acciones': acciones.count(),
                'total_indicadores': len(todos_indicadores),
                'analisis_comparativo': response.text
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

    def analizar_tendencias_temporales(self, indicador):
        """
        Analiza las tendencias temporales de un indicador

        Args:
            indicador: Instancia del modelo Indicador

        Returns:
            dict con análisis de tendencias
        """
        resultados = indicador.resultados.order_by('fecha')

        if resultados.count() < 3:
            return {
                'exito': False,
                'error': 'Se necesitan al menos 3 mediciones para análisis de tendencias'
            }

        # Preparar serie temporal
        serie_temporal = []
        for resultado in resultados:
            serie_temporal.append({
                'fecha': resultado.fecha.strftime('%Y-%m-%d'),
                'valor': resultado.valor,
                'observacion': resultado.observacion
            })

        variacion = indicador.variacion_valor

        prompt = f"""
        Analiza las tendencias temporales del siguiente indicador de adaptación:

        INDICADOR: {indicador.nombre}
        TIPO: {indicador.tipo_indicador.nombre}
        FRECUENCIA DE MEDICIÓN: {indicador.frecuencia_medicion}
        DIRECCIÓN ÓPTIMA: {indicador.get_direccion_optima_display()}

        SERIE TEMPORAL ({resultados.count()} mediciones):
        {json.dumps(serie_temporal, indent=2, ensure_ascii=False)}

        ESTADÍSTICAS:
        - Valor promedio: {indicador.promedio_valor:.2f} {indicador.unidad_medida.sigla}
        - Valor máximo: {indicador.mayor_valor.valor if indicador.mayor_valor else 'N/A'}
        - Valor mínimo: {indicador.menor_valor.valor if indicador.menor_valor else 'N/A'}
        - Variación total: {variacion['variacion_numerica']:.2f} ({variacion['variacion_porcentual']:.2f}%)

        Por favor proporciona:
        1. Identificación de patrones y tendencias
        2. Análisis de estacionalidad o ciclos (si aplica)
        3. Puntos de inflexión o cambios significativos
        4. Proyección a corto plazo basada en la tendencia
        5. Factores que podrían estar influenciando la tendencia
        6. Recomendaciones para mantener o mejorar la tendencia
        """

        try:
            response = self.model.generate_content(prompt)
            return {
                'exito': True,
                'indicador_id': indicador.id,
                'total_mediciones': resultados.count(),
                'analisis_tendencias': response.text,
                'serie_temporal': serie_temporal
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }

    def _preparar_datos_indicador(self, indicador):
        """Prepara los datos del indicador para el análisis"""
        resultados = indicador.resultados.order_by('-fecha')

        historial_valores = []
        for resultado in resultados[:10]:  # Últimos 10 resultados
            historial_valores.append({
                'fecha': resultado.fecha.strftime('%Y-%m-%d'),
                'valor': resultado.valor,
                'fuente': resultado.fuente_dato,
                'observacion': resultado.observacion
            })

        variacion = indicador.variacion_valor

        datos = {
            'id': indicador.id,
            'nombre': indicador.nombre,
            'tipo': indicador.tipo_indicador.nombre,
            'descripcion': indicador.descripcion,
            'unidad_medida': indicador.unidad_medida.sigla,
            'direccion_optima': indicador.get_direccion_optima_display(),
            'formula': indicador.formula,
            'frecuencia_medicion': str(
                indicador.frecuencia_medicion) if indicador.frecuencia_medicion else 'No definida',
            'ultimo_valor': indicador.get_ultimo_valor(),
            'promedio': round(indicador.promedio_valor, 2) if indicador.promedio_valor else None,
            'variacion_numerica': round(variacion['variacion_numerica'], 2) if variacion[
                'variacion_numerica'] else None,
            'variacion_porcentual': round(variacion['variacion_porcentual'], 2) if variacion[
                'variacion_porcentual'] else None,
            'total_mediciones': resultados.count(),
            'historial_valores': historial_valores,
            'meta_valor': indicador.meta_valor,
            'meta_fecha': indicador.meta_fecha_limite.strftime('%Y-%m-%d') if indicador.meta_fecha_limite else None,
            'valor_baseline': indicador.valor_baseline,
        }

        # Añadir progreso si hay meta
        if indicador.meta_valor:
            progreso = indicador.calcular_progreso_meta()
            if progreso:
                datos['progreso_meta'] = {
                    'porcentaje': round(progreso['progreso_porcentaje'], 2),
                    'meta_alcanzada': progreso['meta_alcanzada']
                }

        return datos

    def _construir_prompt_individual(self, datos):
        """Construye el prompt para análisis individual"""
        prompt = f"""
        Analiza el siguiente indicador de adaptación al cambio climático:

        INFORMACIÓN GENERAL:
        - Nombre: {datos['nombre']}
        - Tipo: {datos['tipo']}
        - Descripción: {datos['descripcion'] or 'No especificada'}
        - Unidad de medida: {datos['unidad_medida']}
        - Dirección óptima: {datos['direccion_optima']}
        - Fórmula de cálculo: {datos['formula']}
        - Frecuencia de medición: {datos['frecuencia_medicion']}

        RESULTADOS ACTUALES:
        - Valor actual: {datos['ultimo_valor']} {datos['unidad_medida']}
        - Valor promedio: {datos['promedio']} {datos['unidad_medida']}
        - Variación total: {datos['variacion_numerica']} {datos['unidad_medida']} ({datos['variacion_porcentual']}%)
        - Total de mediciones: {datos['total_mediciones']}
        """

        if datos.get('meta_valor'):
            prompt += f"""

        INFORMACIÓN DE META:
        - Valor baseline: {datos['valor_baseline']}
        - Meta a alcanzar: {datos['meta_valor']} {datos['unidad_medida']}
        - Fecha límite: {datos['meta_fecha']}
        - Progreso actual: {datos.get('progreso_meta', {}).get('porcentaje', 'N/A')}%
        - Meta alcanzada: {'Sí' if datos.get('progreso_meta', {}).get('meta_alcanzada') else 'No'}
        """

        prompt += f"""

        HISTORIAL RECIENTE:
        {self._formatear_historial_valores(datos['historial_valores'])}

        Por favor proporciona un análisis que incluya:
        1. Evaluación del desempeño actual del indicador
        2. Interpretación de las tendencias observadas
        3. Análisis de cumplimiento de meta (si aplica)
        4. Identificación de factores que pueden estar influyendo en los resultados
        5. Recomendaciones específicas para mejorar el indicador
        6. Alertas o señales de atención que requieran acción inmediata
        """

        return prompt

    def _construir_prompt_accion(self, accion, resumen_indicadores):
        """Construye el prompt para análisis de acción"""
        prompt = f"""
        Analiza los indicadores de la siguiente acción de adaptación al cambio climático:

        INFORMACIÓN DE LA ACCIÓN:
        - Nombre: {accion.nombre}
        - Tipo: {accion.tipo_accion.nombre}
        - Objetivo: {accion.objetivo or 'No especificado'}
        - Sector: {accion.sector.nombre}
        - Estado: {accion.estado_accion.nombre if accion.estado_accion else 'No definido'}
        - Fecha inicio: {accion.fecha_inicio}
        - Fecha fin: {accion.fecha_fin}
        - Días desde inicio: {accion.calcular_dias_desde_inicio}

        INDICADORES ASOCIADOS ({len(resumen_indicadores)}):
        """

        for i, ind in enumerate(resumen_indicadores, 1):
            prompt += f"""

        {i}. {ind['nombre']} ({ind['tipo']})
           - Valor actual: {ind['ultimo_valor']} {ind['unidad_medida']}
           - Variación: {ind['variacion_porcentual']}%
           - Mediciones: {ind['total_mediciones']}
           """
            if ind.get('progreso_meta'):
                prompt += f"- Progreso meta: {ind['progreso_meta']['porcentaje']}%\n"

        prompt += """

        Por favor proporciona:
        1. Resumen ejecutivo del estado de la acción
        2. Análisis de desempeño de cada indicador
        3. Identificación de indicadores con mejor y peor desempeño
        4. Evaluación del cumplimiento de objetivos
        5. Correlaciones o interdependencias entre indicadores
        6. Recomendaciones estratégicas para la acción
        7. Prioridades de intervención
        """

        return prompt

    def _formatear_historial_valores(self, historial):
        """Formatea el historial de valores para el prompt"""
        if not historial:
            return "No hay historial disponible"

        texto = ""
        for item in historial:
            texto += f"- {item['fecha']}: {item['valor']}"
            if item.get('observacion'):
                texto += f" (Obs: {item['observacion']})"
            texto += "\n"

        return texto

    def _formatear_resumen_indicadores(self, indicadores):
        """Formatea el resumen de múltiples indicadores"""
        texto = ""
        for ind in indicadores:
            texto += f"""
        - Acción: {ind['accion_nombre']}
          Indicador: {ind['nombre']} ({ind['tipo']})
          Valor actual: {ind['ultimo_valor']} {ind['unidad_medida']}
          Variación: {ind['variacion_porcentual']}%
        """

        return texto