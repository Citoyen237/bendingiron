"""
Gabarit universel (étape 4) : page produit, calcul en direct, ajout au panier.

- page_produit : appelée par produits.views.detail_produit quand le produit a
  une configuration ACTIVE (case « utiliser le gabarit universel ») ;
- apercu       : la même page pour un administrateur, même si la case n'est
  pas encore cochée (pour vérifier avant la bascule) ;
- calcul_json  : appelé par la page à chaque saisie ; renvoie prix,
  longueurs et dessin calculés par le serveur.
"""
from decimal import Decimal

from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from auth_app.permissions import admin_required, is_admin
from gestion_prix_fer.models import Fournisseur, TypeFer
from produits.models import Produit
from usesOrders.models import Cart, CartItem

from .calcul import FER_BENDING_IRON, FER_CLIENT, CalculImpossible, calculer
from .dessin import calculer_dessin, svg_miniature
from .formules import FormuleInvalide
from .models import SOUS_CATEGORIES_AUTORISEES, ConfigProduit

TEMPLATE = "boutique/gabarit/produit.html"
CLE_MINIATURE = "dessin_svg"   # clé du dessin 70 x 70 dans CartItem.details (non affichée en texte)
QUANTITE_MAX = 10000
CHOIX_FER = [(FER_BENDING_IRON, "L’entreprise (Bending Iron SARL)"), (FER_CLIENT, "Le client (moi)")]


def config_active(produit):
    """Configuration à utiliser pour ce produit, ou None (ancienne page)."""
    if produit.sous_categorie not in SOUS_CATEGORIES_AUTORISEES:
        return None
    return ConfigProduit.objects.filter(produit=produit, actif=True).first()


def _config_pour(request, produit):
    """Active pour tout le monde ; non active : visible seulement par un administrateur."""
    config = ConfigProduit.objects.filter(produit=produit,
                                          produit__sous_categorie__in=SOUS_CATEGORIES_AUTORISEES).first()
    if config is None or (not config.actif and not is_admin(request.user)):
        raise Http404
    return config


def _saisies(post):
    """Lit les choix du client ; les champs de prix éventuels sont ignorés."""
    return {
        "fer": post.get("fer"),
        "marque_fer": post.get("marque_fer"),
        "type_fer": post.get("type_fer"),
        "diametre": post.get("diametre"),
        "angle": post.get("angle"),
        "quantite": post.get("quantite") or 1,
        "dimensions": {cle[4:]: valeur for cle, valeur in post.items() if cle.startswith("dim_")},
    }


def _choix_fer_disponibles(config):
    """Marques et types qui ont un prix à la tonne pour au moins un diamètre du produit."""
    types = (TypeFer.objects.filter(fournisseur__actif=True, prix_tonne__diametre__in=config.diametres)
             .select_related("fournisseur").distinct())
    marques = sorted({t.fournisseur.nom for t in types}, key=str.lower)
    noms_types = sorted({t.nom for t in types})
    return marques, noms_types


def _lignes_du_bas(config):
    """Lignes affichées sous le cadre (numérotées pour la grille de la page)."""
    lignes = [("quantite", "Quantité de pièce (u)")]
    if config.afficher_r:
        lignes.append(("r", "Rayon de courbure R (cm)"))
    if config.afficher_ld:
        lignes.append(("ldf", "Longueur départ & fin Ldf (cm)"))
    lignes += [("lt", "Longueur totale (cm)"),
               ("poids", "Poids d'une pièce (kg)"), ("poids_total", "Poids total (kg)"),
               ("pu", "Prix unitaire (FCFA)"), ("total", "Prix total (FCFA)")]
    return lignes


def _rendre(request, produit, config, saisies=None, erreur=None, status=200):
    """erreur : CalculImpossible à afficher sous son champ (ou en haut si pas de champ)."""
    saisies = saisies or {}
    marques, types = _choix_fer_disponibles(config)
    angles = list(config.angles.filter(actif=True))
    caracs = ["fer", "marque", "diametre"] + (["angle"] if angles else []) + ["dimension"]
    premiere_ligne = len(caracs) + 1
    lignes = [{"cle": cle, "libelle": libelle, "row": premiere_ligne + i}
              for i, (cle, libelle) in enumerate(_lignes_du_bas(config))]
    dimensions = [{"dim": d, "champ": f"dim_{d.abreviation}",
                   "valeur": (saisies.get("dimensions") or {}).get(d.abreviation, "")}
                  for d in config.dimensions.all()]
    # Choix cochés : ceux du client (page renvoyée après une erreur). Qui fournit le fer,
    # la marque et le type restent VIDES : le client doit les choisir lui-même.
    choisis = {
        "fer": saisies.get("fer") or "",
        "marque": saisies.get("marque_fer") or "",
        "type": (saisies.get("type_fer") or "").lower(),
        "diametre": str(saisies.get("diametre") or (config.diametres[0] if config.diametres else "")),
        "angle": str(saisies.get("angle") or (angles[0].valeur if angles else "")),
        "quantite": saisies.get("quantite") or 1,
    }
    return render(request, TEMPLATE, {
        "product": produit,
        "config": config,
        "rows": {nom: i + 1 for i, nom in enumerate(caracs)},
        "derniere_ligne": premiere_ligne + len(lignes),
        "choix_fer": CHOIX_FER,
        "marques": marques,
        "types": types,
        "diametres": config.diametres,
        "angles": angles,
        "dimensions": dimensions,
        "lignes": lignes,
        "choisis": choisis,
        "erreur_champ": getattr(erreur, "champ", None) if erreur else None,
        "erreur_message": str(erreur) if erreur else "",
        "quantite_max": QUANTITE_MAX,
        "apercu": not config.actif,
        "current_url": "/produits/",
    }, status=status)


def _calculer(config, saisies):
    """Contrôle de la quantité maximale puis calcul ; lève CalculImpossible."""
    try:
        quantite = int(saisies["quantite"])
    except (TypeError, ValueError):
        raise CalculImpossible("Quantité invalide.", "quantite")
    if quantite > QUANTITE_MAX:
        raise CalculImpossible(f"La quantité ne peut pas dépasser {QUANTITE_MAX} pièces.", "quantite")
    return calculer(config, saisies)


def _dessin(config, resultat):
    if not config.forme:
        return None
    try:
        return calculer_dessin(config.forme, resultat.variables)
    except FormuleInvalide:
        return None   # le prix reste valable ; seul le dessin manque


def page_produit(request, produit, config):
    """GET : affiche la page. POST : recalcule le prix (le serveur fait foi) et ajoute au panier."""
    if request.method != "POST":
        return _rendre(request, produit, config)

    saisies = _saisies(request.POST)
    try:
        resultat = _calculer(config, saisies)
    except CalculImpossible as exc:
        return _rendre(request, produit, config, saisies=saisies, erreur=exc)

    cart, _ = Cart.objects.get_or_create(user=request.user)
    details = dict(resultat.details)
    miniature = svg_miniature(_dessin(config, resultat))
    if miniature:
        details[CLE_MINIATURE] = miniature   # dessin 70 x 70 px, pour la facture
    existant = CartItem.objects.filter(cart=cart, produit=produit, details=details).first()
    if existant:
        existant.quantite += resultat.quantite
        existant.save(update_fields=["quantite"])
    else:
        CartItem.objects.create(cart=cart, produit=produit, details=details, quantite=resultat.quantite,
                                prix_u=resultat.pu, prix_revient=round(resultat.ps, 2))
    return redirect("panier")


@admin_required
def apercu(request, product_id):
    """Page du gabarit universel pour un administrateur, avant la bascule."""
    produit = get_object_or_404(Produit, id=product_id)
    config = _config_pour(request, produit)
    if request.method == "POST":
        messages.info(request, "Aperçu : l'ajout au panier se fait depuis la vraie page, après la bascule.")
        return _rendre(request, produit, config, saisies=_saisies(request.POST))
    return _rendre(request, produit, config)


def _nombre(valeur, decimales=2):
    return float(round(Decimal(valeur), decimales))


@require_POST
def calcul_json(request, product_id):
    """Calcul en direct pendant la saisie (aucune écriture)."""
    produit = get_object_or_404(Produit, id=product_id)
    config = _config_pour(request, produit)
    saisies = _saisies(request.POST)
    try:
        r = _calculer(config, saisies)
    except CalculImpossible as exc:
        return JsonResponse({"ok": False, "erreur": str(exc), "champ": exc.champ})

    dessin = _dessin(config, r)
    return JsonResponse({
        "ok": True,
        "ltp": _nombre(r.ltp), "ldf": _nombre(r.ldf), "lt": r.lt, "r": _nombre(r.r),
        "poids": _nombre(r.poids, 3), "poids_total": _nombre(r.poids_total, 2),
        "pu": r.pu, "quantite": r.quantite, "total": r.total,
        "dessin": dessin,
    })
