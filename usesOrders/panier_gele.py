"""Panier contenant un produit gelé (case « Disponible dans la boutique » décochée), 14/11/2026.

Le produit a pu être ajouté au panier AVANT d'être gelé : la validation du panier
(commande client, projet, proforma, commande additionnelle) est alors refusée et
le client est renvoyé au panier avec un message.
"""
from django.contrib import messages
from django.shortcuts import redirect


def produits_indisponibles(panier):
    """Noms des produits gelés présents dans le panier (sans doublon, dans l'ordre)."""
    if panier is None:
        return []
    noms = []
    for item in panier.items.select_related("produit"):
        if not item.produit.disponible and item.produit.nom not in noms:
            noms.append(item.produit.nom)
    return noms


def refuser_si_indisponible(request, panier):
    """Redirection vers le panier si un produit est gelé, sinon None."""
    noms = produits_indisponibles(panier)
    if not noms:
        return None
    messages.error(request, "Indisponible pour le moment : " + ", ".join(noms)
                   + ". Retirez ce produit du panier pour continuer.")
    return redirect("panier")
