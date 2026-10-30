from orders.models import Order

NOT_PICKED_UP = "non-recuperees"
PICKED_UP = "recuperees"


def orders_for_distribution(distribution, pickup_filter):
	queryset = Order.objects.filter(distribution=distribution).select_related("user")
	if pickup_filter == PICKED_UP:
		return queryset.filter(status=Order.Status.PICKED_UP)
	return queryset.exclude(status__in=[Order.Status.PICKED_UP, Order.Status.CANCELLED])
