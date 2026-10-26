from django.urls import path
from . import views
from .views import add_to_cart, cart_page

urlpatterns = [
  path("", views.orders_page, name="orders"),
	path("cart/", cart_page, name="cart"),
	path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
	path("cart/place/", views.place_order, name="place_order"),
	path("distributions/", views.distributions_page, name="distributions"),
	path("distributions/nouvelle/", views.distribution_create, name="distribution_create"),
	path(
		"distributions/<int:distribution_id>/modifier/",
		views.distribution_edit,
		name="distribution_edit",
	),
	path(
		"distributions/<int:distribution_id>/ouvrir/",
		views.distribution_open,
		name="distribution_open",
	),
	path(
		"distributions/<int:distribution_id>/fermer/",
		views.distribution_close,
		name="distribution_close",
	),
]
