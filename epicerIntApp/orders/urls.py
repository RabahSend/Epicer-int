from django.urls import path
from . import views
from .views import add_to_cart, cart_page

urlpatterns = [
  path("", views.orders_page, name="orders"),
	path("cart/", cart_page, name="cart"),
	path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
	path("cart/place/", views.place_order, name="place_order"),
	path("distributions/", views.distributions_page, name="distributions"),
	path(
		"distributions/<int:distribution_id>/commandes/",
		views.distribution_orders_page,
		name="distribution_orders",
	),
]
