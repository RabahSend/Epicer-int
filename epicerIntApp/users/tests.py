from django.test import TestCase
from django.urls import reverse

from .models import User


class SignupTests(TestCase):
	def test_signup_creates_non_member_account(self):
		response = self.client.post(
			reverse("signup"),
			{
				"first_name": "Adel",
				"last_name": "Khaldoun",
				"email": "visitor@example.com",
				"password1": "secure-test-password",
				"password2": "secure-test-password",
			},
		)

		self.assertRedirects(response, reverse("profile"))
		user = User.objects.get(email="visitor@example.com")
		self.assertEqual(user.first_name, "Adel")
		self.assertEqual(user.last_name, "Khaldoun")
		self.assertFalse(user.is_member)
		self.assertTrue(user.is_authenticated)

	def test_profile_requires_authentication(self):
		response = self.client.get(reverse("profile"))

		self.assertRedirects(response, f"{reverse('login')}?next={reverse('profile')}")


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="member@example.com",
            password="secure-test-password",
            first_name="Ancien",
            last_name="Nom",
        )
        self.client.force_login(self.user)

    def test_user_can_update_first_name_and_last_name(self):
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Nouveau",
                "last_name": "Nom modifié",
            },
        )

        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Nouveau")
        self.assertEqual(self.user.last_name, "Nom modifié")

    def test_email_and_membership_cannot_be_updated_from_profile(self):
        response = self.client.post(
            reverse("profile"),
            {
                "first_name": "Nouveau",
                "last_name": "Nom",
                "email": "changed@example.com",
                "is_member": True,
            },
        )

        self.assertRedirects(response, reverse("profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "member@example.com")
        self.assertFalse(self.user.is_member)

    def test_profile_displays_account_information(self):
        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "member@example.com")
        self.assertContains(response, "En attente de validation")
        self.assertContains(response, f'href="{reverse("orders")}"')
