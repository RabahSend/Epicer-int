from django.db import transaction

from catalog.models import Product
from orders.models import Distribution, Order, OrderItem


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



    