from django.shortcuts import render , get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from .form import *
from .models import *
from django.views.generic import ListView
from django import forms
from usesOrders.models import *



def get_produit_solution(request):
      current_url = request.get_full_path()
      context = {
           'current_url': current_url
      }
      return render(request, 'presentation-produit.html', context)

# affichage des categorie
# def get_boutique(request):
#     categories = Categorie.objects.all()
#     current_url = request.get_full_path()
#     context = {
#            'current_url': current_url
#       }
#     return render(request, 'boutique/categorie.html', context)

# Create your views here.
def all_produit(request):
    sous_categories = (
        Produit.objects
        .filter(sous_categorie__isnull=False)
        .values_list('sous_categorie', flat=True)
        .distinct()
    )

    # Dictionnaire { "sous_categorie": [produits] }
    produits_groupes = {
        sc: Produit.objects.filter(sous_categorie=sc)
        for sc in sous_categories
    }

    return render(request, 'boutique.html', {
        'produits_groupes': produits_groupes
    })
# class ListCategorie(ListView):
#     model=Categorie
#     context_object_name = 'categories'
#     template_name = "boutique/categorie.html"

#     def get_context_data(self, **kwargs):
#       context = super().get_context_data(**kwargs)
#       context['current_url'] = self.request.path
#       return context 

def get_sous_categorie(request, categorie_id):
    current_url = request.get_full_path()
    categorie_name= Categorie.objects.filter(id=categorie_id).first()
    #verifier si la categorie a des sous categories
    produit = Produit.objects.filter(categorie=categorie_id).first()

    #verifier si la categorie a des sous categories
    if produit.sous_categorie :
        '''retourne la sous categories'''
        is_true=True
        produits = Produit.objects.filter(categorie=categorie_id).all()
    else :
        '''retourne diretectement les produis'''
        is_true=False
        produits = Produit.objects.filter(categorie=categorie_id).all()

    context = {
           'current_url': current_url,
           'produits' : produits,
           'categorie' : categorie_name,
           'is_true' : is_true,
    }
    return render(request, 'boutique/sous-categorie.html', context)

def get_produit(request, produit_id):
    current_url = request.get_full_path()
    is_true=False
    produit = Produit.objects.filter(id=produit_id).first()
    categorie_name = produit.sous_categorie
    produits = Produit.objects.filter(sous_categorie=produit.sous_categorie).all()
    context = {
           'current_url': current_url,
           'produits' : produits,
           'categorie' : categorie_name,
           'is_true' : is_true,
    }
    return render(request, 'boutique/sous-categorie.html', context)


# # @login_required
def detail_produit(request, product_id):
    product = get_object_or_404(Produit, id=product_id)
    template=None
    form=None

    if(product.nom=="cadre carre"):
        form=CarreForm(request.POST or None)
        template="produits/cadre-carre.html"
    
    if(product.nom=="cadre rectangle"):
        form=RectangleForm(request.POST or None)
        template="produits/cadre-rectangle.html"
        
    if(product.nom=="cadre hexagonale"):
        form=HexagonaleForm(request.POST or None)
        template="produits/cadre-hexagonale.html"
    
    if(product.nom=="cadre triangulaire"):
        form=TriangleForm(request.POST or None)
        template="produits/cadre-triangulaire.html"
        
    if(product.nom=="cintrage de l'etrier"):
        form=EtrierForm(request.POST or None)
        template="produits/cintrage-etrier.html"
        
    if(product.nom=="cintrage en T"):
        form=TForm(request.POST or None)
        template="produits/cintrage-T.html"
        
    if(product.nom=="cintrage en T economique"):
        form=TeconoForm(request.POST or None)
        template="produits/cintrage-T-economique.html"
        
    if(product.nom=="cintrage en U"):
        form=UForm(request.POST or None)
        template="produits/cintrage-U.html"
        
    if(product.nom=="cintrage en U ouvert"):
        form=UouvertForm(request.POST or None)
        template="produits/cintrage-U-ouvert.html"
        
    if(product.nom=="cintrage en U ferme"):
        form=UfermeForm(request.POST or None)
        template="produits/cintrage-U-ferme.html"
        
    if(product.nom=="cintrage de la pince"):
        form=PinceForm(request.POST or None)
        template="produits/cintrage-pince.html"
        
    if(product.nom=="cintrage du crochet"):
        form=CrochetForm(request.POST or None)
        template="produits/cintrage-crochet.html"
        
    #redressage et decoupage
    if(product.nom=="barre droite"):
        form=BarreDroiteForm(request.POST or None)
        template="produits/barre-droite.html"
    
    #Cintrage
    if(product.nom=="barre coude a une extremite"):
        form=BarreCouUneExForm(request.POST or None)
        template="produits/barre-coude-a-une-extremite.html"
    
    if(product.nom=="barre coude aux deux extremites"):
        form=BarreCouDeuxExForm(request.POST or None)
        template="produits/barre-coude-aux-deux-extremite.html"
    
    #pour les bardages et toitures
    if(product.nom=="etrier a fond circulaire"):
        form=EtrierFondRondForm(request.POST or None)
        template="produits/etrier-fond-circulaire.html"
        
    if(product.nom=="etrier a une seul branche a fond circulaire"):
        form=EtrierFondRondForm(request.POST or None)
        template="produits/etrier-une-branche-fond-circulaire.html"
        
    if(product.nom=="etrier a fond droit"):
        form=EtrierFondRondForm(request.POST or None)
        template="produits/etrier-fond-droit.html"
        
    if(product.nom=="etrier a une seul branche a fond droit"):
        form=EtrierFondRondForm(request.POST or None)
        template="produits/etrier-une-branche-fond-droit.html"
        
    if(product.nom=="etrier a fond triangulaire"):
        form=EtrierFondRondForm(request.POST or None)
        template="produits/etrier-fond-triangulaire.html"
        
    if(product.nom=="Ancrage forme J"):
        form=AncrageJForm(request.POST or None)
        template="produits/ancrage-forme-J.html"
    
    if(product.nom=="Ancrage forme L"):
        form=AncrageJForm(request.POST or None)
        template="produits/ancrage-forme-L.html"
    
    if(product.nom=="Ancrage simple"):
        form=AncrageJForm(request.POST or None)
        template="produits/ancrage-simple.html"
    
    if(product.nom=="Ancrage en forme de crosse"):
        form=AncrageCrossForm(request.POST or None)
        template="produits/ancrage-forme-crosse.html"
        
    if(product.nom=="Ancrage en forme de crochet"):
        form=AncrageCrossForm(request.POST or None)
        template="produits/ancrage-forme-crochet.html"
    
    if(product.nom=="Ancrage en forme de crochet à double cambrure"):
        form=AncrageCrossForm(request.POST or None)
        template="produits/ancrage-crochet-double-cambrure.html"
    
 #print(product.nom)
    if(product.nom=="Ecrou hexagonale"):
        form=EcrouForm(request.POST or None)
        template="produits/ecrou.html"
        
    #print(product.nom)
    if(product.nom=="fer a beton de 12m"):
        form=FerABetonForm(request.POST or None)
        template="produits/quincaillerie.html"
        
    #print(product.nom)
    if(product.nom=="fil d'attache"):
       form=FilForm(request.POST or None)
       template="produits/file-attache.html"
       
    #print(product.nom)
    if(product.nom=="rondelle plate"):
       form=EcrouForm(request.POST or None)
       template="produits/rondelle.html"
       
    
    # if(product.name=="cadre triangulaire"):
    #     form=TriangleForm(request.POST or None)
    #     template="triangle.html"
    
    # if(product.name=="cadre en pince"):
    #     form=PinceForm(request.POST or None)
    #     template="pince.html"
    
    # if(product.name=="cadre en t"):
    #     form=TForm(request.POST or None)
    #     template="t.html"
    
    # if(product.name=="cadre en u"):
        # form = UForm(request.POST or None)
        # template="u.html"
    
     # Vérifier si le formulaire a été soumis
    if request.method == "POST" and form:
        # form = form.__class__(request.POST)  # Recharger le formulaire avec les données POST
        if form.is_valid():
             # 1. Récupérer les données du formulaire
            datas = form.cleaned_data
            quantite =datas.get('quantite', 1)
            prix =datas['prix']  # prix unitaire
            details = {k: v for k, v in form.cleaned_data.items() if k not in ['quantite', 'prix']}
            # 2. Obtenir ou créer le panier de l'utilisateur
            cart, created = Cart.objects.get_or_create(user=request.user)

            # 3. Vérifier si le produit avec les mêmes détails existe déjà dans le panier
            existing_item = CartItem.objects.filter(
                cart=cart,
                produit=product,
                details=details  # doit matcher exactement le JSON
            ).first()

            if existing_item:
                # Mettre à jour la quantité si le produit existe déjà
                existing_item.quantite += quantite
                existing_item.save()
            else:
                # Créer une nouvelle ligne de produit dans le panier
                CartItem.objects.create(
                    cart=cart,
                    produit=product,
                    details=details,
                    quantite=quantite,
                    prix_u=prix
                )
            # Rediriger l'utilisateur vers la page du panier
            return redirect('panier') 
        else:
            print("Formulaire invalide!")  # Ajoutez ceci pour vérifier
            print(form.errors) # Remplacez par l'URL de votre page panier
    current_url = '/produits/'
    return render(request, template, {
        'product': product,
        'form': form,
        'current_url':current_url,
    })

