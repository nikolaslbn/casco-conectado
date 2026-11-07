from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    edad = models.IntegerField(default=18)
    nombre_negocio = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.usuario.email

class Alerta(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    categoria = models.CharField(max_length=50)
    urgencia = models.CharField(max_length=20)
    armas = models.BooleanField(default=False)
    lat = models.FloatField()
    lon = models.FloatField()
    direccion = models.CharField(max_length=255, default="Valparaíso")
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.categoria} ({self.urgencia})"