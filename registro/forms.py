from django import forms
from django.core.exceptions import ValidationError
from django.forms import Textarea

from registro.models import Accion, PresupuestoPlanificado, PresupuestoEjecutado, Indicador, \
    ResultadoIndicador, ResultadoAccion, Cobeneficio
from nomencladores.models import VariableIndicador


class AccionForm(forms.ModelForm):
    class Meta:
        model = Accion
        fields = ['tipo_accion', 'nombre', 'objetivo', 'descripcion', 'sector', 'escala', 'alcance',
                  'lugar_intervencion', 'escenario',
                  'meta', 'fecha_inicio', 'fecha_fin', 'estado_accion', 'entidad_responsable', 'otras_entidades',
                  'programa_apoyo', 'provincias', 'municipios'
            , 'programa_productivo']

        widgets = {
            'tipo_accion': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control '}),
            'meta': forms.TextInput(attrs={'class': 'form-control '}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control '}),
            'descripcion': Textarea(
                attrs={
                    'class': 'form-control ', 'rows': 3, 'cols': 2
                }
            ),
            'sector': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'fecha_fin': forms.DateInput(
                attrs={'class': 'form-control  rounded rounded-end-0', 'id': 'kt_fecha_fin_flatpickr'}),
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'form-control  rounded rounded-end-0', 'id': 'kt_fecha_inicio_flatpickr'}),
            'alcance': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'escenario': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'escala': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'lugar_intervencion': Textarea(
                attrs={
                    'class': 'form-control ', 'rows': 3, 'cols': 2
                }
            ),
            'estado_accion': forms.Select(attrs={'class': 'form-select', 'data-control': 'select2'}),
            'programa_apoyo': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'programa_productivo': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'otras_entidades': forms.SelectMultiple(
                attrs={'class': 'form-select ', 'data-control': 'select2', 'multiple': 'multiple'}),
            'provincias': forms.SelectMultiple(
                attrs={'class': 'form-select ', 'data-control': 'select2', 'multiple': 'multiple'}),
            'municipios': forms.SelectMultiple(
                attrs={'class': 'form-select ', 'data-control': 'select2', 'multiple': 'multiple'}),
            'entidad_responsable': forms.Select(
                attrs={'class': 'form-select', 'data-control': 'select2'}),

        }


class PresupuestoPlanificadoForm(forms.ModelForm):
    class Meta:
        model = PresupuestoPlanificado
        fields = ['tipo_presupuesto', 'tipo_moneda', 'monto', 'fuente_financiamiento',
                  'estado_presupuesto', 'categoria']

        widgets = {
            'tipo_presupuesto': forms.Select(
                attrs={'class': 'form-select', 'data-control': 'select2', }),
            'tipo_moneda': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'categoria': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'estado_presupuesto': forms.Select(
                attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control'}),
            'fuente_financiamiento': forms.TextInput(attrs={'class': 'form-control '}),
        }


class PresupuestoEjecutadoForm(forms.ModelForm):
    class Meta:
        model = PresupuestoEjecutado
        fields = ['monto', 'fecha_inicio', 'fecha_fin', 'observacion']

        widgets = {
            'monto': forms.NumberInput(attrs={'class': 'form-control ' 'required'}),
            'fecha_fin': forms.DateInput(
                attrs={'class': 'form-control  rounded rounded-end-0', 'id': 'kt_fecha_fin_flatpickr'}),
            'fecha_inicio': forms.DateInput(
                attrs={'class': 'form-control  rounded rounded-end-0', 'id': 'kt_fecha_inicio_flatpickr'}),

            'observacion': Textarea(
                attrs={
                    'class': 'form-control', 'rows': 3, 'cols': 2
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')

        # Fecha inicio no puede ser después de fecha fin
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValidationError({
                'fecha_inicio': 'La fecha de inicio no puede ser posterior a la fecha de finalización.'
            })

        return cleaned_data


class IndicadorForm(forms.ModelForm):
    class Meta:
        model = Indicador
        fields = ['nombre', 'tipo_indicador', 'descripcion', 'fuente_indicador', 'formula',
                  'enfoqueIPCC', 'objetivos_relacionados', 'frecuencia_medicion', 'unidad_medida', 'meta_valor',
                  'meta_fecha_limite', 'valor_baseline','direccion_optima'
                  ]

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': Textarea(
                attrs={
                    'class': 'form-control', 'rows': 3, 'cols': 2
                }
            ),
            'fuente_indicador': forms.Textarea(
                attrs={
                    'class': 'form-control', 'rows': 3, 'cols': 2
                }
            ),
            'formula': forms.TextInput(attrs={'class': 'form-control '}),
            'meta_valor': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_baseline': forms.NumberInput(attrs={'class': 'form-control'}),
            'direccion_optima': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'tipo_indicador': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'enfoqueIPCC': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'objetivos_relacionados': forms.SelectMultiple(
                attrs={'class': 'form-select ', 'data-control': 'select2', 'multiple': 'multiple'}),
            'frecuencia_medicion': forms.Select(attrs={'class': 'form-select ', 'data-control': 'select2'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-select ', 'data-kt-repeater': 'select2'})
        }


class ResultadoIndicadorForm(forms.ModelForm):
    class Meta:
        model = ResultadoIndicador
        fields = ['fuente_dato', 'variable_indicador', 'observacion', 'fecha']

        widgets = {
            'fuente_dato': forms.TextInput(attrs={'class': 'form-control '}),
            'observacion': Textarea(attrs={'class': 'form-control ', 'rows': 3, 'cols': 2}),
            'fecha': forms.DateInput(attrs={'class': 'form-control rounded rounded-end-0'}),
        }


class ResultadoVariableForm(forms.Form):
    variable_indicador = forms.CharField(widget=forms.HiddenInput(), required=False)
    variable_indicador_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    valor = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}))
    # class Meta:
    #     model = ResultadoVariable
    #     # fields = '__all__'
    #     fields = ['variable_indicador','valor']
    #
    #     widgets = {
    #         'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder':'Valor'}),
    #         # 'id': forms.HiddenInput(attrs={'class': 'form-control'}),
    #     }


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class DocumentoForm(forms.Form):
    documentos = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.xls,.xlsx'
        }),
        required=False,
        label="Documentos adjuntos"
    )


# class DocumentoForm(forms.Form):
#     documentos = forms.FileField(widget=forms.Mul(attrs={'multiple': True,'class':'form-control'}), required=False)
# class Meta:
#     model = Documento
#     fields = ['documentos']
#
#     widgets = {
#         'name': forms.HiddenInput(attrs={'class': 'form-control'}),
#     }


class VariableIndicadorForm(forms.ModelForm):
    class Meta:
        model = VariableIndicador
        fields = ['nombre', 'variable']

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'variable': forms.TextInput(attrs={'class': 'form-control'}),
            # 'unidad_medida': forms.Select(attrs={'class': 'form-select ', 'data-kt-repeater': 'select2'}),
        }


class ResultadoAccionForm(forms.ModelForm):
    class Meta:
        model = ResultadoAccion
        fields = ['descripcion']

        widgets = {

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control', 'rows': 5, 'cols': 2, 'id': 'editor'
                }
            ),
        }


class CobeneficioForm(forms.ModelForm):
    class Meta:
        model = Cobeneficio
        fields = ['nombre', 'descripcion', 'cumplimiento']

        widgets = {

            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control', 'rows': 5, 'cols': 2
                }
            ),
        }
