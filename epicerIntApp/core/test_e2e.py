import os

# Playwright fait tourner une boucle asyncio. Django bloque alors l'ORM synchrone.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse
from django.utils import timezone

from catalog.models import Category, Product
from orders.models import Distribution, Order
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

	def test_member_adds_product_within_stock_and_places_order(self):
		category = Category.objects.create(name="Féculents")
		product = Product.objects.create(name="Pâtes", category=category, price="1.50", stock=3)
		member = User.objects.create_user(
			email="membre@example.com",
			password="secure-test-password",
			is_member=True,
		)
		Distribution.objects.create(starts_at=timezone.now(), location="C206", is_active=True)

		self.goto("login")
		self.page.locator("#id_username").fill(member.email)
		self.page.locator("#id_password").fill("secure-test-password")
		self.page.get_by_role("button", name="Se connecter").click()
		self.expect(self.page.get_by_role("button", name="Déconnexion")).to_be_visible()

		self.goto("products")
		self.page.locator(f"#quantity-{product.pk}").fill("2")
		self.page.get_by_role("button", name="Ajouter au panier").click()
		self.expect(self.page.get_by_text("Pâtes a été ajouté au panier.")).to_be_visible()

		nav = self.page.get_by_role("navigation", name="Navigation principale")
		nav.get_by_role("link", name="Mon panier").click()
		self.expect(self.page.get_by_role("heading", name="Mon panier")).to_be_visible()
		self.page.get_by_role("button", name="Valider la commande").click()

		self.expect(self.page.get_by_text("Votre commande a été enregistrée.")).to_be_visible()
		self.expect(self.page.get_by_text("En attente de paiement")).to_be_visible()
		order = Order.objects.get()
		self.assertEqual(order.user, member)
		self.assertEqual(order.status, Order.Status.PENDING)
		self.assertEqual(order.items.get().quantity, 2)
		product.refresh_from_db()
		self.assertEqual(product.stock, 1)

	def test_non_member_cannot_add_to_cart(self):
		category = Category.objects.create(name="Féculents")
		Product.objects.create(name="Pâtes", category=category, price="1.50", stock=3)
		visitor = User.objects.create_user(
			email="visiteur@example.com",
			password="secure-test-password",
		)

		self.goto("login")
		self.page.locator("#id_username").fill(visitor.email)
		self.page.locator("#id_password").fill("secure-test-password")
		self.page.get_by_role("button", name="Se connecter").click()
		self.expect(self.page.get_by_role("button", name="Déconnexion")).to_be_visible()

		self.goto("products")
		self.expect(self.page.get_by_role("link", name="Cotiser pour commander")).to_be_visible()
		self.expect(self.page.get_by_role("button", name="Ajouter au panier")).to_have_count(0)
		nav = self.page.get_by_role("navigation", name="Navigation principale")
		self.expect(nav.get_by_role("link", name="Mon panier")).to_have_count(0)

		self.goto("cart")
		self.expect(self.page.get_by_role("heading", name="Mon compte")).to_be_visible()
		self.expect(self.page.get_by_text("Le panier est réservé aux membres dont la cotisation est active.")).to_be_visible()

	def test_admin_activates_membership_opens_distribution_and_lists_orders(self):
		member = User.objects.create_user(
			email="membre@example.com",
			password="secure-test-password",
		)
		admin = User.objects.create_superuser(
			email="admin@example.com",
			password="secure-test-password",
		)

		self.goto("login")
		self.page.locator("#id_username").fill(admin.email)
		self.page.locator("#id_password").fill("secure-test-password")
		self.page.get_by_role("button", name="Se connecter").click()
		self.expect(self.page.get_by_role("button", name="Déconnexion")).to_be_visible()

		self.goto("admin:users_user_change", member.pk)
		self.page.get_by_label("Cotisation active").check()
		self.page.get_by_role("button", name="Save", exact=True).click()
		self.expect(self.page.get_by_text("was changed successfully")).to_be_visible()
		member.refresh_from_db()
		self.assertTrue(member.is_member)

		self.goto("distribution_create")
		self.page.locator("#id_starts_at").fill("2026-12-01T10:00")
		self.page.locator("#id_ends_at").fill("2026-12-01T18:00")
		self.page.locator("#id_location").fill("TSP")
		self.page.get_by_role("button", name="Enregistrer").click()
		self.expect(self.page.get_by_text("La distribution a été créée.")).to_be_visible()
		self.page.get_by_role("button", name="Ouvrir").click()
		self.expect(self.page.get_by_text("La distribution est ouverte.")).to_be_visible()

		distribution = Distribution.objects.get(location="TSP")
		self.assertTrue(distribution.is_active)
		Order.objects.create(user=member, distribution=distribution, status=Order.Status.PENDING)
		self.page.locator("table").get_by_role("link", name="Commandes").click()
		self.expect(self.page.get_by_text("membre@example.com")).to_be_visible()
		self.expect(self.page.get_by_text("En attente de paiement")).to_be_visible()
