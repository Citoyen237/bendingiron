"""Annulation des commandes : client, proforma, projet, travaux additionnels (13/11/2026).

Règles :
  - annulation permise tant que le statut ne dépasse pas le réglage
    « Annulation permise jusqu'au statut » (admin « larue », par défaut
    « Prêt pour livraison ») ; jamais après « Livraison terminée » ;
  - définitive : un traitement « annule » est ajouté, le bouton « suivant »
    disparaît ;
  - le statut au moment de l'annulation et le montant déjà payé sont
    enregistrés (Annulation) pour les remboursements / retenues (proposition G)
    et pour le stock (proposition F : rien n'est encore retiré du stock).
"""
import logging
from decimal import Decimal

from django.db import transaction
from django.urls import reverse

from .models import STATUTS_ANNULABLES, Annulation, ReglageCommande

logger = logging.getLogger(__name__)

ANNULE = "annule"
ORDRE = [cle for cle, _ in STATUTS_ANNULABLES]          # en_attente ... solde_facture


class AnnulationImpossible(Exception):
    pass


# --------------------------------------------------------------------------- #
# Ce qui diffère d'un type de commande à l'autre
# --------------------------------------------------------------------------- #
def _modele(type_commande):
    from partenaires.models import OrderAdd, ProjetOrder
    from proforma.models import OrderPro
    from .models import Order
    return {"client": Order, "proforma": OrderPro, "projet": ProjetOrder, "additionnel": OrderAdd}[type_commande]


def _creer_traitement(type_commande, commande, user):
    from partenaires.models import TraimentAdd, TraimentOrder
    from proforma.models import TraimentPro
    from .models import Traiment
    if type_commande == "client":
        Traiment.objects.create(order=commande, user=user, statut=ANNULE)
    elif type_commande == "proforma":
        TraimentPro.objects.create(order=commande, user=user, statut=ANNULE)
    elif type_commande == "projet":
        TraimentOrder.objects.create(projet_order=commande, user=user, statut=ANNULE)
    else:
        TraimentAdd.objects.create(order=commande, user=user, statut=ANNULE)


def _montants(type_commande, commande):
    """(montant de la commande, montant déjà payé)."""
    if type_commande == "client":
        paye = sum(Decimal(str(p.amount_paid)) for p in commande.payments.all())
        return Decimal(commande.net_payer), paye
    if type_commande in ("proforma", "additionnel"):
        return Decimal(commande.net_payer), Decimal(commande.total_paye)
    # Commande projet : le projet est payé par tranches, pas la commande ;
    # montant = valeur HT des quantités commandées.
    total = sum(i.quantite * i.projet_item.prix_u for i in commande.projet_order.select_related("projet_item"))
    return Decimal(total), Decimal(0)


def _numero(type_commande, commande):
    if type_commande == "projet":
        return f"{commande.projet.name} - commande {commande.id}"
    return f"{commande.numero}"


def _destinataire(type_commande, commande):
    """(utilisateur, e-mail) prévenu de l'annulation, ou None (proforma : pas de compte client)."""
    if type_commande in ("client", "additionnel"):
        return commande.user
    if type_commande == "projet":
        return commande.projet.partenariat.user
    return None


def url_detail(type_commande, commande_id):
    return reverse({"client": "order.detail", "proforma": "detail.proforma",
                    "projet": "partenariat.orders.details",
                    "additionnel": "partenariat.detail.order.additional"}[type_commande], args=[commande_id])


# --------------------------------------------------------------------------- #
# Règles
# --------------------------------------------------------------------------- #
def peut_annuler(statut, reglage=None):
    if statut == ANNULE or statut == "termine":
        return False
    if statut not in ORDRE:          # « Aucun traitement » : commande pas encore traitée
        return True
    limite = (reglage or ReglageCommande.actuel()).annulation_jusqu_a
    return ORDRE.index(statut) <= ORDRE.index(limite)


def contexte(type_commande, commande):
    """Variables pour le bloc « Annuler la commande » des pages de détail (admin)."""
    annulation = Annulation.objects.filter(type_commande=type_commande, commande_id=commande.id).first()
    return {
        "annulation": annulation,
        "peut_annuler": annulation is None and peut_annuler(commande.get_statut_actuel),
        "url_annulation": reverse("commande.annuler", args=[type_commande, commande.id]),
    }


def annuler(type_commande, commande_id, user, motif):
    """Annule la commande ; renvoie l'Annulation. Lève AnnulationImpossible sinon."""
    motif = (motif or "").strip()
    if not motif:
        raise AnnulationImpossible("Indiquez le motif de l'annulation.")
    Modele = _modele(type_commande)
    with transaction.atomic():
        commande = Modele.objects.select_for_update().get(pk=commande_id)
        statut = commande.get_statut_actuel
        if Annulation.objects.filter(type_commande=type_commande, commande_id=commande.id).exists() \
                or statut == ANNULE:
            raise AnnulationImpossible("Cette commande est déjà annulée.")
        if not peut_annuler(statut):
            raise AnnulationImpossible(
                "Cette commande ne peut plus être annulée : son statut dépasse la limite "
                "fixée dans les réglages des commandes.")
        montant, paye = _montants(type_commande, commande)
        _creer_traitement(type_commande, commande, user)
        annulation = Annulation.objects.create(
            type_commande=type_commande, commande_id=commande.id, numero=_numero(type_commande, commande),
            statut_avant=statut if statut in ORDRE else "aucun", motif=motif[:500],
            montant_commande=montant, montant_paye=paye, user=user)

    destinataire = _destinataire(type_commande, commande)
    if destinataire and destinataire.email:
        # L'e-mail part après l'enregistrement ; une panne de messagerie ne bloque pas l'annulation
        try:
            from auth_app.utils import send_custom_email
            send_custom_email("Annulation de votre commande", "mail-annulation.html",
                              {"user": destinataire, "annulation": annulation}, [destinataire.email])
        except Exception:
            logger.exception("E-mail d'annulation non envoyé (%s %s)", type_commande, commande.id)
    return annulation
