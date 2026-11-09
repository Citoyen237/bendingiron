from auth_app.models import CustomUser
from .models import *
from .models import *

def panier_count(request):
    # count_order=Commande.objects.filter(statut='en_attente')
    if request.user.is_authenticated:
        panier = Cart.objects.filter(user=request.user).first()
        if panier :
            items=CartItem.objects.filter(cart_id=panier.id)
            total_articles = items.count()
            if total_articles :
                total_articles = items.count() 
            else :
                total_articles = 0 
        else:
         total_articles = 0 
    else:
        total_articles = 0  # Si l'utilisateur n'est pas connecté, il n'y a pas de panier
    return {'panier_count': total_articles,}
            # 'count_order':count_order.count()}
    # return {}

def commandes_en_attente(request):
    """Nombre de commandes clients en attente — seulement pour les admins, en UNE requête."""
    from django.db.models import OuterRef, Subquery
    from auth_app.permissions import is_admin
    if not is_admin(getattr(request, "user", None)):
        return {}
    dernier = Traiment.objects.filter(order=OuterRef("pk")).order_by("-created_at")
    nb_en_attente = (Order.objects
                     .annotate(dernier_statut=Subquery(dernier.values("statut")[:1]))
                     .filter(dernier_statut="en_attente")
                     .count())
    return {'nb_order': nb_en_attente}
