from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages as django_messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.urls import reverse
from .models import (
    Actividad, Grupo, Categoria, Conversacion, Mensaje,
    Perfil, Reporte, Bloqueo,
)
from .forms import RegistroForm, ActividadForm, GrupoForm, ReporteForm, PerfilForm


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
        form = RegistroForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Creamos el Perfil con los datos de seguridad recolectados en el registro
            Perfil.objects.create(
                user=user,
                fecha_nacimiento=form.cleaned_data['fecha_nacimiento'],
                acepto_terminos=form.cleaned_data['acepto_terminos'],
                documento_identidad=form.cleaned_data.get('documento_identidad'),
                verificado=False,  # queda pendiente hasta revisión de un administrador
            )

            login(request, user)
            django_messages.success(
                request,
                'Cuenta creada correctamente. Si subiste tu identificación, '
                'la revisaremos pronto para verificar tu cuenta.'
            )
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
        grupo_id = request.POST.get('grupo')

        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.organizador = request.user
            actividad.save()
            if actividad.grupo:
                return redirect('plataforma:detalle_grupo', grupo_id=actividad.grupo.id)
        elif grupo_id:
            return redirect('plataforma:detalle_grupo', grupo_id=grupo_id)

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
    # Excluimos conversaciones con usuarios que el usuario actual bloqueó
    ids_bloqueados = Bloqueo.objects.filter(usuario=request.user).values_list('bloqueado_id', flat=True)

    conversaciones = list(
        request.user.conversaciones.prefetch_related('participantes', 'mensajes')
    )

    conversaciones_visibles = []
    for conv in conversaciones:
        otro = conv.otro_participante(request.user)
        if otro and otro.id in ids_bloqueados:
            continue  # ocultamos conversaciones con usuarios bloqueados
        conv.otro_usuario = otro
        conv.ultimo_mensaje = conv.mensajes.last()
        conv.no_leidos = conv.mensajes.filter(leido=False).exclude(autor=request.user).count()
        conv.otro_usuario_en_linea = False
        conversaciones_visibles.append(conv)

    conversacion_actual = None
    mensajes_lista = []
    usuario_bloqueado = False

    conversacion_id = request.GET.get('conversacion')
    if conversacion_id:
        conversacion_actual = get_object_or_404(
            Conversacion, id=conversacion_id, participantes=request.user
        )
        conversacion_actual.otro_usuario = conversacion_actual.otro_participante(request.user)
        conversacion_actual.otro_usuario_en_linea = False

        usuario_bloqueado = conversacion_actual.otro_usuario_id in ids_bloqueados if conversacion_actual.otro_usuario else False

        conversacion_actual.mensajes.exclude(autor=request.user).update(leido=True)

        mensajes_lista = list(conversacion_actual.mensajes.select_related('autor'))
        for m in mensajes_lista:
            m.es_propio = (m.autor_id == request.user.id)

    return render(request, 'plataforma/mensajes.html', {
        'conversaciones': conversaciones_visibles,
        'conversacion_actual': conversacion_actual,
        'mensajes': mensajes_lista,
        'usuario_bloqueado': usuario_bloqueado,
    })


@login_required(login_url='plataforma:login')
def enviar_mensaje(request, conversacion_id):
    conversacion = get_object_or_404(
        Conversacion, id=conversacion_id, participantes=request.user
    )

    otro_usuario = conversacion.otro_participante(request.user)
    bloqueado = Bloqueo.objects.filter(usuario=request.user, bloqueado=otro_usuario).exists() if otro_usuario else False

    if request.method == 'POST' and not bloqueado:
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
            grupo = form.save(commit=False)
            grupo.creador = request.user
            grupo.save()
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

@login_required(login_url='plataforma:login')
def eliminar_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    if request.method == 'POST' and grupo.creador == request.user:
        grupo.delete()
        django_messages.success(request, 'Grupo eliminado correctamente.')
        return redirect('plataforma:grupos')
    return redirect('plataforma:detalle_grupo', grupo_id=grupo.id)


@login_required(login_url='plataforma:login')
def eliminar_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    if request.method == 'POST' and actividad.organizador == request.user:
        grupo_id = actividad.grupo.id if actividad.grupo else None
        actividad.delete()
        django_messages.success(request, 'Actividad eliminada correctamente.')
        if grupo_id:
            return redirect('plataforma:detalle_grupo', grupo_id=grupo_id)
        return redirect('plataforma:actividades')
    return redirect('plataforma:detalle_actividad', actividad_id=actividad.id)


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


# -----------------------------------------------------------------
# SEGURIDAD: REPORTES Y BLOQUEOS
# -----------------------------------------------------------------

@login_required(login_url='plataforma:login')
def reportar_usuario(request, usuario_id):
    usuario_reportado = get_object_or_404(User, id=usuario_id)

    if request.method == 'POST':
        form = ReporteForm(request.POST)
        if form.is_valid() and usuario_reportado != request.user:
            Reporte.objects.create(
                reportante=request.user,
                usuario_reportado=usuario_reportado,
                motivo=form.cleaned_data['motivo'],
                descripcion=form.cleaned_data['descripcion'],
            )
            django_messages.success(
                request,
                'Gracias por avisarnos. Nuestro equipo revisará este reporte lo antes posible.'
            )
    else:
        form = ReporteForm()

    return render(request, 'plataforma/reportar_usuario.html', {
        'form': form,
        'usuario_reportado': usuario_reportado,
    })


@login_required(login_url='plataforma:login')
def bloquear_usuario(request, usuario_id):
    usuario_bloqueado = get_object_or_404(User, id=usuario_id)

    if request.method == 'POST' and usuario_bloqueado != request.user:
        Bloqueo.objects.get_or_create(usuario=request.user, bloqueado=usuario_bloqueado)
        django_messages.success(request, f'Bloqueaste a {usuario_bloqueado.first_name or usuario_bloqueado.username}.')

    return redirect(request.META.get('HTTP_REFERER') or reverse('plataforma:mensajes'))


@login_required(login_url='plataforma:login')
def desbloquear_usuario(request, usuario_id):
    if request.method == 'POST':
        Bloqueo.objects.filter(usuario=request.user, bloqueado_id=usuario_id).delete()
        django_messages.success(request, 'Usuario desbloqueado.')

    return redirect(request.META.get('HTTP_REFERER') or reverse('plataforma:mensajes'))


# -----------------------------------------------------------------
# Perfil
# -----------------------------------------------------------------
@login_required(login_url='plataforma:login')
def perfil(request, usuario_id):
    usuario = get_object_or_404(User, id=usuario_id)
    perfil = get_object_or_404(Perfil, user=usuario)
    es_propio = (usuario == request.user)

    mostrar_formulario = es_propio and (request.method == 'POST' or request.GET.get('editar') == '1')

    if request.method == 'POST' and es_propio:
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('plataforma:perfil', usuario_id=usuario.id)
    else:
        form = PerfilForm(instance=perfil)

    grupos_qs = usuario.grupos.all()
    actividades_qs = usuario.actividades_creadas.order_by('-fecha')

    return render(request, 'plataforma/perfil.html', {
        'perfil': perfil,
        'usuario_perfil': usuario,
        'es_propio': es_propio,
        'form': form,
        'mostrar_formulario': mostrar_formulario,
        'grupos_usuario': grupos_qs[:4],
        'total_grupos': grupos_qs.count(),
        'actividades_usuario': actividades_qs[:4],
        'total_actividades': actividades_qs.count(),
    })