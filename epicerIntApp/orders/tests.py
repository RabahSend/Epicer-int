from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from catalog.models import Category, Product
from orders.models import Distribution, Order
from orders.services import (
	create_order_from_cart,
	mark_order_as_picked_up,
	mark_order_as_ready,
)
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
		)
		self.distribution.is_active = True
		self.distribution.save()
		self.client.force_login(self.user)
		session = self.client.session
		session["cart"] = {str(self.product.pk): 2}
		session.save()

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



class DistributionOrdersTests(TestCase):
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
		self.picked_up_member = User.objects.create_user(
			email="picked-up@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.ready_member = User.objects.create_user(
			email="ready@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.distribution = Distribution.objects.create(
			starts_at=timezone.now(),
			location="C206",
		)
		self.other_distribution = Distribution.objects.create(
			starts_at=timezone.now(),
			location="C207",
		)
		self.pending = Order.objects.create(
			user=self.member,
			distribution=self.distribution,
			status=Order.Status.PENDING,
		)
		self.ready = Order.objects.create(
			user=self.ready_member,
			distribution=self.distribution,
			status=Order.Status.READY,
		)
		self.picked_up_at = timezone.now()
		self.picked_up = Order.objects.create(
			user=self.picked_up_member,
			distribution=self.distribution,
			status=Order.Status.PICKED_UP,
			picked_up_at=self.picked_up_at,
		)
		Order.objects.create(
			user=self.member,
			distribution=self.distribution,
			status=Order.Status.CANCELLED,
		)
		Order.objects.create(
			user=self.member,
			distribution=self.other_distribution,
			status=Order.Status.PAID,
		)
		self.orders_url = reverse("distribution_orders", args=[self.distribution.pk])

	def test_visitor_is_sent_to_login(self):
		response = self.client.get(self.orders_url)

		self.assertRedirects(response, f"{reverse('login')}?next={self.orders_url}")

	def test_member_cannot_consult_distribution_orders(self):
		self.client.force_login(self.member)

		response = self.client.get(self.orders_url, follow=True)

		self.assertRedirects(response, reverse("home"))
		self.assertContains(response, "Cette consultation est réservée aux administrateurs.")
		self.assertNotContains(response, reverse("distributions"))

	def test_admin_chooses_a_distribution(self):
		self.client.force_login(self.admin)

		response = self.client.get(reverse("distributions"))

		self.assertContains(response, "C206")
		self.assertContains(response, self.orders_url)
		self.assertContains(response, reverse("distributions"))

	def test_admin_sees_not_picked_up_orders_by_default(self):
		self.client.force_login(self.admin)
		self.pending.refresh_from_db()

		response = self.client.get(self.orders_url)

		self.assertContains(response, "member@example.com")
		self.assertContains(response, "En attente de paiement")
		self.assertContains(response, "ready@example.com")
		self.assertContains(response, "Prête à récupérer")
		self.assertContains(
			response,
			timezone.localtime(self.pending.created_at).strftime("%d/%m/%Y %H:%M"),
		)
		self.assertNotContains(response, "picked-up@example.com")
		self.assertNotContains(response, "Annulée")
		self.assertNotContains(response, "Payée")

	def test_admin_filters_picked_up_orders(self):
		self.client.force_login(self.admin)

		response = self.client.get(self.orders_url, {"filtre": "recuperees"})

		self.assertContains(response, "picked-up@example.com")
		self.assertContains(response, "Récupérée")
		self.assertContains(
			response,
			timezone.localtime(self.picked_up.picked_up_at).strftime("%d/%m/%Y %H:%M"),
		)
		self.assertNotContains(response, "member@example.com")
		self.assertNotContains(response, "ready@example.com")
		self.assertNotContains(response, "Annulée")
		self.assertNotContains(response, "Payée")
		self.assertNotContains(response, "En attente de paiement")


class MarkOrderReadyTests(TestCase):
	def setUp(self):
		self.member = User.objects.create_user(
			email="member@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.admin = User.objects.create_superuser(
			email="admin@example.com",
			password="secure-test-password",
		)
		self.distribution = Distribution.objects.create(
			starts_at=timezone.now(),
			location="C206",
		)

	def make_order(self, status):
		return Order.objects.create(
			user=self.member,
			distribution=self.distribution,
			status=status,
		)

	def test_paid_order_becomes_ready(self):
		order = self.make_order(Order.Status.PAID)

		self.assertTrue(mark_order_as_ready(order))
		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.READY)

	def test_other_statuses_are_refused(self):
		for status in (
			Order.Status.PENDING,
			Order.Status.READY,
			Order.Status.PICKED_UP,
			Order.Status.CANCELLED,
		):
			with self.subTest(status=status):
				order = self.make_order(status)

				self.assertFalse(mark_order_as_ready(order))
				order.refresh_from_db()
				self.assertEqual(order.status, status)

	def test_admin_marks_a_paid_order_as_ready(self):
		order = self.make_order(Order.Status.PAID)
		self.client.force_login(self.admin)

		response = self.client.post(
			reverse("admin:orders_order_changelist"),
			{"action": "mark_as_ready", "_selected_action": [order.pk]},
			follow=True,
		)

		self.assertEqual(response.status_code, 200)
		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.READY)
		self.assertContains(response, "est prête à récupérer")

	def test_member_cannot_open_the_order_admin(self):
		self.client.force_login(self.member)
		url = reverse("admin:orders_order_changelist")

		response = self.client.get(url)

		self.assertRedirects(response, f"/admin/login/?next={url}")
