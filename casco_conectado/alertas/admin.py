from django.contrib import admin
from .models import Perfil

# Registramos la tabla para verla en el panel de control
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'edad', 'nombre_negocio')