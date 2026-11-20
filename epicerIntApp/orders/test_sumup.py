import json
from decimal import Decimal
from email.message import EmailMessage
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from catalog.models import Category, Product
from orders.models import Distribution, Order, OrderItem, Payment
from orders.sumup import SumUpError, SumUpNotConfigured, create_checkout, retrieve_checkout, sumup_config
from users.models import User


class SumUpConfigTests(SimpleTestCase):
	@override_settings(
		SUMUP_API_KEY="test-key",
		SUMUP_MERCHANT_CODE="MCODE",
		SUMUP_CURRENCY="EUR",
		SUMUP_API_BASE_URL="https://api.sumup.com/",
	)
	def test_reads_credentials_from_settings(self):
		config = sumup_config()

		self.assertEqual(config["api_key"], "test-key")
		self.assertEqual(config["merchant_code"], "MCODE")
		self.assertEqual(config["currency"], "EUR")
		self.assertEqual(config["api_base_url"], "https://api.sumup.com")

	@override_settings(SUMUP_API_KEY="", SUMUP_MERCHANT_CODE="MCODE")
	def test_missing_api_key_is_refused(self):
		with self.assertRaises(SumUpNotConfigured):
			sumup_config()

	@override_settings(SUMUP_API_KEY="test-key", SUMUP_MERCHANT_CODE="")
	def test_missing_merchant_code_is_refused(self):
		with self.assertRaises(SumUpNotConfigured):
			sumup_config()


SUMUP_SETTINGS = {
	"SUMUP_API_KEY": "test-key",
	"SUMUP_MERCHANT_CODE": "MCODE",
	"SUMUP_CURRENCY": "EUR",
	"SUMUP_API_BASE_URL": "https://api.sumup.com/",
}


class FakeResponse:
	def __init__(self, payload):
		self.payload = json.dumps(payload).encode()

	def read(self):
		return self.payload

	def __enter__(self):
		return self

	def __exit__(self, *args):
		return False


def http_error(code):
	return HTTPError(
		"https://api.sumup.com/v0.1/checkouts",
		code,
		"error",
		EmailMessage(),
		BytesIO(b"{}"),
	)


@override_settings(**SUMUP_SETTINGS)
class SumUpClientTests(SimpleTestCase):
	def test_create_checkout_opens_a_hosted_payment_page(self):
		def fake_urlopen(request, timeout):
			self.request = request
			self.timeout = timeout
			return FakeResponse(
				{
					"id": "checkout-1",
					"status": "PENDING",
					"hosted_checkout_url": "https://checkout.sumup.com/pay/checkout-1",
				}
			)

		with patch("orders.sumup.urlopen", fake_urlopen):
			checkout = create_checkout(
				Decimal("3.00"),
				"order-12",
				"https://example.com/orders/12/retour/",
				description="Commande 12",
			)

		self.assertEqual(self.timeout, 15)
		self.assertEqual(self.request.full_url, "https://api.sumup.com/v0.1/checkouts")
		self.assertEqual(self.request.get_method(), "POST")
		self.assertEqual(self.request.get_header("Authorization"), "Bearer test-key")
		body = json.loads(self.request.data.decode())
		self.assertEqual(body["checkout_reference"], "order-12")
		self.assertEqual(Decimal(str(body["amount"])), Decimal("3.00"))
		self.assertEqual(body["currency"], "EUR")
		self.assertEqual(body["merchant_code"], "MCODE")
		self.assertEqual(body["description"], "Commande 12")
		self.assertEqual(body["redirect_url"], "https://example.com/orders/12/retour/")
		self.assertEqual(body["hosted_checkout"], {"enabled": True})
		self.assertEqual(checkout["id"], "checkout-1")
		self.assertEqual(checkout["status"], "PENDING")
		self.assertEqual(
			checkout["hosted_checkout_url"],
			"https://checkout.sumup.com/pay/checkout-1",
		)

	def test_create_checkout_requires_a_payment_page(self):
		with patch("orders.sumup.urlopen", return_value=FakeResponse({"id": "checkout-1", "status": "PENDING"})):
			with self.assertRaises(SumUpError):
				create_checkout(Decimal("3.00"), "order-12", "https://example.com/retour/")

	def test_invalid_checkout_request_does_not_call_sumup(self):
		with patch("orders.sumup.urlopen") as urlopen:
			with self.assertRaises(SumUpError):
				create_checkout(Decimal("3.00"), "x" * 65, "https://example.com/retour/")
		urlopen.assert_not_called()

	def test_http_error_is_reported(self):
		with patch("orders.sumup.urlopen", side_effect=http_error(401)):
			with self.assertRaisesMessage(SumUpError, "SumUp a répondu 401."):
				create_checkout(Decimal("3.00"), "order-12", "https://example.com/retour/")

	def test_unreachable_sumup_is_reported(self):
		with patch("orders.sumup.urlopen", side_effect=URLError("down")):
			with self.assertRaisesMessage(SumUpError, "SumUp est injoignable."):
				retrieve_checkout("checkout-1")

	def test_retrieve_checkout_returns_the_paid_transaction(self):
		def fake_urlopen(request, timeout):
			self.request = request
			return FakeResponse(
				{
					"id": "checkout-1",
					"status": "PAID",
					"transaction_id": "tx-sumup-1",
				}
			)

		with patch("orders.sumup.urlopen", fake_urlopen):
			checkout = retrieve_checkout("checkout/1")

		self.assertEqual(
			self.request.full_url,
			"https://api.sumup.com/v0.1/checkouts/checkout%2F1",
		)
		self.assertEqual(self.request.get_method(), "GET")
		self.assertEqual(checkout["status"], "PAID")
		self.assertEqual(checkout["transaction_id"], "tx-sumup-1")

	def test_missing_credentials_do_not_call_sumup(self):
		with override_settings(SUMUP_API_KEY=""):
			with patch("orders.sumup.urlopen") as urlopen:
				with self.assertRaises(SumUpNotConfigured):
					create_checkout(Decimal("3.00"), "order-12", "https://example.com/retour/")
		urlopen.assert_not_called()


class PayOrderTests(TestCase):
	def setUp(self):
		category = Category.objects.create(name="Féculents")
		self.product = Product.objects.create(
			name="Pâtes", category=category, price="1.50", stock=3
		)
		self.member = User.objects.create_user(
			email="member@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.distribution = Distribution.objects.create(
			starts_at=timezone.now(),
			location="C206",
		)

	def make_order(self, status, user=None, quantity=2):
		order = Order.objects.create(
			user=user or self.member,
			distribution=self.distribution,
			status=status,
		)
		OrderItem.objects.create(
			order=order,
			product=self.product,
			quantity=quantity,
			unit_price="1.50",
		)
		return order

	def test_orders_page_offers_payment_only_while_pending(self):
		pending = self.make_order(Order.Status.PENDING)
		paid = self.make_order(Order.Status.PAID)
		self.client.force_login(self.member)

		response = self.client.get(reverse("orders"))

		self.assertContains(response, "Payer", count=1)
		self.assertContains(response, reverse("pay_order", args=[pending.pk]))
		self.assertNotContains(response, reverse("pay_order", args=[paid.pk]))

	def test_member_is_sent_to_sumup_for_a_pending_order(self):
		order = self.make_order(Order.Status.PENDING)
		self.client.force_login(self.member)
		checkout = {
			"id": "checkout-1",
			"status": "PENDING",
			"hosted_checkout_url": "https://checkout.sumup.com/pay/checkout-1",
			"transaction_id": "",
		}

		with patch("orders.views.create_checkout", return_value=checkout) as create:
			response = self.client.post(reverse("pay_order", args=[order.pk]))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, checkout["hosted_checkout_url"])
		amount, reference, redirect_url = create.call_args.args
		self.assertEqual(amount, Decimal("3.00"))
		self.assertTrue(reference.startswith(f"order-{order.pk}-"))
		self.assertLessEqual(len(reference), 64)
		self.assertEqual(
			redirect_url,
			f"http://testserver{reverse('order_payment_return', args=[order.pk])}",
		)
		self.assertEqual(create.call_args.kwargs["description"], f"Commande {order.pk}")
		self.assertEqual(self.client.session["sumup_checkouts"], {str(order.pk): "checkout-1"})
		order.refresh_from_db()
		self.product.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PENDING)
		self.assertEqual(self.product.stock, 3)
		self.assertFalse(Payment.objects.filter(order=order).exists())

	def test_other_statuses_are_refused(self):
		self.client.force_login(self.member)
		for status in (
			Order.Status.PAID,
			Order.Status.READY,
			Order.Status.PICKED_UP,
			Order.Status.CANCELLED,
		):
			with self.subTest(status=status):
				order = self.make_order(status)
				with patch("orders.views.create_checkout") as create:
					response = self.client.post(reverse("pay_order", args=[order.pk]), follow=True)
				create.assert_not_called()
				order.refresh_from_db()
				self.product.refresh_from_db()
				self.assertEqual(order.status, status)
				self.assertEqual(self.product.stock, 3)
				self.assertContains(response, "Cette commande ne peut plus être payée.")

	def test_succeeded_or_refunded_payment_is_refused(self):
		self.client.force_login(self.member)
		for payment_status in (Payment.Status.SUCCEEDED, Payment.Status.REFUNDED):
			with self.subTest(payment_status=payment_status):
				order = self.make_order(Order.Status.PENDING)
				Payment.objects.create(
					order=order,
					amount=Decimal("3.00"),
					status=payment_status,
				)
				with patch("orders.views.create_checkout") as create:
					response = self.client.post(reverse("pay_order", args=[order.pk]), follow=True)
				create.assert_not_called()
				order.refresh_from_db()
				self.assertEqual(order.status, Order.Status.PENDING)
				self.assertContains(response, "Cette commande ne peut plus être payée.")

	def test_failed_payment_can_start_a_new_checkout(self):
		order = self.make_order(Order.Status.PENDING)
		Payment.objects.create(
			order=order,
			amount=Decimal("3.00"),
			status=Payment.Status.FAILED,
		)
		self.client.force_login(self.member)
		checkout = {
			"id": "checkout-2",
			"hosted_checkout_url": "https://checkout.sumup.com/pay/checkout-2",
		}

		with patch("orders.views.create_checkout", return_value=checkout):
			response = self.client.post(reverse("pay_order", args=[order.pk]))

		self.assertEqual(response.url, checkout["hosted_checkout_url"])
		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PENDING)
		self.assertEqual(order.payment.status, Payment.Status.FAILED)

	def test_another_members_order_is_refused(self):
		order = self.make_order(Order.Status.PENDING)
		other = User.objects.create_user(
			email="other@example.com",
			password="secure-test-password",
			is_member=True,
		)
		self.client.force_login(other)

		with patch("orders.views.create_checkout") as create:
			response = self.client.post(reverse("pay_order", args=[order.pk]))

		create.assert_not_called()
		self.assertEqual(response.status_code, 404)
		order.refresh_from_db()
		self.product.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PENDING)
		self.assertEqual(self.product.stock, 3)

	def test_visitor_is_sent_to_login(self):
		order = self.make_order(Order.Status.PENDING)
		url = reverse("pay_order", args=[order.pk])

		response = self.client.post(url)

		self.assertRedirects(response, f"{reverse('login')}?next={url}")
		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PENDING)

	def test_missing_configuration_keeps_the_order_pending(self):
		order = self.make_order(Order.Status.PENDING)
		self.client.force_login(self.member)

		with patch("orders.views.create_checkout", side_effect=SumUpNotConfigured):
			response = self.client.post(reverse("pay_order", args=[order.pk]), follow=True)

		order.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PENDING)
		self.assertNotIn("sumup_checkouts", self.client.session)
		self.assertContains(response, "Le paiement en ligne est indisponible pour le moment.")

	def test_sumup_error_keeps_the_order_pending(self):
		order = self.make_order(Order.Status.PENDING)
		self.client.force_login(self.member)

		with patch("orders.views.create_checkout", side_effect=SumUpError("down")):
			response = self.client.post(reverse("pay_order", args=[order.pk]), follow=True)

		order.refresh_from_db()
		self.product.refresh_from_db()
		self.assertEqual(order.status, Order.Status.PENDING)
		self.assertEqual(self.product.stock, 3)
		self.assertContains(response, "Impossible de lancer le paiement. Réessayez.")

	def test_unsafe_payment_url_is_not_followed(self):
		order = self.make_order(Order.Status.PENDING)
		self.client.force_login(self.member)
		checkout = {"id": "checkout-1", "hosted_checkout_url": "http://example.test/pay"}

		with patch("orders.views.create_checkout", return_value=checkout):
			response = self.client.post(reverse("pay_order", args=[order.pk]), follow=True)

		self.assertRedirects(response, reverse("orders"))
		self.assertNotIn("sumup_checkouts", self.client.session)
		self.assertContains(response, "Impossible de lancer le paiement. Réessayez.")
