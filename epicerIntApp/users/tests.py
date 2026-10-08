from django.test import TestCase
from django.urls import reverse

from .models import User


class SignupTests(TestCase):
	def test_signup_creates_non_member_account(self):
		response = self.client.post(
			reverse("signup"),
			{"email": "visitor@example.com", "password1": "secure-test-password", "password2": "secure-test-password"},
		)

		self.assertRedirects(response, reverse("profile"))
		user = User.objects.get(email="visitor@example.com")
		self.assertFalse(user.is_member)
		self.assertTrue(user.is_authenticated)

	def test_profile_requires_authentication(self):
		response = self.client.get(reverse("profile"))

		self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")
