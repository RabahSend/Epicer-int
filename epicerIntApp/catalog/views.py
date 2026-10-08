from django.views.generic import TemplateView

from .models import Product


class ProductsPage(TemplateView):
    template_name = "catalog/products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(is_active=True)
        return context