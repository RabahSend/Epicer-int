from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product
from users.models import User

from django.utils import timezone

from orders.models import Distribution, Order
from orders.services import mark_order_as_picked_up


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

class MarkOrderAsPickedUpTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			email="member@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.distribution = Distribution.objects.create(
			starts_at=timezone.now(),
			location="C206",
		)

	def make_order(self, status):
		return Order.objects.create(
			user=self.user,
			distribution=self.distribution,
			status=status,
		)

	def test_paid_order_is_marked_picked_up(self):
		order = self.make_order(Order.Status.PAID)

		self.assertTrue(mark_order_as_picked_up(order))
		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PICKED_UP)
		self.assertIsNotNone(order.picked_up_at)

	def test_ready_order_is_marked_picked_up(self):
		order = self.make_order(Order.Status.READY)

		self.assertTrue(mark_order_as_picked_up(order))
		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PICKED_UP)
		self.assertIsNotNone(order.picked_up_at)

	def test_pending_cancelled_and_picked_up_orders_are_refused(self):
		for status in (Order.Status.PENDING, Order.Status.CANCELLED, Order.Status.PICKED_UP):
			with self.subTest(status=status):
				order = self.make_order(status)

				self.assertFalse(mark_order_as_picked_up(order))
				order.refresh_from_db()
				self.assertEqual(order.status, status)
				self.assertIsNone(order.picked_up_at)