from django.urls import path

from registro.views import HomeView, ActionListView, ActionCreateView, ActionUpdateView, DetailtsActionUpdateView, \
    PresupuestoPlanificadoListView, PresupuestoPlanificadoCreateView, PresupuestoPlanificadoUpdateView, \
    eliminar_presupuesto_planificado, \
    PresupuestoEjecutadoView, PresupuestoEjecutadoUpdateView, eliminar_presupuesto_ejecutado, IndicadoresListView, \
    eliminar_accion, IndicadorCreateView, IndicadorUpdateView, eliminar_indicador, ResultadosIndicadorListView, \
    ResultadoIndicadorCreateView, ResultadoIndicadorUpdateView, \
    eliminar_resultado_indicador, mapa_cuba_leaflet, municipios_por_tipo_accion

app_name = 'registro'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),

    # Accion
    path('acciones/', ActionListView.as_view(), name='lista_accion'),
    path('acciones/crear/', ActionCreateView.as_view(), name='registrar_accion'),
    path('acciones/editar/<int:pk>/', ActionUpdateView.as_view(), name='editar_accion'),
    path('acciones/detalle/<int:pk>/', DetailtsActionUpdateView.as_view(), name='detalle_accion'),
    path('acciones/eliminar/<int:id_accion>/', eliminar_accion, name='eliminar_accion'),

    # Presupuesto Planificado
    path('accion/<int:id_accion>/presupuesto/lista/', PresupuestoPlanificadoListView.as_view(), name='lista_presupuesto_planificado'),
    path('accion/<int:id_accion>/presupuesto/crear/', PresupuestoPlanificadoCreateView.as_view(), name='registrar_presupuesto_planificado'),
    path('accion/<int:id_accion>/presupuesto/editar/<int:id_presupuesto>/', PresupuestoPlanificadoUpdateView.as_view(), name='editar_presupuesto_planificado'),
    path('accion/<int:id_accion>/presupuesto/eliminar/<int:id_presupuesto>/', eliminar_presupuesto_planificado ,name='eliminar_presupuesto_planificado'),

    # Presupuesto Ejecutado
    path("accion/<int:id_accion>/presupuesto_planificado/<int:id_presupuesto>/ejecutado/crear/", PresupuestoEjecutadoView.as_view(), name="registrar_presupuesto_ejecutado"),
    path("accion/<int:id_accion>/presupuesto_planificado/<int:id_presupuesto>/ejecutado/editar/<int:id_ejecutado>/", PresupuestoEjecutadoUpdateView.as_view(), name="editar_presupuesto_ejecutado"),
    path("accion/<int:id_accion>/presupuesto_planificado/<int:id_presupuesto>/ejecutado/eliminar/<int:id_ejecutado>/", eliminar_presupuesto_ejecutado, name="eliminar_presupuesto_ejecutado"),

    #Indicador
    path("accion/<int:id_accion>/indicadores/lista/", IndicadoresListView.as_view(), name="lista_indicador"),
    path("accion/<int:id_accion>/indicadores/crear/", IndicadorCreateView.as_view(), name="registrar_indicador"),
    path("accion/<int:id_accion>/indicadores/editar/<int:id_indicador>/", IndicadorUpdateView.as_view(), name="editar_indicador"),
    path("accion/<int:id_accion>/indicadores/eliminar/<int:id_indicador>/", eliminar_indicador, name="eliminar_indicador"),
    path("accion/<int:id_accion>/indicadores/<int:id_indicador>/resultado/crear", ResultadoIndicadorCreateView.as_view(), name="registrar_resultado_indicador"),
    path("accion/<int:id_accion>/indicadores/<int:id_indicador>/resultado/comportamiento/", ResultadosIndicadorListView.as_view(), name="lista_resultado_indicador"),
    path("accion/<int:id_accion>/indicadores/<int:id_indicador>/resultado/editar/<int:id_resultado>/", ResultadoIndicadorUpdateView.as_view(), name="editar_resultado_indicador"),
    path("accion/<int:id_accion>/indicadores/<int:id_indicador>/resultado/eliminar/<int:id_resultado>/", eliminar_resultado_indicador, name="eliminar_resultado_indicador"),


    path("accion/mapa/", mapa_cuba_leaflet, name="mapa"),
    path('api/municipios-por-tipo-accion/', municipios_por_tipo_accion, name='municipios_por_tipo_accion'),

]
