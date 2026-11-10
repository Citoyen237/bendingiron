"""Images des factures PDF (client, proforma, projet, commande additionnelle).

Les fichiers sont dans static/factures/ : suivis par Git, ils partent sur le
serveur à chaque déploiement (contrairement à medias/, réservé aux envois de
l'admin). Pour changer une image : remplacer le fichier, garder le même nom.
"""
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
