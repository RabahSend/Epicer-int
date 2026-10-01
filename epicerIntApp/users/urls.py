from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import ProfilePage, SignupPage

urlpatterns = [
    path(
        "connexion/",
        LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "inscription/",
        SignupPage.as_view(),
        name="signup",
    ),
    path(
        "deconnexion/",
        LogoutView.as_view(template_name="users/logout.html"),
        name="logout",
    ),
    path(
        "profil/",
        ProfilePage.as_view(),
        name="profile",
    ),
]