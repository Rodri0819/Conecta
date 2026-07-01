from django.db import models
from django.contrib.auth.models import User


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

    def __str__(self):
        return self.user.username


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