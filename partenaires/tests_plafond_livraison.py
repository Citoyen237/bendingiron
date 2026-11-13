"""Livraisons partielles : plafond des tranches payées, demande en cours comprise (13/11/2026)."""
import json

from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from auth_app.models import CustomUser
from produits.models import Categorie, Produit
from usesOrders.models import Annulation

from .models import PaiementProjet, Partenariats, Projet, ProjetItem, ProjetOrder, ProjetOrderItem


class PlafondLivraisonTests(TestCase):
    def setUp(self):
        self.partenaire = CustomUser.objects.create_user(username="p@x.cm", email="p@x.cm",
                                                         password="MotDePasse-Solide-2026")
        self.partenaire.groups.add(Group.objects.get_or_create(name="partenaire")[0])
        part = Partenariats.objects.create(user=self.partenaire, name="Entreprise A", email="ea@x.cm",
                                           adresse="D", telephone="6", date_debut="2026-01-01T00:00:00Z",
                                           date_fin="2027-01-01T00:00:00Z")
        self.projet = Projet.objects.create(partenariat=part, user=self.partenaire, name="Projet A")
        cat = Categorie.objects.create(libelle="Cadres")
        produit = Produit.objects.create(categorie=cat, nom="cadre", name_page="p", imageshop2d="a.png",
                                         imageshop3d="b.png")
        # 1 000 pièces prévues : 600 + 400
        self.a = ProjetItem.objects.create(projet=self.projet, produit=produit, details={}, prix_revient=1,
                                           quantite=600, prix_u=10)
        self.b = ProjetItem.objects.create(projet=self.projet, produit=produit, details={}, prix_revient=1,
                                           quantite=400, prix_u=10)
        self.client.force_login(self.partenaire)

    def payer(self, *tranches):
        for t in tranches:
            PaiementProjet.objects.create(projet=self.projet, tranche=t)

    def livre(self, item, quantite):
        po = ProjetOrder.objects.create(projet=self.projet)
        ProjetOrderItem.objects.create(projet_order=po, projet_item=item, quantite=quantite)
        return po

    def demander(self, **quantites):
        panier = {str(getattr(self, cle).id): {"quantite": q} for cle, q in quantites.items()}
        return self.client.post(reverse("valider_commande_partenaire"),
                                json.dumps({"panier": panier, "projet_id": self.projet.id}),
                                content_type="application/json", secure=True)

    def test_aucune_tranche_aucune_livraison(self):
        self.assertEqual(self.projet.plafond_livraison, 0)
        self.assertFalse(self.projet.peut_commander)
        self.assertEqual(self.demander(a=1).status_code, 400)
        self.assertEqual(self.projet.message_etape_suivante, "La 1re tranche n'est pas encore payée.")

    def test_1re_tranche_plafond_50_pour_cent_demande_comprise(self):
        self.payer(1)
        self.livre(self.a, 300)
        self.assertEqual(self.projet.quantite_encore_demandable, 200)

        reponse = self.demander(a=150, b=100)                  # 300 + 250 = 55 % : refusé
        self.assertEqual(reponse.status_code, 400)
        self.assertIn("jusqu'à 50 %", reponse.json()["error"])
        self.assertIn("encore demander 200 pièce(s)", reponse.json()["error"])
        self.assertIn("Payez la 2e tranche", reponse.json()["error"])
        self.assertEqual(ProjetOrder.objects.count(), 1)

        self.assertEqual(self.demander(a=100, b=100).status_code, 200)   # pile 50 % : accepté
        projet = Projet.objects.get(pk=self.projet.pk)
        self.assertFalse(projet.peut_commander)
        self.assertEqual(projet.message_etape_suivante,
                         "Plafond de 50 % atteint : la 2e tranche n'est pas encore payée.")

    def test_une_seule_demande_ne_prend_plus_tout_le_projet(self):
        self.payer(1)
        self.assertEqual(self.demander(a=600, b=400).status_code, 400)
        self.assertFalse(ProjetOrder.objects.exists())

    def test_2e_puis_3e_tranche(self):
        self.payer(1, 2)
        self.assertEqual(self.projet.quantite_max_livrable, 900)
        self.assertEqual(self.demander(a=600, b=301).status_code, 400)
        self.assertEqual(self.demander(a=600, b=300).status_code, 200)
        self.payer(3)
        self.assertEqual(self.demander(b=100).status_code, 200)
        projet = Projet.objects.get(pk=self.projet.pk)
        self.assertEqual(projet.quantite_commande_totale, 1000)
        self.assertEqual(projet.message_etape_suivante, "")       # tout livré : pas de message

    def test_tranches_dans_l_ordre(self):
        self.payer(2)                                      # 2e sans la 1re : ne compte pas
        self.assertEqual(self.projet.tranches_payees, 0)

    def test_demande_annulee_libere_le_plafond(self):
        self.payer(1)
        po = self.livre(self.a, 500)
        self.assertFalse(self.projet.peut_commander)
        Annulation.objects.create(type_commande="projet", commande_id=po.id, statut_avant="en_attente", motif="x")
        self.assertEqual(self.projet.quantite_encore_demandable, 500)

    def test_page_affiche_ce_qui_reste_demandable(self):
        self.payer(1)
        self.livre(self.a, 100)
        html = self.client.get(reverse("partenaire.detail", args=[self.projet.id]), secure=True).content.decode()
        self.assertIn("Vous pouvez encore demander : <b>400 pièce(s)</b>", html)
        self.assertIn("const ENCORE_DEMANDABLE = 400;", html)
