"""
Tests des tranches de paiement d'un projet : montant figé au paiement,
ordre imposé 1 -> 2 -> 3.

Lancer :  python manage.py test partenaires
"""
from decimal import Decimal
from importlib import import_module

from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse

from auth_app.models import CustomUser
from partenaires.form import PaiementProjetForm
from partenaires.models import PaiementProjet, Partenariats, Projet, ProjetItem
from produits.models import Categorie, Produit


def creer_admin():
    user = CustomUser.objects.create_user(username="admin@x.cm", email="admin@x.cm", password="MotDePasse-Solide-2026")
    g, _ = Group.objects.get_or_create(name="admin")
    user.groups.add(g)
    return user


@override_settings(SECURE_SSL_REDIRECT=False)
class TranchesBase(TestCase):
    def setUp(self):
        self.admin = creer_admin()
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png")
        part = Partenariats.objects.create(
            user=self.admin, name="Entreprise A", email="ea@x.cm", adresse="Douala", telephone="6",
            date_debut="2026-01-01T00:00:00Z", date_fin="2030-01-01T00:00:00Z")
        # réduction 0 et frais 0 : net = 10 000 HT + 1 925 TVA = 11 925
        self.projet = Projet.objects.create(partenariat=part, user=self.admin, name="P1",
                                            reduction=0, frais_ingenieurie="0")
        self.item = ProjetItem.objects.create(projet=self.projet, produit=self.produit, details={},
                                              prix_revient=0, quantite=10, prix_u=1000)

    def payer(self, tranche, mode="Cash"):
        form = PaiementProjetForm({"tranche": tranche, "mode_paiement": mode}, projet=self.projet)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.user = self.admin
            paiement.save()
            return paiement, form
        return None, form


class MontantFigeTests(TranchesBase):

    def test_montants_prevus_40_40_20(self):
        self.assertEqual(self.projet.net_payer, 11925)
        self.assertEqual(PaiementProjet.montant_prevu(self.projet, 1), 4770)
        self.assertEqual(PaiementProjet.montant_prevu(self.projet, 2), 4770)
        self.assertEqual(PaiementProjet.montant_prevu(self.projet, 3), 2385)

    def test_montant_enregistre_au_paiement(self):
        paiement, _ = self.payer(1)
        paiement.refresh_from_db()
        self.assertEqual(paiement.montant, Decimal("4770"))

    def test_regression_montant_ne_change_plus_si_le_projet_change(self):
        """Avant : le montant était recalculé à chaque affichage."""
        paiement, _ = self.payer(1)
        self.item.quantite = 20          # le projet double
        self.item.save()
        paiement.refresh_from_db()
        self.assertEqual(paiement.montant, Decimal("4770"))
        self.assertEqual(PaiementProjet.montant_prevu(self.projet, 1), 9540)

    def test_montant_rempli_aussi_hors_formulaire(self):
        paiement = PaiementProjet.objects.create(projet=self.projet, tranche=1, mode_paiement="Cash")
        self.assertEqual(paiement.montant, Decimal("4770"))

    def test_choix_affiche_le_montant(self):
        form = PaiementProjetForm(projet=self.projet)
        self.assertEqual(form.fields["tranche"].choices, [(1, "1ère tranche : 4770 FCFA")])


class OrdreDesTranchesTests(TranchesBase):

    def test_seule_la_prochaine_tranche_est_proposee(self):
        self.assertEqual([c[0] for c in PaiementProjetForm(projet=self.projet).fields["tranche"].choices], [1])
        self.payer(1)
        self.assertEqual([c[0] for c in PaiementProjetForm(projet=self.projet).fields["tranche"].choices], [2])

    def test_tranche_3_avant_la_1_refusee(self):
        paiement, form = self.payer(3)
        self.assertIsNone(paiement)
        self.assertIn("tranche", form.errors)
        self.assertFalse(PaiementProjet.objects.exists())

    def test_tranche_deja_payee_refusee(self):
        self.payer(1)
        paiement, form = self.payer(1)
        self.assertIsNone(paiement)
        self.assertEqual(PaiementProjet.objects.count(), 1)

    def test_ordre_complet_puis_projet_solde(self):
        for n in (1, 2, 3):
            paiement, form = self.payer(n)
            self.assertIsNotNone(paiement, form.errors)
        self.assertTrue(self.projet.is_solde)
        self.assertIsNone(PaiementProjet.prochaine_tranche(self.projet))
        self.assertEqual(sum(p.montant for p in self.projet.paiements.all()), Decimal("11925"))

    def test_tout_paye_plus_de_paiement_possible(self):
        for n in (1, 2, 3):
            self.payer(n)
        paiement, form = self.payer(3)
        self.assertIsNone(paiement)
        self.assertFalse(form.is_valid())


class VueAdminTranchesTests(TranchesBase):

    def setUp(self):
        super().setUp()
        self.client.force_login(self.admin)
        self.url = reverse("partenariat.projet.detail", args=[self.projet.id])

    def test_affichage_sans_erreur_de_formulaire(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.context["form"].is_bound)

    def test_enregistrement_puis_redirection(self):
        r = self.client.post(self.url, {"tranche": 1, "mode_paiement": "Cash"})
        self.assertRedirects(r, self.url, fetch_redirect_response=False)
        paiement = PaiementProjet.objects.get()
        self.assertEqual((paiement.tranche, paiement.montant, paiement.user), (1, Decimal("4770"), self.admin))

    def test_tranche_hors_ordre_refusee_par_la_vue(self):
        r = self.client.post(self.url, {"tranche": 2, "mode_paiement": "Cash"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(PaiementProjet.objects.exists())

    def test_historique_affiche_le_montant(self):
        self.payer(1)
        r = self.client.get(reverse("partenariat.projet.historique", args=[self.projet.id]))
        self.assertContains(r, "Montant payé")
        # séparateur de milliers français (« 4 770 ») : on vérifie la valeur affichée
        self.assertEqual(r.context["paiements"][0].montant, Decimal("4770"))
        self.assertRegex(r.content.decode(), r"4\D?770 FCFA")


class MigrationMontantsExistantsTests(TranchesBase):
    """La migration 0006 fige le montant des tranches enregistrées avant elle."""

    def test_calcul_de_la_migration_identique_au_modele(self):
        migration = import_module("partenaires.migrations.0006_paiementprojet_montant")
        for n in (1, 2, 3):
            self.assertEqual(migration._montant_tranche(self.projet, n),
                             PaiementProjet.montant_prevu(self.projet, n))

    def test_calcul_avec_reduction_et_frais(self):
        self.projet.reduction = 15
        self.projet.frais_ingenieurie = "5000"
        self.projet.save()
        self.item.prix_revient = 3000
        self.item.save()
        migration = import_module("partenaires.migrations.0006_paiementprojet_montant")
        for n in (1, 2, 3):
            self.assertEqual(migration._montant_tranche(self.projet, n),
                             PaiementProjet.montant_prevu(self.projet, n))

    def test_remplit_les_paiements_sans_montant(self):
        PaiementProjet.objects.bulk_create([PaiementProjet(projet=self.projet, tranche=1, mode_paiement="Cash")])
        self.assertIsNone(PaiementProjet.objects.get().montant)   # bulk_create n'appelle pas save()
        migration = import_module("partenaires.migrations.0006_paiementprojet_montant")
        migration.figer_montants_existants(django_apps, None)
        self.assertEqual(PaiementProjet.objects.get().montant, Decimal("4770"))

# --- Ajouté le 11/11/2026 : quantités de 1 000 et plus dans la page projet ---
class PageProjetGrandesQuantitesTests(TestCase):
    """Le séparateur de milliers (« 2 500 ») faisait lire 2 au JavaScript :
    le partenaire ne pouvait commander que 1 ou 2 pièces."""

    def test_nombres_pour_le_javascript_sans_separateur(self):
        partenaire = CustomUser.objects.create_user(username="p@x.cm", email="p@x.cm", password="MotDePasse-Solide-2026")
        admin = CustomUser.objects.create_user(username="a@x.cm", email="a@x.cm", password="MotDePasse-Solide-2026")
        cat = Categorie.objects.create(libelle="Barres")
        produit = Produit.objects.create(categorie=cat, nom="Barre coudée à l'extrémité", name_page="p",
                                         imageshop2d="a.png", imageshop3d="b.png")
        part = Partenariats.objects.create(user=partenaire, name="Entreprise A", email="ea@x.cm", adresse="Douala",
                                           telephone="6", date_debut="2026-01-01T00:00:00Z", date_fin="2027-01-01T00:00:00Z")
        projet = Projet.objects.create(partenariat=part, user=admin, name="Grand projet")
        PaiementProjet.objects.create(projet=projet, tranche=1)   # tranche 1 payée : commande possible
        item = ProjetItem.objects.create(projet=projet, produit=produit, details={}, prix_revient=10,
                                         quantite=2500, prix_u=100)
        self.client.force_login(partenaire)

        html = self.client.get(reverse("partenaire.detail", args=[projet.id]), secure=True).content.decode()

        self.assertIn('data-restant="2500"', html)
        self.assertIn(f'addToCart({item.id}, ', html)
        # apostrophe échappée pour le script : antislash + u0027 (antislash = chr(92))
        self.assertIn("Barre coudée à l" + chr(92) + "u0027extrémité", html)
        self.assertNotIn("'Barre coudée à l'extrémité'", html)
        # panier propre au projet (plus de panier commun « panier » pour tous les projets)
        self.assertIn('const CLE_PANIER = "panier_projet_" + projetId;', html)
        self.assertIn(f'const projetId = {projet.id};', html)
        self.assertNotIn('localStorage.getItem("panier")', html)

# --- Ajouté le 12/11/2026 : commande de projet sans cookie CSRF ---
@override_settings(ALLOWED_HOSTS=["bending-iron.com", "testserver"])
class CommandeProjetSansCookieCsrfTests(TestCase):
    """Sur téléphone, le cookie csrftoken manquait : le serveur renvoyait une page
    403 HTML et le script affichait « Unexpected token '<' … is not valid JSON »."""

    def test_commande_avec_le_jeton_de_la_page(self):
        import json, re
        from django.test import Client
        partenaire = CustomUser.objects.create_user(username="p@x.cm", email="p@x.cm", password="MotDePasse-Solide-2026")
        admin = CustomUser.objects.create_user(username="a@x.cm", email="a@x.cm", password="MotDePasse-Solide-2026")
        cat = Categorie.objects.create(libelle="Cadres")
        produit = Produit.objects.create(categorie=cat, nom="cadre carre", name_page="p",
                                         imageshop2d="a.png", imageshop3d="b.png")
        part = Partenariats.objects.create(user=partenaire, name="Entreprise A", email="ea@x.cm", adresse="Douala",
                                           telephone="6", date_debut="2026-01-01T00:00:00Z", date_fin="2027-01-01T00:00:00Z")
        projet = Projet.objects.create(partenariat=part, user=admin, name="Projet téléphone")
        PaiementProjet.objects.create(projet=projet, tranche=1)
        item = ProjetItem.objects.create(projet=projet, produit=produit, details={}, prix_revient=10,
                                         quantite=1000, prix_u=100)
        hote = dict(secure=True, HTTP_HOST="bending-iron.com")

        client = Client(enforce_csrf_checks=True)     # aucun cookie csrftoken au départ
        client.force_login(partenaire)
        html = client.get(reverse("partenaire.detail", args=[projet.id]), **hote).content.decode()
        jeton = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html)
        self.assertIsNotNone(jeton, "la page doit contenir le jeton de sécurité")

        corps = json.dumps({"panier": {str(item.id): {"nom": "cadre", "quantite": 6}}, "projet_id": projet.id})
        reponse = client.post(reverse("valider_commande_partenaire"), corps, content_type="application/json",
                              HTTP_X_CSRFTOKEN=jeton.group(1),
                              HTTP_REFERER="https://bending-iron.com/partenaire/", **hote)
        self.assertEqual(reponse.status_code, 200)
        self.assertEqual(reponse.json(), {"success": "Commande enregistrée"})
        self.assertEqual(item.quantite_commande, 6)

    def test_alerte_etape_cachee_sans_message(self):
        """Projet commandable : pas de message d'étape, donc pas de cadre d'alerte vide."""
        partenaire = CustomUser.objects.create_user(username="q@x.cm", email="q@x.cm", password="MotDePasse-Solide-2026")
        cat = Categorie.objects.create(libelle="Cadres")
        produit = Produit.objects.create(categorie=cat, nom="cadre", name_page="p", imageshop2d="a.png", imageshop3d="b.png")
        part = Partenariats.objects.create(user=partenaire, name="B", email="b@x.cm", adresse="D", telephone="6",
                                           date_debut="2026-01-01T00:00:00Z", date_fin="2027-01-01T00:00:00Z")
        projet = Projet.objects.create(partenariat=part, user=partenaire, name="Projet B")
        ProjetItem.objects.create(projet=projet, produit=produit, details={}, prix_revient=1, quantite=5, prix_u=10)
        self.client.force_login(partenaire)
        url = reverse("partenaire.detail", args=[projet.id])
        html = self.client.get(url, secure=True).content.decode()
        self.assertEqual(html.count("La 1er tranche"), 1)   # une seule fois
        PaiementProjet.objects.create(projet=projet, tranche=1)
        html = self.client.get(url, secure=True).content.decode()
        self.assertNotIn('class="alert alert-info text-center text-dark"', html)
