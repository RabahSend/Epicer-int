from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.translation import gettext as _

from catalog.models import Category, Product
from catalog.services import import_products_from_json


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_list_template = "admin/catalog/product/change_list.html"
    list_display = ("name", "category", "price", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    autocomplete_fields = ("category",)

    def changelist_view(self, request, extra_context=None):
        extra_context = {
            **(extra_context or {}),
            "can_import_products": (
                self.has_add_permission(request) and self.has_change_permission(request)
            ),
        }
        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        return [
            path(
                "import-json/",
                self.admin_site.admin_view(self.import_json_view),
                name="catalog_product_import_json",
            ),
            *super().get_urls(),
        ]

    def import_json_view(self, request):
        if not self.has_add_permission(request) or not self.has_change_permission(request):
            raise PermissionDenied
        if request.method not in ("GET", "POST"):
            return HttpResponseNotAllowed(["GET", "POST"])

        context = {
            **self.admin_site.each_context(request),
            "title": _("Importer des produits depuis un fichier JSON"),
            "opts": self.model._meta,
            "errors": [],
            "changelist_url": reverse(
                f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
            ),
        }

        if request.method == "POST":
            uploaded_file = request.FILES.get("file")
            if uploaded_file is None:
                context["errors"] = ["Sélectionnez un fichier JSON à importer."]
            elif not uploaded_file.name.lower().endswith(".json"):
                context["errors"] = ["Le fichier doit avoir l’extension .json."]
            else:
                try:
                    content = uploaded_file.read().decode("utf-8-sig")
                    result = import_products_from_json(content)
                except UnicodeDecodeError:
                    context["errors"] = ["Le fichier doit être encodé en UTF-8."]
                except ValidationError as error:
                    context["errors"] = error.messages
                else:
                    messages.success(
                        request,
                        _("%(created)s produit(s) créé(s), %(updated)s produit(s) mis à jour.")
                        % result,
                    )
                    return redirect(
                        f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_changelist"
                    )

        return TemplateResponse(
            request,
            "admin/catalog/product/import_json.html",
            context,
        )
