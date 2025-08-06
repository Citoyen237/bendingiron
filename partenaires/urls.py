from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='partenaire.index'),
    path('detail-sur-le-projet/<int:projet_id>', detail_projet, name='partenaire.detail'),
    path('creer-un-nouveau-projet/', confirm_projet, name='partanaire.confirm'),
    path('valider-commande-partnaire/', valider_commande_partenaire, name='valider_commande_partenaire'),
    path('commandes/<int:projet_id>/', historique_order, name='historique-order'),
]
