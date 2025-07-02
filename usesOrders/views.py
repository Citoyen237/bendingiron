from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
# from weasyprint import HTML

def show_cart(request):
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

    return render(request, 'panier.html', {'paniers': paniers_details, 'total_prix': total_prix})

def get_resumer(request, product_id):
    current_url = '/produits/'
    product = get_object_or_404(Produit, id=product_id)
    context = {
        'current_url':current_url,
        'product':product
    }
    return render(request, 'resume-item.html', context)

@login_required
def supprimer_du_panier(request, item_id):
     # Trouver l'élément CartItem dans le panier de l'utilisateur connecté
    item = CartItem.objects.filter(id=item_id, cart__user=request.user).first()

    if item:
        cart = item.cart  # récupérer le panier associé
        item.delete()     # supprimer l'élément

        # Vérifier si le panier est maintenant vide
        if not cart.cartitem_set.exists():
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
    for item in cart.cartitem_set.all():
        OrderItem.objects.create(
            order=order,
            produit=item.produit,
            details=item.details,
            quantite=item.quantite,
            prix_u=item.prix_u
        )

    # 4. Créer le traitement de suivi de commande
    Traiment.objects.create(
        order=order,
        user=user,
        statut='en_attente'
    )

    # 5. Supprimer panier et items
    cart.cartitem_set.all().delete()
    cart.delete()

    # 5. Rediriger vers la page de confirmation ou liste des commandes
    return redirect('mes_commande')  # à adapter selon ton URL


# # Create your views here.
@login_required
def mes_commande(request):
    commandes = Order.objects.filter(user=request.user).order_by('-created_at')
    current_url = request.get_full_path()
    print(current_url)
    context = {
        'commandes': commandes,
        'current_url':current_url,
    }
    return render(request, 'commandes.html',context)

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
    context = {
        'current_url':current_url,
        'produits':produits_details,
        'totals':commande.get_prix_total,
        'status':commande.get_statut_actuel,
        'order':commande.id
    }
    return render(request, 'detail-commande.html',context)


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


    # Charger le template HTML
    template_path = 'invoice.html'
    context = {'order': order,
               'produits':produits_details,
                'totals':order.get_prix_total,
                'status':order.get_statut_actuel             
               }  # Contexte à passer au template

    # Charger et rendre le template avec le contexte
    template = get_template(template_path)
    html = template.render(context)

    # Créer une réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_DendingIron_{invoice_id}.pdf"'

    # Générer le PDF avec xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    # Gérer les erreurs
    if pisa_status.err:
        return HttpResponse('Une erreur est survenue lors de la génération du PDF', status=500)

    return response


    # return render(request, 'invoice.html')