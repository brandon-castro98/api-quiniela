from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass

class Quiniela(models.Model):
    nombre = models.CharField(max_length=100)
    apuesta_individual = models.DecimalField(max_digits=10, decimal_places=2)
    creada_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quinielas_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(null=True, blank=True)
    mostrar_elecciones = models.BooleanField(default=True)  # <-- nuevo campo

class Participante(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    quiniela = models.ForeignKey(Quiniela, on_delete=models.CASCADE, related_name='participantes')
    ya_selecciono = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username

class Partido(models.Model):
    quiniela = models.ForeignKey(Quiniela, on_delete=models.CASCADE, related_name='partidos')
    equipo_local = models.CharField(max_length=50)
    equipo_visitante = models.CharField(max_length=50)
    resultado_real = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante}"

class Eleccion(models.Model):
    participante = models.ForeignKey(Participante, related_name='elecciones', on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, related_name='elecciones', on_delete=models.CASCADE)
    equipo_elegido = models.CharField(max_length=100)

    class Meta:
        unique_together = ('participante', 'partido')  # No puede votar dos veces el mismo participante por el mismo partido

    def __str__(self):
        return f"{self.participante.usuario.username} eligió {self.equipo_elegido} en {self.partido}"