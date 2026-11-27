import json
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Category, Product
from .services import import_products_from_json


class ProductJsonImportServiceTests(TestCase):
    def product_json(self, **overrides):
        record = {
            "name": "Riz",
            "category": "Féculents",
            "price": "2.50",
            "description": "Riz basmati",
            "stock": 20,
            "is_active": True,
        }
        record.update(overrides)
        return record

    def test_import_creates_products_and_missing_categories(self):
        result = import_products_from_json(
            '[{"name":"Riz","category":"Féculents","price":"2.50",'
            '"description":"Riz basmati","stock":20,"is_active":true}]'
        )

        product = Product.objects.get(name="Riz")
        self.assertEqual(result, {"created": 1, "updated": 0})
        self.assertEqual(product.category.name, "Féculents")
        self.assertEqual(product.price, Decimal("2.50"))
        self.assertEqual(product.stock, 20)
        self.assertTrue(product.is_active)

    def test_import_updates_product_with_same_name_and_category(self):
        category = Category.objects.create(name="Féculents")
        Product.objects.create(
            name="Riz",
            category=category,
            price="1.00",
            description="Ancienne description",
            stock=2,
            is_active=False,
        )

        result = import_products_from_json(
            '[{"name":"Riz","category":"Féculents","price":"2.50",'
            '"description":"Riz basmati","stock":20,"is_active":true}]'
        )

        product = Product.objects.get(name="Riz", category=category)
        self.assertEqual(result, {"created": 0, "updated": 1})
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(product.price, Decimal("2.50"))
        self.assertEqual(product.description, "Riz basmati")
        self.assertEqual(product.stock, 20)
        self.assertTrue(product.is_active)

    def test_import_requires_all_fields(self):
        record = self.product_json()
        del record["description"]

        with self.assertRaisesMessage(ValidationError, "description"):
            import_products_from_json(json.dumps([record]))

        self.assertEqual(Product.objects.count(), 0)

    def test_import_rejects_non_boolean_is_active(self):
        record = self.product_json(is_active="true")

        with self.assertRaisesMessage(ValidationError, "is_active"):
            import_products_from_json(json.dumps([record]))

        self.assertEqual(Product.objects.count(), 0)

    def test_invalid_product_rolls_back_the_whole_import(self):
        records = [
            self.product_json(),
            self.product_json(name="Pâtes", price="not-a-price"),
        ]

        with self.assertRaises(ValidationError):
            import_products_from_json(json.dumps(records))

        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(Category.objects.count(), 0)
