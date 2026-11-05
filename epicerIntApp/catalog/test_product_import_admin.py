from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductJsonImportAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="secure-test-password",
        )
        self.client.force_login(self.admin_user)
        self.import_url = reverse("admin:catalog_product_import_json")

    def test_product_changelist_links_to_import_page(self):
        response = self.client.get(reverse("admin:catalog_product_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.import_url)

    def test_admin_can_upload_json_and_sees_import_summary(self):
        response = self.client.post(
            self.import_url,
            {
                "file": SimpleUploadedFile(
                    "products.json",
                    (
                        '[{"name":"Riz","category":"Féculents","price":"2.50",'
                        '"description":"Riz basmati","stock":20,"is_active":true}]'
                    ).encode("utf-8"),
                    content_type="application/json",
                ),
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 produit(s) créé(s), 0 produit(s) mis à jour.")
        self.assertTrue(Product.objects.filter(name="Riz").exists())

    def test_invalid_json_is_reported_without_creating_products(self):
        response = self.client.post(
            self.import_url,
            {
                "file": SimpleUploadedFile(
                    "products.json",
                    b"{invalid json}",
                    content_type="application/json",
                ),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Le fichier JSON est invalide")
        self.assertEqual(Product.objects.count(), 0)

    def test_non_json_file_is_rejected(self):
        response = self.client.post(
            self.import_url,
            {
                "file": SimpleUploadedFile(
                    "products.txt",
                    b"not json",
                    content_type="text/plain",
                ),
            },
        )

        self.assertContains(response, "Le fichier doit avoir l’extension .json.")
        self.assertEqual(Product.objects.count(), 0)

    def test_non_staff_user_cannot_access_import_page(self):
        regular_user = get_user_model().objects.create_user(
            email="user@example.com",
            password="secure-test-password",
        )
        self.client.force_login(regular_user)

        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)

    def test_staff_without_product_permissions_cannot_import(self):
        staff_user = get_user_model().objects.create_user(
            email="staff@example.com",
            password="secure-test-password",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 403)
