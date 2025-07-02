from django.urls import path
from .views import *

urlpatterns = [
    # path('', ListProduitFront.as_view(), name='boutique'),
    path('<int:product_id>/detail_produit',detail_produit, name='produit.detail'),
    # path('<int:product_id>/resumer-des-parametres', get_resumer, name='resumer'),
    path('produit-solution-btp', get_produit_solution, name='solution.btp'),
    path("", all_produit, name="boutique"),
    path("<int:categorie_id>", get_sous_categorie, name="souscategorie"),
    path("sous-categorie/<int:produit_id>", get_produit, name="produit"),

]
