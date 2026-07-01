from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "plataforma"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("registro/", views.registro, name="registro"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="plataforma/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="plataforma:login"),
        name="logout",
    ),
]