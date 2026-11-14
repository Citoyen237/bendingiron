"""Produit gelé : visible dans la boutique, « Indisponible pour le moment » au clic (14/11/2026)."""
from django.test import TestCase
from django.urls import reverse

from auth_app.models import CustomUser
from produits.models import Categorie, Produit
from usesOrders.models import CartItem


class ProduitGeleTests(TestCase):
    def setUp(self):
        cat = Categorie.objects.create(libelle="Cintrages")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre carre", sous_categorie="Cintrage de cadre",
                                              name_page="p", imageshop2d="a.png", imageshop3d="b.png",
                                              disponible=False)
        self.url = reverse("produit.detail", args=[self.produit.id])

    def test_disponible_par_defaut(self):
        autre = Produit.objects.create(categorie=self.produit.categorie, nom="etrier", name_page="p",
                                       imageshop2d="a.png", imageshop3d="b.png")
        self.assertTrue(autre.disponible)

    def test_toujours_dans_la_boutique(self):
        page = self.client.get(reverse("boutique"), secure=True)
        self.assertContains(page, self.url)

    def test_clic_affiche_indisponible_sans_guillemets(self):
        page = self.client.get(self.url, secure=True)
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, "Indisponible pour le moment")
        self.assertNotContains(page, "« Indisponible")
        self.assertNotContains(page, "&lt;&lt;")

    def test_rien_ne_va_au_panier(self):
        client = CustomUser.objects.create_user(username="c@x.cm", email="c@x.cm", password="MotDePasse-Solide-2026")
        self.client.force_login(client)
        self.client.post(self.url, {"quantite": "1", "fer": "bending iron"}, secure=True)
        self.assertFalse(CartItem.objects.exists())

    def test_calcul_refuse(self):
        reponse = self.client.post(reverse("boutique.calcul", args=[self.produit.id]), {}, secure=True)
        self.assertEqual(reponse.json()["erreur"], "Indisponible pour le moment")


class PanierAvecProduitGeleTests(TestCase):
    """Produit ajouté au panier puis gelé : la validation du panier est refusée."""

    def setUp(self):
        from django.contrib.auth.models import Group
        from usesOrders.models import Cart
        cat = Categorie.objects.create(libelle="Cintrages")
        self.gele = Produit.objects.create(categorie=cat, nom="cadre gele", name_page="p", imageshop2d="a.png",
                                           imageshop3d="b.png")
        self.user = CustomUser.objects.create_user(username="a@x.cm", email="a@x.cm",
                                                   password="MotDePasse-Solide-2026", email_verified=True)
        self.user.groups.add(Group.objects.get_or_create(name="admin")[0])
        panier = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=panier, produit=self.gele, details={}, quantite=2, prix_u=100, prix_revient=1)
        Produit.objects.filter(pk=self.gele.pk).update(disponible=False)      # gelé APRÈS l'ajout
        self.client.force_login(self.user)

    def test_les_4_validations_renvoient_au_panier(self):
        for nom in ("confirmer-commande", "partanaire.confirm", "confirm-proforma", "additional-order"):
            for methode in (self.client.get, self.client.post):
                reponse = methode(reverse(nom), secure=True)
                self.assertRedirects(reponse, reverse("panier"), fetch_redirect_response=False,
                                     msg_prefix=nom)

    def test_panier_signale_le_produit_et_le_message(self):
        self.client.get(reverse("confirmer-commande"), secure=True)
        page = self.client.get(reverse("panier"), secure=True)
        self.assertContains(page, '<span class="badge bg-danger">Indisponible pour le moment</span>', html=False)
        self.assertContains(page, "Indisponible pour le moment : cadre gele. Retirez ce produit du panier pour continuer.")
