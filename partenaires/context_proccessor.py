from .models import *

def order_en_attente(request):
    nb_en_attente = 0
        # Récupérer toutes les commandes de l'utilisateur
    commandes = ProjetOrder.objects.all()

    for commande in commandes:
        dernier_traiment = TraimentOrder.objects.filter(projet_order=commande).order_by('-created_at').first()
        if dernier_traiment and dernier_traiment.statut == 'en_attente':
            nb_en_attente += 1

    return {
        'nb_order_partenaire': nb_en_attente
    }