from SiteDFmac.factures import image_dessin, images_facture
from django.shortcuts import render,redirect,get_object_or_404
from usesOrders.models import *
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import *
from .form import *
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from collections import defaultdict
from django.template.loader import get_template, render_to_string
from django.utils.decorators import method_decorator
from weasyprint import HTML
from django.conf import settings
from django.http import HttpResponse
from django.db import transaction
from auth_app.permissions import is_admin, admin_required, get_owned_or_404
from usesOrders.promo import retirer_remise

# Propriétaire de chaque objet, vu depuis l'utilisateur partenaire
OWNER_PROJET = "partenariat__user"
OWNER_PROJET_ORDER = "projet__partenariat__user"
OWNER_ORDER_ADD = "projet_order__partenariat__user"

# Create your views here.
@login_required
def index(request):
    current_url = request.get_full_path()
    
    partenariat = Partenariats.objects.filter(user=request.user).first()
    if partenariat is None:
        messages.info(request, "Aucun partenariat n'est associé à votre compte.")
        return redirect('boutique')
    projets = Projet.objects.filter(partenariat=partenariat)
    context = {
        'projets':projets,
        'current_url':current_url,
        'partenariat':partenariat,
    }
    return render(request, 'partenaire.html', context)

@login_required
def detail_projet(request, projet_id):
    current_url = request.get_full_path()
    projet = get_owned_or_404(request, Projet, OWNER_PROJET, id=projet_id)
    produits = ProjetItem.objects.filter(projet=projet)

     # Ajouter un champ 'prix_total' calculé pour chaque produit
    produits_details = []
    for item in produits:
        produits_details.append({
                'id':item.id,
                'produit': item.produit,
                'details': item.details_to_text(),
                'quantite': item.quantite,
                'prix': item.prix_u,
                'quantite_restant':item.quantite_restant,
                'quantite_commande':item.quantite_commande,
                'total': item.get_prix_total,
                'prix_revient':item.prix_revient,
            })
        
    context = {
        'produits':produits_details,
        'projet':projet,
        'current_url':current_url,
    }
    return render(request, 'detail-projet.html', context)

@admin_required
def confirm_projet(request):
    # Récupérer le panier de l'utilisateur
    panier = Cart.objects.filter(user=request.user).first()
    retirer_remise(panier)  # pas de code promo pour les projets
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
        messages.info(request, "Le panier est vide.")
        return redirect('panier')

    user=request.user
    if request.method == "POST":
        form=ProjetForm(request.POST)

        

        if form.is_valid():

            if form.cleaned_data['frais_ingenieurie'] == 'personne morale' :
                frais_ingenieurie = 10000
            else :
                frais_ingenieurie = 5000
            projet=Projet.objects.create(
                user=user,
                partenariat=form.cleaned_data['partenariat'],
                reduction=form.cleaned_data['reduction'],
                name=form.cleaned_data['name'],
                frais_ingenieurie=frais_ingenieurie,
            )

            # 3. Copier chaque CartItem en OrderItem
            for item in panier.items.all():
                ProjetItem.objects.create(
                projet=projet,
                produit=item.produit,
                details=item.details,
                quantite=item.quantite,
                prix_revient=item.prix_revient,
                prix_u=item.prix_u
            )
            
            # 5. Supprimer panier et items
            panier.items.all().delete()
            panier.delete()
            # 5. Rediriger vers la page de confirmation ou liste des commandes
            return redirect('boutique')  # à adapter selon ton UR
    else :
        form = ProjetForm()

    return render(request, 'nouveau-projet.html', {'paniers': paniers_details, 'total_prix': total_prix,'form':form})

# @method_decorator(csrf_exempt, name='dispatch')  # seulement si CSRFToken non présent
@login_required
def valider_commande_partenaire(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Données JSON invalides'}, status=400)

    panier = data.get('panier')
    projet_id = data.get('projet_id')

    if not isinstance(panier, dict) or not panier or not projet_id:
        return JsonResponse({'error': 'Projet ou panier manquant'}, status=400)

    # Le projet doit appartenir au partenaire connecté (les admins peuvent tout faire)
    qs = Projet.objects.all() if is_admin(request.user) else Projet.objects.filter(**{OWNER_PROJET: request.user})
    projet = qs.filter(id=projet_id).first()
    if projet is None:
        return JsonResponse({'error': 'Projet introuvable'}, status=404)
    if not projet.peut_commander:
        return JsonResponse({'error': "Ce projet ne permet pas de commander pour le moment."}, status=400)

    # Validation complète AVANT de créer quoi que ce soit
    lignes = []
    for item_id, info in panier.items():
        try:
            item = projet.projetitems.get(id=int(item_id))   # article de CE projet uniquement
            quantite = int(info['quantite'])
        except (ProjetItem.DoesNotExist, ValueError, KeyError, TypeError):
            return JsonResponse({'error': f"Article invalide : {item_id}"}, status=400)
        if quantite <= 0:
            continue
        if quantite > item.quantite_restant:
            return JsonResponse({'error': f"Quantité demandée supérieure au restant pour {item.produit}"}, status=400)
        lignes.append((item, quantite))

    if not lignes:
        return JsonResponse({'error': 'Aucune quantité à commander'}, status=400)

    with transaction.atomic():
        commande = ProjetOrder.objects.create(projet=projet)
        for item, quantite in lignes:
            ProjetOrderItem.objects.create(projet_order=commande, projet_item=item, quantite=quantite)
        TraimentOrder.objects.create(projet_order=commande, user=request.user)

    return JsonResponse({'success': 'Commande enregistrée'})

@login_required
def historique_order(request, projet_id):
    projet = get_owned_or_404(request, Projet, OWNER_PROJET, pk=projet_id)
    orders = ProjetOrder.objects.filter(projet=projet).order_by('created_at')
    paiements = PaiementProjet.objects.filter(projet=projet)

    grouped_orders = defaultdict(list)

    for order in orders:
        # tronquer à l'année, mois, jour, heure et minute
        created_minute = order.created_at.replace(second=0, microsecond=0)
        grouped_orders[created_minute].append(order)

    context = {
        'projet': projet,
        'paiements':paiements,
        'orders': orders
    }

    return render(request, 'historique.html', context)

@login_required
def genrate_bon(request, projet_id):
    # Charger les données nécessaires (exemple : une commande)
    order = get_owned_or_404(request, ProjetOrder, OWNER_PROJET_ORDER, id=projet_id)

    produits = ProjetOrderItem.objects.filter(projet_order=order)

    produits_details = []
    for item in produits:
       produits_details.append({
                'id':item.id,
                'produit': item.projet_item.produit,
                'details': item.projet_item.details_to_text(),
                'dessin': image_dessin(item.projet_item.details),
                'quantite': item.quantite,
            })
    # from pathlib import Path
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # os.path.join(BASE_DIR, "medias")
    image_url, background_url, cachet_url, footer_url = images_facture(request)
    
    # Charger le template HTML 
    template_path = 'bon_pdf.html'
    context = {'order': order,
               'produits':produits_details,
                'status':order.get_statut_actuel,
                'image_url': image_url,
                'background_url':background_url,
                'cachet_url':cachet_url,
                'footer_url':footer_url,
               }  # Contexte à passer au template
    # Préparation du HTML avec image
    html_string = render_to_string('bon_pdf.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%d%m%y")
    filename=f'DLP_{order.projet.name}_{date}BI{order.id}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required
def download_projet(request, projet_id):
    # Charger les données nécessaires (exemple : une commande)
    order = get_owned_or_404(request, Projet, OWNER_PROJET, id=projet_id)

    produits = ProjetItem.objects.filter(projet=order)

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
    template_path = 'projet_pdf.html'
    context = {'order': order,
               'produits':produits_details,
                'image_url': image_url,
                'background_url':background_url,
                'cachet_url':cachet_url,
                'footer_url':footer_url,
               }  # Contexte à passer au template
    # Préparation du HTML avec image
    html_string = render_to_string('projet_pdf.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%d%m%y")
    filename=f'projet_{order.numero}BI{date}_{order.name}_{order.partenariat}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required
def get_detail_order(request, order_id):
      # Récupérer la commande avec son ID
    commande = get_owned_or_404(request, ProjetOrder, OWNER_PROJET_ORDER, id=order_id)

    # Récupérer les produits associés à cette commande
    produits = ProjetOrderItem.objects.filter(projet_order=commande)

     # Ajouter un champ 'prix_total' calculé pour chaque produit
    produits_details = []
    for item in produits:
        produits_details.append({
                'id':item.id,
                'produit': item.projet_item.produit,
                'details': item.projet_item.details_to_text(),
                'quantite': item.quantite,
            })
    context = {
        'produits':produits_details,
        'status':commande.get_statut_actuel,
        'orderId':commande.id,
        'order':commande
    }
    return render(request, "detail-order.html", context)

@admin_required
def confirm_additional_order(request):
    # Récupérer le panier de l'utilisateur
    panier = Cart.objects.filter(user=request.user).first()
    retirer_remise(panier)  # pas de code promo pour les commandes de projet
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
        messages.info(request, "Le panier est vide.")
        return redirect('panier')
    projets_data = list(Projet.objects.order_by("name").values("id", "name", "partenariat_id"))
    if request.method == "POST":

        form= OrderAddForm(request.POST)
        if form.is_valid():
            user = request.user
            # 1. Récupérer le panier
            cart = Cart.objects.filter(user=user).first()
            if not cart:
                return redirect('panier')  # panier vide

            # 2. Créer la commande
            order = form.save(commit=False)
            order.user = request.user
            order.save()  # attribue annee + sequence (numéro)
            # 3. Copier chaque CartItem en OrderItem
            for item in cart.items.all():
                OrderItemAdd.objects.create(
                    order=order,
                    produit=item.produit,
                    details=item.details,
                    quantite=item.quantite,
                    prix_u=item.prix_u,
                    prix_revient=item.prix_revient
                )
            

            # 5. Créer le traitement de suivi de commande
            TraimentAdd.objects.create(
                order=order,
                user=user,
                statut='en_attente'
            )

            # 6. Supprimer panier et items
            cart.items.all().delete()
            cart.delete()

            # 7. Rediriger vers la page de confirmation ou liste des commandes
            return redirect('partenariat.order.additional')  # à adapter selon ton URL

    else:
        form=form= OrderAddForm()
    context={
            'paniers': paniers_details, 
            'total_prix': total_prix,
            'montant_tva' :panier.montant_tva,
            'net_payer':panier.net_payer,
            'get_tranche1':panier.get_tranche1,
            'get_tranche2':panier.get_tranche2,
            'form':form,
            "projets_data": projets_data,
    }
    return render(request, 'confirmer-commande-additional.html', context)

@admin_required
def projets_par_partenaire(request, partenaire_id):
    projets = Projet.objects.filter(partenariat_id=partenaire_id).order_by("name")
    return JsonResponse(
        {"results": [{"id": p.pk, "label": p.name} for p in projets]}
    )


@login_required
def get_order_additional_list(request, projet_id):
    projet = get_owned_or_404(request, Projet, OWNER_PROJET, pk=projet_id)
    commandes = OrderAdd.objects.filter(projet_order=projet).order_by("created_at")
    context = {
        'commandes': commandes,
        'projet':projet,
    }
    return render(request, 'order-additional.html', context)

@login_required
def detail_commande_additional(request, order_id):
     # Récupérer la commande avec son ID
    commande = get_owned_or_404(request, OrderAdd, OWNER_ORDER_ADD, id=order_id)

    # Récupérer les produits associés à cette commande
    produits = OrderItemAdd.objects.filter(order=commande)

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
    filename=f'facture_{date}BI{commande.numero}_{commande.projet_order.name}'
    context = {
        'current_url':current_url,
        'produits':produits_details,
        'totals':commande.get_prix_total,
        'status':commande.get_statut_actuel,
        'order':commande,
        'montant_tva' :commande.montant_tva,
        'net_payer':commande.net_payer,
        'filename':filename
    }
    return render(request, 'detail-additional-order.html',context)

@login_required
def generate_order_additional(request, order_id):
     # Charger les données nécessaires (exemple : une commande)
    order = get_owned_or_404(request, OrderAdd, OWNER_ORDER_ADD, id=order_id)

    produits = OrderItemAdd.objects.filter(order=order)

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
               }  # Contexte à passer au template
    # Préparation du HTML avec image
    html_string = render_to_string('invoice-additional.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%y%m%d")
    filename=f'facture_Add_{order.numero}BI{date}_{order.projet_order.name}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required
def genrate_bon_livraison(request, projet_id):
    # Charger les données nécessaires (exemple : une commande)
    order = get_owned_or_404(request, ProjetOrder, OWNER_PROJET_ORDER, id=projet_id)

    produits = ProjetOrderItem.objects.filter(projet_order=order)

    produits_details = []
    for item in produits:
       produits_details.append({
                'id':item.id,
                'produit': item.projet_item.produit,
                'details': item.projet_item.details_to_text(),
                'dessin': image_dessin(item.projet_item.details),
                'quantite': item.quantite,
            })
    # from pathlib import Path
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # os.path.join(BASE_DIR, "medias")
    image_url, background_url, cachet_url, footer_url = images_facture(request)
    
    # Charger le template HTML 
    template_path = 'bon_pdf.html'
    context = {'order': order,
               'produits':produits_details,
                'status':order.get_statut_actuel,
                'image_url': image_url,
                'background_url':background_url,
                'cachet_url':cachet_url,
                'footer_url':footer_url,
               }  # Contexte à passer au template
    # Préparation du HTML avec image
    html_string = render_to_string('invoice-order-pro.html', context)

    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    date=order.created_at.strftime("%d%m%y")
    filename=f'FACTURE_DLP_{order.projet.name}_{date}BI{order.id}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response