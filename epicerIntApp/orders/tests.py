from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from catalog.models import Category, Product
from orders.models import Distribution, Order
from users.models import User
from decimal import Decimal


class CartAccessTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name="Féculents")
		self.product = Product.objects.create(
			name="Pâtes", category=category, price="1.50", stock=3
		)
		self.add_url = reverse("add_to_cart", args=[self.product.pk])

	def test_visitor_is_sent_to_signup_when_adding_product(self):
		response = self.client.post(self.add_url, {"quantity": 1})

		self.assertRedirects(response, reverse("signup"))
		self.assertNotIn("cart", self.client.session)

	def test_non_member_cannot_add_product(self):
		user = User.objects.create_user(email="visitor@example.com", password="secure-test-password")
		self.client.force_login(user)

		response = self.client.post(self.add_url, {"quantity": 1})

		self.assertRedirects(response, reverse("profile"))
		self.assertNotIn("cart", self.client.session)

	def test_member_can_add_only_available_quantity(self):
		user = User.objects.create_user(
			email="member@example.com", password="secure-test-password", is_member=True
		)
		self.client.force_login(user)

		response = self.client.post(self.add_url, {"quantity": 2})

		self.assertRedirects(response, reverse("cart"))
		self.assertEqual(self.client.session["cart"], {str(self.product.pk): 2})

		response = self.client.post(self.add_url, {"quantity": 2})

		self.assertRedirects(response, reverse("products"))
		self.assertEqual(self.client.session["cart"], {str(self.product.pk): 2})

class PlaceOrderTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name="Féculents")
		self.product = Product.objects.create(
			name="Pâtes", category=category, price="1.50", stock=3
		)
		self.user = User.objects.create_user(
			email="member@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.distribution = Distribution.objects.create(
			starts_at=timezone.now(),
			location="C206",
			is_active=True,
		)
		self.client.force_login(self.user)
		session = self.client.session
		session["cart"] = {str(self.product.pk): 2}
		session.save()

	def test_member_places_order_from_cart(self):
		response = self.client.post(reverse("place_order"))

		self.assertRedirects(response, reverse("orders"))
		order = Order.objects.get()
		self.assertEqual(order.user, self.user)
		self.assertEqual(order.distribution, self.distribution)
		self.assertEqual(order.status, Order.Status.PENDING)
		item = order.items.get()
		self.assertEqual(item.product, self.product)
		self.assertEqual(item.quantity, 2)
		self.assertEqual(item.unit_price, Decimal("1.50"))
		self.assertEqual(self.client.session.get("cart", {}), {})
		self.product.refresh_from_db()
		self.assertEqual(self.product.stock, 3)

	def test_member_cannot_place_order_without_active_distribution(self):
		self.distribution.is_active = False
		self.distribution.save()

		response = self.client.post(reverse("place_order"))

		self.assertRedirects(response, reverse("cart"))
		self.assertEqual(Order.objects.count(), 0)
		self.assertEqual(self.client.session["cart"], {str(self.product.pk): 2})

	def test_member_cannot_place_order_with_empty_cart(self):
		session = self.client.session
		session["cart"] = {}
		session.save()

		response = self.client.post(reverse("place_order"))

		self.assertRedirects(response, reverse("cart"))
		self.assertEqual(Order.objects.count(), 0)

	def test_cart_page_offers_order_validation(self):
		response = self.client.get(reverse("cart"))

		self.assertContains(response, "Valider la commande")

	def test_orders_page_shows_only_the_members_orders(self):
		self.client.post(reverse("place_order"))

		response = self.client.get(reverse("orders"))

		self.assertContains(response, "Pâtes x 2")
		self.assertContains(response, "En attente de paiement")

		other = User.objects.create_user(
			email="other@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.client.force_login(other)
		response = self.client.get(reverse("orders"))

		self.assertNotContains(response, "Pâtes")
		self.assertContains(response, "Vous n'avez pas encore de commande.")