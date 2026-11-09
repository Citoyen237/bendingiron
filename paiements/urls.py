"""
payments/urls.py

À inclure depuis le urls.py racine du projet :

    # config/urls.py
    from django.urls import include, path

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("paiements/", include("payments.urls")),
    ]

IMPORTANT : les URLs des webhooks doivent correspondre exactement à ce que
tu configures côté Orange/MTN (OM_NOTIF_URL, etc.), par exemple :
    https://tondomaine.cm/paiements/notif/orange/
    https://tondomaine.cm/paiements/notif/mtn/
"""

from django.urls import path

from .views import *

#app_name = "payments"

urlpatterns = [
    # --- CAS A : panier -> nouvelle commande --- #
    path("confirmer/", send_info_user, name="confirmer-commande"),

    # --- CAS B : solder une commande existante --- #
    path("solde/<int:order_id>/", payer_solde, name="payer-solde"),

    # --- Webhooks (AVANT les routes <str:pay_token>, sinon "notif" serait
    #     interprété comme un pay_token) --- #
    path("notif/orange/", orange_money_notif, name="notif-orange"),
    path("notif/mtn/", mtn_momo_notif, name="notif-mtn"),

    # --- Statut JSON (AVANT la page HTML, suffixe plus spécifique) --- #
    path("<str:pay_token>/statut.json", statut_paiement_json, name="statut-paiement-json"),

    # --- Page d'attente (spinner) --- #
    path("<str:pay_token>/", paiement_en_cours, name="paiement-en-cours"),
]