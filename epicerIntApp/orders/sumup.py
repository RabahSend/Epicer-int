from django.conf import settings


class SumUpNotConfigured(Exception):
	"""Les identifiants SumUp ne sont pas définis dans l'environnement."""


def sumup_config():
	api_key = settings.SUMUP_API_KEY
	merchant_code = settings.SUMUP_MERCHANT_CODE
	if not api_key or not merchant_code:
		raise SumUpNotConfigured("Renseignez SUMUP_API_KEY et SUMUP_MERCHANT_CODE.")
	return {
		"api_key": api_key,
		"merchant_code": merchant_code,
		"currency": settings.SUMUP_CURRENCY,
		"api_base_url": settings.SUMUP_API_BASE_URL.rstrip("/"),
	}
