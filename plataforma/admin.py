from django.contrib import admin
from .models import Categoria, Perfil, Grupo, Actividad


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono']


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    filter_horizontal = ['intereses']


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'total_miembros', 'creado_en']
    filter_horizontal = ['miembros']


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'fecha', 'lugar', 'organizador', 'total_participantes']
    list_filter = ['categoria', 'fecha']
    filter_horizontal = ['participantes']