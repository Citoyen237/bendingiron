"""TVA décidée par l'admin, compte par compte (14/11/2026).

  - client : case « Appliquer la TVA » de son compte (CustomUser.soumis_tva) ;
  - partenaire : case du partenariat (Partenariats.soumis_tva) ;
  - proforma : case cochée ou non à la création de la proforma.

Le taux est FIGÉ sur chaque commande à sa création (champ taux_tva : 19,25 ou 0) :
décocher une case plus tard ne change pas les factures déjà émises.
"""
from decimal import Decimal

TAUX_TVA = Decimal("19.25")
EXONERE = Decimal("0")


def taux_pour(soumis):
    """Taux à appliquer selon la case « Appliquer la TVA »."""
    return TAUX_TVA if soumis else EXONERE


def calculer_tva(base, taux):
    """Montant de TVA arrondi au franc (même arrondi qu'avant : round)."""
    return round((Decimal(base) * Decimal(taux if taux is not None else TAUX_TVA)) / 100)


def libelle_tva(taux):
    """« TVA 19,25% » ou « TVA (exonéré) » pour les factures et pages."""
    taux = Decimal(taux if taux not in (None, "") else TAUX_TVA)
    if taux == 0:
        return "TVA (exonéré)"
    texte = f"{taux.normalize():f}".replace(".", ",")
    return f"TVA {texte}%"
