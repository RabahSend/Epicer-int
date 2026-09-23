from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path(
        "connexion/",
        LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "deconnexion/",
        LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
]