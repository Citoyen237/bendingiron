"""Statut « Annulée » des commandes client, proforma, projet et additionnelles (13/11/2026)."""
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from auth_app.models import CustomUser
from partenaires.models import (OrderAdd, OrderItemAdd, Partenariats, PaymentAdd, Projet, ProjetItem,
                                ProjetOrder, ProjetOrderItem, TraimentAdd, TraimentOrder)
from produits.models import Categorie, Produit
from proforma.models import OrderItemPro, OrderPro, PaymentPro, TraimentPro
from usesOrders.annulation import peut_annuler
from usesOrders.models import Annulation, Order, OrderItem, Payment, ReglageCommande, Traiment

from .statistiques import statistiques


def utilisateur(email, groupe):
    u = CustomUser.objects.create_user(username=email, email=email, password="MotDePasse-Solide-2026",
                                       first_name="Paul")
    g, _ = Group.objects.get_or_create(name=groupe)
    u.groups.add(g)
    return u


class Base(TestCase):
    def setUp(self):
        self.admin = utilisateur("admin@x.cm", "admin")
        self.client_a = utilisateur("a@x.cm", "simple")
        cat = Categorie.objects.create(libelle="Cadres")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre carre", name_page="p",
                                              imageshop2d="a.png", imageshop3d="b.png")
        self.client.force_login(self.admin)

    def commande_client(self, statut="en_attente"):
        o = Order.objects.create(user=self.client_a)
        OrderItem.objects.create(order=o, produit=self.produit, details={}, quantite=2, prix_u=1000, prix_revient=1)
        Traiment.objects.create(order=o, user=self.admin, statut=statut)
        return o

    def annuler(self, type_commande, commande_id, motif="Le client renonce"):
        return self.client.post(reverse("commande.annuler", args=[type_commande, commande_id]),
                                {"motif": motif}, secure=True)


class AnnulationCommandeClientTests(Base):
    def test_annulation_enregistree_et_definitive(self):
        o = self.commande_client("en_production")
        Payment.objects.create(order=o, amount_paid=700)
        reponse = self.annuler("client", o.id)
        self.assertRedirects(reponse, reverse("order.detail", args=[o.id]), fetch_redirect_response=False)

        self.assertEqual(Order.objects.get(pk=o.pk).get_statut_actuel, "annule")
        a = Annulation.objects.get(type_commande="client", commande_id=o.id)
        self.assertEqual(a.statut_avant, "en_production")
        self.assertEqual(a.montant_paye, Decimal("700"))
        self.assertEqual(a.montant_commande, o.net_payer)
        self.assertEqual(a.motif, "Le client renonce")
        self.assertIsNone(a.montant_rembourse)              # proposition G : pas encore géré

        # e-mail au client
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["a@x.cm"])
        self.assertIn("annulée", mail.outbox[0].body)
        self.assertIn("Montant à rembourser : 700 FCFA", mail.outbox[0].body)
        self.assertIn("Sept cents francs CFA", mail.outbox[0].body)
        self.assertIn("direction de BENDING IRON", mail.outbox[0].body)

        # le bouton « suivant » ne fait plus avancer
        self.client.post(reverse("change.status", args=[o.id]), secure=True)
        self.assertEqual(Order.objects.get(pk=o.pk).get_statut_actuel, "annule")

        # pas de seconde annulation
        self.annuler("client", o.id)
        self.assertEqual(Annulation.objects.count(), 1)

        page = self.client.get(reverse("order.detail", args=[o.id]), secure=True)
        self.assertContains(page, "Annulée")
        self.assertContains(page, "Le client renonce")
        self.assertNotContains(page, reverse("change.status", args=[o.id]))

    def test_motif_obligatoire(self):
        o = self.commande_client()
        self.annuler("client", o.id, motif="  ")
        self.assertFalse(Annulation.objects.exists())
        self.assertEqual(Order.objects.get(pk=o.pk).get_statut_actuel, "en_attente")

    def test_limite_par_defaut_pret_pour_livraison(self):
        self.assertTrue(peut_annuler("en_attente"))
        self.assertTrue(peut_annuler("pret_pour_livraison"))
        self.assertFalse(peut_annuler("solde_facture"))
        self.assertFalse(peut_annuler("termine"))
        self.assertFalse(peut_annuler("annule"))

        o = self.commande_client("solde_facture")
        page = self.client.get(reverse("order.detail", args=[o.id]), secure=True)
        self.assertNotContains(page, reverse("commande.annuler", args=["client", o.id]))
        self.annuler("client", o.id)
        self.assertFalse(Annulation.objects.exists())

    def test_limite_reglable_dans_larue(self):
        ReglageCommande.objects.create(annulation_jusqu_a="en_attente")
        o = self.commande_client("en_production")
        self.annuler("client", o.id)
        self.assertFalse(Annulation.objects.exists())

        ReglageCommande.objects.update(annulation_jusqu_a="solde_facture")
        o2 = self.commande_client("solde_facture")
        page = self.client.get(reverse("order.detail", args=[o2.id]), secure=True)
        self.assertContains(page, reverse("commande.annuler", args=["client", o2.id]))
        self.annuler("client", o2.id)
        self.assertTrue(Annulation.objects.filter(commande_id=o2.id).exists())

    def test_terminee_jamais_annulable(self):
        ReglageCommande.objects.create(annulation_jusqu_a="solde_facture")
        o = self.commande_client("termine")
        self.annuler("client", o.id)
        self.assertFalse(Annulation.objects.exists())

    def test_reserve_aux_admins(self):
        o = self.commande_client()
        self.client.force_login(self.client_a)
        self.assertEqual(self.annuler("client", o.id).status_code, 403)
        self.assertFalse(Annulation.objects.exists())

    def test_type_inconnu(self):
        self.assertEqual(self.annuler("autre", 1).status_code, 404)

    def test_solde_refuse_et_affichage_client(self):
        o = self.commande_client("pret_pour_livraison")
        self.annuler("client", o.id)
        self.client.force_login(self.client_a)
        reponse = self.client.get(reverse("payer-solde", args=[o.id]), secure=True)
        self.assertRedirects(reponse, reverse("mes_commande"), fetch_redirect_response=False)
        liste = self.client.get(reverse("mes_commande"), secure=True)
        self.assertContains(liste, "Annulée")


class AnnulationProjetTests(Base):
    def setUp(self):
        super().setUp()
        self.partenaire = utilisateur("p@x.cm", "partenaire")
        part = Partenariats.objects.create(user=self.partenaire, name="Entreprise A", email="ea@x.cm",
                                           adresse="D", telephone="6", date_debut="2026-01-01T00:00:00Z",
                                           date_fin="2027-01-01T00:00:00Z")
        self.projet = Projet.objects.create(partenariat=part, user=self.admin, name="Projet A")
        self.item = ProjetItem.objects.create(projet=self.projet, produit=self.produit, details={},
                                              prix_revient=1, quantite=10, prix_u=100)

    def test_quantites_rendues_au_restant(self):
        po = ProjetOrder.objects.create(projet=self.projet)
        ProjetOrderItem.objects.create(projet_order=po, projet_item=self.item, quantite=4)
        TraimentOrder.objects.create(projet_order=po, user=self.admin, statut="en_attente")
        self.assertEqual(self.item.quantite_restant, 6)

        self.annuler("projet", po.id)
        self.assertEqual(ProjetItem.objects.get(pk=self.item.pk).quantite_restant, 10)
        self.assertEqual(Projet.objects.get(pk=self.projet.pk).quantite_commande_totale, 0)
        a = Annulation.objects.get(type_commande="projet")
        self.assertEqual(a.montant_commande, Decimal("400"))
        self.assertEqual(mail.outbox[0].to, ["p@x.cm"])

        self.client.post(reverse("partenariat.orders.statut", args=[po.id]), secure=True)
        self.assertEqual(ProjetOrder.objects.get(pk=po.pk).get_statut_actuel, "annule")

        # côté partenaire : badge rouge et motif dans l'historique, bandeau sur le détail
        self.client.force_login(self.partenaire)
        historique = self.client.get(reverse("historique-order", args=[self.projet.id]), secure=True)
        self.assertContains(historique, '<span class="badge bg-danger"', html=False)
        self.assertContains(historique, "Motif : Le client renonce")
        detail = self.client.get(reverse("front.orders.details", args=[po.id]), secure=True)
        self.assertContains(detail, "Cette demande de livraison partielle est annulée")
        self.assertContains(detail, "Motif : Le client renonce")

    def test_travaux_additionnels(self):
        travail = OrderAdd.objects.create(projet_order=self.projet, user=self.partenaire)
        OrderItemAdd.objects.create(order=travail, produit=self.produit, details={}, quantite=1,
                                    prix_u=1000, prix_revient=1)
        TraimentAdd.objects.create(order=travail, user=self.admin, statut="pret_pour_livraison")
        PaymentAdd.objects.create(user=self.admin, order=travail, amount_paid=300, mode_paid="om")

        url = reverse("partenariat.detail.order.additional", args=[travail.id])
        self.assertContains(self.client.get(url, secure=True), reverse("commande.annuler", args=["additionnel", travail.id]))
        self.annuler("additionnel", travail.id)
        a = Annulation.objects.get(type_commande="additionnel")
        self.assertEqual((a.statut_avant, a.montant_paye), ("pret_pour_livraison", Decimal("300")))

        # plus aucun paiement enregistré
        self.client.post(url, {"amount_paid": "100", "mode_paid": "om"}, secure=True)
        self.assertEqual(PaymentAdd.objects.filter(order=travail).count(), 1)
        page = self.client.get(reverse("partenariat.order.additional.projet", args=[self.projet.id]), secure=True)
        self.assertContains(page, "Annulée")


class AnnulationProformaTests(Base):
    def test_proforma(self):
        pro = OrderPro.objects.create(user=self.admin)
        OrderItemPro.objects.create(order=pro, produit=self.produit, details={}, quantite=1, prix_u=1000, prix_revient=1)
        TraimentPro.objects.create(order=pro, user=self.admin, statut="en_attente")
        self.annuler("proforma", pro.id)
        pro = OrderPro.objects.get(pk=pro.pk)
        self.assertEqual(pro.get_statut_actuel, "annule")
        self.assertEqual(pro.statut_final, "Annulée")
        self.assertEqual(len(mail.outbox), 0)              # proforma : pas de compte client
        self.client.post(reverse("detail.proforma", args=[pro.id]), {"amount_paid": "100", "mode_paid": "om"},
                         secure=True)
        self.assertFalse(PaymentPro.objects.filter(order=pro).exists())


class StatistiquesAnnulationsTests(Base):
    def test_exclues_du_chiffre_affaires_et_comptees_a_part(self):
        annee = timezone.localdate().year
        gardee = self.commande_client()
        annulee = self.commande_client("en_production")
        Payment.objects.create(order=annulee, amount_paid=500)
        self.annuler("client", annulee.id)

        s = statistiques(annee)
        self.assertEqual(s["ca"]["par_type"]["client"], gardee.net_payer)
        self.assertEqual(s["commandes"]["nombre"]["client"], 1)
        self.assertEqual(s["encaissements"]["reste"], gardee.net_payer)
        self.assertEqual(s["annulations"]["nombre"]["client"], 1)
        self.assertEqual(s["annulations"]["montant_total"], annulee.net_payer)
        self.assertEqual(s["annulations"]["par_statut"], [("En production", 1)])
        self.assertEqual(s["annulations"]["deja_paye"], 500)
        self.assertIsNone(s["annulations"]["a_rembourser"])

        page = self.client.get(reverse("admin.statistiques"), secure=True)
        self.assertContains(page, 'id="bloc-annulations"')
        self.assertContains(page, "Remboursements à faire")


class RemboursementTests(Base):
    """Remboursement d'une commande annulée, enregistré par l'admin (14/11/2026)."""

    def setUp(self):
        super().setUp()
        self.o = self.commande_client("en_production")
        Payment.objects.create(order=self.o, amount_paid=700)
        self.annuler("client", self.o.id)
        self.url = reverse("commande.rembourser", args=["client", self.o.id])

    def test_formulaire_puis_mention_remboursee(self):
        detail = reverse("order.detail", args=[self.o.id])
        self.assertContains(self.client.get(detail, secure=True), "Enregistrer le remboursement")

        reponse = self.client.post(self.url, {"montant": "700", "mode": "Espèces", "reference": "REC-12"}, secure=True)
        self.assertRedirects(reponse, detail, fetch_redirect_response=False)
        a = Annulation.objects.get(type_commande="client", commande_id=self.o.id)
        self.assertTrue(a.est_rembourse)
        self.assertEqual((a.montant_rembourse, a.montant_retenu, a.mode_remboursement), (Decimal("700"), 0, "Espèces"))
        self.assertEqual(a.rembourse_par, self.admin)

        page = self.client.get(detail, secure=True)
        self.assertContains(page, "Remboursée")
        self.assertContains(page, "réf. REC-12")
        self.assertNotContains(page, "Enregistrer le remboursement")

        # côté client
        from usesOrders.models import OrderUserInfo
        OrderUserInfo.objects.create(order=self.o, nom="Alice", telephone="6", adresse="Douala")
        self.client.force_login(self.client_a)
        page_client = self.client.get(reverse("detail_commande", args=[self.o.id]), secure=True)
        self.assertContains(page_client, "Remboursée")

        # statistiques : remboursement fait
        s = statistiques(timezone.localdate().year)
        self.assertEqual(s["annulations"]["rembourse"], 700)
        self.assertEqual(s["annulations"]["a_rembourser"], 0)

    def test_remboursement_partiel_le_reste_est_retenu(self):
        self.client.post(self.url, {"montant": "500", "mode": "Orange Money"}, secure=True)
        a = Annulation.objects.get(commande_id=self.o.id)
        self.assertEqual((a.montant_rembourse, a.montant_retenu), (Decimal("500"), Decimal("200")))

    def test_refus(self):
        for donnees in ({"montant": "800", "mode": "Espèces"},      # plus que le déjà payé
                        {"montant": "0", "mode": "Espèces"},
                        {"montant": "700", "mode": ""}):            # mode manquant
            self.client.post(self.url, donnees, secure=True)
            self.assertFalse(Annulation.objects.get(commande_id=self.o.id).est_rembourse, donnees)
        self.client.post(self.url, {"montant": "700", "mode": "Espèces"}, secure=True)
        self.client.post(self.url, {"montant": "100", "mode": "Espèces"}, secure=True)   # 2e fois : ignoré
        self.assertEqual(Annulation.objects.get(commande_id=self.o.id).montant_rembourse, Decimal("700"))

    def test_reserve_aux_admins(self):
        self.client.force_login(self.client_a)
        self.assertEqual(self.client.post(self.url, {"montant": "700", "mode": "Espèces"}, secure=True).status_code, 403)
