from django.urls import path
from .views import *

urlpatterns = [
    path('', indexA, name='admin.index'),

    # gestion du stock
    path('stocks/',ListFer.as_view() ,name='admin.fer.list'),
    path('stocks/ajouter-un-produit',CreateFer.as_view() ,name='admin.fer.create'),
    path("stocks/mouvements", ListMouvement.as_view(), name='admin.mouvement'),
    path("stocks/mouvements/entree", CreateMouvement.as_view(), name="admin.new_entrer"),
    path("stocks/suivis-produit/<int:fer_id>", get_suivis, name="admin.suivis.produit"),

    path('stocks/produits-en-stock',ListProduits.as_view() ,name='admin.stock.list'),
    
    path('contact/', ListMessage.as_view(), name="contact.list"),
    path('contact/<int:message_id>/lecture', mark_message_as_read, name="is_read"),
    path('contact/<int:message_id>/reponse', send_response, name="contact.reponse"),
    path('contact/<int:pk>/message', DeleteMessage.as_view(), name="contact.delete"),
    path("message/lire-le-devis/<int:message_id>", read_devis, name="open.devis"),
    path("message/lire-le-devis-proposer/<int:message_id>", read_devis_response, name="open.devis.proposer"),

    path('utilisateur/', ListUser.as_view(), name="user.list"),
    path('utilisateur/<int:user_id>/locked', toggle_user_status, name="toggle_user_status"),
    path('change-role/<int:user_id>/<str:group_name>/', change_user_role, name='change_user_role'),


    path('commandes/', ListOrder.as_view(), name='order.list'),
    path('commandes/<int:order_id>', detail_commande, name='order.detail'),
    path('commandes/<int:order_id>/suivis', suivis_commande, name='order.suivis'),
    path('commandes/change-statut/<int:order_id>', change_statut, name='change.status'),

    
    path('partenariats/', ListPartenariats.as_view(), name='partenariat.list'),
    path('partenariats/ajouter-un-partenariat/', CreatePartenariat.as_view(), name='partenariat.create'),
    path('partenariats/<int:pk>/modifier/', UpdatePartenriat.as_view(), name='partenariat.update'),
    path('partenariats/projets/', ListProjets.as_view(), name='partenariat.projet'),
    path('partenariats/projets/<int:projet_id>/', get_detail_projet, name='partenariat.projet.detail'),
    path('partenariats/detail/<int:partenariat_id>/', get_detail_partenariat, name='partenariat.detail'),
]
