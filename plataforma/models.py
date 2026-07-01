from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Categoria(models.Model):
    nombre = models.CharField(max_length=50)
    icono = models.CharField(max_length=50, blank=True)  # ej: "music", "gamepad", nombre de icono

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    intereses = models.ManyToManyField(Categoria, related_name='interesados', blank=True)

    fecha_nacimiento = models.DateField(null=True, blank=True)
    acepto_terminos = models.BooleanField(default=False)
    documento_identidad = models.ImageField(
        upload_to='identificaciones/', blank=True, null=True,
        help_text='Documento subido por el usuario para verificación manual.'
    )
    verificado = models.BooleanField(
        default=False,
        help_text='Se marca en True solo cuando un administrador revisó y aprobó el documento.'
    )
    suspendido = models.BooleanField(
        default=False,
        help_text='Cuenta suspendida por un administrador tras un reporte.'
    )

    def __str__(self):
        return self.user.username

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = timezone.now().date()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
    
class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    imagen = models.ImageField(upload_to='grupos/', blank=True, null=True)
    miembros = models.ManyToManyField(User, related_name='grupos', blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    @property
    def total_miembros(self):
        return self.miembros.count()


class Actividad(models.Model):
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    grupo = models.ForeignKey(
        Grupo, on_delete=models.CASCADE, null=True, blank=True, related_name='actividades'
    )
    imagen = models.ImageField(upload_to='actividades/', blank=True, null=True)
    lugar = models.CharField(max_length=150, blank=True)
    fecha = models.DateTimeField()
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actividades_creadas')
    participantes = models.ManyToManyField(User, related_name='actividades_inscritas', blank=True)

    def __str__(self):
        return self.titulo

    @property
    def total_participantes(self):
        return self.participantes.count()

class Conversacion(models.Model):
    participantes = models.ManyToManyField(User, related_name='conversaciones')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']

    def __str__(self):
        nombres = ", ".join(u.username for u in self.participantes.all())
        return f"Conversación: {nombres}"

    def otro_participante(self, usuario):
        """Devuelve el otro usuario de una conversación 1 a 1."""
        return self.participantes.exclude(id=usuario.id).first()


class Mensaje(models.Model):
    conversacion = models.ForeignKey(
        Conversacion, on_delete=models.CASCADE, related_name='mensajes'
    )
    autor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='mensajes_enviados'
    )
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f'{self.autor}: {self.contenido[:30]}'


class Reporte(models.Model):
    MOTIVO_CHOICES = [
        ('acoso', 'Acoso o comportamiento inapropiado'),
        ('suplantacion', 'Suplantación de identidad'),
        ('contenido', 'Contenido inapropiado u ofensivo'),
        ('menor_riesgo', 'Sospecha de riesgo hacia un menor'),
        ('spam', 'Spam o cuenta falsa'),
        ('otro', 'Otro motivo'),
    ]

    reportante = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reportes_hechos'
    )
    usuario_reportado = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reportes_recibidos'
    )
    motivo = models.CharField(max_length=20, choices=MOTIVO_CHOICES)
    descripcion = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    revisado = models.BooleanField(default=False)
    accion_tomada = models.TextField(blank=True, help_text='Notas del administrador tras revisar.')

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Reporte de {self.reportante} sobre {self.usuario_reportado} ({self.get_motivo_display()})'


class Bloqueo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bloqueos_hechos')
    bloqueado = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bloqueos_recibidos')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'bloqueado')

    def __str__(self):
        return f'{self.usuario} bloqueó a {self.bloqueado}'
