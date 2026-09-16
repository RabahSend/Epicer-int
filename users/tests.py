from django.test import TestCase

from users.business.rules import InvalidUserError, validate_user


class UserBusinessTests(TestCase):
    def test_validate_user_accepts_valid_email_and_name(self):
        validate_user("ada@telecom-sudparis.eu", "Ada", "")

    def test_validate_user_rejects_invalid_email(self):
        with self.assertRaises(InvalidUserError):
            validate_user("invalid", "Ada", "")


class UserApiTests(TestCase):
    def test_list_users_starts_empty(self):
        response = self.client.get("/api/users/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"users": []})

    def test_register_user(self):
        response = self.client.post(
            "/api/users/",
            data={
                "email": "ada@telecom-sudparis.eu",
                "first_name": "Ada",
                "last_name": "Lovelace",
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["email"], "ada@telecom-sudparis.eu")
