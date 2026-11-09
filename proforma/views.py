from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template, render_to_string
from usesOrders.models import *
import os
from django.conf import settings
from .form import *
import tempfile
from weasyprint import HTML
from django.contrib import messages
from auth_app.permissions import admin_required
from usesOrders.promo import retirer_remise

# Les proformas sont un outil interne : toutes les vues sont réservées aux administrateurs.
# (La liste et le détail sont dans admin_site/views.py.)

@admin_required
def confirm_order_pro(request):
    # Récupérer le panier de l'utilisateur
    panier = Cart.objects.filter(user=request.user).first()
    retirer_remise(panier)  # pas de code promo pour les proformas
    paniers_details = []
    total_prix = 0
    if panier:
        for item in panier.items.all():
            paniers_details.append({
                'id':item.id,
                'produit': item.produit,
                'details': item.details_to_text(),
                'quantite': item.quantite,
                'prix': item.prix_u,
                'total': item.get_prix_total,
            })
            # Calculer le prix total du panier si nécessaire
        total_prix = panier.get_prix_total
    else:
        messages.info(request, "Votre panier est vide.")
        return redirect('panier')

    if request.method == "POST":

        form=OrderUserInfoFormPro(request.POST)
        if form.is_valid():
            user = request.user
            # 1. Récupérer le panier
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                return redirect('panier')  # panier vide

            # 2. Créer la commande
            order = OrderPro.objects.create(user=user, remise=0)  # pas de code promo
            order.save()
            # 3. Copier chaque CartItem en OrderItem
            for item in cart.items.all():
                OrderItemPro.objects.create(
                    order=order,
                    produit=item.produit,
                    details=item.details,
                    quantite=item.quantite,
                    prix_u=item.prix_u,
                    prix_revient=item.prix_revient
                )
            
            # 4. Enregistrement des infos sur le client
            if form.cleaned_data['mode_livraison'] == 'retrait en usine' : 
                adresse = 'bepanda l\'an 200' 
            else :
                adresse = form.cleaned_data['adresse']

            OrderUserInfoPro.objects.create(
                order=order,
                nom=form.cleaned_data['nom'],
                telephone=form.cleaned_data['telephone'],
                adresse=adresse,
                mode_livraison=form.cleaned_data['mode_livraison']
            )

            # 5. Créer le traitement de suivi de commande
            TraimentPro.objects.create(
                order=order,
                user=user,
                statut='en_attente'
            )

            # 6. Supprimer panier et items
            cart.items.all().delete()
            cart.delete()

            # 7. Rediriger vers la page de confirmation ou liste des commandes
            return redirect('liste-order-pro')  # à adapter selon ton URL
    else:
        form=OrderUserInfoFormPro() 
    context={
            'paniers': paniers_details, 
            'total_prix': total_prix,
            'montant_tva' :panier.montant_tva,
            'net_payer':panier.net_payer,
            'get_tranche1':panier.get_tranche1,
            'get_tranche2':panier.get_tranche2,
            'form':form
    }
    return render(request, 'confirmer-commande-pro.html', context)


@admin_required
def generate_invoice_pro(request, invoice_id):
  # Charger les données nécessaires (exemple : une commande)
    order = get_object_or_404(OrderPro, id=invoice_id)

    produits = OrderItemPro.objects.filter(order=order)

    produits_details = []
    for item in produits:
       produits_details.append({
                'id':item.id,
                'produit': item.produit,
                'details': item.details_to_text(),
                'quantite': item.quantite,
                'prix': item.prix_u,
                'total': item.get_prix_total,
            })
    # from pathlib import Path
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # os.path.join(BASE_DIR, "medias")
    image_url = request.build_absolute_uri(settings.MEDIA_URL + 'logobon.png')
    background_url = request.build_absolute_uri(settings.MEDIA_URL + 'filigramme.png')
    cachet_url = request.build_absolute_uri(settings.MEDIA_URL + 'signaturebon.jpg')
    footer_url = request.build_absolute_uri(settings.MEDIA_URL + 'page2.png')
    
    # Charger le template HTML 
    template_path = 'invoice.html'
    context = {'order': order,
               'produits':produits_details,
                'totals':order.get_prix_total,
                'status':order.get_statut_actuel,
                'image_url': image_url,
                'background_url':background_url,
                'cachet_url':cachet_url,
                'footer_url':footer_url,
                'montant_tva' :order.montant_tva,
                'net_payer':order.net_payer,
                'get_tranche1':order.get_tranche1,
                'get_tranche2':order.get_tranche2
               }  # Contexte à passer au template
    # Préparation du HTML avec image
    html_string = render_to_string('invoice_pro.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%y%m%d")
    filename=f'facture_proforma_{order.numero}BI{date}_{order.infoclient.nom}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@admin_required
def generate_bon_livraison_pro(request, invoice_id):
     # Charger les données nécessaires (exemple : une commande)
    order = get_object_or_404(OrderPro, id=invoice_id)

    produits = OrderItemPro.objects.filter(order=order)

    produits_details = []
    for item in produits:
       produits_details.append({
                'id':item.id,
                'produit': item.produit,
                'details': item.details_to_text(),
                'quantite': item.quantite,
                'prix': item.prix_u,
                'total': item.get_prix_total,
            })
    # from pathlib import Path
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # os.path.join(BASE_DIR, "medias")
    image_url = request.build_absolute_uri(settings.MEDIA_URL + 'logobon.png')
    background_url = request.build_absolute_uri(settings.MEDIA_URL + 'filigramme.png')
    cachet_url = request.build_absolute_uri(settings.MEDIA_URL + 'signaturebon.jpg')
    footer_url = request.build_absolute_uri(settings.MEDIA_URL + 'page2.png')
    
    # Charger le template HTML 
    template_path = 'invoice.html'
    context = {'order': order,
               'produits':produits_details,
                'totals':order.get_prix_total,
                'status':order.get_statut_actuel,
                'image_url': image_url,
                'background_url':background_url,
                'cachet_url':cachet_url,
                'footer_url':footer_url,
                'montant_tva' :order.montant_tva,
                'net_payer':order.net_payer,
                'get_tranche1':order.get_tranche1,
                'get_tranche2':order.get_tranche2
               }  # Contexte à passer au template
    # Préparation du HTML avec image
    html_string = render_to_string('bon-livraison-pro.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%y%m%d")
    filename=f'bon_libraison_{order.numero}BI{date}_{order.infoclient.nom}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response