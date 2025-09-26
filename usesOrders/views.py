from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa
import tempfile
from weasyprint import HTML
from django.conf import settings
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .form import *

@login_required
def show_cart(request):
    # Récupérer le panier de l'utilisateur
    panier = Cart.objects.filter(user=request.user).first()
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
        context={
            'paniers': paniers_details, 
            'total_prix': total_prix,
            'montant_tva' :panier.montant_tva,
            'net_payer':panier.net_payer,
            'get_tranche1':panier.get_tranche1,
            'get_tranche2':panier.get_tranche2,
            'prix_revient':panier.prix_revient_total
        }
    else:
        panier = None
        context={}  # ou crée un panier vide, selon besoin

    return render(request, 'panier.html', context)

@login_required
def supprimer_du_panier(request, item_id):
     # Trouver l'élément CartItem dans le panier de l'utilisateur connecté
    item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()

    if item:
        cart = item.cart  # récupérer le panier associé
        item.delete()     # supprimer l'élément

        # Vérifier si le panier est maintenant vide
        if not cart.items.exists():
            cart.delete()  # supprimer aussi le panier s'il n'a plus d'items
    return redirect('panier')

@login_required
def confirmer_commande(request):
    user = request.user
    # 1. Récupérer le panier
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        return redirect('panier')  # panier vide

    # 2. Créer la commande
    order = Order.objects.create(user=user)

    # 3. Copier chaque CartItem en OrderItem
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            produit=item.produit,
            details=item.details,
            quantite=item.quantite,
            prix_u=item.prix_u,
            prix_revient=item.prix_revient
        )

    # 4. Créer le traitement de suivi de commande
    Traiment.objects.create(
        order=order,
        user=user,
        statut='en_attente'
    )

    # 5. Supprimer panier et items
    cart.items.all().delete()
    cart.delete()

    # 5. Rediriger vers la page de confirmation ou liste des commandes
    return redirect('mes_commande')  # à adapter selon ton URL

# # Create your views here.
@login_required
def mes_commande(request):
    commandes = Order.objects.filter(user=request.user).order_by('-created_at')
    current_url = request.get_full_path()
    context = {
        'commandes': commandes,
        'current_url':current_url,
    }
    return render(request, 'commandes.html',context)

@login_required
def detail_commande(request, order_id):
     # Récupérer la commande avec son ID
    commande = get_object_or_404(Order, id=order_id, user=request.user)

    # Récupérer les produits associés à cette commande
    produits = OrderItem.objects.filter(order=commande)

     # Ajouter un champ 'prix_total' calculé pour chaque produit
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
    current_url = '/mes-commandes/'
    date=commande.created_at.strftime("%d%m%y")
    filename=f'facture_{date}B-iron{commande.id}_{commande.infoclient.nom}_solde'
    context = {
        'current_url':current_url,
        'produits':produits_details,
        'totals':commande.get_prix_total,
        'status':commande.get_statut_actuel,
        'order':commande,
        'montant_tva' :commande.montant_tva,
        'net_payer':commande.net_payer,
        'get_tranche1':commande.get_tranche1,
        'get_tranche2':commande.get_tranche2,
        'filename':filename
    }
    return render(request, 'detail-commande.html',context)

@login_required
def send_info_user(request):
    # Récupérer le panier de l'utilisateur
    panier = Cart.objects.filter(user=request.user).first()
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
        panier = None  # ou crée un panier vide, selon besoin
    
    if request.method == "POST":

        form=OrderUserInfoForm(request.POST)
        if form.is_valid():
            user = request.user
            # 1. Récupérer le panier
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                return redirect('panier')  # panier vide

            # 2. Créer la commande
            order = Order.objects.create(user=user)

            # 3. Copier chaque CartItem en OrderItem
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    produit=item.produit,
                    details=item.details,
                    quantite=item.quantite,
                    prix_u=item.prix_u,
                    prix_revient=item.prix_revient
                )
            
            # 4. Enregistrement des infos sur le client
            OrderUserInfo.objects.create(
                order=order,
                nom=form.cleaned_data['nom'],
                telephone=form.cleaned_data['telephone'],
                adresse=form.cleaned_data['adresse']
            )

            # 5. Créer le traitement de suivi de commande
            Traiment.objects.create(
                order=order,
                user=user,
                statut='en_attente'
            )

            # 6. Supprimer panier et items
            cart.items.all().delete()
            cart.delete()

            # 7. Rediriger vers la page de confirmation ou liste des commandes
            return redirect('mes_commande')  # à adapter selon ton URL
        else :
            print(form.errors)

    else:
        form=OrderUserInfoForm() 
    context={
            'paniers': paniers_details, 
            'total_prix': total_prix,
            'montant_tva' :panier.montant_tva,
            'net_payer':panier.net_payer,
            'get_tranche1':panier.get_tranche1,
            'get_tranche2':panier.get_tranche2,
            'form':form
    }
    return render(request, 'confirmer-commande.html', context)

@login_required
def generate_invoice_pdf(request, invoice_id):
  # Charger les données nécessaires (exemple : une commande)
    order = get_object_or_404(Order, id=invoice_id)

    produits = OrderItem.objects.filter(order=order)

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
    image_url = request.build_absolute_uri(settings.MEDIA_URL + 'logo.png')
    background_url = request.build_absolute_uri(settings.MEDIA_URL + 'filigramme.png')
    cachet_url = request.build_absolute_uri(settings.MEDIA_URL + 'signaturecachet.jpg')
    footer_url = request.build_absolute_uri(settings.MEDIA_URL + 'pieddepage.png')
    
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
    html_string = render_to_string('invoice.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%d%m%y")
    filename=f'facture_{date}B-iron{order.id}_{order.infoclient.nom}_acompte'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required
def generate_invoice_pdf_solde(request, invoice_id):
  # Charger les données nécessaires (exemple : une commande)
    order = get_object_or_404(Order, id=invoice_id)

    produits = OrderItem.objects.filter(order=order)

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
    image_url = request.build_absolute_uri(settings.MEDIA_URL + 'logo.png')
    background_url = request.build_absolute_uri(settings.MEDIA_URL + 'filigramme.png')
    cachet_url = request.build_absolute_uri(settings.MEDIA_URL + 'signaturecachet.png')
    footer_url = request.build_absolute_uri(settings.MEDIA_URL + 'pieddepage.png')
    
    # Charger le template HTML 
    template_path = 'invoice2.html'
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
    html_string = render_to_string('invoice2.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%d%m%y")
    filename=f'facture_{date}B-iron{order.id}_{order.infoclient.nom}_solde'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@csrf_exempt
def appliquer_code_promo(request):
        code_saisi = request.POST.get("code")
        user = request.user  

        # Récupérer le panier de l'utilisateur
        panier = Cart.objects.filter(user=user).first()
        if not panier:
            return JsonResponse({"success": False, "message": "Panier introuvable."})

        # Vérifier la quantité totale dans le panier
        quantite_totale = sum(item.quantite for item in panier.items.all())
        if quantite_totale < 500:
            return JsonResponse({
                "success": False,
                "message": "Vous devez avoir au moins 500 produits pour appliquer un code promo."
            })
        
        # Vérifier description des produits
        for item in panier.items.all():
            description = item.details  # JSON (dict)
            # Vérifier que la clé "Fer" existe et que sa valeur est "bending iron"
            if not description or description.get("fer") != "bending iron":
                return JsonResponse({
                    "success": False,
                    "message": "Le fer de tous les produits doit être fourni par 'bending iron' pour appliquer ce code."
                })

        # Vérifier si le code promo existe
        try:
            code_promo = CodePromo.objects.get(code=code_saisi, client=user)
        except CodePromo.DoesNotExist:
            return JsonResponse({"success": False, "message": "Code promo invalide."})

        # Vérifier expiration
        if code_promo.is_expired:
            return JsonResponse({"success": False, "message": "Ce code promo est expiré."})

        # ✅ Appliquer la remise
        panier.remise = code_promo.remise
        panier.save()

        return JsonResponse({
            "success": True,
            "message": f"Code promo appliqué ! Remise : {code_promo.remise}%",
            "remise": float(code_promo.remise)
        })