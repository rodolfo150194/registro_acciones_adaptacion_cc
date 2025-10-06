from auditlog.models import LogEntry
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from seguridad.forms import PerfilForm
from seguridad.models import Notificacion, Perfil


class PerfilAdaptacionView(LoginRequiredMixin, UpdateView):
    model = Perfil
    form_class = PerfilForm
    template_name = 'account/profile.html'
    success_url = reverse_lazy('seguridad:perfil')

    def get_object(self, queryset=None):
        try:
            return self.request.user.perfil
        except Perfil.DoesNotExist:
            return Perfil.objects.create(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title_html': 'Perfil',
            'title_head': 'Perfil',
            'acciones': LogEntry.objects.filter(
                actor_id=self.request.user.id
            ).order_by('-timestamp')[:8],
            'notificaciones': Notificacion.objects.filter(
                user=self.request.user
            ).order_by("-created_at"),
            'stats': self.get_user_stats(),
        })
        return context

    def get_user_stats(self):
        return {
            'logins_count': LogEntry.objects.filter(
                actor_id=self.request.user.id,
            ).count(),
        }

    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado correctamente')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Por favor corrija los errores en el formulario')
        return super().form_invalid(form)

