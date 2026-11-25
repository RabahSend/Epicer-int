import os

# Playwright fait tourner une boucle asyncio. Django bloque alors l'ORM synchrone.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse

from catalog.models import Category, Product
from users.models import User


@tag("e2e")
class EndToEndTests(StaticLiveServerTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		from playwright.sync_api import expect, sync_playwright

		cls.expect = expect
		cls.playwright = sync_playwright().start()
		cls.browser = cls.playwright.chromium.launch()

	@classmethod
	def tearDownClass(cls):
		cls.browser.close()
		cls.playwright.stop()
		super().tearDownClass()

	def setUp(self):
		self.page = self.browser.new_page()

	def tearDown(self):
		self.page.close()

	def goto(self, viewname, *args):
		self.page.goto(self.live_server_url + reverse(viewname, args=args))

	def test_visitor_browses_home_and_catalog_without_cart(self):
		category = Category.objects.create(name="Féculents")
		Product.objects.create(name="Pâtes", category=category, price="1.50", stock=3)

		self.goto("home")
		nav = self.page.get_by_role("navigation", name="Navigation principale")
		self.expect(self.page.get_by_role("heading", name="Des distributions alimentaires pour les étudiants")).to_be_visible()
		self.expect(nav.get_by_role("link", name="Produits")).to_be_visible()
		self.expect(nav.get_by_role("link", name="Connexion")).to_be_visible()
		self.expect(nav.get_by_role("link", name="Adhérer")).to_be_visible()
		self.expect(nav.get_by_role("link", name="Mon panier")).to_have_count(0)

		self.goto("products")
		self.expect(self.page.get_by_role("heading", name="Pâtes")).to_be_visible()
		self.expect(self.page.get_by_text("Disponible · 3 en stock")).to_be_visible()
		self.expect(self.page.get_by_role("link", name="Adhérer et créer un compte")).to_be_visible()
		self.expect(self.page.get_by_role("button", name="Ajouter au panier")).to_have_count(0)
		self.expect(nav.get_by_role("link", name="Mon panier")).to_have_count(0)

	def test_signup_creates_account_without_active_membership(self):
		self.goto("signup")
		self.page.locator("#id_first_name").fill("Ada")
		self.page.locator("#id_last_name").fill("Lovelace")
		self.page.locator("#id_email").fill("ada@example.com")
		self.page.locator("#id_password1").fill("secure-test-password")
		self.page.locator("#id_password2").fill("secure-test-password")
		self.page.get_by_role("button", name="Créer mon compte").click()

		self.expect(self.page.get_by_role("heading", name="Mon compte")).to_be_visible()
		self.expect(self.page.get_by_text("ada@example.com")).to_be_visible()
		self.expect(self.page.get_by_text("En attente de validation")).to_be_visible()
		nav = self.page.get_by_role("navigation", name="Navigation principale")
		self.expect(nav.get_by_role("link", name="Mon panier")).to_have_count(0)

		user = User.objects.get(email="ada@example.com")
		self.assertFalse(user.is_member)
		self.assertEqual(user.username, "ada@example.com")
