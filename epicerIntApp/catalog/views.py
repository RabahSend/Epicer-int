from django.views.generic import TemplateView

from .models import Category


class ProductsPage(TemplateView):
    template_name = "catalog/products.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(
            products__is_active=True
        ).distinct().prefetch_related(
            "products"
        )
        return context