from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductAvailabilityTests(TestCase):
	def test_visitor_can_see_active_product_availability(self):
		Product.objects.create(
			name="Riz", category=Product.Category.STARCHES, price="2.50", stock=4
		)

		response = self.client.get(reverse("products"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Riz")
		self.assertContains(response, "4 en stock")
		self.assertContains(response, reverse("signup"))

	def test_inactive_products_are_not_public(self):
		Product.objects.create(
			name="Produit masqué",
			category=Product.Category.STARCHES,
			price="2.50",
			stock=4,
			is_active=False,
		)

		response = self.client.get(reverse("products"))

		self.assertNotContains(response, "Produit masqué")
