from django.contrib import admin

# Register your models here.
from django.contrib import admin

from nomencladores.models import *


# Register your models here.

class ProvinciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'codigo', 'sigla')


class MunicipioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'codigo')


class CargoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class TipoEntidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class EntidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'correo', 'municipio')


class SectorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class TipoAccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class TipoIndicadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class AlcanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


# class LugarIntervencionAdmin(admin.ModelAdmin):
#     list_display = ('id', 'nombre')


class TipoMonedaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class TipoPresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class EstadoAccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class EstadoPresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class ProgramaProductivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class ProgramaApoyoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class UnidadMedidaIndicadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class EnfoqueIPCCAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class ObjetivosDesarrolloSostenibleAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class AmenazaClimaticaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


class FrecuenciaMedicionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cantidad','unidad')


class EscenarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

class EscalaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')

class VariableIndicadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre','variable')


class CategoriaPresupuestoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')


admin.site.register(Provincia, ProvinciaAdmin)
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(TipoEntidad, TipoEntidadAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(Entidad, EntidadAdmin)
admin.site.register(Sector, SectorAdmin)
admin.site.register(TipoAccion, TipoAccionAdmin)
admin.site.register(TipoIndicador, TipoIndicadorAdmin)
admin.site.register(Alcance, AlcanceAdmin)
admin.site.register(TipoMoneda, TipoMonedaAdmin)
admin.site.register(TipoPresupuesto, TipoPresupuestoAdmin)
admin.site.register(Escenario, EscenarioAdmin)
admin.site.register(Escala, EscalaAdmin)
admin.site.register(EstadoAccion, EstadoAccionAdmin)
admin.site.register(EstadoPresupuesto, EstadoPresupuestoAdmin)
admin.site.register(ProgramaProductivo, ProgramaProductivoAdmin)
admin.site.register(ProgramaApoyo, ProgramaApoyoAdmin)
admin.site.register(UnidadMedidaIndicador, UnidadMedidaIndicadorAdmin)
admin.site.register(EnfoqueIPCC, EnfoqueIPCCAdmin)
admin.site.register(ObjetivosDesarrolloSostenible, ObjetivosDesarrolloSostenibleAdmin)
admin.site.register(AmenazaClimatica, AmenazaClimaticaAdmin)
admin.site.register(FrecuenciaMedicion, FrecuenciaMedicionAdmin)
admin.site.register(VariableIndicador, VariableIndicadorAdmin)
admin.site.register(CategoriaPresupuesto, CategoriaPresupuestoAdmin)
