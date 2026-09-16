from django.urls import path

from users.presentation.views import UserView

urlpatterns = [
    path("", UserView.as_view(), name="user-list"),
]
