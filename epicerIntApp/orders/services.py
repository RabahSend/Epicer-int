from django.utils import timezone

from orders.models import Order


def mark_order_as_picked_up(order):
    if order.status not in (Order.Status.PAID, Order.Status.READY):
        return False
    order.status = Order.Status.PICKED_UP
    order.picked_up_at = timezone.now()
    order.save()
    return True