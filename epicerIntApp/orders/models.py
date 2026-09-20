from django.db import models
from django.conf import settings

class Distribution(models.Model):
    """Séance de distribution alimentaire."""

    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-starts_at"]

    def __str__(self) -> str:
        return f"Distribution {self.starts_at:%Y-%m-%d %H:%M}"


class Order(models.Model):
    """Commande d'un cotisant pour une distribution."""

    class Status(models.TextChoices):
        PENDING = "pending", "En attente de paiement"
        PAID = "paid", "Payée"
        READY = "ready", "Prête à récupérer"
        PICKED_UP = "picked_up", "Récupérée"
        CANCELLED = "cancelled", "Annulée"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    distribution = models.ForeignKey(
        Distribution,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Commande #{self.pk} ({self.user})"


class OrderItem(models.Model):
    """Ligne de commande : un produit et sa quantité."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order", "product"],
                name="orders_orderitem_unique_product_per_order",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.product} × {self.quantity}"


class Payment(models.Model):
    """Paiement lié à une commande. Le prestataire reste à définir."""

    class Status(models.TextChoices):
        PENDING = "pending", "En attente"
        SUCCEEDED = "succeeded", "Réussi"
        FAILED = "failed", "Échoué"
        REFUNDED = "refunded", "Remboursé"

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    provider = models.CharField(max_length=50, blank=True)
    external_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"Paiement commande #{self.order_id} ({self.status})"
