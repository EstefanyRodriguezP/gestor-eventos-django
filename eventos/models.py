from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    privado = models.BooleanField(default=False)
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos_creados')
    asistentes = models.ManyToManyField(User, related_name='eventos_asistidos', blank=True)

    def __str__(self):
        return self.titulo