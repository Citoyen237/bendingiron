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
# Fonction pour vérifier si l'utilisateur appartient au groupe 'admin'
def is_admin(user):
   return user.groups.filter(name='admin').exists() or user.groups.filter(name='superadmin').exists()

# Create your views here.
@login_required
def index(request):
    current_url = request.get_full_path()
    
    partenariat = Partenariats.objects.filter(user=request.user).first()
    projets =Projet.objects.filter(partenariat=partenariat.id)
    context = {
        'projets':projets,
        'current_url':current_url,
        'partenariat':partenariat,
    }
    return render(request, 'partenaire.html', context)

@login_required
def detail_projet(request, projet_id):
    current_url = request.get_full_path()
    projet = get_object_or_404(Projet, id=projet_id)
    produits = ProjetItem.objects.filter(projet=projet_id)

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

@login_required
@user_passes_test(is_admin)
def confirm_projet(request):
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

    user=request.user
    if request.method == "POST":
        form=ProjetForm(request.POST)
        if form.is_valid():
            projet=Projet.objects.create(
                user=user,
                partenariat=form.cleaned_data['partenariat'],
                reduction=form.cleaned_data['reduction'],
                name=form.cleaned_data['name'],
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

    if not panier or not projet_id:
        return JsonResponse({'error': 'Projet ou panier manquant'}, status=400)

    try:
        projet = Projet.objects.get(id=projet_id)
    except Projet.DoesNotExist:
        return JsonResponse({'error': 'Projet introuvable'}, status=404)

    # Étape 1 : Créer la commande principale
    commande = ProjetOrder.objects.create(
        projet=projet
    )

    # Étape 2 : Ajouter les produits de la commande
    for item_id, info in panier.items():
        try:
            produit = ProjetItem.objects.get(id=item_id)
            quantite = int(info['quantite'])
            ProjetOrderItem.objects.create(
                projet_order=commande,
                projet_item=produit,
                quantite=quantite
            )
        except (ProjetItem.DoesNotExist, ValueError, KeyError):
            continue  # Ignore les entrées invalides

    # Étape 3 : Ajouter une ligne de traitement associée à l'utilisateur
    TraimentOrder.objects.create(
        projet_order=commande,
        user=request.user
    )

    return JsonResponse({'success': 'Commande enregistrée'})

@login_required
def historique_order(request, projet_id):
    projet = Projet.objects.get(pk=projet_id)
    orders = ProjetOrder.objects.filter(projet=projet).order_by('created_at')
    paiements =PaiementProjet.objects.filter(projet=projet_id).all() 

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
    order = get_object_or_404(ProjetOrder, id=projet_id)

    produits = ProjetOrderItem.objects.filter(projet_order=order)

    produits_details = []
    for item in produits:
       produits_details.append({
                'id':item.id,
                'produit': item.projet_item.produit,
                'details': item.projet_item.details_to_text(),
                'quantite': item.quantite,
            })
    # from pathlib import Path
    # BASE_DIR = Path(__file__).resolve().parent.parent
    # os.path.join(BASE_DIR, "medias")
    image_url = request.build_absolute_uri(settings.MEDIA_URL + 'logo.png')
    background_url = request.build_absolute_uri(settings.MEDIA_URL + 'filigramme.png')
    cachet_url = request.build_absolute_uri(settings.MEDIA_URL + 'signaturecachet.png')
    footer_url = request.build_absolute_uri(settings.MEDIA_URL + 'pieddepage.png')
    
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
    filename=f'bon_{date}B-iron{order.id}_{order.projet.partenariat}_{order.projet.name}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required
def download_projet(request, projet_id):
    # Charger les données nécessaires (exemple : une commande)
    order = get_object_or_404(Projet, id=projet_id)

    produits = ProjetItem.objects.filter(projet=order)

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
    filename=f'projet_{date}B-iron{order.id}_{order.name}_{order.partenariat}'
    

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    return response

@login_required
def get_detail_order(request, order_id):
      # Récupérer la commande avec son ID
    commande = get_object_or_404(ProjetOrder, id=order_id)

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