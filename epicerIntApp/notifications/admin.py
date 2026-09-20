from django.contrib import admin

from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "event", "channel", "created_at", "read_at")
    list_filter = ("event", "channel")
    search_fields = ("title", "message", "user__email")
    readonly_fields = ("created_at",)
