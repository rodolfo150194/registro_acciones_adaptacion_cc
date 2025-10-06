from django import forms
from django.core.validators import validate_email

from seguridad.models import Perfil


class PerfilForm(forms.ModelForm):

    class Meta:
        model = Perfil
        fields = ['nombre', 'apellidos', 'correo', 'telefono', 'cargo', 'entidad', 'sexo', 'edad', 'foto']

        widgets = {
            'cargo': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control ','min': 18,
                'max': 120}),
            'telefono': forms.TextInput(attrs={'class': 'form-control '}),
            'nombre': forms.TextInput(attrs={'class': 'form-control '}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control '}),
            'correo': forms.TextInput(attrs={'class': 'form-control '}),
            'entidad': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'sexo': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
        }

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if correo and Perfil.objects.filter(correo=correo).exclude(user=self.instance.user).exists():
            raise forms.ValidationError("Este correo ya está registrado por otro usuario")
        return correo