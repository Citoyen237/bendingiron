from django.shortcuts import render,redirect,get_object_or_404
from usesOrders.models import *
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import *
from .form import *
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
# Fonction pour vérifier si l'utilisateur appartient au groupe 'admin'
def is_admin(user):
   return user.groups.filter(name='admin').exists() or user.groups.filter(name='superadmin').exists()

# Create your views here.
@login_required
def index(request):
    current_url = request.get_full_path()
    projets =Projet.objects.filter(user=request.user)
    partenariat = Partenariats.objects.filter(user=request.user).first()
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
        for item in panier.cartitem_set.all():
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
            for item in panier.cartitem_set.all():
                ProjetItem.objects.create(
                projet=projet,
                produit=item.produit,
                details=item.details,
                quantite=item.quantite,
                prix_u=item.prix_u
            )
            
            # 5. Supprimer panier et items
            panier.cartitem_set.all().delete()
            panier.delete()
            # 5. Rediriger vers la page de confirmation ou liste des commandes
            return redirect('boutique')  # à adapter selon ton UR
    else :
        form = ProjetForm()

    return render(request, 'nouveau-projet.html', {'paniers': paniers_details, 'total_prix': total_prix,'form':form})

@login_required
@csrf_exempt
def valider_commande(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        panier = data.get('panier')
        projet_id = data.get('projet_id')

        if not projet_id or not panier:
            return JsonResponse({'error': 'Projet ou panier manquant'}, status=400)

        try:
            projet = Projet.objects.get(id=projet_id)
        except Projet.DoesNotExist:
            return JsonResponse({'error': 'Projet introuvable'}, status=404)

        for item_id, info in panier.items():
            try:
                produit = ProjetItem.objects.get(id=item_id)
                ProjetOrder.objects.create(
                    projet=projet,
                    projet_item=produit,
                    quantite=info['quantite']
                )
            except ProjetItem.DoesNotExist:
                continue  # on ignore les produits invalides

        return JsonResponse({'success': 'Commande enregistrée'})
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)