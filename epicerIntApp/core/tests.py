from django.core.management import call_command
from django.test import TestCase

from catalog.models import Category, Product
from orders.models import Distribution
from users.models import User

from .management.commands.seed_demo import DEMO_MEMBER_EMAIL, PRODUCTS


class SeedDemoTests(TestCase):
	def test_seed_demo_creates_catalogue_member_and_distribution(self):
		call_command("seed_demo")

		self.assertEqual(Category.objects.count(), 4)
		self.assertEqual(Product.objects.count(), len(PRODUCTS))
		member = User.objects.get(email=DEMO_MEMBER_EMAIL)
		self.assertTrue(member.is_member)
		self.assertTrue(member.check_password("projetinfo1A"))
		self.assertEqual(Distribution.objects.filter(is_active=True).count(), 1)

	def test_seed_demo_is_idempotent(self):
		call_command("seed_demo")
		call_command("seed_demo")

		self.assertEqual(Product.objects.count(), len(PRODUCTS))
		self.assertEqual(User.objects.filter(email=DEMO_MEMBER_EMAIL).count(), 1)
		self.assertEqual(Distribution.objects.filter(is_active=True).count(), 1)
