from SiteDFmac.factures import image_dessin, images_facture
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template, render_to_string
import tempfile
from weasyprint import HTML
from django.conf import settings
import os
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from auth_app.permissions import admin_required, get_owned_or_404, is_admin
from django.utils.decorators import method_decorator
from .form import *
from .promo import erreur_conditions, retirer_remise_si_invalide

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

@admin_required
def confirmer_commande(request):
    """Création manuelle d'une commande SANS paiement en ligne (ex. paiement en espèces).
    Réservée aux administrateurs : les clients passent par /paiements/confirmer/."""
    user = request.user
    # 1. Récupérer le panier
    cart = Cart.objects.filter(user=user).first()
    if not cart:
        return redirect('panier')  # panier vide

    erreur = retirer_remise_si_invalide(cart)
    if erreur:
        messages.error(request, f"Code promo retiré : {erreur}")
        return redirect('panier')

    # 2. Créer la commande
    order = Order.objects.create(user=user, remise=cart.remise)  # remise du code promo conservée

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
    filename=f'facture_{date}BI{commande.numero}_{commande.infoclient.nom}_solde'
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

@admin_required
def send_info_user(request):
    """Comme confirmer_commande : réservé aux administrateurs (commande sans paiement en ligne)."""
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
        messages.info(request, "Votre panier est vide.")
        return redirect('panier')

    if request.method == "POST":

        form=OrderUserInfoForm(request.POST)
        if form.is_valid():
            user = request.user
            # 1. Récupérer le panier
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                return redirect('panier')  # panier vide

            erreur = retirer_remise_si_invalide(cart)
            if erreur:
                messages.error(request, f"Code promo retiré : {erreur}")
                return redirect('info_user')

            # 2. Créer la commande
            order = Order.objects.create(user=user, remise=cart.remise)  # remise du code promo conservée

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
    else:
        form=OrderUserInfoForm() 
    context={
            'paniers': paniers_details,
            'total_prix': total_prix,
            'montant_ht_brut': panier.montant_ht_brut,
            'remise': panier.remise,
            'montant_remise': round(panier.montant_remise()),
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
    order = get_owned_or_404(request, Order, "user", id=invoice_id)

    produits = OrderItem.objects.filter(order=order)

    produits_details = []
    for item in produits:
       produits_details.append({
                'id':item.id,
                'produit': item.produit,
                'details': item.details_to_text(),
                'dessin': image_dessin(item.details),
                'quantite': item.quantite,
                'prix': item.prix_u,
                'total': item.get_prix_total,
            })
    # from pathlib import Path
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # os.path.join(BASE_DIR, "medias")
    image_url, background_url, cachet_url, footer_url = images_facture(request)
    
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
    filename=f'facture_{date}BI{order.id}_{order.infoclient.nom}_acompte'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required
def generate_invoice_pdf_solde(request, invoice_id):
  # Charger les données nécessaires (exemple : une commande)
    order = get_owned_or_404(request, Order, "user", id=invoice_id)

    produits = OrderItem.objects.filter(order=order)

    produits_details = []
    for item in produits:
       produits_details.append({
                'id':item.id,
                'produit': item.produit,
                'details': item.details_to_text(),
                'dessin': image_dessin(item.details),
                'quantite': item.quantite,
                'prix': item.prix_u,
                'total': item.get_prix_total,
            })
    # from pathlib import Path
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # os.path.join(BASE_DIR, "medias")
    image_url, background_url, cachet_url, footer_url = images_facture(request)
    
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

@login_required
@require_POST
def appliquer_code_promo(request):
    """Applique un code distributeur au panier.

    Le jeton CSRF est obligatoire : le JavaScript doit envoyer l'en-tête
    X-CSRFToken (voir panier.html). L'utilisation n'est comptée qu'une fois
    par panier, et après tous les contrôles.
    """
    code_saisi = (request.POST.get("code") or "").strip()
    user = request.user

    if not code_saisi:
        return JsonResponse({"success": False, "message": "Veuillez saisir un code."})

    with transaction.atomic():
        panier = Cart.objects.select_for_update().filter(user=user).first()
        if not panier:
            return JsonResponse({"success": False, "message": "Panier introuvable."})

        # Conditions : fer fourni par Bending Iron + quantité minimale (0 par défaut)
        erreur = erreur_conditions(panier)
        if erreur:
            return JsonResponse({"success": False, "message": erreur})

        # Un client ne peut utiliser que SES codes. Un administrateur qui passe
        # une commande pour un client saisit le code de ce client.
        codes = CodePromo.objects.select_for_update().filter(code=code_saisi)
        if not is_admin(user):
            codes = codes.filter(client=user)
        code_promo = codes.first()
        if code_promo is None:
            return JsonResponse({"success": False, "message": "Code promo invalide."})

        # Expiration vérifiée AVANT de compter une utilisation
        if code_promo.expiration > 0 and code_promo.is_expired:
            return JsonResponse({"success": False, "message": "Ce code promo est expiré."})

        deja_applique = panier.remise == code_promo.remise and panier.remise > 0
        if not deja_applique:
            if code_promo.nb_utilidation > 0 and code_promo.nb_uses_atteint:
                return JsonResponse({"success": False, "message": "Le nombre d'utilisations de ce code a été atteint."})
            if code_promo.nb_utilidation > 0:
                CodePromoUse.objects.create(promo_code=code_promo)

        # ✅ Appliquer la remise
        panier.remise = code_promo.remise
        panier.save(update_fields=["remise", "updated_at"])

    return JsonResponse({
        "success": True,
        "message": f"Code promo appliqué ! Remise : {code_promo.remise}%",
        "remise": float(code_promo.remise)
    })
