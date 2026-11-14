"""Filtres de gabarit pour les montants.

    {% load montants %}
    {{ net_payer|en_lettres|capfirst }} francs CFA
"""
from django import template

from usesOrders.lettres import en_lettres as _en_lettres

register = template.Library()


@register.filter
def en_lettres(valeur):
    """Montant en toutes lettres (arrondi au franc) ; vide si la valeur n'est pas un nombre."""
    try:
        return _en_lettres(valeur)
    except Exception:
        return ""


@register.filter
def tva_libelle(taux):
    """« TVA 19,25% » ou « TVA (exonéré) » selon le taux figé de la commande."""
    from usesOrders.tva import libelle_tva
    try:
        return libelle_tva(taux)
    except Exception:
        return "TVA"
