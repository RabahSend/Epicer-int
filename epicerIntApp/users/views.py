from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import SignupForm


class SignupPage(CreateView):
	template_name = "users/signup_form.html"
	form_class = SignupForm
	success_url = reverse_lazy("profile")

	def form_valid(self, form):
		response = super().form_valid(form)
		login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
		messages.info(
			self.request,
			"Votre compte est créé. La cotisation doit être validée par l'association avant de commander.",
		)
		return response


class SigninPage(LoginView):
	template_name = "users/login_form.html"


class ProfilePage(LoginRequiredMixin, TemplateView):
	template_name = "users/profile.html"
