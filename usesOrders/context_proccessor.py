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
    nb_en_attente = 0

        # Récupérer toutes les commandes de l'utilisateur
    commandes = Order.objects.all()

    for commande in commandes:
        dernier_traiment = Traiment.objects.filter(order=commande).order_by('-created_at').first()
        if dernier_traiment and dernier_traiment.statut == 'en_attente':
            nb_en_attente += 1

    return {
        'nb_order': nb_en_attente
    }
