from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from .forms import SignupForm

class ProfilePage(TemplateView):
    template_name = "users/profile.html"

class SignupPage(CreateView):
    template_name = "users/signup.html"
    form_class = SignupForm
    success_url = reverse_lazy("login")