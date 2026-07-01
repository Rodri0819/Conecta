from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from plataforma.models import Categoria, Actividad, Perfil, Grupo
from django.utils import timezone


class Command(BaseCommand):
    help = 'Pobla la base de datos con categorías, grupos y actividades de prueba de la UdeC'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando la población de datos...')

        # 1. Crear Categorías tal como aparecen en el prototipo
        datos_categorias = [
            {"nombre": "Arte y creatividad", "icono": "🎨"},
            {"nombre": "Música", "icono": "🎵"},
            {"nombre": "Juegos", "icono": "🎮"},
            {"nombre": "Deportes", "icono": "⚽"},
            {"nombre": "Lectura", "icono": "📚"},
            {"nombre": "Tecnología", "icono": "💻"},
        ]

        categorias_creadas = {}
        for cat in datos_categorias:
            obj, created = Categoria.objects.get_or_create(nombre=cat["nombre"], defaults={"icono": cat["icono"]})
            categorias_creadas[cat["nombre"]] = obj
            if created:
                self.stdout.write(f'Categoría creada: {cat["nombre"]}')

        # 2. Obtener o crear un usuario administrador para asociarlo como organizador
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.create_superuser('admin_udec', 'admin@udec.cl', 'conecta2026')
            self.stdout.write('Superusuario "admin_udec" creado de forma automática (Clave: conecta2026).')

        # Asegurar que el admin tenga su Perfil (tu modelo se llama Perfil)
        Perfil.objects.get_or_create(user=admin_user)

        # 3. Crear los Grupos Sugeridos del documento
        datos_grupos = [
            {"nombre": "Gamers chill", "descripcion": "Jugamos de todo un poco.",
             "categoria": categorias_creadas["Juegos"]},
            {"nombre": "Amantes del cine", "descripcion": "Espacio para discutir películas.",
             "categoria": categorias_creadas["Arte y creatividad"]},
            {"nombre": "Fotografía urbana", "descripcion": "Rutas fotográficas.",
             "categoria": categorias_creadas["Arte y creatividad"]},
            {"nombre": "Cocina creativa", "descripcion": "Compartir recetas.",
             "categoria": categorias_creadas["Arte y creatividad"]},
            {"nombre": "Skate & amigos", "descripcion": "Rutas, trucos y buena vibra.",
             "categoria": categorias_creadas["Deportes"]},
        ]

        grupos_creados = {}
        for grp in datos_grupos:
            obj, created = Grupo.objects.get_or_create(
                nombre=grp["nombre"],
                defaults={"descripcion": grp["descripcion"], "categoria": grp["categoria"]}
            )
            grupos_creados[grp["nombre"]] = obj
            if created:
                self.stdout.write(f'Grupo creado: {grp["nombre"]}')

        # 4. Crear las Actividades vinculadas a los grupos
        ahora = timezone.now()

        datos_actividades = [
            {
                "titulo": "Taller de acuarela",
                "descripcion": "Taller práctico presencial.",
                "categoria": categorias_creadas["Arte y creatividad"],
                "grupo": grupos_creados["Cocina creativa"],  # Vinculado a un grupo por integridad
                "lugar": "Centro Cultural Creative",
            },
            {
                "titulo": "Tarde de videojuegos",
                "descripcion": "Instancia para compartir partidas.",
                "categoria": categorias_creadas["Juegos"],
                "grupo": grupos_creados["Gamers chill"],
                "lugar": "Espacio Joven",
            },
            {
                "titulo": "Caminata en grupo",
                "descripcion": "Actividad al aire libre.",
                "categoria": categorias_creadas["Deportes"],
                "grupo": grupos_creados["Skate & amigos"],
                "lugar": "Parque Central",
            }
        ]

        for act in datos_actividades:
            obj, created = Actividad.objects.get_or_create(
                titulo=act["titulo"],
                defaults={
                    "descripcion": act["descripcion"],
                    "categoria": act["categoria"],
                    "grupo": act["grupo"],
                    "lugar": act["lugar"],
                    "fecha": ahora,
                    "organizador": admin_user
                }
            )
            if created:
                self.stdout.write(f'Actividad creada: {act["titulo"]}')

        self.stdout.write(self.style.SUCCESS('¡Base de datos poblada con éxito con tus modelos reales!'))