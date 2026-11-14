"""Lien « Travaux additionnels » de la page projet (admin), 13/11/2026."""
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from auth_app.models import CustomUser
from partenaires.models import OrderAdd, OrderItemAdd, Partenariats, Projet
from produits.models import Categorie, Produit


def utilisateur(email, groupe):
    u = CustomUser.objects.create_user(username=email, email=email, password="MotDePasse-Solide-2026")
    g, _ = Group.objects.get_or_create(name=groupe)
    u.groups.add(g)
    return u


class TravauxAdditionnelsProjetTests(TestCase):
    def setUp(self):
        self.admin = utilisateur("admin@x.cm", "admin")
        partenaire = utilisateur("p@x.cm", "partenaire")
        part = Partenariats.objects.create(user=partenaire, name="Entreprise A", email="ea@x.cm", adresse="D",
                                           telephone="6", date_debut="2026-01-01T00:00:00Z",
                                           date_fin="2027-01-01T00:00:00Z")
        self.projet = Projet.objects.create(partenariat=part, user=self.admin, name="Projet A")
        self.autre = Projet.objects.create(partenariat=part, user=self.admin, name="Projet B")
        cat = Categorie.objects.create(libelle="Cadres")
        produit = Produit.objects.create(categorie=cat, nom="cadre carre", name_page="p",
                                         imageshop2d="a.png", imageshop3d="b.png")
        self.travail = OrderAdd.objects.create(projet_order=self.projet, user=partenaire)
        OrderItemAdd.objects.create(order=self.travail, produit=produit, details={}, quantite=2,
                                    prix_u=1000, prix_revient=1)
        self.travail_autre = OrderAdd.objects.create(projet_order=self.autre, user=partenaire)
        self.url = reverse("partenariat.order.additional.projet", args=[self.projet.id])

    def test_lien_sur_la_page_du_projet(self):
        self.client.force_login(self.admin)
        page = self.client.get(reverse("partenariat.projet.detail", args=[self.projet.id]), secure=True)
        self.assertContains(page, f'href="{self.url}"')

    def test_liste_seulement_les_travaux_du_projet(self):
        self.client.force_login(self.admin)
        reponse = self.client.get(self.url, secure=True)
        self.assertEqual(reponse.status_code, 200)
        commandes = [l["commande"] for l in reponse.context["lignes"]]
        self.assertEqual(commandes, [self.travail])                     # pas celui du projet B
        self.assertEqual(reponse.context["total_net"], self.travail.net_payer)
        self.assertContains(reponse, reverse("partenariat.detail.order.additional", args=[self.travail.id]))
        self.assertNotContains(reponse, reverse("partenariat.detail.order.additional", args=[self.travail_autre.id]))

    def test_reserve_aux_admins(self):
        self.client.force_login(utilisateur("c@x.cm", "simple"))
        self.assertEqual(self.client.get(self.url, secure=True).status_code, 403)

    def test_boutons_du_detail_vers_le_travail_additionnel_et_pas_une_proforma(self):
        """Avant : « Bon livraison pdf » et « Voir historique » ouvraient une PROFORMA de même
        numéro (erreur 404 « No OrderPro matches the given query », ou le document d'un autre client)."""
        from unittest import mock
        from partenaires.models import PaymentAdd
        self.client.force_login(self.admin)
        page = self.client.get(reverse("partenariat.detail.order.additional", args=[self.travail.id]), secure=True)
        url_bon = reverse("bon-livraison-additionnel", args=[self.travail.id])
        url_paiements = reverse("historique-paiement-additionnel", args=[self.travail.id])
        self.assertContains(page, url_bon)
        self.assertContains(page, url_paiements)
        self.assertNotContains(page, reverse("generate_bon_livraison_pro", args=[self.travail.id]))
        self.assertNotContains(page, reverse("historique-paiement-pro", args=[self.travail.id]))

        PaymentAdd.objects.create(user=self.admin, order=self.travail, amount_paid=500, mode_paid="om")
        historique = self.client.get(url_paiements, secure=True)
        self.assertEqual(historique.status_code, 200)
        self.assertContains(historique, "500 FCFA")

        capture = {}

        class FauxHTML:
            def __init__(self, string=None, **kwargs):
                capture["html"] = string

            def write_pdf(self):
                return b"%PDF-1.4"

        with mock.patch("partenaires.views.HTML", FauxHTML):
            reponse = self.client.get(url_bon, secure=True)
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse["Content-Type"], "application/pdf")
        self.assertIn("TRAVAUX ADDITIONNELS", capture["html"])
        self.assertIn("Projet A", capture["html"])
        self.assertIn("cadre carre", capture["html"])

    def test_bouton_paiement_cache_quand_solde(self):
        from partenaires.models import PaymentAdd
        self.client.force_login(self.admin)
        url = reverse("partenariat.detail.order.additional", args=[self.travail.id])
        bouton = 'data-bs-target="#verticalycentered"'
        self.assertFalse(self.travail.est_solde)
        self.assertContains(self.client.get(url, secure=True), bouton)
        PaymentAdd.objects.create(user=self.admin, order=self.travail, amount_paid=self.travail.net_payer,
                                  mode_paid="Cash")
        self.assertTrue(self.travail.est_solde)
        self.assertNotContains(self.client.get(url, secure=True), bouton)
