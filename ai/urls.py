from django.urls import path
from . import views

app_name = 'analisis'

urlpatterns = [
    # APIs JSON para análisis
    path('indicadores/<int:indicador_id>/analizar/',
         views.analizar_indicador,
         name='analizar_indicador'),

    path('indicadores/<int:indicador_id>/progreso-meta/',
         views.analizar_progreso_meta,
         name='progreso_meta'),

    path('indicadores/<int:indicador_id>/tendencias/',
         views.analizar_tendencias,
         name='tendencias'),

    path('acciones/<int:accion_id>/analizar-indicadores/',
         views.analizar_accion,
         name='analizar_accion'),

    path('sectores/<int:sector_id>/comparar-indicadores/',
         views.comparar_sector,
         name='comparar_sector'),

    # Dashboards HTML
    path('indicadores/<int:indicador_id>/dashboard/',
         views.dashboard_analisis_indicador,
         name='dashboard_indicador'),

    path('acciones/<int:accion_id>/dashboard-indicadores/',
         views.dashboard_analisis_accion,
         name='dashboard_accion'),

    # AJAX
    path('api/analisis-indicadores/',
         views.obtener_analisis_ajax,
         name='analisis_ajax'),
]