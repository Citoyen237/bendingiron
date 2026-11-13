"""
payments/models.py — DemandePaiement = une transaction de paiement (tentative
auprès d'Orange/MTN), qu'elle serve à CRÉER une commande (1ère tranche) ou à
SOLDER une commande déjà existante (tranche suivante).

Deux cas d'usage, distingués par order_id au moment de la création :

  CAS A — Nouvelle commande (order=None à la création)
    Le panier n'est pas encore converti en Order. donnees_client/donnees_items
    contiennent le snapshot du formulaire + du panier. confirmer() créera
    Order + OrderItem + OrderUserInfo.

  CAS B — Tranche suivante sur une commande existante (order=<Order> dès la création)
    Order/OrderUserInfo existent déjà (créés au CAS A précédent). Pas besoin
    de donnees_client/donnees_items. confirmer() se contente d'ajouter un
    Payment et de mettre à jour le Traiment.

Dans les deux cas, CHAQUE transaction (réussie ou non) laisse une ligne
DemandePaiement — c'est l'historique complet des tentatives de paiement.
"""

import logging

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from auth_app.models import CustomUser
logger = logging.getLogger(__name__)


class DemandePaiement(models.Model):
    class Provider(models.TextChoices):
        ORANGE = "ORANGE", "Orange Money"
        MTN = "MTN", "MTN Mobile Money"

    class TypePaiement(models.TextChoices):
        INTEGRAL = "INTEGRAL", "Paiement intégral"
        ECHELONNE = "ECHELONNE", "Paiement échelonné (tranche)"

    class Statut(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente de confirmation client"
        CONFIRME = "CONFIRME", "Confirmé et enregistré"
        ECHEC = "ECHEC", "Échoué"
        EXPIRE = "EXPIRE", "Expiré"
    
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)

   # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    provider = models.CharField(max_length=10, choices=Provider.choices)
    provider_reference = models.CharField(max_length=64, unique=True, db_index=True)
    montant = models.PositiveIntegerField()  # montant réellement payé par CETTE transaction
    subscriber_msisdn_last4 = models.CharField(max_length=4)
    type_paiement = models.CharField(max_length=10, choices=TypePaiement.choices)

    statut = models.CharField(max_length=12, choices=Statut.choices, default=Statut.EN_ATTENTE)

    # Renseigné dès la création SI ET SEULEMENT SI la commande existe déjà
    # (CAS B). Reste null jusqu'à confirmer() pour une nouvelle commande (CAS A).
    order = models.ForeignKey(
        "usesOrders.Order",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="transactions",
    )

    # --- Uniquement utile au CAS A (nouvelle commande) ; vide au CAS B --- #
    cart_id = models.PositiveIntegerField(null=True, blank=True)
    donnees_client = models.JSONField(blank=True, default=dict)
    donnees_items = models.JSONField(blank=True, default=list)

    last_raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.provider} — {self.provider_reference} — {self.statut}"

    @property
    def est_nouvelle_commande(self) -> bool:
        """True si cette transaction doit créer la commande (CAS A)."""
        return self.order_id is None

    # ------------------------------------------------------------------ #
    # Statut renvoyé par l'opérateur -> statut interne + motif affiché
    # ------------------------------------------------------------------ #
    STATUTS_SUCCES = ("SUCCESSFULL", "SUCCESSFUL")
    STATUTS_ECHEC = {"FAILED": "ECHEC", "REJECTED": "ECHEC", "CANCELLED": "ECHEC", "EXPIRED": "EXPIRE"}
    MOTIFS_PAR_DEFAUT = {
        "ECHEC": "Le paiement a été refusé ou annulé sur le téléphone.",
        "EXPIRE": "La demande n'a pas été validée à temps sur le téléphone.",
    }

    @property
    def motif(self) -> str:
        """Raison de l'échec (ou du succès) à afficher au client."""
        motif = (self.last_raw_response or {}).get("motif")
        if motif:
            return motif
        if self.statut == self.Statut.CONFIRME and self.order_id:
            return f"Commande n° {self.order.numero} enregistrée."
        return self.MOTIFS_PAR_DEFAUT.get(self.statut, "")

    def marquer_echec(self, statut: str, raw_response: dict, motif: str) -> None:
        if self.statut == self.Statut.CONFIRME or \
                DemandePaiement.objects.filter(pk=self.pk, statut=self.Statut.CONFIRME).exists():
            return  # un paiement confirmé ne repasse jamais en échec
        raw = dict(raw_response or {})
        raw["motif"] = motif or self.MOTIFS_PAR_DEFAUT.get(statut, "")
        self.statut = statut
        self.last_raw_response = raw
        self.save(update_fields=["statut", "last_raw_response"])

    def appliquer_statut_operateur(self, raw_response: dict) -> None:
        """Applique le statut lu chez Orange/MTN (webhook ou vérification active).
        Statut encore en attente -> rien ne change."""
        raw_response = raw_response or {}
        statut = raw_response.get("status")
        if statut in self.STATUTS_SUCCES:
            self.confirmer(raw_response)
        elif statut in self.STATUTS_ECHEC:
            interne = self.STATUTS_ECHEC[statut]
            motif = (raw_response.get("confirmtxnmessage") or raw_response.get("inittxnmessage")
                     or raw_response.get("reason") or self.MOTIFS_PAR_DEFAUT[interne])
            self.marquer_echec(interne, raw_response, motif)

    @transaction.atomic
    def confirmer(self, raw_response: dict) -> None:
        """
        Appelée uniquement après re-vérification réussie auprès d'Orange/MTN
        (jamais sur la seule foi du webhook). Enregistre tout ce qui doit
        l'être — création de la commande si besoin, puis dans tous les cas
        le Payment et la mise à jour du Traiment.
        """
        from usesOrders.models import Cart, Order, OrderItem, OrderUserInfo, Traiment, Payment

        if self.statut == self.Statut.CONFIRME:
            return  # idempotence

        # Verrou : la page d'attente et le webhook peuvent confirmer en même
        # temps ; un seul des deux crée la commande.
        actuel = DemandePaiement.objects.select_for_update().get(pk=self.pk)
        if actuel.statut == self.Statut.CONFIRME:
            self.statut, self.order_id = actuel.statut, actuel.order_id
            return

        # Le montant réellement payé chez l'opérateur doit correspondre à celui demandé
        montant_recu = raw_response.get("amount")
        if montant_recu is not None:
            try:
                montant_ok = round(float(montant_recu)) == int(self.montant)
            except (TypeError, ValueError):
                montant_ok = False
            if not montant_ok:
                logger.error("Montant incohérent pour %s : attendu %s, reçu %s",
                             self.provider_reference, self.montant, montant_recu)
                self.marquer_echec(
                    self.Statut.ECHEC, raw_response,
                    "Le montant payé ne correspond pas au montant demandé. Contactez-nous.")
                return
        else:
            logger.warning("Réponse opérateur sans montant pour %s", self.provider_reference)

        self.last_raw_response = raw_response
        nouvelle_commande = self.est_nouvelle_commande  # capturé AVANT de muter self.order

        if nouvelle_commande:
            # --- CAS A : on matérialise la commande pour la 1ère fois --- #
            # La remise du code promo appliquée au panier est conservée sur la commande
            order = Order.objects.create(user=self.user, remise=self.donnees_client.get("remise", 0))

            for item in self.donnees_items:
                OrderItem.objects.create(
                    order=order,
                    produit_id=item["produit_id"],
                    details=item["details"],
                    quantite=item["quantite"],
                    prix_u=item["prix_u"],
                    prix_revient=item["prix_revient"],
                )

            OrderUserInfo.objects.create(
                order=order,
                nom=self.donnees_client["nom"],
                telephone=self.donnees_client["telephone"],
                adresse=self.donnees_client["adresse"],
                mode_livraison=self.donnees_client["mode_livraison"],
            )

            if self.cart_id:
                Cart.objects.filter(id=self.cart_id).delete()

            self.order = order
        else:
            # --- CAS B : la commande existe déjà, rien à créer côté commande --- #
            order = self.order

        # --- Commun aux deux cas : enregistrer CETTE transaction --- #
        Payment.objects.create(order=order, amount_paid=self.montant)

        # 1ère transaction (intégral ou 1ère tranche) -> 'en_attente' : la
        # commande est reçue, la production peut démarrer.
        # Transaction sur commande déjà existante (règlement du solde restant,
        # CAS B) -> 'solde_facture' : le client vient de régler ce qu'il devait
        # encore.
        statut_traitement = "en_attente" if nouvelle_commande else "solde_facture"
        if not nouvelle_commande and order.get_statut_actuel == "annule":
            # Commande annulée pendant le paiement : l'argent est enregistré
            # (à rembourser), mais l'annulation reste le dernier statut.
            logger.warning("Paiement reçu sur la commande annulée %s", order.id)
            from django.db.models import F
            from usesOrders.models import Annulation
            Annulation.objects.filter(type_commande="client", commande_id=order.id).update(
                montant_paye=F("montant_paye") + self.montant)
        else:
            Traiment.objects.create(order=order, user=self.user, statut=statut_traitement)

        self.statut = self.Statut.CONFIRME
        self.confirmed_at = timezone.now()
        self.save()

        logger.info(
            "Transaction confirmée : order=%s user=%s montant=%s nouvelle_commande=%s",
            order.id, self.user_id, self.montant, nouvelle_commande,
        )


def expirer_demandes_perimees(delai_secondes: int = 60) -> int:
    """
    À planifier en tâche périodique (Celery beat toutes les 15-30s, ou cron
    appelant une management command). Pour chaque DemandePaiement encore
    EN_ATTENTE depuis plus de `delai_secondes` :
      - on revérifie une DERNIÈRE fois le vrai statut auprès du provider
        (au cas où le paiement aurait réussi mais que le webhook n'a pas
        encore été reçu) ;
      - si c'est bien un succès -> on confirme normalement (confirmer()) ;
      - sinon -> on marque EXPIRE, sans toucher à Order/Payment/Traiment.

    Retourne le nombre de demandes traitées.
    """
    from .services import client_pour
    from .services.exceptions import PaiementError

    seuil = timezone.now() - timezone.timedelta(seconds=delai_secondes)
    perimees = DemandePaiement.objects.filter(
        statut=DemandePaiement.Statut.EN_ATTENTE, created_at__lt=seuil
    )

    traitees = 0
    for demande in perimees:
        try:
            real_status = client_pour(demande.provider).get_payment_status(demande.provider_reference)
        except PaiementError:
            logger.exception(
                "Échec re-vérification avant expiration pour %s", demande.provider_reference
            )
            continue  # on retentera au prochain passage de la tâche

        statut_reel = real_status.get("status")

        if statut_reel in DemandePaiement.STATUTS_SUCCES or statut_reel in DemandePaiement.STATUTS_ECHEC:
            demande.appliquer_statut_operateur(real_status)
        else:
            demande.marquer_echec(DemandePaiement.Statut.EXPIRE, real_status,
                                  DemandePaiement.MOTIFS_PAR_DEFAUT["EXPIRE"])
            logger.info("Demande de paiement expirée : %s", demande.provider_reference)

        traitees += 1

    return traitees