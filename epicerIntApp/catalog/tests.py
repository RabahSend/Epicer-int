from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from .models import Category, Product


class ProductAvailabilityTests(TestCase):
	def test_product_image_is_saved(self):
		png_image = (
			b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
			b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
			b"\x00\x00\x00\x0bIDAT\x08\xd7c\xf8\x0f\x00\x01\x01"
			b"\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
		)
		with TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				category = Category.objects.create(name="Féculents")
				product = Product.objects.create(
					name="Riz",
					category=category,
					price="2.50",
					image=SimpleUploadedFile(
						"riz.png", png_image, content_type="image/png"
					),
				)

				self.assertEqual(product.image.name, "products/riz.png")
				self.assertTrue(product.image.storage.exists(product.image.name))

	def test_product_image_is_shown_on_catalogue(self):
		png_image = (
			b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
			b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
			b"\x00\x00\x00\x0bIDAT\x08\xd7c\xf8\x0f\x00\x01\x01"
			b"\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82"
		)
		with TemporaryDirectory() as media_root:
			with override_settings(MEDIA_ROOT=media_root):
				category = Category.objects.create(name="Féculents")
				product = Product.objects.create(
					name="Riz",
					category=category,
					price="2.50",
					image=SimpleUploadedFile(
						"riz.png", png_image, content_type="image/png"
					),
				)

				response = self.client.get(reverse("products"))

				self.assertContains(response, product.image.url)
				self.assertContains(response, 'alt="Riz"')

	def test_visitor_can_see_active_product_availability(self):
		category = Category.objects.create(name="Féculents")
		Product.objects.create(
			name="Riz", category=category, price="2.50", stock=4
		)

		response = self.client.get(reverse("products"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Riz")
		self.assertContains(response, "4 en stock")
		self.assertContains(response, reverse("signup"))

	def test_inactive_products_are_not_public(self):
		category = Category.objects.create(name="Féculents")
		Product.objects.create(
			name="Produit masqué",
			category=category,
			price="2.50",
			stock=4,
			is_active=False,
		)

		response = self.client.get(reverse("products"))

		self.assertNotContains(response, "Produit masqué")
