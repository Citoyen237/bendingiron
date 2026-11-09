"""Choix du service de paiement selon le moyen choisi par le client."""
from django.conf import settings

from .exceptions import PaiementError

try:  # le client MTN n'est pas encore écrit (services/mtn_momo.py)
    from .mtn_momo import MtnMomoClient
except ImportError:
    MtnMomoClient = None

MTN_DISPONIBLE = MtnMomoClient is not None


def simulation_active() -> bool:
    # Double contrôle : jamais de faux paiement si DEBUG est désactivé
    return bool(getattr(settings, "PAIEMENT_SIMULATION", False) and settings.DEBUG)


def client_pour(provider: str):
    """provider : "orange" / "mtn" (formulaire) ou "ORANGE" / "MTN" (DemandePaiement)."""
    provider = (provider or "").lower()
    if provider == "mtn" and not MTN_DISPONIBLE:
        raise PaiementError("MTN Mobile Money est indisponible pour le moment. Utilisez Orange Money.")
    if provider not in ("orange", "mtn"):
        raise PaiementError(f"Moyen de paiement inconnu : {provider}")
    if simulation_active():
        from .simulation import SimulationClient
        return SimulationClient()
    if provider == "orange":
        from .orange_money import OrangeMoneyClient
        return OrangeMoneyClient()
    return MtnMomoClient()
