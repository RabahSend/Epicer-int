from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def orders_page(request):
    return render(request, "orders/orders.html")