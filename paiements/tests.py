"""
Tests du paiement : MTN indisponible, paiement simulé (dev), erreur affichée
avec son motif, coupures réseau, page d'attente (succès / échec + motif).

Lancer :  python manage.py test paiements
"""
from unittest import mock

import requests
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from auth_app.models import CustomUser
from paiements.models import DemandePaiement
from paiements.services import client_pour, simulation_active
from paiements.services.exceptions import PaiementError
from paiements.services.orange_money import OrangeMoneyClient
from paiements.services.simulation import MOTIF_REFUS, SimulationClient
from produits.models import Categorie, Produit
from usesOrders.form import OrderUserInfoForm
from usesOrders.models import Cart, CartItem, Order, Payment

FORM = {"pour_qui": "moi", "mode_livraison": "retrait en usine", "mode_payement": "orange",
        "reglement": "integrale", "telephone_pay": "677112233"}


def creer_user(email, groupe="simple"):
    user = CustomUser.objects.create_user(
        username=email, email=email, password="MotDePasse-Solide-2026",
        first_name="Paul", last_name="Mbarga", phone_number="677112233", email_verified=True)
    g, _ = Group.objects.get_or_create(name=groupe)
    user.groups.add(g)
    return user


@override_settings(SECURE_SSL_REDIRECT=False, DEBUG=False, PAIEMENT_SIMULATION=False)
class PaiementBase(TestCase):
    def setUp(self):
        cache.clear()
        self.user = creer_user("client@exemple.cm")
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png")
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, produit=self.produit, details={"fer": "bending iron"},
                                quantite=2, prix_u=1000, prix_revient=1)
        self.client.force_login(self.user)

    def statut(self, demande):
        cache.clear()  # lève la limite d'une vérification toutes les 4 s
        return self.client.get(reverse("statut-paiement-json", args=[demande.provider_reference])).json()


# ---------------------------------------------------------------------- #
# MTN indisponible
# ---------------------------------------------------------------------- #
class MtnIndisponibleTests(PaiementBase):

    def test_mtn_grise_dans_la_liste(self):
        r = self.client.get(reverse("confirmer-commande"))
        self.assertContains(r, 'value="mtn" disabled')
        self.assertContains(r, "MTN momo (indisponible)")

    def test_orange_reste_selectionnable(self):
        html = self.client.get(reverse("confirmer-commande")).content.decode()
        debut = html.index('value="orange"')
        self.assertNotIn("disabled", html[debut:html.index(">", debut)])

    def test_mtn_force_refuse_par_le_serveur(self):
        with mock.patch("paiements.views._client_pour") as client_paiement:
            r = self.client.post(reverse("confirmer-commande"), {**FORM, "mode_payement": "mtn"})
        client_paiement.assert_not_called()
        self.assertIn("mode_payement", r.context["form"].errors)
        self.assertFalse(DemandePaiement.objects.exists())

    def test_formulaire_refuse_mtn(self):
        form = OrderUserInfoForm({**FORM, "mode_payement": "mtn"}, pour_soi_possible=True)
        self.assertFalse(form.is_valid())

    def test_client_pour_mtn_leve_une_erreur_claire(self):
        with self.assertRaisesMessage(PaiementError, "indisponible"):
            client_pour("mtn")

    def test_solde_mtn_grise(self):
        order = Order.objects.create(user=self.user)
        from usesOrders.models import OrderItem
        OrderItem.objects.create(order=order, produit=self.produit, details={}, quantite=1,
                                 prix_u=1000, prix_revient=1)
        r = self.client.get(reverse("payer-solde", args=[order.id]))
        self.assertContains(r, "MTN Mobile Money (indisponible)")


# ---------------------------------------------------------------------- #
# Paiement simulé (développement)
# ---------------------------------------------------------------------- #
class SimulationTests(PaiementBase):

    def test_simulation_impossible_sans_debug(self):
        with override_settings(DEBUG=False, PAIEMENT_SIMULATION=True):
            self.assertFalse(simulation_active())
            self.assertIsInstance(client_pour("orange"), OrangeMoneyClient)

    def test_simulation_active_en_debug(self):
        with override_settings(DEBUG=True, PAIEMENT_SIMULATION=True):
            self.assertTrue(simulation_active())
            self.assertIsInstance(client_pour("orange"), SimulationClient)

    def test_simulation_ne_rend_pas_mtn_disponible(self):
        with override_settings(DEBUG=True, PAIEMENT_SIMULATION=True):
            with self.assertRaises(PaiementError):
                client_pour("mtn")

    def test_parcours_complet_simule_succes(self):
        with override_settings(DEBUG=True, PAIEMENT_SIMULATION=True):
            r = self.client.post(reverse("confirmer-commande"), FORM)
            demande = DemandePaiement.objects.get()
            self.assertRedirects(r, reverse("paiement-en-cours", args=[demande.provider_reference]),
                                 fetch_redirect_response=False)
            self.assertFalse(Order.objects.exists())          # rien avant confirmation
            data = self.statut(demande)
        self.assertTrue(data["is_final"])
        self.assertTrue(data["succes"])
        order = Order.objects.get(user=self.user)
        self.assertIn(order.numero, data["motif"])
        self.assertEqual(Payment.objects.get(order=order).amount_paid, demande.montant)
        self.assertFalse(Cart.objects.filter(user=self.user).exists())

    def test_parcours_complet_simule_echec_avec_motif(self):
        with override_settings(DEBUG=True, PAIEMENT_SIMULATION=True):
            self.client.post(reverse("confirmer-commande"), {**FORM, "telephone_pay": "690000000"})
            data = self.statut(DemandePaiement.objects.get())
        self.assertTrue(data["is_final"])
        self.assertFalse(data["succes"])
        self.assertEqual(data["status"], "ECHEC")
        self.assertEqual(data["motif"], MOTIF_REFUS)
        self.assertFalse(Order.objects.exists())
        self.assertTrue(Cart.objects.filter(pk=self.cart.pk).exists())   # panier conservé


# ---------------------------------------------------------------------- #
# Erreur de lancement visible, avec motif
# ---------------------------------------------------------------------- #
class ErreurLancementTests(PaiementBase):

    def poster(self, erreur):
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.pay.side_effect = erreur
            return self.client.post(reverse("confirmer-commande"), FORM)

    def test_erreur_affichee_sur_l_etape_paiement(self):
        r = self.poster(PaiementError("Orange Money a refusé l'accès : identifiants marchand invalides ou manquants."))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'data-etape-initiale="3"')   # étape « paiement »
        self.assertContains(r, "Le paiement n'a pas pu être lancé.")
        self.assertContains(r, "identifiants marchand invalides")
        self.assertFalse(DemandePaiement.objects.exists())

    def test_saisies_conservees(self):
        r = self.poster(PaiementError("x"))
        self.assertContains(r, 'value="677112233"')
        self.assertContains(r, '<option value="orange" selected>')

    def test_reponse_sans_reference_de_paiement(self):
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.pay.return_value = {}
            r = self.client.post(reverse("confirmer-commande"), FORM)
        self.assertContains(r, "sans référence de paiement")
        self.assertFalse(DemandePaiement.objects.exists())

    def test_erreur_sur_le_solde_affichee(self):
        from usesOrders.models import OrderItem
        order = Order.objects.create(user=self.user)
        OrderItem.objects.create(order=order, produit=self.produit, details={}, quantite=1,
                                 prix_u=1000, prix_revient=1)
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.pay.side_effect = PaiementError("Orange Money ne répond pas.")
            r = self.client.post(reverse("payer-solde", args=[order.id]),
                                 {"telephone_pay": "677112233", "mode_payement": "orange"}, follow=True)
        self.assertContains(r, "Motif : Orange Money ne répond pas.")


# ---------------------------------------------------------------------- #
# Coupures réseau : plus d'erreur 500
# ---------------------------------------------------------------------- #
class ReseauTests(PaiementBase):

    def test_delai_depasse_devient_paiement_error(self):
        with mock.patch("paiements.services.orange_money.requests.request", side_effect=requests.Timeout):
            with self.assertRaisesMessage(PaiementError, "délai dépassé"):
                OrangeMoneyClient().get_access_token(force_refresh=True)

    def test_pas_d_internet_devient_paiement_error(self):
        with mock.patch("paiements.services.orange_money.requests.request",
                        side_effect=requests.ConnectionError):
            with self.assertRaisesMessage(PaiementError, "Impossible de joindre Orange Money"):
                OrangeMoneyClient().get_access_token(force_refresh=True)

    def test_identifiants_refuses_message_clair(self):
        reponse = mock.Mock(ok=False, status_code=401, text="Unauthorized")
        with mock.patch("paiements.services.orange_money.requests.request", return_value=reponse):
            with self.assertRaisesMessage(PaiementError, "identifiants marchand"):
                OrangeMoneyClient().get_access_token(force_refresh=True)

    def test_reponse_illisible_devient_paiement_error(self):
        reponse = mock.Mock(ok=True, status_code=200, text="<html>")
        reponse.json.side_effect = ValueError
        with mock.patch("paiements.services.orange_money.requests.request", return_value=reponse):
            with self.assertRaises(PaiementError):
                OrangeMoneyClient().get_access_token(force_refresh=True)

    def test_page_ne_plante_pas_si_orange_injoignable(self):
        """Sans mock du client : vraie classe OrangeMoneyClient, réseau coupé."""
        with mock.patch("paiements.services.orange_money.requests.request",
                        side_effect=requests.ConnectionError):
            r = self.client.post(reverse("confirmer-commande"), FORM)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Impossible de joindre Orange Money")


# ---------------------------------------------------------------------- #
# Page d'attente : statut, motif, vérification active
# ---------------------------------------------------------------------- #
class PageAttenteTests(PaiementBase):

    def demande(self, **extra):
        return DemandePaiement.objects.create(
            user=self.user, cart_id=self.cart.id, provider="ORANGE", provider_reference="TOK-1",
            montant=2386, subscriber_msisdn_last4="2233", type_paiement="INTEGRAL",
            donnees_client={"nom": "Mbarga Paul", "telephone": "677112233", "adresse": "Retrait en usine",
                            "mode_livraison": "retrait en usine", "remise": 0},
            donnees_items=[{"produit_id": self.produit.id, "details": {}, "quantite": 2,
                            "prix_u": "1000", "prix_revient": "1"}], **extra)

    def verifier_avec(self, demande, reponse_operateur):
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.get_payment_status.return_value = reponse_operateur
            return self.statut(demande)

    def test_page_affiche_attente_succes_et_echec(self):
        r = self.client.get(reverse("paiement-en-cours", args=[self.demande().provider_reference]))
        for bloc in ("bloc-attente", "bloc-succes", "bloc-echec", "Réessayer le paiement"):
            self.assertContains(r, bloc)

    def test_en_attente(self):
        data = self.verifier_avec(self.demande(), {"status": "PENDING"})
        self.assertFalse(data["is_final"])

    def test_succes_cree_la_commande(self):
        data = self.verifier_avec(self.demande(), {"status": "SUCCESSFULL", "amount": "2386"})
        self.assertTrue(data["succes"])
        self.assertTrue(Order.objects.filter(user=self.user).exists())
        self.assertFalse(Cart.objects.filter(pk=self.cart.pk).exists())

    def test_echec_avec_motif_de_l_operateur(self):
        data = self.verifier_avec(self.demande(), {"status": "FAILED", "inittxnmessage": "Solde insuffisant"})
        self.assertEqual(data["status"], "ECHEC")
        self.assertEqual(data["motif"], "Solde insuffisant")
        self.assertFalse(Order.objects.exists())

    def test_echec_sans_motif_message_par_defaut(self):
        data = self.verifier_avec(self.demande(), {"status": "FAILED"})
        self.assertIn("refusé ou annulé", data["motif"])

    def test_expire(self):
        data = self.verifier_avec(self.demande(), {"status": "EXPIRED"})
        self.assertEqual(data["status"], "EXPIRE")
        self.assertIn("pas été validée à temps", data["motif"])

    def test_montant_incoherent_motif(self):
        data = self.verifier_avec(self.demande(), {"status": "SUCCESSFULL", "amount": "100"})
        self.assertEqual(data["status"], "ECHEC")
        self.assertIn("ne correspond pas", data["motif"])
        self.assertFalse(Order.objects.exists())

    def test_operateur_injoignable_reste_en_attente(self):
        demande = self.demande()
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.get_payment_status.side_effect = PaiementError("coupure")
            data = self.statut(demande)
        self.assertFalse(data["is_final"])

    def test_verification_limitee_dans_le_temps(self):
        demande = self.demande()
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.get_payment_status.return_value = {"status": "PENDING"}
            url = reverse("statut-paiement-json", args=[demande.provider_reference])
            self.client.get(url)
            self.client.get(url)
        self.assertEqual(client_paiement.return_value.get_payment_status.call_count, 1)

    def test_regression_webhook_statut_interne(self):
        """Avant : le webhook enregistrait « FAILED » (hors des choix) -> « Statut inconnu »."""
        demande = self.demande()
        with mock.patch("paiements.views._client_pour") as client_paiement:
            client_paiement.return_value.get_payment_status.return_value = {"status": "FAILED"}
            self.client.post(reverse("notif-orange"), {"payToken": demande.provider_reference})
        demande.refresh_from_db()
        self.assertEqual(demande.statut, DemandePaiement.Statut.ECHEC)

    def test_confirmation_en_double_une_seule_commande(self):
        """La page d'attente et le webhook confirment tous les deux : une seule commande."""
        demande = self.demande()
        copie = DemandePaiement.objects.get(pk=demande.pk)   # 2e instance « en retard »
        demande.confirmer({"status": "SUCCESSFULL", "amount": "2386"})
        copie.confirmer({"status": "SUCCESSFULL", "amount": "2386"})
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Payment.objects.count(), 1)

    def test_paiement_confirme_ne_repasse_pas_en_echec(self):
        demande = self.demande()
        copie = DemandePaiement.objects.get(pk=demande.pk)
        demande.confirmer({"status": "SUCCESSFULL", "amount": "2386"})
        copie.marquer_echec("EXPIRE", {}, "trop tard")
        demande.refresh_from_db()
        self.assertEqual(demande.statut, DemandePaiement.Statut.CONFIRME)
