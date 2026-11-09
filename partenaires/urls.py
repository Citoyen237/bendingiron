from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='partenaire.index'),
    path('detail-sur-le-projet/<int:projet_id>', detail_projet, name='partenaire.detail'),
    path('creer-un-nouveau-projet/', confirm_projet, name='partanaire.confirm'),
    path('valider-commande-partnaire/', valider_commande_partenaire, name='valider_commande_partenaire'),
    path('commandes/<int:projet_id>/', historique_order, name='historique-order'),
    path('commandes/telecharger/bon/<int:projet_id>/', genrate_bon, name='download-bon'),
    path('commandes/telecharger/facture/<int:projet_id>/', genrate_bon_livraison, name='download-bon-livraion'),
    path('telecharger/projet/<int:projet_id>/', download_projet, name='download.projet'),
    path('commandes/<int:order_id>', get_detail_order, name='front.orders.details'), 

    path('commandes-additionnel/', confirm_additional_order, name='additional-order'),
    path('commandes-additionnel/<int:projet_id>/liste/', get_order_additional_list, name='additional-order-list'),
    path('commandes-additionnel/<int:order_id>/detail', detail_commande_additional , name='detail_commande_additional'),
    path('commandes-additionnel/projet/<int:order_id>/telecharger/', generate_order_additional, name='download.additional'),


]
