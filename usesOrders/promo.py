"""
Règles d'application d'un code promo (code distributeur) sur un panier.

Conditions pour qu'un code s'applique :
  1. le fer de TOUS les produits du panier est fourni par Bending Iron
     (details["fer"] == "bending iron") ;
  2. la quantité totale du panier atteint le minimum défini par la constante
     « quantite_min_code_promo » (modifiable dans l'admin, gestion_prix_fer >
     Constantes). Sans cette constante, le minimum vaut 0.

La remise (en %) s'applique ensuite sur le montant total HT de la facture
(voir Cart.montant_remise / Order.montant_remise).
"""

FOURNISSEUR_FER = "bending iron"
CLE_QUANTITE_MIN = "quantite_min_code_promo"
QUANTITE_MIN_PAR_DEFAUT = 0


def quantite_minimum():
    """Quantité totale minimale du panier pour accepter un code promo."""
    from gestion_prix_fer.models import Constante

    constante = Constante.objects.filter(cle=CLE_QUANTITE_MIN).first()
    if constante is None:
        return QUANTITE_MIN_PAR_DEFAUT
    return max(int(constante.valeur), 0)


def fer_fourni_par_bending_iron(item):
    fer = (item.details or {}).get("fer") if isinstance(item.details, dict) else None
    return str(fer or "").strip().lower() == FOURNISSEUR_FER


def erreur_conditions(panier):
    """Renvoie None si le panier remplit les conditions, sinon le message d'erreur."""
    items = list(panier.items.all())
    if not items:
        return "Votre panier est vide."

    minimum = quantite_minimum()
    quantite_totale = sum(item.quantite for item in items)
    if quantite_totale < minimum:
        return f"Vous devez avoir au moins {minimum} produits pour appliquer un code promo."

    if not all(fer_fourni_par_bending_iron(item) for item in items):
        return ("Le fer de tous les produits doit être fourni par 'bending iron' "
                "pour appliquer ce code.")
    return None


def retirer_remise(panier):
    """Le code promo est réservé aux commandes client : pour un projet, une
    proforma ou une commande additionnelle, la remise du panier est annulée."""
    if panier and panier.remise:
        panier.remise = 0
        panier.save(update_fields=["remise", "updated_at"])


def retirer_remise_si_invalide(panier):
    """À appeler avant de transformer le panier en commande : si le panier a
    changé depuis l'application du code et ne remplit plus les conditions,
    la remise est annulée. Renvoie le message d'erreur, ou None."""
    if not panier or not panier.remise:
        return None
    erreur = erreur_conditions(panier)
    if erreur:
        panier.remise = 0
        panier.save(update_fields=["remise", "updated_at"])
    return erreur
