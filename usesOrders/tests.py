"""
Tests du code promo (code distributeur) et du calcul de la remise.

Lancer :  python manage.py test usesOrders
(avec DB_ENGINE=sqlite dans l'environnement pour ne pas avoir besoin de MySQL)

Règles testées :
  - le formulaire de code promo n'est plus dans le panier ; il s'affiche sur la
    page de confirmation d'une commande client (client connecté, ou admin qui
    a cliqué sur « Client ») ;
  - conditions : fer fourni par Bending Iron + quantité minimale (constante
    « quantite_min_code_promo », 0 par défaut) ;
  - la remise s'applique sur le total HT de la facture ;
  - les commandes existantes gardent l'ancien calcul (remise_sur_total=False).
"""
from decimal import Decimal
from datetime import timedelta
from unittest import mock

from django.contrib.auth.models import Group
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from auth_app.models import CustomUser
from gestion_prix_fer.models import Constante
from produits.models import Categorie, Produit
from usesOrders import promo
from usesOrders.models import (Cart, CartItem, CodePromo, CodePromoUse, Order,
                               OrderItem)

BI = {"fer": "bending iron"}
CLIENT_FER = {"fer": "client"}


def creer_user(email, groupe="simple"):
    user = CustomUser.objects.create_user(
        username=email, email=email, password="MotDePasse-Solide-2026",
        first_name="Jean", last_name="Test", email_verified=True)
    g, _ = Group.objects.get_or_create(name=groupe)
    user.groups.add(g)
    return user


@override_settings(SECURE_SSL_REDIRECT=False)
class PromoBase(TestCase):
    def setUp(self):
        cache.clear()
        self.client_a = creer_user("a@exemple.cm")
        self.client_b = creer_user("b@exemple.cm")
        self.admin = creer_user("admin@exemple.cm", "admin")
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre carre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png")

    def panier(self, user, lignes):
        """lignes = [(details, quantite, prix_u), ...]"""
        cart = Cart.objects.create(user=user)
        for details, quantite, prix_u in lignes:
            CartItem.objects.create(cart=cart, produit=self.produit, details=details,
                                    quantite=quantite, prix_u=prix_u, prix_revient=1)
        return cart

    def code(self, client, code="PROMO10", remise=10, **extra):
        return CodePromo.objects.create(user=self.admin, client=client, remise=remise, code=code, **extra)

    def appliquer(self, user, code="PROMO10"):
        self.client.force_login(user)
        return self.client.post(reverse("appliquer_code"), {"code": code}).json()


# ---------------------------------------------------------------------- #
# Tests unitaires : règles d'éligibilité (usesOrders/promo.py)
# ---------------------------------------------------------------------- #
class ConditionsPromoTests(PromoBase):

    def test_quantite_minimum_par_defaut_zero(self):
        self.assertEqual(promo.quantite_minimum(), 0)

    def test_quantite_minimum_lue_dans_les_constantes(self):
        Constante.objects.create(cle=promo.CLE_QUANTITE_MIN, valeur=500)
        self.assertEqual(promo.quantite_minimum(), 500)

    def test_quantite_minimum_negative_ramenee_a_zero(self):
        Constante.objects.create(cle=promo.CLE_QUANTITE_MIN, valeur=-3)
        self.assertEqual(promo.quantite_minimum(), 0)

    def test_panier_bending_iron_eligible(self):
        cart = self.panier(self.client_a, [(BI, 1, 1000)])
        self.assertIsNone(promo.erreur_conditions(cart))

    def test_nom_du_fournisseur_insensible_casse_et_espaces(self):
        cart = self.panier(self.client_a, [({"fer": "  Bending Iron "}, 1, 1000)])
        self.assertIsNone(promo.erreur_conditions(cart))

    def test_panier_vide_refuse(self):
        cart = Cart.objects.create(user=self.client_a)
        self.assertIsNotNone(promo.erreur_conditions(cart))

    def test_un_seul_produit_avec_fer_client_refuse_tout(self):
        cart = self.panier(self.client_a, [(BI, 10, 1000), (CLIENT_FER, 1, 1000)])
        self.assertIn("bending iron", promo.erreur_conditions(cart))

    def test_details_sans_fer_refuse(self):
        cart = self.panier(self.client_a, [({}, 10, 1000)])
        self.assertIsNotNone(promo.erreur_conditions(cart))

    def test_quantite_insuffisante_refusee(self):
        Constante.objects.create(cle=promo.CLE_QUANTITE_MIN, valeur=50)
        cart = self.panier(self.client_a, [(BI, 20, 1000), (BI, 29, 1000)])
        self.assertIn("50", promo.erreur_conditions(cart))

    def test_quantite_totale_atteinte_acceptee(self):
        Constante.objects.create(cle=promo.CLE_QUANTITE_MIN, valeur=50)
        cart = self.panier(self.client_a, [(BI, 20, 1000), (BI, 30, 1000)])
        self.assertIsNone(promo.erreur_conditions(cart))

    def test_retirer_remise_si_invalide(self):
        cart = self.panier(self.client_a, [(CLIENT_FER, 1, 1000)])
        cart.remise = 10
        cart.save()
        self.assertIsNotNone(promo.retirer_remise_si_invalide(cart))
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 0)

    def test_retirer_remise_garde_une_remise_valide(self):
        cart = self.panier(self.client_a, [(BI, 1, 1000)])
        cart.remise = 10
        cart.save()
        self.assertIsNone(promo.retirer_remise_si_invalide(cart))
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 10)


# ---------------------------------------------------------------------- #
# Tests unitaires : calcul de la remise sur le total de la facture
# ---------------------------------------------------------------------- #
class CalculRemiseTests(PromoBase):

    def test_panier_sans_remise(self):
        cart = self.panier(self.client_a, [(BI, 2, 1000), (BI, 1, 500)])
        self.assertEqual(cart.get_prix_total, 2500)
        self.assertEqual(cart.montant_tva, 481)          # 2500 × 19,25 % = 481,25
        self.assertEqual(cart.net_payer, 2981)

    def test_remise_sur_le_total_ht_du_panier(self):
        cart = self.panier(self.client_a, [(BI, 2, 1000), (BI, 1, 500)])
        cart.remise = 10
        self.assertEqual(cart.montant_ht_brut, Decimal(2500))
        self.assertEqual(cart.montant_remise(), Decimal(250))
        self.assertEqual(cart.get_prix_total, 2250)
        self.assertEqual(cart.montant_tva, 433)          # 2250 × 19,25 % = 433,125
        self.assertEqual(cart.net_payer, 2683)
        self.assertEqual(cart.get_tranche1, 805)
        self.assertEqual(cart.get_tranche2, 1878)

    def test_remise_ne_depend_plus_du_prix_de_revient(self):
        cart = self.panier(self.client_a, [(BI, 1, 1000)])
        cart.items.update(prix_revient=999)
        cart.remise = 10
        self.assertEqual(cart.get_prix_total, 900)

    def _commande(self, **kwargs):
        order = Order.objects.create(user=self.client_a, **kwargs)
        OrderItem.objects.create(order=order, produit=self.produit, details=BI,
                                 quantite=2, prix_u=1000, prix_revient=100)
        return order

    def test_nouvelle_commande_sans_remise_par_defaut(self):
        order = self._commande()
        self.assertEqual(order.remise, 0)
        self.assertTrue(order.remise_sur_total)
        self.assertEqual(order.get_prix_total, 2000)

    def test_commande_remise_sur_total(self):
        order = self._commande(remise=10)
        self.assertEqual(order.get_prix_total, 1800)
        self.assertEqual(order.net_payer, 1800 + 346)    # 1800 × 19,25 % = 346,5 -> 346

    def test_regression_ancienne_commande_garde_son_calcul(self):
        """Commande créée avant la migration 0013 : remise sur le prix de revient."""
        order = self._commande(remise=10, remise_sur_total=False)
        # prix_revient_total = 100 -> remise = 10
        self.assertEqual(order.get_prix_total, 1990)


# ---------------------------------------------------------------------- #
# Tests de la vue appliquer_code_promo
# ---------------------------------------------------------------------- #
class AppliquerCodeTests(PromoBase):

    def test_client_applique_son_code(self):
        cart = self.panier(self.client_a, [(BI, 1, 1000)])
        self.code(self.client_a)
        r = self.appliquer(self.client_a)
        self.assertTrue(r["success"], r)
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 10)
        self.assertEqual(cart.get_prix_total, 900)

    def test_regression_plus_de_minimum_500_en_dur(self):
        """Avant : il fallait 500 produits. Désormais le minimum par défaut est 0."""
        self.panier(self.client_a, [(BI, 1, 1000)])
        self.code(self.client_a)
        self.assertTrue(self.appliquer(self.client_a)["success"])

    def test_minimum_configurable_respecte(self):
        Constante.objects.create(cle=promo.CLE_QUANTITE_MIN, valeur=500)
        cart = self.panier(self.client_a, [(BI, 499, 10)])
        self.code(self.client_a)
        self.assertFalse(self.appliquer(self.client_a)["success"])
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 0)

    def test_fer_non_fourni_par_bending_iron_refuse(self):
        cart = self.panier(self.client_a, [(BI, 1, 1000), (CLIENT_FER, 1, 1000)])
        self.code(self.client_a)
        self.assertFalse(self.appliquer(self.client_a)["success"])
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 0)

    def test_client_ne_peut_pas_utiliser_le_code_d_un_autre(self):
        cart = self.panier(self.client_a, [(BI, 1, 1000)])
        self.code(self.client_b)
        self.assertFalse(self.appliquer(self.client_a)["success"])
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 0)

    def test_admin_applique_le_code_d_un_client(self):
        cart = self.panier(self.admin, [(BI, 1, 1000)])
        self.code(self.client_b)
        self.assertTrue(self.appliquer(self.admin)["success"])
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 10)

    def test_code_inconnu(self):
        self.panier(self.client_a, [(BI, 1, 1000)])
        self.assertFalse(self.appliquer(self.client_a, "NEXISTEPAS")["success"])

    def test_code_vide(self):
        self.panier(self.client_a, [(BI, 1, 1000)])
        self.assertFalse(self.appliquer(self.client_a, "")["success"])

    def test_sans_panier(self):
        self.code(self.client_a)
        self.assertFalse(self.appliquer(self.client_a)["success"])

    def test_code_expire_refuse_sans_compter_d_utilisation(self):
        self.panier(self.client_a, [(BI, 1, 1000)])
        code = self.code(self.client_a, expiration=1, nb_utilidation=3)
        CodePromo.objects.filter(pk=code.pk).update(created_at=timezone.now() - timedelta(days=62))
        self.assertFalse(self.appliquer(self.client_a)["success"])
        self.assertEqual(CodePromoUse.objects.count(), 0)

    def test_nombre_d_utilisations_atteint(self):
        self.panier(self.client_a, [(BI, 1, 1000)])
        code = self.code(self.client_a, nb_utilidation=1)
        CodePromoUse.objects.create(promo_code=code)
        self.assertFalse(self.appliquer(self.client_a)["success"])

    def test_reappliquer_ne_compte_qu_une_utilisation(self):
        self.panier(self.client_a, [(BI, 1, 1000)])
        self.code(self.client_a, nb_utilidation=5)
        self.appliquer(self.client_a)
        self.appliquer(self.client_a)
        self.assertEqual(CodePromoUse.objects.count(), 1)

    def test_anonyme_et_get_refuses(self):
        r = self.client.post(reverse("appliquer_code"), {"code": "X"})
        self.assertEqual(r.status_code, 302)
        self.client.force_login(self.client_a)
        self.assertEqual(self.client.get(reverse("appliquer_code")).status_code, 405)


# ---------------------------------------------------------------------- #
# Tests d'affichage : où se trouve le formulaire du code promo
# ---------------------------------------------------------------------- #
class AffichageFormulaireTests(PromoBase):

    def test_formulaire_retire_du_panier(self):
        self.panier(self.client_a, [(BI, 1, 1000)])
        self.client.force_login(self.client_a)
        r = self.client.get(reverse("panier"))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'id="codeForm"')
        self.assertNotContains(r, reverse("appliquer_code"))

    def test_formulaire_affiche_pour_le_client_a_la_confirmation(self):
        self.panier(self.client_a, [(BI, 1, 1000)])
        self.client.force_login(self.client_a)
        r = self.client.get(reverse("confirmer-commande"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'id="codeForm"')
        self.assertContains(r, reverse("appliquer_code"))

    def test_formulaire_affiche_pour_l_admin_commande_client(self):
        """Bouton « Client » du panier admin -> page confirmer-commande."""
        self.panier(self.admin, [(BI, 1, 1000)])
        self.client.force_login(self.admin)
        r = self.client.get(reverse("confirmer-commande"))
        self.assertContains(r, 'id="codeForm"')
        r = self.client.get(reverse("info_user"))
        self.assertContains(r, 'id="codeForm"')

    def test_ligne_remise_affichee_quand_code_applique(self):
        cart = self.panier(self.client_a, [(BI, 2, 1000)])
        cart.remise = 10
        cart.save()
        self.client.force_login(self.client_a)
        r = self.client.get(reverse("confirmer-commande"))
        self.assertContains(r, "Remise code promo (10%)")
        self.assertContains(r, "- 200 FCFA")
        # séparateur de milliers français : on vérifie les valeurs du contexte
        self.assertEqual(r.context["montant_remise"], 200)
        self.assertEqual(r.context["total_prix"], 1800)
        self.assertEqual(r.context["net_payer"], 2146)

    def test_pas_de_ligne_remise_sans_code(self):
        self.panier(self.client_a, [(BI, 2, 1000)])
        self.client.force_login(self.client_a)
        r = self.client.get(reverse("confirmer-commande"))
        self.assertNotContains(r, "Remise code promo")


# ---------------------------------------------------------------------- #
# Tests de régression : pas de code promo pour projet / proforma / commande additionnelle
# ---------------------------------------------------------------------- #
class PasDePromoHorsCommandeClientTests(PromoBase):
    """L'admin applique un code sur la page « Client », puis revient au panier
    et choisit un autre parcours : la remise doit disparaître."""

    URLS = ["partanaire.confirm", "confirm-proforma", "additional-order"]

    def test_remise_retiree_et_totaux_sans_remise(self):
        for name in self.URLS:
            with self.subTest(page=name):
                Cart.objects.filter(user=self.admin).delete()
                cart = self.panier(self.admin, [(BI, 2, 1000)])
                cart.remise = 10
                cart.save()
                self.client.force_login(self.admin)
                r = self.client.get(reverse(name))
                self.assertEqual(r.status_code, 200)
                cart.refresh_from_db()
                self.assertEqual(cart.remise, 0)
                self.assertEqual(r.context["total_prix"], 2000)
                self.assertNotContains(r, 'id="codeForm"')


# ---------------------------------------------------------------------- #
# Tests de régression : la remise suit le panier jusqu'à la commande
# ---------------------------------------------------------------------- #
class RemiseJusquALaCommandeTests(PromoBase):

    FORM = {"pour_qui": "autre", "nom": "Client A", "telephone": "690000000", "adresse": "Douala",
            "mode_livraison": "retrait en usine", "mode_payement": "orange",
            "reglement": "integrale", "telephone_pay": "690000000"}

    def test_admin_commande_conserve_la_remise_sur_total(self):
        cart = self.panier(self.admin, [(BI, 2, 1000)])
        cart.remise = 10
        cart.save()
        self.client.force_login(self.admin)
        self.client.get(reverse("confirmer"))
        order = Order.objects.get(user=self.admin)
        self.assertEqual(order.remise, 10)
        self.assertTrue(order.remise_sur_total)
        self.assertEqual(order.get_prix_total, 1800)

    def test_panier_modifie_apres_le_code_remise_annulee(self):
        """Code appliqué puis ajout d'un produit avec fer client : pas de commande remisée."""
        cart = self.panier(self.admin, [(BI, 2, 1000)])
        self.code(self.client_b)
        self.assertTrue(self.appliquer(self.admin)["success"])
        CartItem.objects.create(cart=cart, produit=self.produit, details=CLIENT_FER,
                                quantite=1, prix_u=1000, prix_revient=1)
        r = self.client.get(reverse("confirmer"))
        self.assertRedirects(r, reverse("panier"), fetch_redirect_response=False)
        self.assertFalse(Order.objects.exists())
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 0)

    def test_paiement_client_remise_annulee_si_panier_invalide(self):
        from paiements.models import DemandePaiement
        cart = self.panier(self.client_a, [(CLIENT_FER, 2, 1000)])
        cart.remise = 10
        cart.save()
        self.client.force_login(self.client_a)
        with mock.patch("paiements.views._client_pour") as client_paiement:
            r = self.client.post(reverse("confirmer-commande"), self.FORM)
        self.assertRedirects(r, reverse("confirmer-commande"), fetch_redirect_response=False)
        client_paiement.assert_not_called()
        self.assertFalse(DemandePaiement.objects.exists())
        cart.refresh_from_db()
        self.assertEqual(cart.remise, 0)

    def test_paiement_client_montant_avec_remise(self):
        from paiements.models import DemandePaiement
        cart = self.panier(self.client_a, [(BI, 2, 1000)])
        cart.remise = 10
        cart.save()
        self.client.force_login(self.client_a)
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.pay.return_value = {"payToken": "TOKEN-1"}
            self.client.post(reverse("confirmer-commande"), self.FORM)
        demande = DemandePaiement.objects.get()
        # 1800 HT + 346 TVA
        self.assertEqual(demande.montant, 2146)
        self.assertEqual(demande.donnees_client["remise"], 10.0)


# ---------------------------------------------------------------------- #
# Parcours commande client : code promo -> paiement -> facturation
# ---------------------------------------------------------------------- #
class ParcoursCommandeClientTests(PromoBase):
    """« Pour moi » : nom et téléphone repris du compte. « Autre client » ou
    admin : infos saisies. Rien n'est enregistré avant la confirmation du
    paiement ; ensuite tout est enregistré et le panier est vidé."""

    PAIEMENT = {"mode_payement": "orange", "reglement": "integrale", "telephone_pay": "690000000"}

    def setUp(self):
        super().setUp()
        self.client_a.first_name, self.client_a.last_name = "Paul", "Mbarga"
        self.client_a.phone_number = "677112233"
        self.client_a.save()
        self.cart = self.panier(self.client_a, [(BI, 2, 1000)])

    def payer(self, user, **champs):
        from paiements.models import DemandePaiement
        self.client.force_login(user)
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.pay.return_value = {"payToken": "TOKEN-1"}
            r = self.client.post(reverse("confirmer-commande"), {**self.PAIEMENT, **champs})
        return r, DemandePaiement.objects.first()

    # --- Affichage --------------------------------------------------- #
    def test_ordre_des_sections(self):
        self.client.force_login(self.client_a)
        html = self.client.get(reverse("confirmer-commande")).content.decode()
        promo_, paiement, facturation = (html.index("Code promo</h4>"),
                                         html.index("Informations de paiement"),
                                         html.index("Informations de facturation"))
        # code promo -> facturation -> paiement
        self.assertLess(promo_, facturation)
        self.assertLess(facturation, paiement)

    def test_client_voit_le_choix_et_ses_infos(self):
        self.client.force_login(self.client_a)
        r = self.client.get(reverse("confirmer-commande"))
        self.assertContains(r, "Cette commande est pour moi")
        self.assertContains(r, "Pour un autre client")
        self.assertContains(r, "Mbarga Paul")
        self.assertContains(r, "677112233")

    def test_admin_n_a_pas_le_choix_pour_moi(self):
        self.panier(self.admin, [(BI, 1, 1000)])
        self.client.force_login(self.admin)
        r = self.client.get(reverse("confirmer-commande"))
        self.assertNotContains(r, "Cette commande est pour moi")
        self.assertContains(r, 'name="nom"')

    # --- Pour moi ---------------------------------------------------- #
    def test_pour_moi_infos_reprises_du_compte(self):
        r, demande = self.payer(self.client_a, pour_qui="moi",
                                mode_livraison="livraison sur chantier", adresse="Bonamoussadi")
        self.assertRedirects(r, reverse("paiement-en-cours", args=["TOKEN-1"]),
                             fetch_redirect_response=False)
        self.assertEqual(demande.donnees_client["nom"], "Mbarga Paul")
        self.assertEqual(demande.donnees_client["telephone"], "677112233")
        self.assertEqual(demande.donnees_client["adresse"], "Bonamoussadi")

    def test_pour_moi_ignore_un_nom_envoye_par_le_navigateur(self):
        _, demande = self.payer(self.client_a, pour_qui="moi", nom="Pirate", telephone="600000000",
                                mode_livraison="retrait en usine")
        self.assertEqual(demande.donnees_client["nom"], "Mbarga Paul")
        self.assertEqual(demande.donnees_client["telephone"], "677112233")

    # --- Autre client ------------------------------------------------ #
    def test_autre_client_infos_saisies(self):
        _, demande = self.payer(self.client_a, pour_qui="autre", nom="Awa Ndiaye", telephone="655000000",
                                mode_livraison="livraison sur chantier", adresse="Akwa")
        self.assertEqual(demande.donnees_client["nom"], "Awa Ndiaye")
        self.assertEqual(demande.donnees_client["telephone"], "655000000")

    def test_autre_client_sans_nom_refuse(self):
        r, demande = self.payer(self.client_a, pour_qui="autre", telephone="655000000",
                                mode_livraison="retrait en usine")
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(demande)
        self.assertTrue(r.context["form"].errors["nom"])

    def test_admin_doit_saisir_les_infos_meme_avec_pour_moi(self):
        self.panier(self.admin, [(BI, 1, 1000)])
        r, demande = self.payer(self.admin, pour_qui="moi", mode_livraison="retrait en usine")
        self.assertIsNone(demande)
        self.assertIn("nom", r.context["form"].errors)

    # --- Adresse ----------------------------------------------------- #
    def test_retrait_en_usine_sans_adresse_accepte(self):
        _, demande = self.payer(self.client_a, pour_qui="moi", mode_livraison="retrait en usine")
        self.assertEqual(demande.donnees_client["adresse"], "Retrait en usine")

    def test_livraison_sans_adresse_refusee(self):
        r, demande = self.payer(self.client_a, pour_qui="moi", mode_livraison="livraison sur chantier")
        self.assertIsNone(demande)
        self.assertIn("adresse", r.context["form"].errors)

    # --- Enregistrement après paiement ------------------------------ #
    def test_rien_enregistre_avant_confirmation_du_paiement(self):
        self.payer(self.client_a, pour_qui="moi", mode_livraison="retrait en usine")
        self.assertFalse(Order.objects.exists())
        self.assertTrue(Cart.objects.filter(pk=self.cart.pk).exists())

    def test_paiement_confirme_tout_enregistre_et_panier_vide(self):
        from usesOrders.models import OrderUserInfo, Payment, Traiment
        _, demande = self.payer(self.client_a, pour_qui="moi", mode_livraison="livraison sur chantier",
                                adresse="Bonamoussadi")
        demande.confirmer({"status": "SUCCESSFULL", "amount": demande.montant})

        order = Order.objects.get(user=self.client_a)
        self.assertEqual(order.orderitem_set.count(), 1)
        self.assertEqual(order.net_payer, demande.montant)
        info = OrderUserInfo.objects.get(order=order)
        self.assertEqual((info.nom, info.telephone, info.adresse, info.mode_livraison),
                         ("Mbarga Paul", "677112233", "Bonamoussadi", "livraison sur chantier"))
        self.assertEqual(Payment.objects.get(order=order).amount_paid, demande.montant)
        self.assertEqual(Traiment.objects.get(order=order).statut, "en_attente")
        self.assertFalse(Cart.objects.filter(user=self.client_a).exists())

    def test_paiement_avec_code_promo_puis_confirmation(self):
        self.code(self.client_a)
        self.assertTrue(self.appliquer(self.client_a)["success"])
        _, demande = self.payer(self.client_a, pour_qui="moi", mode_livraison="retrait en usine")
        demande.confirmer({"status": "SUCCESSFULL", "amount": demande.montant})
        order = Order.objects.get(user=self.client_a)
        self.assertEqual(order.remise, 10)
        self.assertEqual(order.get_prix_total, 1800)
        self.assertEqual(order.net_payer, demande.montant)


# ---------------------------------------------------------------------- #
# Étapes affichées une par une (JavaScript) : structure de la page
# ---------------------------------------------------------------------- #
class EtapesConfirmationTests(ParcoursCommandeClientTests):
    """Le JavaScript lui-même se vérifie dans le navigateur ; ici on contrôle
    que la page fournit ce dont il a besoin."""

    def page(self):
        self.client.force_login(self.client_a)
        return self.client.get(reverse("confirmer-commande"))

    def test_trois_etapes_dans_l_ordre(self):
        html = self.page().content.decode()
        positions = [html.index(f'data-etape="{n}"') for n in (1, 2, 3)]
        self.assertEqual(positions, sorted(positions))

    def test_question_code_promo_oui_non(self):
        r = self.page()
        self.assertContains(r, "Avez-vous un code promo ?")
        self.assertContains(r, 'id="promo-oui"')
        self.assertContains(r, 'id="promo-non"')

    def test_ouverture_sur_l_etape_1_par_defaut(self):
        self.assertContains(self.page(), 'data-etape-initiale="1"')

    def test_code_deja_applique_pas_de_question(self):
        self.cart.remise = 10
        self.cart.save()
        r = self.page()
        self.assertContains(r, "Code promo appliqué : remise de 10%")
        self.assertNotContains(r, 'id="question-promo"')
        self.assertNotContains(r, 'id="codeForm"')

    def test_erreur_de_facturation_rouvre_l_etape_2(self):
        r, _ = self.payer(self.client_a, pour_qui="moi", mode_livraison="livraison sur chantier")
        self.assertContains(r, 'data-etape-initiale="2"')

    def test_erreur_de_paiement_rouvre_l_etape_3(self):
        r, _ = self.payer(self.client_a, pour_qui="moi", mode_livraison="retrait en usine",
                          mode_payement="")
        self.assertContains(r, 'data-etape-initiale="3"')

    def test_erreurs_facturation_et_paiement_ouvre_la_facturation(self):
        """Deux erreurs : on rouvre la première étape concernée (facturation)."""
        r, _ = self.payer(self.client_a, pour_qui="moi", mode_livraison="livraison sur chantier",
                          mode_payement="")
        self.assertContains(r, 'data-etape-initiale="2"')

    def test_facturation_en_etape_2_paiement_en_etape_3(self):
        html = self.page().content.decode()
        e2, e3 = html.index('data-etape="2"'), html.index('data-etape="3"')
        self.assertLess(e2, html.index("Informations de facturation"))
        self.assertLess(html.index("Informations de facturation"), e3)
        self.assertLess(e3, html.index("Informations de paiement"))
        # Le bouton « Payer » et les cases CGV sont dans l'étape paiement
        self.assertLess(e3, html.index('id="bouton-payer"'))
        self.assertLess(e3, html.index('id="accepte-cgv"'))

    def test_ecran_de_lancement_present(self):
        r = self.page()
        self.assertContains(r, 'id="ecran-lancement" hidden')
        self.assertContains(r, "Lancement du paiement…")

    def test_formulaire_de_commande_hors_du_formulaire_promo(self):
        """Deux <form> distincts : le code promo ne soumet pas la commande."""
        html = self.page().content.decode()
        self.assertLess(html.index('id="codeForm"'), html.index('id="commandeForm"'))
        self.assertLess(html.index("</form>"), html.index('id="commandeForm"'))
