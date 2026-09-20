from django.conf import settings
from django.db import models


class Notification(models.Model):
    """Notification envoyée à un cotisant."""

    class Event(models.TextChoices):
        PRODUCT_ADDED = "product_added", "Nouvel article"
        PRODUCT_UPDATED = "product_updated", "Article modifié"
        DISTRIBUTION_REMINDER = "distribution_reminder", "Rappel de distribution"

    class Channel(models.TextChoices):
        IN_APP = "in_app", "Dans l'application"
        EMAIL = "email", "Email"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    event = models.CharField(max_length=32, choices=Event.choices)
    channel = models.CharField(
        max_length=16,
        choices=Channel.choices,
        default=Channel.IN_APP,
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.user}: {self.title}"
