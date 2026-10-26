from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from catalog.models import Category, Product
from orders.models import Distribution, Order
from orders.services import create_order_from_cart
from users.models import User


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


class DistributionManagementTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			email="admin@example.com",
			password="secure-test-password",
			is_staff=True,
		)
		self.member = User.objects.create_user(
			email="member@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.distribution_data = {
			"starts_at": "2026-10-26T10:00",
			"ends_at": "2026-10-26T12:00",
			"location": "C206",
		}

	def test_visitor_is_sent_to_login(self):
		url = reverse("distributions")

		response = self.client.get(url)

		self.assertRedirects(response, f"{reverse('login')}?next={url}")

	def test_member_cannot_manage_distributions(self):
		self.client.force_login(self.member)

		response = self.client.get(reverse("distributions"), follow=True)

		self.assertRedirects(response, reverse("home"))
		self.assertContains(response, "Cette page est réservée aux administrateurs.")
		self.assertNotContains(response, reverse("distributions"))

	def test_admin_creates_a_closed_distribution(self):
		self.client.force_login(self.admin)
		already_open = Distribution.objects.create(
			starts_at=timezone.now(),
			location="A101",
			is_active=True,
		)

		response = self.client.post(reverse("distribution_create"), self.distribution_data)

		self.assertRedirects(response, reverse("distributions"))
		created = Distribution.objects.exclude(pk=already_open.pk).get()
		self.assertEqual(created.location, "C206")
		self.assertEqual(created.starts_at, self.aware(2026, 10, 26, 10, 0))
		self.assertEqual(created.ends_at, self.aware(2026, 10, 26, 12, 0))
		self.assertFalse(created.is_active)
		already_open.refresh_from_db()
		self.assertTrue(already_open.is_active)

	def test_admin_rejects_an_end_before_the_start(self):
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse("distribution_create"),
			{
				"starts_at": "2026-10-26T12:00",
				"ends_at": "2026-10-26T10:00",
				"location": "C206",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "La fin de la distribution ne peut pas être antérieure au début.")
		self.assertEqual(Distribution.objects.count(), 0)

	def test_admin_can_create_a_distribution_without_an_end(self):
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse("distribution_create"),
			{"starts_at": "2026-10-26T10:00", "ends_at": "", "location": "C206"},
		)

		self.assertRedirects(response, reverse("distributions"))
		distribution = Distribution.objects.get()
		self.assertIsNone(distribution.ends_at)

	def test_admin_updates_a_distribution_without_changing_its_status(self):
		self.client.force_login(self.admin)
		distribution = Distribution.objects.create(
			starts_at=self.aware(2026, 10, 26, 10, 0),
			ends_at=self.aware(2026, 10, 26, 12, 0),
			location="C206",
			is_active=True,
		)

		response = self.client.post(
			reverse("distribution_edit", args=[distribution.pk]),
			{
				"starts_at": "2026-10-27T09:00",
				"ends_at": "2026-10-27T11:00",
				"location": "C207",
			},
		)

		self.assertRedirects(response, reverse("distributions"))
		distribution.refresh_from_db()
		self.assertEqual(distribution.location, "C207")
		self.assertEqual(distribution.starts_at, self.aware(2026, 10, 27, 9, 0))
		self.assertEqual(distribution.ends_at, self.aware(2026, 10, 27, 11, 0))
		self.assertTrue(distribution.is_active)

	def test_opening_a_distribution_closes_the_previous_one(self):
		self.client.force_login(self.admin)
		previous = Distribution.objects.create(
			starts_at=self.aware(2026, 10, 20, 10, 0),
			location="C206",
			is_active=True,
		)
		current = Distribution.objects.create(
			starts_at=self.aware(2026, 10, 26, 10, 0),
			location="C207",
			is_active=False,
		)

		response = self.client.post(reverse("distribution_open", args=[current.pk]))

		self.assertRedirects(response, reverse("distributions"))
		previous.refresh_from_db()
		current.refresh_from_db()
		self.assertFalse(previous.is_active)
		self.assertTrue(current.is_active)

	def test_admin_closes_a_distribution(self):
		self.client.force_login(self.admin)
		distribution = Distribution.objects.create(
			starts_at=timezone.now(),
			location="C206",
			is_active=True,
		)

		response = self.client.post(reverse("distribution_close", args=[distribution.pk]))

		self.assertRedirects(response, reverse("distributions"))
		distribution.refresh_from_db()
		self.assertFalse(distribution.is_active)

	def test_new_orders_attach_to_the_opened_distribution(self):
		category = Category.objects.create(name="Féculents")
		product = Product.objects.create(
			name="Pâtes", category=category, price="1.50", stock=3
		)
		previous = Distribution.objects.create(
			starts_at=self.aware(2026, 10, 20, 10, 0),
			location="C206",
			is_active=True,
		)
		current = Distribution.objects.create(
			starts_at=self.aware(2026, 10, 26, 10, 0),
			location="C207",
			is_active=False,
		)
		self.client.force_login(self.admin)
		self.client.post(reverse("distribution_open", args=[current.pk]))

		order = create_order_from_cart(self.member, {str(product.pk): 1})

		self.assertEqual(order.distribution, current)
		previous.refresh_from_db()
		self.assertFalse(previous.is_active)

	def aware(self, year, month, day, hour, minute):
		return timezone.make_aware(
			datetime(year, month, day, hour, minute),
			timezone.get_current_timezone(),
		)