from django.urls import path
from . import views
from .views import add_to_cart, cart_page

urlpatterns = [
  path("", views.orders_page, name="orders"),
	path("cart/", cart_page, name="cart"),
	path("cart/add/<int:product_id>/", add_to_cart, name="add_to_cart"),
]
