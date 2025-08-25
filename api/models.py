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
    mostrar_elecciones = models.BooleanField(default=False)  # <-- nuevo campo

class Participante(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    quiniela = models.ForeignKey(Quiniela, on_delete=models.CASCADE, related_name='participantes')
    ya_selecciono = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.username
    
class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=5)
    ciudad = models.CharField(max_length=100)
    logo_url = models.URLField()

    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"

class Partido(models.Model):
    quiniela = models.ForeignKey(Quiniela, on_delete=models.CASCADE, related_name="partidos")
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="partidos_local")
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name="partidos_visitante")
    fecha = models.DateTimeField(null=True, blank=True)
    resultado_real = models.ForeignKey(Equipo, null=True, blank=True, on_delete=models.SET_NULL, related_name='partidos_ganados')

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.quiniela.nombre}"

class Eleccion(models.Model):
    participante = models.ForeignKey(Participante, related_name='elecciones', on_delete=models.CASCADE)
    partido = models.ForeignKey(Partido, related_name='elecciones', on_delete=models.CASCADE)
    equipo_elegido = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('participante', 'partido')  # No puede votar dos veces el mismo participante por el mismo partido

    def __str__(self):
        return f"{self.participante.usuario.username} eligió {self.equipo_elegido} en {self.partido}"

class FCMToken(models.Model):
    """
    Modelo para almacenar tokens de Firebase Cloud Messaging de los usuarios
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fcm_tokens')
    token = models.CharField(max_length=500, unique=True)
    dispositivo = models.CharField(max_length=100, blank=True, null=True)
    plataforma = models.CharField(max_length=20, choices=[
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
        ('unknown', 'Desconocido')
    ], default='unknown')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Token FCM'
        verbose_name_plural = 'Tokens FCM'
        ordering = ['-ultima_actividad']

    def __str__(self):
        return f"{self.usuario.username} - {self.plataforma} ({self.dispositivo})"
    