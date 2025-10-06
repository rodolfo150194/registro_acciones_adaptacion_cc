from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from ai.analisis import GeminiAnalisisIndicadores
from nomencladores.models import Sector
from registro.models import Indicador, Accion


@login_required
@require_http_methods(["GET"])
def analizar_indicador(request, indicador_id):
    """
    Analiza un indicador individual usando Gemini

    URL: /indicadores/<id>/analizar/
    """
    indicador = get_object_or_404(Indicador, id=indicador_id)

    # Analizar con Gemini
    gemini = GeminiAnalisisIndicadores()
    resultado = gemini.analizar_indicador_individual(indicador)

    if resultado['exito']:
        return JsonResponse(resultado)
    else:
        return JsonResponse(resultado, status=500)


@login_required
@require_http_methods(["GET"])
def analizar_accion(request, accion_id):
    """
    Analiza todos los indicadores de una acción

    URL: /acciones/<id>/analizar-indicadores/
    """
    accion = get_object_or_404(Accion, id=accion_id)

    # Verificar permisos
    if accion.user != request.user and not request.user.is_superuser:
        return JsonResponse({
            'exito': False,
            'error': 'No tiene permisos para analizar esta acción'
        }, status=403)

    gemini = GeminiAnalisisIndicadores()
    resultado = gemini.analizar_indicadores_accion(accion)

    if resultado['exito']:
        return JsonResponse(resultado)
    else:
        return JsonResponse(resultado, status=500)


@login_required
@require_http_methods(["GET"])
def analizar_progreso_meta(request, indicador_id):
    """
    Analiza el progreso hacia la meta de un indicador

    URL: /indicadores/<id>/progreso-meta/
    """
    indicador = get_object_or_404(Indicador, id=indicador_id)

    gemini = GeminiAnalisisIndicadores()
    resultado = gemini.generar_reporte_progreso_meta(indicador)

    if resultado['exito']:
        return JsonResponse(resultado)
    else:
        return JsonResponse(resultado, status=500)


@login_required
@require_http_methods(["GET"])
def analizar_tendencias(request, indicador_id):
    """
    Analiza las tendencias temporales de un indicador

    URL: /indicadores/<id>/tendencias/
    """
    indicador = get_object_or_404(Indicador, id=indicador_id)

    gemini = GeminiAnalisisIndicadores()
    resultado = gemini.analizar_tendencias_temporales(indicador)

    if resultado['exito']:
        return JsonResponse(resultado)
    else:
        return JsonResponse(resultado, status=500)


@login_required
@require_http_methods(["GET"])
def comparar_sector(request, sector_id):
    """
    Compara indicadores de todas las acciones de un sector

    URL: /sectores/<id>/comparar-indicadores/
    """
    sector = get_object_or_404(Sector, id=sector_id)

    gemini = GeminiAnalisisIndicadores()
    resultado = gemini.comparar_indicadores_sector(sector)

    if resultado['exito']:
        return JsonResponse(resultado)
    else:
        return JsonResponse(resultado, status=500)


@login_required
def dashboard_analisis_indicador(request, indicador_id):
    """
    Vista HTML para mostrar el dashboard de análisis de un indicador

    URL: /indicadores/<id>/dashboard/
    """
    indicador = get_object_or_404(Indicador, id=indicador_id)

    # Verificar permisos
    usuarios_permitidos = indicador.get_users()
    if request.user not in usuarios_permitidos and not request.user.is_superuser:
        return render(request, '403.html', status=403)

    context = {
        'indicador': indicador,
        'resultados': indicador.resultados.order_by('-fecha')[:10],
        'variacion': indicador.variacion_valor,
        'grafico': indicador.get_grafico,
    }

    # Si hay meta, calcular progreso
    if indicador.meta_valor:
        context['progreso'] = indicador.calcular_progreso_meta()

    return render(request, 'indicadores/dashboard_analisis.html', context)


@login_required
def dashboard_analisis_accion(request, accion_id):
    """
    Vista HTML para mostrar el dashboard de análisis de una acción

    URL: /acciones/<id>/dashboard-indicadores/
    """
    accion = get_object_or_404(Accion, id=accion_id)

    # Verificar permisos
    if accion.user != request.user and not request.user.is_superuser:
        return render(request, '403.html', status=403)

    indicadores = accion.indicadores.all()

    # Preparar datos de cada indicador
    indicadores_data = []
    for ind in indicadores:
        data = {
            'indicador': ind,
            'ultimo_valor': ind.get_ultimo_valor(),
            'variacion': ind.variacion_valor,
        }
        if ind.meta_valor:
            data['progreso'] = ind.calcular_progreso_meta()
        indicadores_data.append(data)

    context = {
        'accion': accion,
        'indicadores_data': indicadores_data,
        'total_indicadores': indicadores.count(),
    }

    return render(request, 'acciones/dashboard_indicadores.html', context)


# Vista AJAX para obtener análisis en tiempo real
@login_required
@require_http_methods(["POST"])
def obtener_analisis_ajax(request):
    """
    Endpoint AJAX para obtener análisis de múltiples indicadores

    URL: /api/analisis-indicadores/
    POST: { "indicador_ids": [1, 2, 3], "tipo_analisis": "individual" }
    """
    import json

    try:
        data = json.loads(request.body)
        indicador_ids = data.get('indicador_ids', [])
        tipo_analisis = data.get('tipo_analisis', 'individual')

        if not indicador_ids:
            return JsonResponse({
                'exito': False,
                'error': 'No se proporcionaron IDs de indicadores'
            }, status=400)

        gemini = GeminiAnalisisIndicadores()
        resultados = []

        for ind_id in indicador_ids:
            try:
                indicador = Indicador.objects.get(id=ind_id)

                if tipo_analisis == 'individual':
                    resultado = gemini.analizar_indicador_individual(indicador)
                elif tipo_analisis == 'tendencias':
                    resultado = gemini.analizar_tendencias_temporales(indicador)
                elif tipo_analisis == 'meta':
                    resultado = gemini.generar_reporte_progreso_meta(indicador)
                else:
                    resultado = gemini.analizar_indicador_individual(indicador)

                resultados.append(resultado)
            except Indicador.DoesNotExist:
                resultados.append({
                    'exito': False,
                    'indicador_id': ind_id,
                    'error': 'Indicador no encontrado'
                })

        return JsonResponse({
            'exito': True,
            'total_analizados': len(resultados),
            'resultados': resultados
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'exito': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)