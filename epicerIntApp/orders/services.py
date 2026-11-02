from decimal import Decimal

from django.utils import timezone
from django.db import transaction
from catalog.models import Product
from orders.models import Distribution, Order, OrderItem, Payment

def mark_order_as_picked_up(order):
	if order.status not in (Order.Status.PAID, Order.Status.READY):
		return False
	order.status = Order.Status.PICKED_UP
	order.picked_up_at = timezone.now()
	order.save()
	return True


def open_distribution(distribution):
	with transaction.atomic():
		Distribution.objects.exclude(pk=distribution.pk).filter(is_active=True).update(is_active=False)
		distribution.is_active = True
		distribution.save(update_fields=["is_active"])
	return distribution


def close_distribution(distribution):
	distribution.is_active = False
	distribution.save(update_fields=["is_active"])
	return distribution


def create_order_from_cart(user, cart):
	distribution = Distribution.objects.filter(is_active=True).order_by("-starts_at").first()
	if distribution is None or not cart:
		return None

	with transaction.atomic():
		lines = []
		for product_id, quantity in cart.items():
			product = Product.objects.select_for_update().get(pk=int(product_id), is_active=True)
			quantity = int(quantity)
			if quantity > product.stock:
				return None
			lines.append((product, quantity))

		order = Order.objects.create(user=user, distribution=distribution)
		for product, quantity in lines:
			OrderItem.objects.create(
				order=order,
				product=product,
				quantity=quantity,
				unit_price=product.price,
			)
			product.stock -= quantity
			product.save(update_fields=["stock"])
	return order


def mark_order_as_ready(order):
	if order.status != Order.Status.PAID:
		return False
	order.status = Order.Status.READY
	order.save()
	return True


def collect_order_payment(order, provider="", external_id=""):
	if order.status != Order.Status.PENDING:
		return False

	payment = Payment.objects.filter(order=order).first()
	if payment is not None and payment.status != Payment.Status.FAILED:
		return False

	amount = sum(
		(item.unit_price * item.quantity for item in order.items.all()),
		Decimal("0"),
	)
	now = timezone.now()
	with transaction.atomic():
		if payment is None:
			Payment.objects.create(
				order=order,
				amount=amount,
				status=Payment.Status.SUCCEEDED,
				provider=provider,
				external_id=external_id,
				paid_at=now,
			)
		else:
			payment.amount = amount
			payment.status = Payment.Status.SUCCEEDED
			payment.provider = provider
			payment.external_id = external_id
			payment.paid_at = now
			payment.save()
		order.status = Order.Status.PAID
		order.save(update_fields=["status", "updated_at"])
	return True

