from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import Actividad, Grupo, Categoria
from .forms import RegistroForm


@login_required(login_url='plataforma:login')
def inicio(request):
    proximos_eventos = Actividad.objects.order_by('fecha')[:3]
    grupos_sugeridos = Grupo.objects.order_by('-creado_en')[:3]
    categorias = Categoria.objects.all()
    recomendaciones = Actividad.objects.order_by('-fecha')[:4]

    return render(request, 'plataforma/inicio.html', {
        'proximos_eventos': proximos_eventos,
        'grupos_sugeridos': grupos_sugeridos,
        'categorias': categorias,
        'recomendaciones': recomendaciones,
    })


def registro(request):
    if request.user.is_authenticated:
        return redirect('plataforma:inicio')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('plataforma:inicio')
    else:
        form = RegistroForm()

    return render(request, 'plataforma/registro.html', {'form': form})