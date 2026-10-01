from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import ProfilePage, SigninPage, SignupPage

urlpatterns = [
	path("connexion/", SigninPage.as_view(), name="login"),
	path("inscription/", SignupPage.as_view(), name="signup"),
	path("deconnexion/", LogoutView.as_view(), name="logout"),
	path("profil/", ProfilePage.as_view(), name="profile"),
]
