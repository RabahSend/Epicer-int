from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Category, Product
from orders.models import Distribution
from users.models import User

DEMO_MEMBER_EMAIL = "membre@epicerint.local"
DEMO_MEMBER_PASSWORD = "projetinfo1A"

CATEGORIES = (
    "Féculents",
    "Fruits et légumes",
    "Conserves",
    "Produits sucrés",
)

PRODUCTS = (
    {"name": "Riz", "category": "Féculents", "price": "2.50", "stock": 20},
    {"name": "Pâtes", "category": "Féculents", "price": "1.80", "stock": 15},
    {"name": "Pommes", "category": "Fruits et légumes", "price": "1.50", "stock": 30},
    {"name": "Carottes", "category": "Fruits et légumes", "price": "1.20", "stock": 25},
    {"name": "Tomates pelées", "category": "Conserves", "price": "1.10", "stock": 18},
    {"name": "Thon", "category": "Conserves", "price": "2.00", "stock": 12},
    {"name": "Biscuits", "category": "Produits sucrés", "price": "1.40", "stock": 10},
    {"name": "Chocolat", "category": "Produits sucrés", "price": "2.30", "stock": 8},
)


class Command(BaseCommand):
    help = "Ajoute les catégories, produits, un cotisant et une distribution de démonstration."

    def handle(self, *args, **options):
        for name in CATEGORIES:
            _, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(f"Catégorie créée : {name}")

        categories = {category.name: category for category in Category.objects.all()}
        for product_data in PRODUCTS:
            _, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults={
                    "category": categories[product_data["category"]],
                    "price": product_data["price"],
                    "stock": product_data["stock"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"Produit créé : {product_data['name']}")

        if User.objects.filter(email=DEMO_MEMBER_EMAIL).exists():
            self.stdout.write(f"Cotisant {DEMO_MEMBER_EMAIL} déjà présent.")
        else:
            User.objects.create_user(
                email=DEMO_MEMBER_EMAIL,
                password=DEMO_MEMBER_PASSWORD,
                first_name="Cotisant",
                last_name="Démo",
                is_member=True,
            )
            self.stdout.write(f"Cotisant créé : {DEMO_MEMBER_EMAIL}")

        if Distribution.objects.filter(is_active=True).exists():
            self.stdout.write("Une distribution active existe déjà.")
            return

        starts_at = timezone.now() + timedelta(days=2)
        Distribution.objects.create(
            starts_at=starts_at,
            ends_at=starts_at + timedelta(hours=2),
            location="Télécom SudParis",
            is_active=True,
        )
        self.stdout.write("Distribution de démonstration créée.")
