"""
payments/views.py

Vues du flux de paiement, couvrant les deux cas gérés par DemandePaiement :
  - send_info_user  -> CAS A : panier -> nouvelle commande (1ère transaction)
  - payer_solde      -> CAS B : commande existante -> tranche suivante

Plus les vues communes aux deux cas : la page d'attente (spinner), le
endpoint de statut en JSON (polling), et le webhook Orange/MTN.

Rappel de la séparation des responsabilités (cf. échange précédent) :
  Les vues ne décident JAMAIS "qu'est-ce que ça veut dire qu'un paiement est
  confirmé" — elles se contentent de récupérer les infos HTTP, appeler le
  service réseau (OrangeMoneyClient), et déléguer au modèle via
  demande.confirmer(). Toute la logique métier vit dans DemandePaiement.confirmer().
"""

import logging
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from usesOrders.models import Cart, Order

from usesOrders.form import *
from usesOrders.promo import retirer_remise_si_invalide
from auth_app.permissions import is_admin
from django.core.cache import cache

from .models import DemandePaiement
from .services import MTN_DISPONIBLE, client_pour
from .services.exceptions import PaiementError

logger = logging.getLogger(__name__)

MESSAGE_ECHEC_LANCEMENT = "Le paiement n'a pas pu être lancé."
INTERVALLE_VERIFICATION = 4  # secondes minimum entre deux vérifications chez l'opérateur


def _client_pour(provider: str):
    """Sélectionne le bon service (Orange, MTN, ou simulation en développement)."""
    return client_pour(provider)


def _lancer_paiement(provider, **kwargs):
    """Lance le paiement ; renvoie (payToken, None) ou (None, motif de l'échec)."""
    try:
        result = _client_pour(provider).pay(**kwargs)
        pay_token = (result or {}).get("payToken")
        if not pay_token:
            raise PaiementError("Réponse de l'opérateur sans référence de paiement.")
        return pay_token, None
    except PaiementError as exc:
        logger.warning("Échec de lancement du paiement (%s) : %s", provider, exc)
        return None, str(exc)


# ---------------------------------------------------------------------- #
# CAS A — panier -> nouvelle commande
# ---------------------------------------------------------------------- #
@login_required
def send_info_user(request):
    panier = Cart.objects.filter(user=request.user).first()
    paniers_details = []
    total_prix = 0

    if panier:
        for item in panier.items.all():
            paniers_details.append({
                "id": item.id,
                "produit": item.produit,
                "details": item.details_to_text(),
                "quantite": item.quantite,
                "prix": item.prix_u,
                "total": item.get_prix_total,
            })
        total_prix = panier.get_prix_total

    # Un client peut commander pour lui (infos reprises de son compte) ou pour
    # un tiers ; un admin (bouton « Client ») saisit toujours les infos du client.
    pour_soi_possible = not is_admin(request.user)

    if request.method == "POST":
        form = OrderUserInfoForm(request.POST, pour_soi_possible=pour_soi_possible)

        if form.is_valid():
            if not panier or not panier.items.exists():
                messages.error(request, "Votre panier est vide.")
                return redirect("panier")

            # Le panier a pu changer depuis l'application du code promo
            erreur = retirer_remise_si_invalide(panier)
            if erreur:
                messages.error(request, f"Code promo retiré : {erreur}")
                return redirect("confirmer-commande")

            data = form.cleaned_data

            # "integrale" -> paiement complet ; "tranche" -> 1ère tranche (30%)
            type_paiement = (
                DemandePaiement.TypePaiement.INTEGRAL
                if data["reglement"] == "integrale"
                else DemandePaiement.TypePaiement.ECHELONNE
            )
            montant_a_payer = (
                panier.net_payer
                if type_paiement == DemandePaiement.TypePaiement.INTEGRAL
                else panier.get_tranche1
            )

            donnees_items = [
                {
                    "produit_id": item.produit_id,
                    "details": item.details,
                    "quantite": item.quantite,
                    # str() : un Decimal n'est pas sérialisable en JSON
                    "prix_u": str(item.prix_u),
                    "prix_revient": str(item.prix_revient),
                }
                for item in panier.items.all()
            ]
            # Rien n'est enregistré comme commande ici : Order, OrderItem,
            # OrderUserInfo et Payment sont créés, et le panier vidé, seulement
            # quand le paiement est confirmé (DemandePaiement.confirmer).
            donnees_client = {
                **form.infos_client(request.user),
                "remise": float(panier.remise or 0),
            }

            provider = data["mode_payement"]  # "orange" ou "mtn"

            pay_token, erreur_paiement = _lancer_paiement(
                provider,
                subscriber_msisdn=str(int(data["telephone_pay"])),
                amount=montant_a_payer,
                order_id=f"cart{panier.id}-{request.user.id}",
                description="Commande matériaux",
            )
            if erreur_paiement:
                # On réaffiche la page sur l'étape « paiement », saisies conservées
                return _page_confirmation(request, panier, paniers_details, total_prix, form,
                                          erreur_paiement=erreur_paiement)

            # CAS A : order=None -> DemandePaiement.est_nouvelle_commande sera True
            demande = DemandePaiement.objects.create(
                user=request.user,
                cart_id=panier.id,
                provider=provider.upper(),
                provider_reference=pay_token,
                montant=montant_a_payer,
                subscriber_msisdn_last4=str(int(data["telephone_pay"]))[-4:],
                type_paiement=type_paiement,
                donnees_client=donnees_client,
                donnees_items=donnees_items,
            )

            return redirect("paiement-en-cours", pay_token=demande.provider_reference)
    else:
        form = OrderUserInfoForm(pour_soi_possible=pour_soi_possible)

    return _page_confirmation(request, panier, paniers_details, total_prix, form)


def _page_confirmation(request, panier, paniers_details, total_prix, form, erreur_paiement=None):
    context = {
        "paniers": paniers_details,
        "total_prix": total_prix,
        "montant_ht_brut": panier.montant_ht_brut if panier else 0,
        "remise": panier.remise if panier else 0,
        "montant_remise": round(panier.montant_remise()) if panier else 0,
        "montant_tva": panier.montant_tva if panier else 0,
        "net_payer": panier.net_payer if panier else 0,
        "get_tranche1": panier.get_tranche1 if panier else 0,
        "get_tranche2": panier.get_tranche2 if panier else 0,
        "form": form,
        "erreur_paiement": erreur_paiement,
    }
    return render(request, "confirmer-commande.html", context)


# ---------------------------------------------------------------------- #
# CAS B — solder une commande déjà existante (tranche suivante)
# ---------------------------------------------------------------------- #
@login_required
def payer_solde(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    total_deja_paye = sum(p.amount_paid for p in order.payments.all())
    reste_a_payer = round(float(order.net_payer) - total_deja_paye)

    if reste_a_payer <= 0:
        messages.info(request, "Cette commande est déjà entièrement payée.")
        return redirect("mes_commande")

    if request.method == "POST":
        telephone_pay = re.sub(r"\D", "", request.POST.get("telephone_pay") or "")
        provider = request.POST.get("mode_payement")  # "orange" ou "mtn"

        if not re.fullmatch(r"(237)?6\d{8}", telephone_pay) or provider not in ("orange", "mtn"):
            messages.error(request, "Merci de renseigner un numéro et un moyen de paiement.")
            return redirect("payer-solde", order_id=order.id)

        pay_token, erreur_paiement = _lancer_paiement(
            provider,
            subscriber_msisdn=telephone_pay,
            amount=reste_a_payer,
            order_id=f"order{order.id}-solde",
            description=f"Solde commande #{order.id}",
        )
        if erreur_paiement:
            messages.error(request, f"{MESSAGE_ECHEC_LANCEMENT} Motif : {erreur_paiement}")
            return redirect("payer-solde", order_id=order.id)

        # CAS B : order est déjà renseigné -> confirmer() ne recréera rien
        demande = DemandePaiement.objects.create(
            user=request.user,
            order=order,
            provider=provider.upper(),
            provider_reference=pay_token,
            montant=reste_a_payer,
            subscriber_msisdn_last4=telephone_pay[-4:],
            type_paiement=DemandePaiement.TypePaiement.ECHELONNE,
        )

        return redirect("paiement-en-cours", pay_token=demande.provider_reference)

    return render(
        request,
        "payments/payer_solde.html",
        {"order": order, "reste_a_payer": reste_a_payer, "mtn_disponible": MTN_DISPONIBLE},
    )


# ---------------------------------------------------------------------- #
# Communes aux deux cas
# ---------------------------------------------------------------------- #
@login_required
def paiement_en_cours(request, pay_token):
    demande = get_object_or_404(DemandePaiement, provider_reference=pay_token, user=request.user)
    return render(request, "payments/paiement_en_cours.html", {"demande": demande})


@login_required
def statut_paiement_json(request, pay_token):
    try:
        demande = DemandePaiement.objects.get(provider_reference=pay_token, user=request.user)
    except DemandePaiement.DoesNotExist:
        raise Http404

    # Vérification active chez l'opérateur (au plus une fois toutes les
    # INTERVALLE_VERIFICATION secondes) : le paiement est confirmé même si le
    # webhook n'arrive pas (cas du développement en local).
    if demande.statut == DemandePaiement.Statut.EN_ATTENTE and \
            cache.add(f"verif-paiement-{demande.pk}", 1, INTERVALLE_VERIFICATION):
        try:
            demande.appliquer_statut_operateur(
                _client_pour(demande.provider).get_payment_status(pay_token))
        except PaiementError as exc:
            logger.warning("Vérification du statut impossible pour %s : %s", pay_token, exc)
        demande.refresh_from_db()

    messages_par_statut = {
        DemandePaiement.Statut.EN_ATTENTE: "En attente de confirmation sur votre téléphone…",
        DemandePaiement.Statut.CONFIRME: "Paiement confirmé avec succès !",
        DemandePaiement.Statut.ECHEC: "Le paiement a échoué.",
        DemandePaiement.Statut.EXPIRE: "La demande de paiement a expiré.",
    }

    return JsonResponse({
        "status": demande.statut,
        "is_final": demande.statut != DemandePaiement.Statut.EN_ATTENTE,
        "succes": demande.statut == DemandePaiement.Statut.CONFIRME,
        "message": messages_par_statut.get(demande.statut, "Statut inconnu."),
        "motif": demande.motif,
        "order_id": demande.order_id,
    })


@csrf_exempt
@require_POST
def orange_money_notif(request):
    """Webhook Orange Money. Ne fait jamais confiance au corps reçu pour la
    décision métier — re-vérifie systématiquement le statut auprès d'Orange."""
    pay_token = request.POST.get("payToken") or request.GET.get("payToken")
    if not pay_token:
        logger.warning("Webhook OM reçu sans payToken: %s", request.body[:500])
        return HttpResponseBadRequest("payToken manquant")

    try:
        demande = DemandePaiement.objects.get(provider_reference=pay_token)
    except DemandePaiement.DoesNotExist:
        logger.warning("Webhook OM pour payToken inconnu: %s", pay_token)
        return HttpResponse(status=200)

    if demande.statut == DemandePaiement.Statut.CONFIRME:
        return HttpResponse(status=200)  # idempotence

    try:
        real_status = _client_pour("orange").get_payment_status(pay_token)
    except PaiementError:
        logger.exception("Échec re-vérification statut pour %s", pay_token)
        return HttpResponse(status=200)

    demande.appliquer_statut_operateur(real_status)
    return HttpResponse(status=200)


# Même logique pour MTN — webhook séparé car le format de notification diffère.
@csrf_exempt
@require_POST
def mtn_momo_notif(request):
    reference_id = request.POST.get("referenceId") or request.GET.get("referenceId")
    if not reference_id:
        return HttpResponseBadRequest("referenceId manquant")

    try:
        demande = DemandePaiement.objects.get(provider_reference=reference_id)
    except DemandePaiement.DoesNotExist:
        logger.warning("Webhook MTN pour referenceId inconnu: %s", reference_id)
        return HttpResponse(status=200)

    if demande.statut == DemandePaiement.Statut.CONFIRME:
        return HttpResponse(status=200)

    if not MTN_DISPONIBLE:
        logger.warning("Webhook MTN reçu alors que le client MTN n'est pas configuré")
        return HttpResponse(status=200)
    try:
        real_status = _client_pour("mtn").get_payment_status(reference_id)
    except PaiementError:
        logger.exception("Échec re-vérification statut MTN pour %s", reference_id)
        return HttpResponse(status=200)

    demande.appliquer_statut_operateur(real_status)
    return HttpResponse(status=200)