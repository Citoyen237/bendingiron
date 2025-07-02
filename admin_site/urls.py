from django.urls import path
from .views import *

urlpatterns = [
    path('', indexA, name='admin.index'),
    path('temoignages/',ListTemoignage.as_view() ,name='admin.temoignage.list'),
    path('temoignages/creer',CreateTemoignage.as_view() ,name='admin.temoignage.create'),
    path('temoignages/<int:pk>/supprimer',DeleteTemoignage.as_view() ,name='admin.temoignage.delete'),
    path('temoignages/<int:pk>/modifier',UpdateTemoignage.as_view() ,name='admin.temoignage.update'), 

    # gestion du stock
    path('stocks/',ListFer.as_view() ,name='admin.fer.list'),
    path('stocks/ajouter-un-produit',CreateFer.as_view() ,name='admin.fer.create'),
    path("stocks/mouvements", ListMouvement.as_view(), name='admin.mouvement'),
    path("stocks/mouvements/entree", CreateMouvement.as_view(), name="admin.new_entrer"),
    path("stocks/suivis-produit/<int:fer_id>", get_suivis, name="admin.suivis.produit"),

    path('stocks/produits-en-stock',ListProduits.as_view() ,name='admin.stock.list'),
    # path('stocks/produits-en-stock/<int:pk>/update',UpdateProduitStock.as_view(),name='admin.stock.update'),
    # path('stocks/produits-en-stock/<int:pk>/delete',DeleteProduitStock.as_view(),name='admin.stock.delete'),
    # path('stocks/produits-en-stock/create',CreateProduit.as_view() ,name='admin.stock.create'),

    # path('formes/',ListForme.as_view() ,name='admin.forme.list'),
    # path('formes/<int:pk>/update',UpdateForme.as_view() ,name='admin.forme.update'),
    # path('formes/create',CreateForme.as_view() ,name='admin.forme.create'),
    # path('formes/<int:pk>/delete',DeleteForme.as_view(),name='admin.forme.delete'),

    # path('dimensions/',ListDimenssion.as_view() ,name='admin.dimenssion.list'),
    # path('dimensions/<int:pk>/update',UpdateDimenssion.as_view() ,name='admin.dimenssion.update'),
    # path('dimensions/create',CreateDimenssion.as_view() ,name='admin.dimenssion.create'),
    # path('dimensions/<int:pk>/delete',DeleteDimenssion.as_view(),name='admin.dimenssion.delete'),

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
]
