import json
from decimal import Decimal
from email.message import EmailMessage
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from django.test import SimpleTestCase, override_settings

from orders.sumup import SumUpError, SumUpNotConfigured, create_checkout, retrieve_checkout, sumup_config


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
