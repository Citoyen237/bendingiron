"""
Tests de non-régression des corrections de sécurité.

Lancer :  python manage.py test auth_app
(avec DB_ENGINE=sqlite dans l'environnement pour ne pas avoir besoin de MySQL)
"""
import json
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from auth_app.models import CustomUser
from contact.models import Contact
from partenaires.models import Partenariats, Projet, ProjetItem, ProjetOrder
from produits.models import Categorie, Produit
from usesOrders.models import Cart, CartItem, CodePromo, Order


def creer_user(email, groupe="simple", **extra):
    user = CustomUser.objects.create_user(
        username=email, email=email, password="MotDePasse-Solide-2026",
        first_name=extra.pop("first_name", "Jean"), last_name="Test", **extra)
    g, _ = Group.objects.get_or_create(name=groupe)
    user.groups.add(g)
    if groupe == "superadmin":
        user.is_superuser = True
        user.is_staff = True
        user.save()
    return user


@override_settings(SECURE_SSL_REDIRECT=False, SITE_URL="https://www.bending-iron.com",
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class BaseTest(TestCase):
    def setUp(self):
        cache.clear()
        self.client_a = creer_user("a@exemple.cm")
        self.client_b = creer_user("b@exemple.cm")
        self.admin = creer_user("admin@exemple.cm", "admin")
        self.superadmin = creer_user("super@exemple.cm", "superadmin")

    def login(self, user):
        self.client.force_login(user)


class AccesCpanelTests(BaseTest):
    """S4 : les pages du tableau de bord sont réservées aux administrateurs."""

    URLS = ["code.revendeur", "admin.fer.list", "admin.mouvement", "admin.stock.list",
            "partenariat.list", "admin.fer.create", "admin.new_entrer"]

    def test_anonyme_redirige_vers_connexion(self):
        for name in self.URLS:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn("/auth/login/", r["Location"], name)

    def test_client_recoit_403(self):
        self.login(self.client_a)
        for name in self.URLS:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403, name)

    def test_admin_a_acces(self):
        self.login(self.admin)
        r = self.client.get(reverse("code.revendeur"))
        self.assertEqual(r.status_code, 200)

    def test_client_ne_peut_pas_supprimer_un_message(self):
        msg = Contact.objects.create(email="x@y.cm", nom="X", telephone="6", message="m", type="autre")
        self.login(self.client_a)
        r = self.client.post(reverse("contact.delete", args=[msg.pk]))
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Contact.objects.filter(pk=msg.pk).exists())

    def test_proforma_reservee_aux_admins(self):
        self.login(self.client_a)
        self.assertEqual(self.client.get(reverse("liste-order-pro")).status_code, 403)
        self.assertEqual(self.client.get(reverse("detail.proforma", args=[1])).status_code, 403)


class FacturesTests(BaseTest):
    """S5 : un client ne peut pas télécharger la facture d'un autre."""

    def test_facture_d_un_autre_client_404(self):
        order = Order.objects.create(user=self.client_a)
        self.login(self.client_b)
        self.assertEqual(self.client.get(reverse("invoice_download", args=[order.id])).status_code, 404)
        self.assertEqual(self.client.get(reverse("invoice_download2", args=[order.id])).status_code, 404)


class CommandeSansPaiementTests(BaseTest):
    """S7 : les anciennes routes qui créaient une commande sans paiement sont réservées aux admins."""

    def test_client_ne_peut_pas_creer_commande_sans_payer(self):
        self.login(self.client_a)
        self.assertEqual(self.client.get(reverse("confirmer")).status_code, 403)
        self.assertEqual(self.client.post(reverse("info_user"), {}).status_code, 403)


class RolesEtCsrfTests(BaseTest):
    """S9 : actions en POST uniquement, et seuls les superadmins gèrent les rôles admin."""

    def test_get_refuse(self):
        self.login(self.superadmin)
        r = self.client.get(reverse("change_user_role", args=[self.client_a.id, "admin"]))
        self.assertEqual(r.status_code, 405)
        r = self.client.get(reverse("toggle_user_status", args=[self.client_a.id]))
        self.assertEqual(r.status_code, 405)

    def test_admin_ne_peut_pas_creer_de_superadmin(self):
        self.login(self.admin)
        self.client.post(reverse("change_user_role", args=[self.client_a.id, "superadmin"]))
        self.client_a.refresh_from_db()
        self.assertFalse(self.client_a.is_superuser)
        self.assertFalse(self.client_a.groups.filter(name="superadmin").exists())

    def test_admin_ne_change_pas_son_propre_role(self):
        self.login(self.admin)
        self.client.post(reverse("change_user_role", args=[self.admin.id, "superadmin"]))
        self.admin.refresh_from_db()
        self.assertFalse(self.admin.is_superuser)

    def test_superadmin_peut_nommer_un_admin(self):
        self.login(self.superadmin)
        self.client.post(reverse("change_user_role", args=[self.client_a.id, "admin"]))
        self.assertTrue(self.client_a.groups.filter(name="admin").exists())


class PartenaireTests(BaseTest):
    """S5/S6 : un partenaire ne voit et ne commande que sur ses propres projets."""

    def setUp(self):
        super().setUp()
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre carre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png")
        self.part_a = Partenariats.objects.create(
            user=self.client_a, name="Entreprise A", email="ea@x.cm", adresse="Douala",
            telephone="6", date_debut="2026-01-01T00:00:00Z", date_fin="2027-01-01T00:00:00Z")
        self.projet_a = Projet.objects.create(partenariat=self.part_a, user=self.admin, name="Projet A")
        self.item_a = ProjetItem.objects.create(projet=self.projet_a, produit=self.produit, details={},
                                                prix_revient=10, quantite=100, prix_u=100)

    def test_autre_utilisateur_ne_voit_pas_le_projet(self):
        self.login(self.client_b)
        self.assertEqual(self.client.get(reverse("partenaire.detail", args=[self.projet_a.id])).status_code, 404)
        self.assertEqual(self.client.get(reverse("download.projet", args=[self.projet_a.id])).status_code, 404)
        self.assertEqual(self.client.get(reverse("historique-order", args=[self.projet_a.id])).status_code, 404)

    def test_autre_utilisateur_ne_peut_pas_commander_sur_le_projet(self):
        self.login(self.client_b)
        r = self.client.post(reverse("valider_commande_partenaire"),
                             data=json.dumps({"projet_id": self.projet_a.id,
                                              "panier": {str(self.item_a.id): {"quantite": 5}}}),
                             content_type="application/json")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(ProjetOrder.objects.count(), 0)


class PrixServeurTests(BaseTest):
    """S3 : le prix envoyé par le navigateur est ignoré pour le cadre carré."""

    def setUp(self):
        super().setUp()
        from gestion_prix_fer.models import Constante, Fournisseur, PrixFer, TypeFer
        f = Fournisseur.objects.create(nom="Prometal")
        t = TypeFer.objects.create(fournisseur=f, nom="FE400")
        PrixFer.objects.create(type_fer=t, diametre=8, prix_achat=5000, prix_vente=6000)
        for cle, val in (("tolerance", 10), ("taxe", 5), ("taux", Decimal("0.1"))):
            Constante.objects.create(cle=cle, valeur=val)
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre carre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png",
                                              sous_categorie="Cintrage de cadre")

    def donnees(self, **extra):
        d = {"fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe400",
             "longueurCote": "20", "longueur_Depart_et_Fin": "0", "rayon_Courbure": "0",
             "longueur_Total": "0", "prix": "1", "prix_Total": "1", "quantite": "10",
             "angle_pliage": "90", "diametre": "8", "prix_revient": "0"}
        d.update(extra)
        return d

    def test_prix_falsifie_ignore(self):
        self.login(self.client_a)
        r = self.client.post(reverse("produit.detail", args=[self.produit.id]), self.donnees())
        self.assertEqual(r.status_code, 302)
        item = CartItem.objects.get(cart__user=self.client_a)
        # Lt = ceil(4*20 + 1.3*8) = 91 ; Ps = 51*91/100 = 46.41 ; Pv = 6000/1200*91 = 455
        # Pu = ceil((455 + 46.41 + 10 + 5) * 1.1) = 569
        self.assertEqual(item.prix_u, 569)
        self.assertAlmostEqual(float(item.prix_revient), 46.41, places=2)
        self.assertEqual(item.details["longueur_Total"], 91)

    def test_dimension_hors_limites_refusee(self):
        self.login(self.client_a)
        self.client.post(reverse("produit.detail", args=[self.produit.id]), self.donnees(longueurCote="500"))
        self.assertFalse(CartItem.objects.exists())

    def test_anonyme_doit_se_connecter(self):
        r = self.client.post(reverse("produit.detail", args=[self.produit.id]), self.donnees())
        self.assertEqual(r.status_code, 302)
        self.assertIn("/auth/login/", r["Location"])


class MotDePasseOublieTests(BaseTest):
    """S8 : la demande de réinitialisation ne change PAS le mot de passe et envoie un lien signé."""

    def test_mot_de_passe_inchange_et_lien_envoye(self):
        r = self.client.post(reverse("resetpass"), {"email": "a@exemple.cm"})
        self.assertEqual(r.status_code, 302)
        self.client_a.refresh_from_db()
        self.assertTrue(self.client_a.check_password("MotDePasse-Solide-2026"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("https://www.bending-iron.com/auth/reinitialiser/", mail.outbox[0].body)

    def test_email_inconnu_meme_reponse(self):
        r = self.client.post(reverse("resetpass"), {"email": "inconnu@exemple.cm"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)


class ConnexionTests(BaseTest):
    """S14 : blocage après 5 échecs ; B1 : deux clients peuvent avoir le même prénom."""

    def test_blocage_apres_5_echecs(self):
        url = reverse("login")
        for _ in range(5):
            self.client.post(url, {"email": "a@exemple.cm", "password": "faux"})
        r = self.client.post(url, {"email": "a@exemple.cm", "password": "MotDePasse-Solide-2026"})
        self.assertEqual(r.status_code, 429)

    def test_connexion_normale(self):
        r = self.client.post(reverse("login"), {"email": "a@exemple.cm", "password": "MotDePasse-Solide-2026"})
        self.assertEqual(r.status_code, 302)

    def test_inscription_meme_prenom(self):
        Group.objects.get_or_create(name="simple")
        for i, email in enumerate(["paul1@exemple.cm", "paul2@exemple.cm"]):
            r = self.client.post(reverse("register"), {
                "first_name": "Paul", "last_name": f"N{i}", "email": email, "phone": "690000000",
                "password": "UnMotDePasse-Long-42", "pwd_confirm": "UnMotDePasse-Long-42"})
            self.assertEqual(r.status_code, 200)
        self.assertEqual(CustomUser.objects.filter(first_name="Paul").count(), 2)
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn("https://www.bending-iron.com/auth/verification-email/", html)


class CodePromoTests(BaseTest):
    """S10 : connexion et POST obligatoires ; un code expiré ne consomme pas d'utilisation."""

    def test_anonyme_et_get_refuses(self):
        r = self.client.post(reverse("appliquer_code"), {"code": "X"})
        self.assertEqual(r.status_code, 302)
        self.login(self.client_a)
        self.assertEqual(self.client.get(reverse("appliquer_code")).status_code, 405)

    def test_code_d_un_autre_client_refuse(self):
        cat = Categorie.objects.create(libelle="C")
        p = Produit.objects.create(categorie=cat, nom="x", name_page="p", imageshop2d="a", imageshop3d="b")
        cart = Cart.objects.create(user=self.client_a)
        CartItem.objects.create(cart=cart, produit=p, details={"fer": "bending iron"}, quantite=600,
                                prix_revient=1, prix_u=10)
        CodePromo.objects.create(user=self.admin, client=self.client_b, remise=5, code="ABCD1234")
        self.login(self.client_a)
        r = self.client.post(reverse("appliquer_code"), {"code": "ABCD1234"})
        self.assertFalse(r.json()["success"])
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 0)


# --- Ajoutés le 10/11/2026 : admin limité, alertes e-mail ---
@override_settings(ADMINS=[("Admin", "alerte@exemple.com")], ALLOWED_HOSTS=["testserver"])
class AdminEtAlertesTests(TestCase):
    def setUp(self):
        cache.clear()
        self.admin = creer_user("chef@exemple.com", groupe="superadmin", is_staff=True)

    def _essai(self, mot_de_passe):
        return self.client.post("/larue/login/", {"username": "chef@exemple.com", "password": mot_de_passe})

    def test_admin_bloque_apres_5_echecs(self):
        for _ in range(5):
            self.assertEqual(self._essai("mauvais").status_code, 200)
        # 6e essai bloqué, même avec le BON mot de passe
        self.assertEqual(self._essai("MotDePasse-Solide-2026").status_code, 429)

    def test_admin_connexion_reussie_remet_le_compteur_a_zero(self):
        for _ in range(4):
            self._essai("mauvais")
        self.assertEqual(self._essai("MotDePasse-Solide-2026").status_code, 302)
        self.client.logout()
        for _ in range(4):
            self.assertEqual(self._essai("mauvais").status_code, 200)

    def test_robot_par_adresse_ip_sans_email(self):
        mail.outbox = []
        with override_settings(DEBUG=False):
            reponse = self.client.get("/.git/config", HTTP_HOST="5.182.18.177")
        self.assertEqual(reponse.status_code, 400)
        self.assertEqual(len(mail.outbox), 0)
