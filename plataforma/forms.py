from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Actividad, Grupo


INPUT_CLASSES = (
    "w-full bg-[#f8f8fc] rounded-xl px-4 py-3 text-sm border border-gray-100 "
    "focus:outline-none focus:ring-4 focus:ring-brand-100 focus:border-brand-400 transition"
)


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=True, label="Nombre", max_length=30)

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password1', 'password2']


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