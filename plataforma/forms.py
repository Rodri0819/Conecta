import datetime
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Actividad, Grupo


INPUT_CLASSES = (
    "w-full bg-[#f8f8fc] rounded-xl px-4 py-3 text-sm border border-gray-100 "
    "focus:outline-none focus:ring-4 focus:ring-brand-100 focus:border-brand-400 transition"
)

EDAD_MINIMA = 18  # años requeridos para poder registrarse


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=True, label="Nombre", max_length=30)

    # --- Verificación de edad ---
    fecha_nacimiento = forms.DateField(
        required=True,
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text=f"Debes tener {EDAD_MINIMA} años o más para crear una cuenta.",
    )

    # --- Verificación de identidad (opcional en el registro, revisado por un admin) ---
    documento_identidad = forms.ImageField(
        required=False,
        label="Foto de tu identificación (opcional, acelera tu verificación)",
    )

    # --- Aceptación de normas ---
    acepto_terminos = forms.BooleanField(
        required=True,
        label="He leído y acepto los Términos de uso y las Normas de convivencia de Conecta.",
    )

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password1', 'password2']

    def clean_fecha_nacimiento(self):
        nacimiento = self.cleaned_data['fecha_nacimiento']
        hoy = timezone.now().date()

        if nacimiento > hoy:
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")

        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

        if edad < EDAD_MINIMA:
            raise forms.ValidationError(
                f"Debes tener al menos {EDAD_MINIMA} años para registrarte en Conecta."
            )
        if edad > 120:
            raise forms.ValidationError("Revisa la fecha de nacimiento ingresada.")

        return nacimiento


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['titulo', 'descripcion', 'categoria', 'grupo', 'imagen', 'lugar', 'fecha']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nombre', 'descripcion', 'categoria', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': INPUT_CLASSES,
                'placeholder': 'Ej: Amantes del senderismo',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': INPUT_CLASSES,
                'rows': 4,
                'placeholder': 'Cuéntale a la gente de qué trata este grupo...',
            }),
            'categoria': forms.Select(attrs={'class': INPUT_CLASSES}),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'text-sm text-gray-600 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl '
                         'file:border-0 file:bg-brand-50 file:text-brand-600 file:font-semibold '
                         'hover:file:bg-brand-100 transition',
            }),
        }


class ReporteForm(forms.Form):
    motivo = forms.ChoiceField(
        choices=[
            ('acoso', 'Acoso o comportamiento inapropiado'),
            ('suplantacion', 'Suplantación de identidad'),
            ('contenido', 'Contenido inapropiado u ofensivo'),
            ('menor_riesgo', 'Sospecha de riesgo hacia un menor'),
            ('spam', 'Spam o cuenta falsa'),
            ('otro', 'Otro motivo'),
        ],
        label="Motivo del reporte",
    )
    descripcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        label="Cuéntanos más (opcional)",
    )