"""
payments/services/exceptions.py

Exception commune aux différents services de paiement (Orange, MTN, futurs
autres providers). Permet à views.py de faire un seul `except PaiementError`
sans se soucier de quel provider a été appelé.

OrangeMoneyError et MtnMomoError (dans leurs modules respectifs) doivent
hériter de PaiementError plutôt que de Exception directement.
"""


class PaiementError(Exception):
    """Levée pour toute erreur renvoyée par un provider de paiement mobile."""

    def __init__(self, message, response=None):
        super().__init__(message)
        self.response = response