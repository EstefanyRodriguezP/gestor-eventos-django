from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Evento

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descripcion', 'fecha', 'privado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            # el widget será tipo datetime-local, compatible con el HTML5
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'privado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Establecer el atributo `min` del input datetime-local para mejorar UX.
        # Esto evita (en el navegador) seleccionar una fecha/hora anterior al momento actual.
        now_local = timezone.localtime()
        min_value = now_local.strftime("%Y-%m-%dT%H:%M")  # formato compatible con datetime-local
        if 'fecha' in self.fields:
            # preserva otros attrs existentes y añade/actualiza min
            attrs = self.fields['fecha'].widget.attrs
            attrs['min'] = min_value
            self.fields['fecha'].widget.attrs = attrs

    def clean_fecha(self):
        # Validación del campo fecha: la fecha/hora debe ser estrictamente futura respecto al momento actual.
        fecha = self.cleaned_data.get('fecha')
        if not fecha:
            return fecha

        now = timezone.now()

        # Si la fecha es naive (lo que ocurre con datetime-local), hacer aware en tz local
        # para comparar correctamente con now (which is aware si USE_TZ=True).
        if timezone.is_naive(fecha):
            fecha = timezone.make_aware(fecha, timezone.get_current_timezone())

        # Comparamos con `now` (aware). Requerimos fecha estrictamente mayor que now.
        if fecha <= now:
            raise ValidationError("La fecha y hora deben ser futuras.")

        return fecha