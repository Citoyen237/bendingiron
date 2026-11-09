from django.urls import path
from .views import *

urlpatterns = [
    path('facturation-proforma/', confirm_order_pro, name='confirm-proforma'),
    path('facture/<int:invoice_id>/download/', generate_invoice_pro, name='invoice_download_pro'),
    path('bon-livraison/<int:invoice_id>/download/', generate_bon_livraison_pro, name='generate_bon_livraison_pro'),
    
]