from django.urls import path
from .views import *

urlpatterns = [
  path('', mes_commande , name='mes_commande'),
  path('panier', show_cart, name='panier'),
  path('panier/supprimer/<int:item_id>/', supprimer_du_panier, name='supprimer_du_panier'),
  path('confirmer-la-commande/', confirmer_commande, name='confirmer'),
  path('detail-commande/<int:order_id>', detail_commande , name='detail_commande'),
  path('invoice/<int:invoice_id>/download/', generate_invoice_pdf, name='invoice_download'),
]
