from django.urls import path

from .views import add_to_cart, cart_page

urlpatterns = [
	path("cart/", cart_page, name="cart"),
	path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
]
