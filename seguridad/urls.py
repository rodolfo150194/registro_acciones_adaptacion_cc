from django.urls import path

from seguridad.views import PerfilAdaptacionView

app_name = 'seguridad'

urlpatterns = [
    path("perfil/", PerfilAdaptacionView.as_view(), name="perfil"),
]