from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "plataforma"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("registro/", views.registro, name="registro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="plataforma/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="plataforma:login"),
        name="logout",
    ),
    path("actividades/", views.actividades, name="actividades"),
    path("actividades/crear/", views.crear_actividad, name="crear_actividad"),
    path(
        "actividades/<int:actividad_id>/",
        views.detalle_actividad,
        name="detalle_actividad",
    ),
    path("mensajes/", views.mensajes, name="mensajes"),
    path(
        "mensajes/<int:conversacion_id>/enviar/",
        views.enviar_mensaje,
        name="enviar_mensaje",
    ),
    path(
        "mensajes/iniciar/<int:usuario_id>/",
        views.iniciar_conversacion,
        name="iniciar_conversacion",
    ),
    path("grupos/", views.grupos, name="grupos"),
    path("grupos/crear/", views.crear_grupo, name="crear_grupo"),
    path("grupos/<int:grupo_id>/", views.detalle_grupo, name="detalle_grupo"),
    path("grupos/<int:grupo_id>/unirse/", views.unirse_grupo, name="unirse_grupo"),
    path("grupos/<int:grupo_id>/salir/", views.salir_grupo, name="salir_grupo"),
    path("explorar/", views.explorar, name="explorar"),

    # Seguridad: reportes y bloqueos
    path("usuarios/<int:usuario_id>/reportar/", views.reportar_usuario, name="reportar_usuario"),
    path("usuarios/<int:usuario_id>/bloquear/", views.bloquear_usuario, name="bloquear_usuario"),
    path("usuarios/<int:usuario_id>/desbloquear/", views.desbloquear_usuario, name="desbloquear_usuario"),

    #Perfil
    path("perfil/<int:usuario_id>/", views.perfil, name="perfil"),

    # Eliminación de grupos y actividades
    path("grupos/<int:grupo_id>/eliminar/", views.eliminar_grupo, name="eliminar_grupo"),
    path("actividades/<int:actividad_id>/eliminar/", views.eliminar_actividad, name="eliminar_actividad"),
]