from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(required=True, label="Nombre", max_length=30)

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email', 'password1', 'password2']