"""
orange_money.py — Service d'intégration Orange Money Cameroun (API locale / USSD)
Endpoints couverts :
    POST /token
    POST /omcoreapis/1.0.2/mp/init
    POST /omcoreapis/1.0.2/mp/pay
    GET  /omcoreapis/1.0.2/mp/paymentstatus/{payToken}

Placer ce fichier dans une app Django, par ex. : payments/services/orange_money.py

Deux jeux d'identifiants DISTINCTS, à ne pas confondre :

  1. OAuth2 (endpoint /token) — Consumer Key / Consumer Secret de ton
     application, récupérés sur le portail développeur Orange.
     -> encodés en base64 dans le header "Authorization: Basic ..."

  2. API Orange Money (endpoints /mp/init, /mp/pay, /mp/paymentstatus) —
     identifiants API fournis à la souscription.
     En sandbox : OM_API_USER="OMSANDBOXAPI", OM_API_PASSWORD="OMS@NDBOX@PI"
     -> encodés en base64 dans le header "X-AUTH-TOKEN"

Variables à ajouter dans settings.py (ou mieux, dans un fichier .env via django-environ) :
    OM_BASE_URL           = "https://api-s1.orange.cm"
    OM_CONSUMER_KEY        = "xxxx"         # portail développeur Orange (pour /token)
    OM_CONSUMER_SECRET     = "xxxx"         # portail développeur Orange (pour /token)
    OM_API_USER            = "xxxx"         # pour X-AUTH-TOKEN (sandbox: OMSANDBOXAPI)
    OM_API_PASSWORD        = "xxxx"         # pour X-AUTH-TOKEN (sandbox: OMS@NDBOX@PI)
    OM_PIN                 = "xxxx"         # PIN MARCHAND fourni par Orange à la souscription
                                             # (PAS le PIN du client final — celui-ci valide la
                                             #  transaction sur son propre téléphone via push
                                             #  notification, avec son propre code secret OM)
    OM_CHANNEL_USER_MSISDN = "6XXXXXXXXX"   # numéro marchand
    OM_NOTIF_URL           = "https://tondomaine.cm/api/paiements/notif/"

Ne JAMAIS committer ces valeurs en dur dans le code — utiliser des variables
d'environnement / un .env exclu du dépôt git.

Rappel sur le flux : après l'appel à pay(), le client reçoit une notification
push sur son téléphone et confirme lui-même avec son code PIN Orange Money
habituel. Le statut renvoyé est d'abord "PENDING", puis passe à "SUCCESSFULL"
(ou un statut d'échec) une fois que le client a confirmé — d'où l'intérêt de
poller get_payment_status() ou d'exploiter le webhook notifUrl.
"""

import base64
import logging

import requests
from django.conf import settings
from django.core.cache import cache

from .exceptions import PaiementError

logger = logging.getLogger(__name__)


class OrangeMoneyError(PaiementError):
    """Levée pour toute erreur renvoyée par l'API Orange Money."""
    pass


class OrangeMoneyClient:
    """Client simple pour l'API locale / USSD Orange Money Cameroun."""

    TOKEN_CACHE_KEY = "orange_money_access_token"
    TIMEOUT = 15  # secondes

    def __init__(self):
        self.base_url = settings.OM_BASE_URL.rstrip("/")

        # Jeu 1 : OAuth2, uniquement pour /token
        self.consumer_key = settings.OM_CONSUMER_KEY
        self.consumer_secret = settings.OM_CONSUMER_SECRET

        # Jeu 2 : identifiants API Orange Money, encodés en base64 pour X-AUTH-TOKEN
        self.x_auth_token = self._b64(
            f"{settings.OM_API_USER}:{settings.OM_API_PASSWORD}"
        )

    @staticmethod
    def _b64(value: str) -> str:
        return base64.b64encode(value.encode("utf-8")).decode("utf-8")

    @staticmethod
    def _appel(methode, url, **kwargs) -> requests.Response:
        """Appel HTTP : une coupure réseau ou un délai dépassé devient une
        OrangeMoneyError (gérée par les vues) au lieu d'une erreur 500."""
        try:
            return requests.request(methode, url, **kwargs)
        except requests.Timeout as exc:
            raise OrangeMoneyError("Orange Money ne répond pas (délai dépassé). Réessayez dans un instant.") from exc
        except requests.RequestException as exc:
            raise OrangeMoneyError("Impossible de joindre Orange Money. Vérifiez la connexion internet.") from exc

    @staticmethod
    def _donnees(response: requests.Response, *cles):
        """Lit response.json()[cles...] ; une réponse inattendue devient une OrangeMoneyError."""
        try:
            valeur = response.json()
            for cle in cles:
                valeur = valeur[cle]
            return valeur
        except (ValueError, KeyError, TypeError) as exc:
            logger.error("Réponse Orange Money inattendue : %s", response.text[:500])
            raise OrangeMoneyError("Réponse inattendue d'Orange Money.", response=response) from exc

    # ------------------------------------------------------------------ #
    # Étape 1 : récupération / cache de l'access token OAuth2
    # ------------------------------------------------------------------ #
    def get_access_token(self, force_refresh: bool = False) -> str:
        if not force_refresh:
            cached = cache.get(self.TOKEN_CACHE_KEY)
            if cached:
                return cached

        # Basic auth OAuth2 = base64(consumer_key:consumer_secret)
        basic_auth = self._b64(f"{self.consumer_key}:{self.consumer_secret}")

        response = self._appel(
            "POST",
            f"{self.base_url}/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {basic_auth}",
            },
            data={"grant_type": "client_credentials"},
            timeout=self.TIMEOUT,
        )
        self._raise_for_error(response)

        token = self._donnees(response, "access_token")
        try:
            expires_in = int(response.json().get("expires_in", 3600))
        except (ValueError, TypeError, AttributeError):
            expires_in = 3600

        # On garde une marge de sécurité de 30s avant expiration réelle
        cache.set(self.TOKEN_CACHE_KEY, token, timeout=max(expires_in - 30, 30))
        return token

    def _auth_headers(self, extra: dict | None = None) -> dict:
        headers = {
            "X-AUTH-TOKEN": self.x_auth_token,
            "Authorization": f"Bearer {self.get_access_token()}",
        }
        if extra:
            headers.update(extra)
        return headers

    # ------------------------------------------------------------------ #
    # Étape 2 : initialisation du paiement -> renvoie un payToken
    # ------------------------------------------------------------------ #
    def init_payment(self) -> str:
        response = self._appel(
            "POST",
            f"{self.base_url}/omcoreapis/1.0.2/mp/init",
            headers=self._auth_headers(),
            timeout=self.TIMEOUT,
        )
        self._raise_for_error(response)
        return self._donnees(response, "data", "payToken")

    # ------------------------------------------------------------------ #
    # Étape 3 : exécution du paiement (déclenche le prompt USSD chez le client)
    # ------------------------------------------------------------------ #
    def pay(
        self,
        *,
        subscriber_msisdn: str,
        amount: int,
        order_id: str,
        description: str,
        pay_token: str | None = None,
        notif_url: str | None = None,
    ) -> dict:
        """
        subscriber_msisdn : numéro du payeur (client final), SANS indicatif
                             (ex: "692954629" ou "237692954629" selon ce que ton
                             sandbox/contrat attend — teste les deux formats)
        amount             : montant en XAF, sans virgule
        order_id            : identifiant unique de ta commande
        pay_token           : payToken renvoyé par init_payment(); généré automatiquement si omis

        Le PIN utilisé ici (settings.OM_PIN) est un identifiant MARCHAND fourni par
        Orange à la souscription — ce n'est pas le PIN du client. Le client confirme
        la transaction lui-même sur son téléphone (notification push) avec son propre
        code secret Orange Money ; ce code ne transite jamais par notre serveur.
        """
        if pay_token is None:
            pay_token = self.init_payment()

        body = {
            "notifUrl": notif_url or settings.OM_NOTIF_URL,
            "channelUserMsisdn": settings.OM_CHANNEL_USER_MSISDN,
            "amount": str(amount),
            "subscriberMsisdn": subscriber_msisdn,
            "pin": settings.OM_PIN,
            "orderId": order_id,
            "description": description,
            "payToken": pay_token,
        }

        response = self._appel(
            "POST",
            f"{self.base_url}/omcoreapis/1.0.2/mp/pay",
            headers=self._auth_headers({"Content-Type": "application/json"}),
            json=body,
            timeout=self.TIMEOUT,
        )
        self._raise_for_error(response)
        return self._donnees(response, "data")

    # ------------------------------------------------------------------ #
    # Étape 4 : vérification du statut d'une transaction
    # ------------------------------------------------------------------ #
    def get_payment_status(self, pay_token: str) -> dict:
        response = self._appel(
            "GET",
            f"{self.base_url}/omcoreapis/1.0.2/mp/paymentstatus/{pay_token}",
            headers=self._auth_headers({"Content-Type": "application/json"}),
            timeout=self.TIMEOUT,
        )
        self._raise_for_error(response)
        return self._donnees(response, "data")

    # ------------------------------------------------------------------ #
    @staticmethod
    def _raise_for_error(response: requests.Response) -> None:
        if response.ok:
            return
        logger.error("Orange Money API error [%s]: %s", response.status_code, response.text)
        if response.status_code in (401, 403):
            message = "Orange Money a refusé l'accès : identifiants marchand invalides ou manquants."
        elif response.status_code >= 500:
            message = "Orange Money rencontre un problème. Réessayez plus tard."
        else:
            message = f"Orange Money a refusé la demande (code {response.status_code})."
        # Le message est affiché au client : pas de détail technique de la réponse
        raise OrangeMoneyError(message, response=response)