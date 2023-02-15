from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import FileExtensionValidator

from eventos.models import Evento

# Create your models here.


class Usuario(AbstractUser):
    first_name = models.CharField(max_length=200, null=True)
    def __str__(self):
        return self.username


class Asambleista(Usuario):
    inmueble = models.CharField(max_length=500, blank=True, null=True)
    coeficiente = models.DecimalField(
        max_digits=30, decimal_places=20, blank=True, null=True)
    coeficientePoderesDia = models.DecimalField(
        max_digits=30, decimal_places=20, default=0.0)
    coeficienteTotal = models.DecimalField(
        max_digits=30, decimal_places=20, default=0.0)
    documento = models.CharField(max_length=120, blank=True, null=True)
    celular = models.CharField(blank=True, null=True, max_length=150)
    mora = models.BooleanField(default=False)
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, blank=True, null=True)
    tiene_representante = models.BooleanField(default=False)
    quorumStatus = models.BooleanField(default=False)
    nombre_completo = models.CharField(max_length=200)
    correo_enviado = models.BooleanField(default=False)
    cantidadPoderes = models.IntegerField(default=0)
    propietario = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'asambleista'
        verbose_name_plural = 'asambleistas'
        ordering = ['inmueble']

    def __str__(self):
        if self.is_staff:
            return self.username
        else:
            try:
                return self.inmueble + ' - ' + self.nombre_completo
            except:
                return self.inmueble + ' - ' + self.first_name
        


doc_poder_ext = ['pdf', 'PDF', 'JPEG', 'JPG', 'PNG', 'png', 'jpg', 'jpeg']


class Apoderado(models.Model):
    evento = models.ForeignKey(
        Evento, on_delete=models.CASCADE, related_name='poder_evento', null=True)
    representa_a = models.ForeignKey(
        Asambleista, on_delete=models.CASCADE, related_name='representa_a', null=True, blank=True)
    representado_por = models.ForeignKey(
        Asambleista, on_delete=models.CASCADE, null=True, related_name='representado_por')
    validado = models.BooleanField(default=False)
    documento_poder = models.FileField(upload_to='poderes/', validators=[
                                       FileExtensionValidator(allowed_extensions=doc_poder_ext)], null=False, blank=True)
    sumado = models.BooleanField(default=False)
    externo = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'apoderado'
        verbose_name_plural = 'apoderados'
