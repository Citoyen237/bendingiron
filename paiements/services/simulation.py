"""
paiements/services/simulation.py — Faux opérateur pour le DÉVELOPPEMENT.

Activé par PAIEMENT_SIMULATION=True dans le .env, et seulement si DEBUG=True
(voir paiements.views._client_pour). Aucun appel à Orange : on peut tester tout
le parcours en local (page d'attente, commande enregistrée, panier vidé),
alors qu'Orange ne peut pas joindre le webhook sur 127.0.0.1.

Pour tester un échec : payer avec un numéro qui se termine par 000
(ex. 690000000) -> paiement refusé, avec un motif.
"""
import uuid

from .exceptions import PaiementError

PREFIXE = "SIMU-"
MOTIF_REFUS = "Paiement refusé (simulation) : solde insuffisant."


class SimulationClient:
    def pay(self, *, subscriber_msisdn, amount, order_id, description, **kwargs):
        if not str(subscriber_msisdn).isdigit():
            raise PaiementError("Numéro de paiement invalide.")
        # Le montant et l'issue sont encodés dans le jeton : pas de stockage à part
        issue = "KO" if str(subscriber_msisdn).endswith("000") else "OK"
        return {"payToken": f"{PREFIXE}{issue}-{int(amount)}-{uuid.uuid4().hex[:12]}"}

    def get_payment_status(self, pay_token):
        try:
            _, issue, montant, _ = pay_token.split("-", 3)
        except ValueError:
            raise PaiementError("Jeton de simulation invalide.")
        if issue == "KO":
            return {"status": "FAILED", "amount": montant, "inittxnmessage": MOTIF_REFUS}
        return {"status": "SUCCESSFULL", "amount": montant}
