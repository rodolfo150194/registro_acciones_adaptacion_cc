from django.contrib import admin
from django.contrib.auth.models import Permission

from seguridad.models import Perfil


# Register your models here.

class PerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellidos', 'correo', 'entidad')


admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Permission)