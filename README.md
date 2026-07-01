# Conecta

**Conecta** es una plataforma web construida con Django que ayuda a las personas a encontrar actividades, grupos y personas afines a sus intereses. Los usuarios pueden explorar y unirse a grupos temáticos, organizar e inscribirse en actividades, y comunicarse entre ellos mediante mensajería directa.

> *"Pequeñas conexiones, grandes momentos."*

---
## 🛠️ Stack técnico

- **Backend**: Django 5.2
- **Base de datos**: SQLite
- **Frontend**: HTML + Tailwind CSS (vía CDN) + plantillas de Django
- **Autenticación**: sistema de auth incorporado de Django

---

## 📂 Estructura del proyecto

```
Conecta/
├── plataforma/
│   ├── models.py          # Categoria, Perfil, Grupo, Actividad, Conversacion, Mensaje
│   ├── views.py            # Lógica de inicio, actividades, grupos, mensajes, explorar
│   ├── urls.py              # Rutas de la app
│   ├── forms.py             # RegistroForm, ActividadForm, GrupoForm
│   ├── admin.py             # Configuración del panel de administración
│   ├── apps.py
│   ├── management/
│   │   └── commands/
│   │       └── poblar.py    # Comando para poblar datos de prueba
│   └── tests.py
├── templates/
│   ├── base.html             # Layout base (sidebar + topbar)
│   └── plataforma/
│       ├── inicio.html
│       ├── explorar.html
│       ├── actividades.html
│       ├── detalle_actividad.html
│       ├── grupos.html
│       ├── detalle_grupo.html
│       ├── crear_grupo.html
│       ├── mensajes.html
│       ├── registro.html
│       └── login.html
└── manage.py
```

---

## 🗃️ Modelo de datos

| Modelo | Descripción |
|---|---|
| `Categoria` | Categorías temáticas (ej: Música, Deportes, Juegos) con nombre e ícono. |
| `Perfil` | Extensión del usuario de Django: foto, bio e intereses (categorías). |
| `Grupo` | Comunidad temática con nombre, descripción, categoría, imagen y miembros (M2M con `User`). |
| `Actividad` | Evento organizado por un usuario, opcionalmente ligado a un grupo, con fecha, lugar y participantes. |
| `Conversacion` | Conversación entre dos o más usuarios. |
| `Mensaje` | Mensaje individual dentro de una conversación, con estado de leído. |

---

## 🚀 Instalación y ejecución
 
### 1. Clonar el repositorio y crear entorno virtual
 
```bash
git clone <url-del-repositorio>
cd Conecta
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate # macOS/Linux
```
 
### 2. Instalar dependencias
 
```bash
pip install -r requirements.txt
```
 
Dependencias del proyecto (`requirements.txt`):
 
```
asgiref==3.11.1
Django==5.2.15
pillow==12.2.0
sqlparse==0.5.5
tzdata==2026.2
```
 
### 3. Aplicar migraciones
 
```bash
python manage.py makemigrations
python manage.py migrate
```
 
### 4. Poblar datos de prueba (opcional)
 
```bash
python manage.py poblar
```

### 5. Correr el servidor
 
```bash
python manage.py runserver
```
 
Visita [http://127.0.0.1:8000/](http://127.0.0.1:8000/) en tu navegador.
 
Para acceder al panel de administración: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

