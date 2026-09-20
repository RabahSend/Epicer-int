from django.db import models


class Product(models.Model):
    """Produit proposé lors des distributions Epicer'INT."""

    class Category(models.TextChoices):
        STARCHES = "starches", "Féculents"
        FRESH = "fresh", "Fruits et légumes"
        CANNED = "canned", "Conserves"
        SWEET = "sweet", "Produits sucrés"

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "name"]

    def __str__(self) -> str:
        return self.name
