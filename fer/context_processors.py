from auth_app.permissions import is_admin
from .models import Fer


def seuil_critique_count(request):
    """Nombre de fers sous le seuil critique — calculé seulement pour les admins."""
    if not is_admin(getattr(request, "user", None)):
        return {}
    seuil_count = sum(1 for fer in Fer.objects.all() if fer.sueil_atteint)
    return {'fer_seuil_critique_count': seuil_count}
