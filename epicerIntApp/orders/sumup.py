import json
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.conf import settings


class SumUpNotConfigured(Exception):
	"""Les identifiants SumUp ne sont pas définis dans l'environnement."""


class SumUpError(Exception):
	"""L'appel à l'API SumUp a échoué."""


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


def create_checkout(amount, checkout_reference, redirect_url, description=""):
	# Sumup refuse une référence de plus de 64 caractères
	# La page hébergée encaisse la carte. elle ne transite pas par ntre serveur
	if not checkout_reference or len(checkout_reference) > 64 or not redirect_url:
		raise SumUpError("La demande de paiement SumUp est invalide.")

	config = sumup_config()
	checkout = _request(
		"POST",
		"/v0.1/checkouts",
		{
			"checkout_reference": checkout_reference,
			"amount": _amount(amount),
			"currency": config["currency"],
			"merchant_code": config["merchant_code"],
			"description": description,
			"redirect_url": redirect_url,
			"hosted_checkout": {"enabled": True},
		},
	)
	result = _checkout(checkout)
	if not result["id"] or not result["hosted_checkout_url"]:
		raise SumUpError("SumUp n'a pas renvoyé de page de paiement.")
	return result


def retrieve_checkout(checkout_id):
	# Le retour du navigateur ne prouve pas le paiement: on relit le statut chez Sumup
	if not checkout_id:
		raise SumUpError("L'identifiant de paiement SumUp est manquant.")
	checkout = _request("GET", f"/v0.1/checkouts/{quote(checkout_id, safe='')}")
	result = _checkout(checkout)
	if not result["id"] or not result["status"]:
		raise SumUpError("SumUp n'a pas renvoyé l'état du paiement.")
	return result


def _amount(amount):
	# Montant en euros envoyé comme nombre json
	quantized = Decimal(amount).quantize(Decimal("0.01"))
	return json.loads(format(quantized, "f"))


def _checkout(payload):
	# id identifie le checkout. transaction_id n'existe qu'une fois le paiement réussi.
	return {
		"id": payload.get("id") or "",
		"status": payload.get("status") or "",
		"hosted_checkout_url": payload.get("hosted_checkout_url") or "",
		"transaction_id": payload.get("transaction_id") or "",
	}


def _request(method, path, payload=None):
	config = sumup_config()
	data = None
	headers = {
		"Authorization": f"Bearer {config['api_key']}",
		"Accept": "application/json",
	}
	if payload is not None:
		data = json.dumps(payload).encode()
		headers["Content-Type"] = "application/json"
	request = Request(
		f"{config['api_base_url']}{path}",
		data=data,
		headers=headers,
		method=method,
	)
	try:
		with urlopen(request, timeout=15) as response:
			body = response.read().decode()
	except HTTPError as error:
		raise SumUpError(f"SumUp a répondu {error.code}.") from error
	except URLError as error:
		raise SumUpError("SumUp est injoignable.") from error
	try:
		return json.loads(body)
	except json.JSONDecodeError as error:
		raise SumUpError("SumUp a renvoyé une réponse illisible.") from error
