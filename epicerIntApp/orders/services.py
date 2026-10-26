from django.db import transaction

from catalog.models import Product
from orders.models import Distribution, Order, OrderItem


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

	lines = []
	for product_id, quantity in cart.items():
		product = Product.objects.get(pk=int(product_id), is_active=True)
		quantity = int(quantity)
		if quantity > product.stock:
			return None
		lines.append((product, quantity))

	with transaction.atomic():
		order = Order.objects.create(user=user, distribution=distribution)
		for product, quantity in lines:
			OrderItem.objects.create(
				order=order,
				product=product,
				quantity=quantity,
				unit_price=product.price,
			)
	return order



    