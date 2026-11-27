from decimal import Decimal
from functools import wraps
from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from orders.forms import DistributionForm
from orders.selectors import NOT_PICKED_UP, PICKED_UP, orders_for_distribution
from orders.services import (
	can_start_order_payment,
	cancel_order as cancel_pending_order,
	close_distribution,
	collect_order_payment,
	create_order_from_cart,
	fail_order_payment,
	open_distribution,
)
from orders.sumup import PROVIDER, SumUpError, SumUpNotConfigured, create_checkout, retrieve_checkout
from orders.models import Distribution, Order
from catalog.models import Product


@login_required
def orders_page(request):
    orders = (
        Order.objects.filter(user=request.user)
        .select_related("distribution")
        .prefetch_related("items__product")
    )
    return render(request, "orders/orders.html", {"orders": orders})
  
  
def member_required(view_func):
	@wraps(view_func)
	def wrapped(request, *args, **kwargs):
		if not request.user.is_authenticated:
			messages.info(request, "Créez un compte et cotisez pour accéder au panier.")
			return redirect("signup")
		if not request.user.is_member:
			messages.info(request, "Le panier est réservé aux membres dont la cotisation est active.")
			return redirect("profile")
		return view_func(request, *args, **kwargs)

	return wrapped


@member_required
def cart_page(request):
	cart = request.session.get("cart", {})
	products = Product.objects.filter(pk__in=cart.keys(), is_active=True)
	items = []
	total = 0
	valid_cart = {}

	for product in products:
		quantity = min(int(cart[str(product.pk)]), product.stock)
		if quantity:
			valid_cart[str(product.pk)] = quantity
			line_total = product.price * quantity
			total += line_total
			items.append({"product": product, "quantity": quantity, "line_total": line_total})

	if valid_cart != cart:
		request.session["cart"] = valid_cart

	if request.method == "POST":
		updated_cart = valid_cart.copy()
		for item in items:
			key = f"quantity_{item['product'].pk}"
			try:
				quantity = int(request.POST.get(key, item["quantity"]))
			except ValueError:
				quantity = -1
			if quantity < 0 or quantity > item["product"].stock:
				messages.error(request, "La quantité demandée dépasse le stock disponible.")
				return redirect("cart")
			if quantity:
				updated_cart[str(item["product"].pk)] = quantity
			else:
				updated_cart.pop(str(item["product"].pk), None)
		request.session["cart"] = updated_cart
		messages.success(request, "Votre panier a été mis à jour.")
		return redirect("cart")

	return render(request, "orders/cart.html", {"items": items, "total": total})


@member_required
@require_POST
def add_to_cart(request, product_id):
	product = get_object_or_404(Product, pk=product_id, is_active=True)
	try:
		quantity = int(request.POST.get("quantity", "1"))
	except ValueError:
		quantity = 0

	cart = request.session.get("cart", {})
	current_quantity = int(cart.get(str(product.pk), 0))
	if quantity < 1 or current_quantity + quantity > product.stock:
		messages.error(request, "La quantité demandée dépasse le stock disponible.")
		return redirect("products")

	cart[str(product.pk)] = current_quantity + quantity
	request.session["cart"] = cart
	messages.success(request, f"{product.name} a été ajouté au panier.", extra_tags="toast")
	return redirect("products")

@member_required
@require_POST
def place_order(request):
	cart = request.session.get("cart", {})
	order = create_order_from_cart(request.user, cart)
	if order is None:
		distribution_open = Distribution.objects.filter(is_active=True).exists()
		if cart and distribution_open:
			messages.error(request, "La quantité demandée dépasse le stock disponible.")
		else:
			messages.error(request, "Aucune distribution n'est ouverte pour le moment.")
		return redirect("cart")

	request.session["cart"] = {}
	messages.success(request, "Votre commande a été enregistrée.")
	return redirect("orders")


@login_required
@require_POST
def pay_order(request, order_id):
	order = get_object_or_404(Order, pk=order_id, user=request.user)
	if not can_start_order_payment(order):
		messages.error(request, "Cette commande ne peut plus être payée.")
		return redirect("orders")

	amount = sum(
		(item.unit_price * item.quantity for item in order.items.all()),
		Decimal("0"),
	)
	return_url = request.build_absolute_uri(reverse("order_payment_return", args=[order.pk]))
	try:
		checkout = create_checkout(
			amount,
			f"order-{order.pk}-{uuid4().hex[:12]}",
			return_url,
			description=f"Commande {order.pk}",
		)
	except SumUpNotConfigured:
		messages.error(request, "Le paiement en ligne est indisponible pour le moment.")
		return redirect("orders")
	except SumUpError:
		messages.error(request, "Impossible de lancer le paiement. Réessayez.")
		return redirect("orders")

	payment_url = checkout["hosted_checkout_url"]
	if not payment_url.startswith("https://"):
		messages.error(request, "Impossible de lancer le paiement. Réessayez.")
		return redirect("orders")

	checkouts = dict(request.session.get("sumup_checkouts", {}))
	checkouts[str(order.pk)] = checkout["id"]
	request.session["sumup_checkouts"] = checkouts
	return redirect(payment_url)


def _sumup_checkout_id(request, order):
	return request.session.get("sumup_checkouts", {}).get(str(order.pk), "")


def _forget_sumup_checkout(request, order):
	checkouts = request.session.get("sumup_checkouts", {})
	checkouts.pop(str(order.pk), None)
	request.session["sumup_checkouts"] = checkouts


@login_required
def payment_return(request, order_id):
	order = get_object_or_404(Order, pk=order_id, user=request.user)
	if order.status == Order.Status.PAID:
		messages.success(request, "Votre commande est payée.")
		return redirect("orders")
	if not can_start_order_payment(order):
		messages.error(request, "Cette commande ne peut plus être payée.")
		return redirect("orders")

	checkout_id = _sumup_checkout_id(request, order)
	if not checkout_id:
		messages.error(request, "Aucun paiement en cours pour cette commande.")
		return redirect("orders")

	try:
		checkout = retrieve_checkout(checkout_id)
	except SumUpNotConfigured:
		messages.error(request, "Le paiement en ligne est indisponible pour le moment.")
		return redirect("orders")
	except SumUpError:
		messages.error(request, "Impossible de confirmer le paiement. Réessayez.")
		return redirect("orders")

	# transaction_id n'existe qu'une fois le paiement réussi. sinon on garde l'id du checkout
	external_id = checkout["transaction_id"] or checkout["id"]
	if checkout["status"] == "PAID":
		if collect_order_payment(order, provider=PROVIDER, external_id=external_id):
			_forget_sumup_checkout(request, order)
			messages.success(request, "Votre commande est payée.")
		else:
			messages.error(request, "Cette commande ne peut plus être payée.")
	elif checkout["status"] in ("FAILED", "EXPIRED"):
		if fail_order_payment(order, provider=PROVIDER, external_id=external_id):
			_forget_sumup_checkout(request, order)
			messages.error(request, "Le paiement a échoué. La commande reste en attente.")
		else:
			messages.error(request, "Cette commande ne peut plus être payée.")
	else:
		messages.info(request, "Le paiement reste en attente de confirmation.")
	return redirect("orders")


@login_required
@require_POST
def cancel_order(request, order_id):
	order = get_object_or_404(Order, pk=order_id, user=request.user)
	if cancel_pending_order(order):
		messages.success(request, "Votre commande a été annulée.")
	else:
		messages.error(request, "Cette commande ne peut plus être annulée.")
	return redirect("orders")


def admin_required(view_func=None, message="Cette page est réservée aux administrateurs."):
	def decorator(func):
		@wraps(func)
		def wrapped(request, *args, **kwargs):
			if not request.user.is_authenticated:
				return redirect_to_login(request.get_full_path())
			if not request.user.is_staff:
				messages.error(request, message)
				return redirect("home")
			return func(request, *args, **kwargs)

		return wrapped

	if view_func is not None:
		return decorator(view_func)
	return decorator


@admin_required
def distributions_page(request):
	return render(
		request,
		"orders/distributions.html",
		{"distributions": Distribution.objects.all()},
	)


@admin_required
def distribution_create(request):
	form = DistributionForm(request.POST or None)
	if request.method == "POST" and form.is_valid():
		distribution = form.save(commit=False)
		distribution.is_active = False
		distribution.save()
		messages.success(request, "La distribution a été créée.")
		return redirect("distributions")
	return render(
		request,
		"orders/distribution_form.html",
		{"form": form, "title": "Nouvelle distribution"},
	)


@admin_required
def distribution_edit(request, distribution_id):
	distribution = get_object_or_404(Distribution, pk=distribution_id)
	form = DistributionForm(request.POST or None, instance=distribution)
	if request.method == "POST" and form.is_valid():
		form.save()
		messages.success(request, "La distribution a été modifiée.")
		return redirect("distributions")
	return render(
		request,
		"orders/distribution_form.html",
		{"form": form, "title": "Modifier la distribution"},
	)


@admin_required
@require_POST
def distribution_open(request, distribution_id):
	distribution = get_object_or_404(Distribution, pk=distribution_id)
	open_distribution(distribution)
	messages.success(request, "La distribution est ouverte.")
	return redirect("distributions")


@admin_required
@require_POST
def distribution_close(request, distribution_id):
	distribution = get_object_or_404(Distribution, pk=distribution_id)
	close_distribution(distribution)
	messages.success(request, "La distribution est fermée.")
	return redirect("distributions")


@admin_required(message="Cette consultation est réservée aux administrateurs.")
def distribution_orders_page(request, distribution_id):
	distribution = get_object_or_404(Distribution, pk=distribution_id)
	pickup_filter = request.GET.get("filtre", NOT_PICKED_UP)
	if pickup_filter not in (NOT_PICKED_UP, PICKED_UP):
		pickup_filter = NOT_PICKED_UP
	orders = orders_for_distribution(distribution, pickup_filter)
	return render(
		request,
		"orders/distribution_orders.html",
		{
			"distribution": distribution,
			"orders": orders,
			"filtre": pickup_filter,
			"not_picked_up": NOT_PICKED_UP,
			"picked_up": PICKED_UP,
		},
	)
