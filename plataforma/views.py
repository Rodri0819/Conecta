from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.urls import reverse
from .models import Actividad, Grupo, Categoria, Conversacion, Mensaje
from .forms import RegistroForm, ActividadForm, GrupoForm


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


@login_required(login_url='plataforma:login')
def actividades(request):
    qs = Actividad.objects.order_by('fecha')

    filtro = request.GET.get('filtro', 'todas')
    if filtro == 'mias':
        qs = qs.filter(organizador=request.user)
    elif filtro == 'inscrito':
        qs = qs.filter(participantes=request.user)

    q = request.GET.get('q')
    if q:
        qs = qs.filter(titulo__icontains=q)

    categoria_id = request.GET.get('categoria')
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)

    fecha = request.GET.get('fecha')
    if fecha:
        qs = qs.filter(fecha__date=fecha)

    paginator = Paginator(qs, 9)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'plataforma/actividades.html', {
        'actividades': page,
        'categorias': Categoria.objects.all(),
        'grupos_usuario': request.user.grupos.all(),
        'filtro_actual': filtro,
    })


@login_required(login_url='plataforma:login')
def crear_actividad(request):
    if request.method == 'POST':
        form = ActividadForm(request.POST, request.FILES)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.organizador = request.user
            actividad.save()
    return redirect('plataforma:actividades')


@login_required(login_url='plataforma:login')
def detalle_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    return render(request, 'plataforma/detalle_actividad.html', {'actividad': actividad})


# -----------------------------------------------------------------
# MENSAJERÍA
# -----------------------------------------------------------------

@login_required(login_url='plataforma:login')
def mensajes(request):
    conversaciones = list(
        request.user.conversaciones.prefetch_related('participantes', 'mensajes')
    )

    for conv in conversaciones:
        conv.otro_usuario = conv.otro_participante(request.user)
        conv.ultimo_mensaje = conv.mensajes.last()
        conv.no_leidos = conv.mensajes.filter(leido=False).exclude(autor=request.user).count()
        conv.otro_usuario_en_linea = False

    conversacion_actual = None
    mensajes_lista = []

    conversacion_id = request.GET.get('conversacion')
    if conversacion_id:
        conversacion_actual = get_object_or_404(
            Conversacion, id=conversacion_id, participantes=request.user
        )
        conversacion_actual.otro_usuario = conversacion_actual.otro_participante(request.user)
        conversacion_actual.otro_usuario_en_linea = False

        conversacion_actual.mensajes.exclude(autor=request.user).update(leido=True)

        mensajes_lista = list(conversacion_actual.mensajes.select_related('autor'))
        for m in mensajes_lista:
            m.es_propio = (m.autor_id == request.user.id)

    return render(request, 'plataforma/mensajes.html', {
        'conversaciones': conversaciones,
        'conversacion_actual': conversacion_actual,
        'mensajes': mensajes_lista,
    })


@login_required(login_url='plataforma:login')
def enviar_mensaje(request, conversacion_id):
    conversacion = get_object_or_404(
        Conversacion, id=conversacion_id, participantes=request.user
    )
    if request.method == 'POST':
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            Mensaje.objects.create(
                conversacion=conversacion,
                autor=request.user,
                contenido=contenido,
            )
    return redirect(f"{reverse('plataforma:mensajes')}?conversacion={conversacion_id}")


@login_required(login_url='plataforma:login')
def iniciar_conversacion(request, usuario_id):
    otro_usuario = get_object_or_404(User, id=usuario_id)

    if otro_usuario == request.user:
        return redirect('plataforma:mensajes')

    conversacion = (
        Conversacion.objects.filter(participantes=request.user)
        .filter(participantes=otro_usuario)
        .first()
    )

    if not conversacion:
        conversacion = Conversacion.objects.create()
        conversacion.participantes.add(request.user, otro_usuario)

    return redirect(f"{reverse('plataforma:mensajes')}?conversacion={conversacion.id}")


# -----------------------------------------------------------------
# GRUPOS
# -----------------------------------------------------------------

@login_required(login_url='plataforma:login')
def grupos(request):
    qs = Grupo.objects.order_by('-creado_en')

    filtro = request.GET.get('filtro', 'todos')
    if filtro == 'mios':
        qs = qs.filter(miembros=request.user)

    q = request.GET.get('q')
    if q:
        qs = qs.filter(nombre__icontains=q)

    categoria_id = request.GET.get('categoria')
    if categoria_id:
        qs = qs.filter(categoria_id=categoria_id)

    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'plataforma/grupos.html', {
        'grupos': page,
        'categorias': Categoria.objects.all(),
        'filtro_actual': filtro,
        'q': q,
        'categoria_actual': categoria_id,
    })


@login_required(login_url='plataforma:login')
def crear_grupo(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST, request.FILES)
        if form.is_valid():
            grupo = form.save()
            grupo.miembros.add(request.user)
            return redirect('plataforma:detalle_grupo', grupo_id=grupo.id)
    else:
        form = GrupoForm()

    return render(request, 'plataforma/crear_grupo.html', {'form': form})


@login_required(login_url='plataforma:login')
def detalle_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    es_miembro = grupo.miembros.filter(id=request.user.id).exists()

    return render(request, 'plataforma/detalle_grupo.html', {
        'grupo': grupo,
        'es_miembro': es_miembro,
    })


@login_required(login_url='plataforma:login')
def unirse_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.method == 'POST':
        grupo.miembros.add(request.user)
    return redirect(request.META.get('HTTP_REFERER') or reverse('plataforma:grupos'))


@login_required(login_url='plataforma:login')
def salir_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.method == 'POST':
        grupo.miembros.remove(request.user)
    return redirect(request.META.get('HTTP_REFERER') or reverse('plataforma:grupos'))


# -----------------------------------------------------------------
# EXPLORAR
# -----------------------------------------------------------------

@login_required(login_url='plataforma:login')
def explorar(request):
    tipo = request.GET.get('tipo', 'actividades')
    q = request.GET.get('q')
    categoria_id = request.GET.get('categoria')

    if tipo == 'grupos':
        qs = Grupo.objects.order_by('-creado_en')
        if q:
            qs = qs.filter(nombre__icontains=q)
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
    else:
        tipo = 'actividades'
        qs = Actividad.objects.order_by('fecha')
        if q:
            qs = qs.filter(titulo__icontains=q)
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)

    paginator = Paginator(qs, 12)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'plataforma/explorar.html', {
        'resultados': page,
        'categorias': Categoria.objects.all(),
        'tipo_actual': tipo,
        'q': q,
        'categoria_actual': categoria_id,
    })