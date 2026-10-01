from functools import wraps

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from catalog.models import Product


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
	messages.success(request, f"{product.name} a été ajouté au panier.")
	return redirect("cart")
