from io import BytesIO
from tempfile import TemporaryDirectory

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test import override_settings
from django.urls import reverse
from PIL import Image

from .models import Category, Product


def create_test_image():
	image = Image.new("RGB", (1, 1), color="white")
	buffer = BytesIO()
	image.save(buffer, format="PNG")
	return buffer.getvalue()


class ProductAvailabilityTests(TestCase):
	def test_product_image_is_saved(self):
		png_image = create_test_image()
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
		png_image = create_test_image()
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

	def test_products_are_grouped_under_their_category(self):
		pasta_category = Category.objects.create(name="Féculents")
		dairy_category = Category.objects.create(name="Produits laitiers")
		Product.objects.create(
			name="Riz", category=pasta_category, price="2.50", stock=4
		)
		Product.objects.create(
			name="Lait", category=dairy_category, price="1.20", stock=3
		)

		response = self.client.get(reverse("products"))

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'id="category-%s"' % pasta_category.pk)
		self.assertContains(response, 'id="category-%s"' % dairy_category.pk)
		self.assertLess(
			response.content.index(b"F\xc3\xa9culents"),
			response.content.index(b"Riz"),
		)
		self.assertLess(
			response.content.index(b"Produits laitiers"),
			response.content.index(b"Lait"),
		)

	def test_categories_without_active_products_are_not_shown(self):
		category = Category.objects.create(name="Catégorie vide")

		response = self.client.get(reverse("products"))

		self.assertNotContains(response, category.name)

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
