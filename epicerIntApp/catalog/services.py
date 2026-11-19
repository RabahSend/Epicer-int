import json
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Category, Product


PRODUCT_FIELDS = {"name", "category", "price", "description", "stock", "is_active"}


def import_products_from_json(content):
    try:
        records = json.loads(content)
    except json.JSONDecodeError as error:
        raise ValidationError(f"Le fichier JSON est invalide : {error.msg}.") from error

    if not isinstance(records, list) or not records:
        raise ValidationError("Le fichier JSON doit contenir une liste non vide de produits.")

    created = 0
    updated = 0

    with transaction.atomic():
        for index, record in enumerate(records, start=1):
            if not isinstance(record, dict):
                raise ValidationError(f"Produit n° {index} : chaque élément doit être un objet JSON.")

            missing_fields = PRODUCT_FIELDS - record.keys()
            unknown_fields = record.keys() - PRODUCT_FIELDS
            if missing_fields:
                names = ", ".join(sorted(missing_fields))
                raise ValidationError(f"Produit n° {index} : champs obligatoires manquants : {names}.")
            if unknown_fields:
                names = ", ".join(sorted(unknown_fields))
                raise ValidationError(f"Produit n° {index} : champs inconnus : {names}.")

            name = record["name"]
            category_name = record["category"]
            description = record["description"]
            price_value = record["price"]
            stock = record["stock"]
            is_active = record["is_active"]

            if not isinstance(name, str) or not name.strip():
                raise ValidationError(f"Produit n° {index} : « name » doit être une chaîne non vide.")
            if not isinstance(category_name, str) or not category_name.strip():
                raise ValidationError(f"Produit n° {index} : « category » doit être une chaîne non vide.")
            if not isinstance(description, str) or not description.strip():
                raise ValidationError(f"Produit n° {index} : « description » doit être une chaîne non vide.")
            if isinstance(price_value, bool) or not isinstance(price_value, (str, int, float)):
                raise ValidationError(f"Produit n° {index} : « price » doit être un nombre.")
            try:
                price = Decimal(str(price_value))
            except InvalidOperation as error:
                raise ValidationError(f"Produit n° {index} : « price » n’est pas un nombre valide.") from error
            if not price.is_finite():
                raise ValidationError(f"Produit n° {index} : « price » doit être un nombre fini.")
            if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
                raise ValidationError(f"Produit n° {index} : « stock » doit être un entier positif ou nul.")
            if not isinstance(is_active, bool):
                raise ValidationError(f"Produit n° {index} : « is_active » doit être un booléen.")

            category_name = category_name.strip()
            category = Category.objects.filter(name=category_name).first()
            if category is None:
                category = Category(name=category_name)
                try:
                    category.full_clean()
                except ValidationError as error:
                    raise ValidationError(
                        f"Produit n° {index} : catégorie invalide : {'; '.join(error.messages)}"
                    ) from error
                category.save()

            name = name.strip()
            matches = Product.objects.filter(name=name, category=category)
            if matches.count() > 1:
                raise ValidationError(
                    f"Produit n° {index} : plusieurs produits portent le nom "
                    f"« {name} » dans la catégorie « {category.name} »."
                )

            product = matches.first() or Product(category=category)
            product.name = name
            product.category = category
            product.price = price
            product.description = description.strip()
            product.stock = stock
            product.is_active = is_active
            try:
                product.full_clean()
            except ValidationError as error:
                raise ValidationError(
                    f"Produit n° {index} : {'; '.join(error.messages)}"
                ) from error

            is_update = product.pk is not None
            product.save()
            if is_update:
                updated += 1
            else:
                created += 1

    return {"created": created, "updated": updated}