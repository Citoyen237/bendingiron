"""Page « Statistiques » du tableau de bord (proposition D, 12/11/2026)."""
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from auth_app.models import CustomUser
from partenaires.models import PaiementProjet, Partenariats, Projet, ProjetItem
from produits.models import Categorie, Produit
from usesOrders.models import Order, OrderItem, Payment

from .statistiques import _mode, statistiques


def utilisateur(email, groupe=None, **extra):
    u = CustomUser.objects.create_user(username=email, email=email, password="MotDePasse-Solide-2026",
                                       first_name=extra.pop("first_name", "Paul"), last_name="Test", **extra)
    if groupe:
        g, _ = Group.objects.get_or_create(name=groupe)
        u.groups.add(g)
    return u


def date(annee, mois, jour=15):
    return timezone.make_aware(datetime(annee, mois, jour, 10, 0))


class AccesStatistiquesTests(TestCase):
    def test_reserve_aux_admins(self):
        url = reverse("admin.statistiques")
        self.assertEqual(self.client.get(url, secure=True).status_code, 302)          # non connecté
        self.client.force_login(utilisateur("client@x.cm", "simple"))
        self.assertEqual(self.client.get(url, secure=True).status_code, 403)          # client
        self.client.force_login(utilisateur("admin@x.cm", "admin"))
        reponse = self.client.get(url, secure=True)
        self.assertEqual(reponse.status_code, 200)
        self.assertContains(reponse, "Statistiques")
        self.assertContains(reponse, 'id="donnees-statistiques"')
        annee = timezone.localdate().year
        self.assertContains(reponse, f"<h1>Statistiques {annee}</h1>")     # pas « 2 026 »
        self.assertContains(reponse, f'<option value="{annee}" selected>')

    def test_annee_invalide_ramenee_a_une_annee_disponible(self):
        self.client.force_login(utilisateur("admin@x.cm", "admin"))
        for valeur in ("abc", "1990"):
            reponse = self.client.get(reverse("admin.statistiques") + f"?annee={valeur}", secure=True)
            self.assertEqual(reponse.status_code, 200)
            self.assertEqual(reponse.context["s"]["annee"], timezone.localdate().year)


class CalculsStatistiquesTests(TestCase):
    def setUp(self):
        self.annee = timezone.localdate().year
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre carre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png")
        self.client_a = utilisateur("a@x.cm", "simple", first_name="Alice")

    def commande(self, prix, quantite, quand):
        o = Order.objects.create(user=self.client_a)
        Order.objects.filter(pk=o.pk).update(created_at=quand)
        OrderItem.objects.create(order=o, produit=self.produit, details={"diametre": 8}, quantite=quantite,
                                 prix_u=prix, prix_revient=1)
        return Order.objects.get(pk=o.pk)

    def test_chiffre_affaires_encaissements_et_comparaison(self):
        o1 = self.commande(1000, 2, date(self.annee, 3))       # HT 2000 -> TVA 385 -> net 2385
        self.commande(1000, 1, date(self.annee, 3))            # HT 1000 -> TVA 192 -> net 1192 (arrondi)
        self.commande(500, 2, date(self.annee - 1, 6))         # année précédente : net 1192
        p = Payment.objects.create(order=o1, amount_paid=Decimal("700"))
        Payment.objects.filter(pk=p.pk).update(created_at=date(self.annee, 4))

        s = statistiques(self.annee)
        self.assertEqual(s["ca"]["par_type"]["client"], o1.net_payer + 1192)
        self.assertEqual(s["ca"]["par_mois"]["client"][2], s["ca"]["par_type"]["client"])   # mars
        self.assertEqual(s["commandes"]["nombre"]["client"], 2)
        self.assertEqual(s["encaissements"]["par_mois"][3], 700)                            # avril
        self.assertEqual(s["encaissements"]["reste"], s["ca"]["par_type"]["client"] - 700)
        self.assertEqual(s["clients"]["top"][0]["nom"], "Alice Test")
        self.assertEqual(s["clients"]["fideles"], 1)
        self.assertEqual(s["produits"]["top_quantite"][0], ("cadre carre", 3))
        self.assertEqual(s["produits"]["diametres"], [("HA8", 3)])
        self.assertEqual(s["precedent"]["ca"], 1192)
        self.assertIsNotNone(s["evolution"]["ca"])

    def test_projet_et_paiement_de_tranche(self):
        partenaire = utilisateur("p@x.cm", "partenaire")
        part = Partenariats.objects.create(user=partenaire, name="Entreprise A", email="ea@x.cm", adresse="D",
                                           telephone="6", date_debut=date(self.annee, 1, 1),
                                           date_fin=date(self.annee + 1, 1, 1))
        projet = Projet.objects.create(partenariat=part, user=partenaire, name="Projet A")
        ProjetItem.objects.create(projet=projet, produit=self.produit, details={}, prix_revient=1,
                                  quantite=10, prix_u=100)
        PaiementProjet.objects.create(projet=projet, tranche=1, mode_paiement="om", date_paiement=date(self.annee, 5))

        s = statistiques(self.annee)
        self.assertEqual(s["ca"]["par_type"]["projet"], projet.net_payer)
        self.assertEqual(s["clients"]["top_partenaires"][0][0], "Entreprise A")
        self.assertEqual(s["encaissements"]["par_mois"][4], projet.tranche1)
        self.assertEqual(dict(s["encaissements"]["modes"])["Orange Money"], projet.tranche1)

    def test_annee_sans_rien(self):
        s = statistiques(2001)
        self.assertEqual(s["ca"]["total"], 0)
        self.assertEqual(s["commandes"]["panier_moyen"], 0)
        self.assertIsNone(s["evolution"]["ca"])


class ModePaiementTests(TestCase):
    def test_libelles_communs(self):
        self.assertEqual(_mode("om"), "Orange Money")
        self.assertEqual(_mode("ORANGE"), "Orange Money")
        self.assertEqual(_mode("momo"), "MTN MoMo")
        self.assertEqual(_mode("Cash"), "Espèces")
        self.assertEqual(_mode("Cheque banquaire"), "Chèque")
        self.assertEqual(_mode(""), "Autre")
