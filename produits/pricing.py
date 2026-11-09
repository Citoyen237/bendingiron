"""
Calcul des prix CÔTÉ SERVEUR.

Pourquoi : avant, le prix unitaire et le prix de revient étaient calculés en
JavaScript puis envoyés dans des champs cachés. Un client pouvait les modifier
dans son navigateur et commander au prix de son choix.

Désormais, pour chaque produit enregistré dans CALCULATEURS, le serveur refait
le calcul à partir des dimensions saisies, de la table PrixFer et des
Constantes, et IGNORE les prix envoyés par le navigateur. Le JavaScript reste
utile pour l'affichage en direct, mais ce n'est plus lui qui fait foi.

Pour ajouter un produit : écrire une fonction calcul_xxx(data, contexte) qui
reproduit EXACTEMENT la formule du gabarit HTML, puis l'ajouter à CALCULATEURS
avec le nom du produit (champ Produit.nom). Les fonctions renvoient un
ResultatPrix ou lèvent PrixInvalide.
"""
import logging
import math
from dataclasses import dataclass, field

from django.conf import settings

logger = logging.getLogger(__name__)


class PrixInvalide(Exception):
    """Les données ne permettent pas de calculer un prix (dimension hors limites, tarif absent...)."""


@dataclass
class ResultatPrix:
    prix_u: int                 # prix unitaire arrondi au FCFA supérieur
    prix_revient: float         # prix du service (Ps)
    details: dict = field(default_factory=dict)  # valeurs calculées à enregistrer dans le détail


def _contexte():
    """Tarifs du fer et constantes, lus en base (mêmes données que celles envoyées au navigateur)."""
    from gestion_prix_fer.models import Constante
    from .views import get_tarifs_fer
    return {"tarifs": get_tarifs_fer(), "constantes": Constante.toutes()}


def _prix_unitaire(prix_vente, prix_revient, constantes):
    """Pu = (Pv + Ps + tolérance + taxe) × (1 + taux), arrondi au supérieur."""
    try:
        tolerance = float(constantes["tolerance"])
        taxe = float(constantes["taxe"])
        taux = float(constantes["taux"])
    except (KeyError, TypeError, ValueError):
        raise PrixInvalide("Constantes de calcul manquantes (tolerance, taxe, taux).")
    base = prix_vente + prix_revient + tolerance + taxe
    return math.ceil(base + base * taux)


def _prix_vente_fer(data, longueur_totale, tarifs):
    """Pv : prix du fer pour la longueur développée, selon qui fournit le fer."""
    marque = data.get("marque_fer")
    type_fer = (data.get("type_fer") or "").lower()
    diametre = str(int(float(data.get("diametre") or 0)))
    tarif = tarifs.get(marque, {}).get(type_fer, {}).get(diametre)
    if not tarif:
        raise PrixInvalide("Ce fer n'est pas disponible pour ce diamètre.")
    pvf, pa = float(tarif["pvf"]), float(tarif["pa"])
    fer = data.get("fer")
    if fer == "bending iron":
        return (pvf / 1200) * longueur_totale
    if fer == "le client":
        return ((pvf - pa) / 1200) * longueur_totale
    raise PrixInvalide("Fournisseur du fer non précisé.")


# ---------------------------------------------------------------------------
# Cadre carré — reprend exactement produits/cintrages_cadres/cadre-carre.html
# ---------------------------------------------------------------------------
COEF_PS_CADRE_CARRE = {
    "autre fer": {6: 22, 8: 47, 10: 73, 12: 105},
    "prometal": {6: 24, 8: 51, 10: 80, 12: 138},
}


def calcul_cadre_carre(data, contexte):
    try:
        cote = float(data.get("longueurCote"))
        diametre = int(float(data.get("diametre")))
    except (TypeError, ValueError):
        raise PrixInvalide("Dimensions invalides.")
    if not (8 <= cote <= 100):
        raise PrixInvalide("La longueur du côté doit être comprise entre 8 et 100 cm.")

    longueur_totale = math.ceil((4 * cote) + (1.3 * diametre))
    longueur_depart = (5 * diametre) / 10
    rayon = (5 * diametre) / 10

    coef = COEF_PS_CADRE_CARRE.get(data.get("marque_fer"), {}).get(diametre)
    if coef is None:
        raise PrixInvalide("Diamètre non proposé pour cette marque de fer.")
    prix_revient = (coef * longueur_totale) / 100

    prix_vente = _prix_vente_fer(data, longueur_totale, contexte["tarifs"])
    prix_u = _prix_unitaire(prix_vente, prix_revient, contexte["constantes"])

    return ResultatPrix(
        prix_u=prix_u,
        prix_revient=prix_revient,
        details={
            "longueur_Total": longueur_totale,
            "longueur_Depart_et_Fin": longueur_depart,
            "rayon_Courbure": rayon,
        },
    )


# Nom du produit (Produit.nom) -> fonction de calcul
CALCULATEURS = {
    "cadre carre": calcul_cadre_carre,
}


def calculer_prix(produit, data):
    """
    Renvoie un ResultatPrix calculé par le serveur, ou None si le produit n'a pas
    encore de calculateur serveur.

    Si PRIX_SERVEUR_OBLIGATOIRE = True dans les réglages, un produit sans
    calculateur est refusé (PrixInvalide) au lieu d'accepter le prix du navigateur.
    """
    calcul = CALCULATEURS.get(produit.nom)
    if calcul is None:
        if getattr(settings, "PRIX_SERVEUR_OBLIGATOIRE", False):
            raise PrixInvalide("Ce produit ne peut pas encore être commandé en ligne.")
        logger.warning("Prix non recalculé côté serveur pour le produit « %s »", produit.nom)
        return None
    return calcul(data, _contexte())
