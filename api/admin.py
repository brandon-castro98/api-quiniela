from django.contrib import admin
from .models import Quiniela, Participante, Partido, Eleccion, Equipo, FCMToken

@admin.register(Quiniela)
class QuinielaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'creada_por', 'apuesta_individual', 'fecha_creacion', 'mostrar_elecciones']
    list_filter = ['fecha_creacion', 'mostrar_elecciones', 'creada_por']
    search_fields = ['nombre', 'creada_por__username']
    readonly_fields = ['fecha_creacion']
    list_per_page = 20

@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'quiniela', 'ya_selecciono']
    list_filter = ['ya_selecciono', 'quiniela']
    search_fields = ['usuario__username', 'quiniela__nombre']
    list_per_page = 20

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ['quiniela', 'equipo_local', 'equipo_visitante', 'fecha', 'resultado_real']
    list_filter = ['quiniela', 'fecha', 'resultado_real']
    search_fields = ['quiniela__nombre', 'equipo_local__nombre', 'equipo_visitante__nombre']
    list_per_page = 20

@admin.register(Eleccion)
class EleccionAdmin(admin.ModelAdmin):
    list_display = ['participante', 'partido', 'equipo_elegido']
    list_filter = ['equipo_elegido', 'partido__quiniela']
    search_fields = ['participante__usuario__username', 'partido__quiniela__nombre']
    list_per_page = 20

@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'abreviatura', 'ciudad']
    list_filter = ['ciudad']
    search_fields = ['nombre', 'abreviatura', 'ciudad']
    list_per_page = 20

@admin.register(FCMToken)
class FCMTokenAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'plataforma', 'dispositivo', 'activo', 'fecha_creacion', 'ultima_actividad']
    list_filter = ['plataforma', 'activo', 'fecha_creacion']
    search_fields = ['usuario__username', 'usuario__email', 'dispositivo']
    readonly_fields = ['fecha_creacion', 'ultima_actividad']
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
