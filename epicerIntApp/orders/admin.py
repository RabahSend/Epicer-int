from django.contrib import admin, messages

from orders.models import Distribution, Order, OrderItem, Payment
from orders.services import mark_order_as_picked_up, mark_order_as_ready


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ("starts_at", "location", "is_active")
    list_filter = ("is_active",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "paid_at")
    list_filter = ("status",)

@admin.action(description="Marquer comme prête à récupérer")
def mark_as_ready(modeladmin, request, queryset):
    for order in queryset:
        if mark_order_as_ready(order):
            messages.success(request, f"La commande n°{order.pk} est prête à récupérer.")
        else:
            messages.error(request, f"La commande n°{order.pk} ne peut pas être marquée comme prête.")


@admin.action(description="Marquer comme récupérée")
def mark_as_picked_up(modeladmin, request, queryset):
    for order in queryset:
        if mark_order_as_picked_up(order):
            messages.success(request, f"La commande n°{order.pk} est récupérée.")
        else:
            messages.error(request, f"La commande n°{order.pk} ne peut pas être récupérée.")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "distribution", "status", "created_at", "picked_up_at")
    list_filter = ("status",)
    actions = [mark_as_ready, mark_as_picked_up]
    inlines = [OrderItemInline, PaymentInline]
