"""Images des factures PDF (client, proforma, projet, commande additionnelle).

Les fichiers sont dans static/factures/ : suivis par Git, ils partent sur le
serveur à chaque déploiement (contrairement à medias/, réservé aux envois de
l'admin). Pour changer une image : remplacer le fichier, garder le même nom.
"""
import base64
import re

from django.templatetags.static import static

LOGO = "factures/logo.png"
FILIGRANE = "factures/filigrane.png"
CACHET = "factures/cachet.jpg"          # signature + cachet « LA DIRECTION »
PIED_PAGE = "factures/pied_page.png"    # siège, RCCM, n° contribuable, compte bancaire


def images_facture(request):
    """Adresses complètes (logo, filigrane, cachet, pied de page) : WeasyPrint
    télécharge les images par HTTP pour fabriquer le PDF."""
    return tuple(request.build_absolute_uri(static(chemin))
                 for chemin in (LOGO, FILIGRANE, CACHET, PIED_PAGE))


# --- Dessin de la pièce, sous le nom du produit (factures, bons de livraison) ---
# Le dessin est enregistré dans chaque ligne de commande (details["dessin_svg"]),
# fabriqué par boutique.dessin.svg_miniature. On n'accepte QUE ce format exact :
# un tracé seul, sans texte, lien ni script. Sinon, un faux dessin
# glissé dans une commande pourrait faire charger d'autres adresses au
# générateur de PDF.
_NOMBRE = r"-?\d+(?:\.\d+)?(?:e-?\d+)?"
_DESSIN_VALIDE = re.compile(
    r'<svg xmlns="http://www\.w3\.org/2000/svg" width="\d{1,3}" height="\d{1,3}" '
    rf'viewBox="{_NOMBRE} {_NOMBRE} {_NOMBRE} {_NOMBRE}">'
    rf'<path d="[MLA0-9 .\-e]+" fill="none" stroke="#[0-9a-fA-F]{{6}}" stroke-width="{_NOMBRE}" '
    r'stroke-linecap="round" stroke-linejoin="round"/></svg>'
)


def image_dessin(details):
    """Adresse « data: » de l'image de la pièce, ou "" (pas de dessin, ou dessin refusé)."""
    svg = (details or {}).get("dessin_svg") if isinstance(details, dict) else None
    if not isinstance(svg, str) or len(svg) > 20000 or not _DESSIN_VALIDE.fullmatch(svg):
        return ""
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
