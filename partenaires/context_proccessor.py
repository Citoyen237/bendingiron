from django.db.models import OuterRef, Subquery

from auth_app.permissions import is_admin
from .models import ProjetOrder, TraimentOrder


def order_en_attente(request):
    """Nombre de commandes partenaires en attente — calculé seulement pour les admins, en UNE requête."""
    if not is_admin(getattr(request, "user", None)):
        return {}
    dernier = TraimentOrder.objects.filter(projet_order=OuterRef("pk")).order_by("-created_at")
    nb = (ProjetOrder.objects
          .annotate(dernier_statut=Subquery(dernier.values("statut")[:1]))
          .filter(dernier_statut="en_attente")
          .count())
    return {"nb_order_partenaire": nb}
