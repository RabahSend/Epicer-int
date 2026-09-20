from django.contrib import admin

from orders.models import Distribution, Order, OrderItem, Payment


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "distribution", "status", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline, PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "paid_at")
    list_filter = ("status",)