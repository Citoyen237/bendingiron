"""TVA décidée par l'admin pour chaque client, partenaire et proforma (14/11/2026)."""
from decimal import Decimal

from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.test import TestCase
from django.urls import reverse

from auth_app.models import CustomUser
from partenaires.models import OrderAdd, OrderItemAdd, Partenariats, Projet
from produits.models import Categorie, Produit
from proforma.models import OrderPro
from usesOrders.models import Cart, CartItem, Order, OrderItem
from usesOrders.tva import calculer_tva, libelle_tva, taux_pour


def compte(email, groupe=None, **extra):
    u = CustomUser.objects.create_user(username=email, email=email, password="MotDePasse-Solide-2026", **extra)
    if groupe:
        u.groups.add(Group.objects.get_or_create(name=groupe)[0])
    return u


class OutilsTvaTests(TestCase):
    def test_taux_et_libelles(self):
        self.assertEqual(taux_pour(True), Decimal("19.25"))
        self.assertEqual(taux_pour(False), Decimal("0"))
        self.assertEqual(calculer_tva(2000, Decimal("19.25")), 385)
        self.assertEqual(calculer_tva(2000, 0), 0)
        self.assertEqual(libelle_tva(Decimal("19.25")), "TVA 19,25%")
        self.assertEqual(libelle_tva(Decimal("0.00")), "TVA (exonéré)")


class TvaParCompteTests(TestCase):
    def setUp(self):
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png")

    def test_par_defaut_tout_le_monde_paie_la_tva(self):
        self.assertTrue(compte("a@x.cm").soumis_tva)
        o = Order.objects.create(user=compte("b@x.cm"))
        self.assertEqual(o.taux_tva, Decimal("19.25"))

    def test_client_exonere_panier_et_commande(self):
        client = compte("c@x.cm", soumis_tva=False)
        panier = Cart.objects.create(user=client)
        CartItem.objects.create(cart=panier, produit=self.produit, details={}, quantite=2, prix_u=1000, prix_revient=1)
        self.assertEqual(panier.taux_tva, 0)
        self.assertEqual(panier.montant_tva, 0)
        self.assertEqual(panier.net_payer, 2000)                  # TTC = HT

        o = Order.objects.create(user=client, taux_tva=panier.taux_tva)
        OrderItem.objects.create(order=o, produit=self.produit, details={}, quantite=2, prix_u=1000, prix_revient=1)
        self.assertEqual((o.montant_tva, o.net_payer), (0, 2000))

        # l'admin recoche la TVA du client : la commande déjà passée ne change pas
        CustomUser.objects.filter(pk=client.pk).update(soumis_tva=True)
        self.assertEqual(Order.objects.get(pk=o.pk).net_payer, 2000)

    def test_paiement_en_ligne_fige_le_taux_du_client(self):
        from paiements.models import DemandePaiement
        client = compte("d@x.cm", soumis_tva=False)
        demande = DemandePaiement.objects.create(
            user=client, provider="ORANGE", provider_reference="TOK-TVA", montant=2000,
            subscriber_msisdn_last4="0000",
            donnees_client={"nom": "D", "telephone": "6", "adresse": "A", "mode_livraison": "retrait en usine",
                            "remise": 0, "taux_tva": "0"},
            donnees_items=[{"produit_id": self.produit.id, "details": {}, "quantite": 2,
                            "prix_u": "1000", "prix_revient": "1"}])
        demande.confirmer({"amount": 2000})
        commande = Order.objects.get(pk=DemandePaiement.objects.get(pk=demande.pk).order_id)
        self.assertEqual(commande.taux_tva, 0)
        self.assertEqual(commande.net_payer, 2000)

    def test_partenaire_exonere_projet_et_travaux(self):
        partenaire = compte("p@x.cm", "partenaire")
        part = Partenariats.objects.create(user=partenaire, name="Entreprise A", email="ea@x.cm", adresse="D",
                                           telephone="6", date_debut="2026-01-01T00:00:00Z",
                                           date_fin="2027-01-01T00:00:00Z", soumis_tva=False)
        admin = compte("adm@x.cm", "admin")
        panier = Cart.objects.create(user=admin)
        CartItem.objects.create(cart=panier, produit=self.produit, details={}, quantite=1, prix_u=1000, prix_revient=1)
        self.client.force_login(admin)
        self.client.post(reverse("partanaire.confirm"), {"partenariat": part.id, "reduction": 0, "name": "Projet X",
                                                         "frais_ingenieurie": "personne physique"}, secure=True)
        projet = Projet.objects.get(name="Projet X")
        self.assertEqual(projet.taux_tva, 0)
        self.assertEqual(projet.montant_tva, 0)

        travail = OrderAdd.objects.create(projet_order=projet, user=partenaire, taux_tva=taux_pour(part.soumis_tva))
        OrderItemAdd.objects.create(order=travail, produit=self.produit, details={}, quantite=1, prix_u=1000,
                                    prix_revient=1)
        self.assertEqual(travail.net_payer, 1000)

    def test_proforma_case_tva(self):
        admin = compte("adm2@x.cm", "admin")
        self.client.force_login(admin)
        for appliquer, attendu in ((False, Decimal("0")), (True, Decimal("19.25"))):
            panier, _ = Cart.objects.get_or_create(user=admin)
            CartItem.objects.create(cart=panier, produit=self.produit, details={}, quantite=1, prix_u=1000,
                                    prix_revient=1)
            donnees = {"nom": "Client", "telephone": "699000000", "adresse": "Douala",
                       "mode_livraison": "retrait en usine"}
            if appliquer:
                donnees["appliquer_tva"] = "on"
            self.client.post(reverse("confirm-proforma"), donnees, secure=True)
            self.assertEqual(OrderPro.objects.order_by("-id").first().taux_tva, attendu)

    def test_facture_affiche_exonere(self):
        html = render_to_string("invoice.html", {"net_payer": 2000, "montant_tva": 0, "taux_tva": Decimal("0"),
                                                 "produits": []})
        self.assertIn("TVA (exonéré)", html)
        self.assertNotIn("19,25", html)
        html = render_to_string("invoice.html", {"net_payer": 2385, "taux_tva": Decimal("19.25"), "produits": []})
        self.assertIn("TVA 19,25%", html)
