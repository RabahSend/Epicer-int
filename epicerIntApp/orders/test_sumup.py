from django.test import SimpleTestCase, override_settings

from orders.sumup import SumUpNotConfigured, sumup_config


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
