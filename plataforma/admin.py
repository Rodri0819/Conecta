from django.contrib import admin
from .models import Categoria, Perfil, Grupo, Actividad, Reporte, Bloqueo


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'icono']


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'edad', 'verificado', 'suspendido', 'acepto_terminos']
    list_filter = ['verificado', 'suspendido', 'acepto_terminos']
    filter_horizontal = ['intereses']
    actions = ['marcar_verificado', 'marcar_suspendido']

    @admin.action(description='Marcar cuentas seleccionadas como verificadas')
    def marcar_verificado(self, request, queryset):
        queryset.update(verificado=True)

    @admin.action(description='Suspender cuentas seleccionadas')
    def marcar_suspendido(self, request, queryset):
        queryset.update(suspendido=True)


@admin.register(Grupo)
class GrupoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'total_miembros', 'creado_en']
    filter_horizontal = ['miembros']


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'categoria', 'fecha', 'lugar', 'organizador', 'total_participantes']
    list_filter = ['categoria', 'fecha']
    filter_horizontal = ['participantes']


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['usuario_reportado', 'motivo', 'reportante', 'fecha', 'revisado']
    list_filter = ['motivo', 'revisado']
    search_fields = ['usuario_reportado__username', 'reportante__username']
    readonly_fields = ['reportante', 'usuario_reportado', 'motivo', 'descripcion', 'fecha']
    actions = ['marcar_revisado']

    @admin.action(description='Marcar reportes seleccionados como revisados')
    def marcar_revisado(self, request, queryset):
        queryset.update(revisado=True)


@admin.register(Bloqueo)
class BloqueoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'bloqueado', 'fecha']