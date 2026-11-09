from django.shortcuts import render , get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import *
from .form import *
from .models import *
from django.views.generic import ListView
from django import forms
from usesOrders.models import *

from .boulon_ancrage_beton import *
from .cintrages_cadres import *
from .cintrages_extremites_redressage_decoupages import *
from .quincallerie import *
from .cintrages_formes import *
from .etries_toiture_bardage import *
from gestion_prix_fer.models import *
from django.contrib import messages
from .pricing import calculer_prix, PrixInvalide


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
    # ('Etrier pour bardage et toiture','Etrier pour bardage et toiture'),
    # ('boulon d\'ancrage a beton','boulon d\'ancrage a beton'),
    # ('Quincaillerie','Quincaillerie'),
    redressages = Produit.objects.filter(sous_categorie='redressage et decoupage').all().order_by('nom')
    extremites = Produit.objects.filter(sous_categorie='cintrage d\'extremite').all().order_by('nom')
    cadres = Produit.objects.filter(sous_categorie='Cintrage de cadre').all().order_by('nom')
    formes = Produit.objects.filter(sous_categorie='Cintrage de forme').all().order_by('nom')
    etries = Produit.objects.filter(sous_categorie='Etrier pour bardage et toiture').all().order_by('nom')
    boulons = Produit.objects.filter(sous_categorie='boulon d\'ancrage a beton').all().order_by('nom')
    quincailleries = Produit.objects.filter(sous_categorie='Quincaillerie').all().order_by('nom')

    context = {
        'redressages':redressages,
        'extremites':extremites,
        'cadres':cadres,
        'formes':formes,
        'etries':etries,
        'boulons':boulons,
        'quincailleries':quincailleries
    }

    return render(request, 'boutique.html', context)



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

# Correspondance : nom du fournisseur en base (en minuscules) -> valeur du radio marque_fer
MARQUES_FORM = {
    'prometal':   'prometal',
    'autre fer': 'autre fer',
}

def get_tarifs_fer():
    """Retourne tarifs[marque_form][type][diametre] = {'pvf': vente, 'pa': achat}"""
    tarifs = {}
    for fournisseur, types in PrixFer.objects.catalogue().items():
        marque = MARQUES_FORM.get(fournisseur.lower())
        if marque is None:
            continue                      # fournisseur sans radio correspondant
        for type_nom, diametres in types.items():
            for diam, p in diametres.items():
                tarifs.setdefault(marque, {}).setdefault(type_nom.lower(), {})[diam] = {
                    'pvf': p['vente'],
                    'pa':  p['achat'],
                }
    return tarifs

# # @login_required
def detail_produit(request, product_id):
    product = get_object_or_404(Produit, id=product_id)

    # L'ajout au panier exige un compte (la page reste consultable par tous)
    if request.method == "POST" and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())

    # Gabarit universel (application boutique) : seulement si la case « utiliser le
    # gabarit universel » est cochée pour ce produit. Sinon, ancienne page inchangée.
    from boutique.views import config_active, page_produit
    config = config_active(product)
    if config is not None:
        return page_produit(request, product, config)

    template=None
    form=None

    if(product.nom=="cadre carre"):
        form=CarreForm(request.POST or None)
        template="produits/cintrages_cadres/cadre-carre.html"
    
    if(product.nom=="cadre rectangulaire"):
        form=RectangleForm(request.POST or None)
        template="produits/cintrages_cadres/cadre-rectangle.html"
        
    if(product.nom=="cadre hexagonale"):
        form=HexagonaleForm(request.POST or None)
        template="produits/cintrages_cadres/cadre-hexagonale.html"
    
    if(product.nom=="cadre triangulaire"):
        form=TriangleForm(request.POST or None)
        template="produits/cintrages_cadres/cadre-triangulaire.html"
        
    if(product.nom=="forme etrier"):
        form=EtrierForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-etrier.html"
        
    if(product.nom=="forme en T"):
        form=TForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-T.html"
        
    if(product.nom=="forme en T economique"):
        form=TeconoForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-T-economique.html"
        
    if(product.nom=="forme en U"):
        form=UForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-U.html"
        
    if(product.nom=="forme en U ouvert"):
        form=UouvertForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-U-ouvert.html"
        
    if(product.nom=="forme en U ferme"):
        form=UfermeForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-U-ferme.html"
        
    if(product.nom=="forme pince"):
        form=PinceForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-pince.html"
        
    if(product.nom=="forme crochet"):
        form=CrochetForm(request.POST or None)
        template="produits/cintrages_formes/cintrage-crochet.html"
        
    #redressage et decoupage
    if(product.nom=="barre droite"):
        form=BarreDroiteForm(request.POST or None)
        template="produits/cintrages_extremites_redressage_et_decoupages/barre-droite.html"
    
    #Cintrage
    if(product.nom=="barre coude a une extremite"):
        form=BarreCouUneExForm(request.POST or None)
        template="produits/cintrages_extremites_redressage_et_decoupages/barre-coude-a-une-extremite.html"
    
    if(product.nom=="barre coude aux deux extremites"):
        form=BarreCouDeuxExForm(request.POST or None)
        template="produits/cintrages_extremites_redressage_et_decoupages/barre-coude-aux-deux-extremite.html"
    
    #pour les bardages et toitures
    if(product.nom=="etrier a fond circulaire"):
        form=EtrierFondRondForm(request.POST or None)
        template="produits/Etriers_pour_badages_et_toitures/etrier-fond-circulaire.html"
        
    if(product.nom=="etrier a une seul branche a fond circulaire"):
        form=EtrierUnPiedFondRondForm(request.POST or None)
        template="produits/Etriers_pour_badages_et_toitures/etrier-une-branche-fond-circulaire.html"
        
    if(product.nom=="etrier a fond droit"):
        form=EtrierFondDroitForm(request.POST or None)
        template="produits/Etriers_pour_badages_et_toitures/etrier-fond-droit.html"
        
    if(product.nom=="etrier a une seul branche a fond droit"):
        form=EtrierFondDroitUneBrancheForm(request.POST or None)
        template="produits/Etriers_pour_badages_et_toitures/etrier-une-branche-fond-droit.html"
        
    if(product.nom=="etrier a fond triangulaire"):
        form=EtrierFondDroitForm(request.POST or None)
        template="produits/Etriers_pour_badages_et_toitures/etrier-fond-triangulaire.html"
        
    if(product.nom=="Ancrage forme J"):
        form=AncrageJForm(request.POST or None)
        template="produits/Boulon_ancrage_beton/ancrage-forme-J.html"
    
    if(product.nom=="Ancrage forme L"):
        form=AncrageJForm(request.POST or None)
        template="produits/Boulon_ancrage_beton/ancrage-forme-L.html"
    
    if(product.nom=="Ancrage simple"):
        form=AncrageJForm(request.POST or None)
        template="produits/Boulon_ancrage_beton/ancrage-simple.html"
    
    if(product.nom=="Ancrage en forme de crosse"):
        form=AncrageCrossForm(request.POST or None)
        template="produits/Boulon_ancrage_beton/ancrage-forme-crosse.html"
        
    if(product.nom=="Ancrage en forme de crochet"):
        form=AncrageCrossForm(request.POST or None)
        template="produits/Boulon_ancrage_beton/ancrage-forme-crochet.html"
    
    if(product.nom=="Ancrage en forme de crochet à double cambrure"):
        form=AncrageCrossForm(request.POST or None)
        template="produits/Boulon_ancrage_beton/ancrage-crochet-double-cambrure.html"
    
 #print(product.nom)
    if(product.nom=="Ecrou hexagonale"):
        form=EcrouForm(request.POST or None)
        template="produits/Quincallerie/ecrou.html"
        
    #print(product.nom)
    if(product.nom=="fer a beton de 12m"):
        form=FerABetonForm(request.POST or None)
        template="produits/Quincallerie/quincaillerie.html"
        
    #print(product.nom)
    if(product.nom=="fil d'attache"):
       form=FilForm(request.POST or None)
       template="produits/Quincallerie/file-attache.html"
       
    #print(product.nom)
    if(product.nom=="rondelle plate"):
       form=EcrouForm(request.POST or None)
       template="produits/Quincallerie/rondelle.html"
       

    # Vérifier si le formulaire a été soumis
    if request.method == "POST" and form and form.is_valid():
        datas = form.cleaned_data
        quantite = int(datas.get('quantite', 1))
        details = {k: v for k, v in datas.items() if k not in ['prix', 'quantite', 'prix_revient', 'prix_Total']}

        # Le prix est recalculé par le serveur : les valeurs envoyées par le navigateur sont ignorées
        prix = prix_revient = None
        try:
            resultat = calculer_prix(product, datas)
            if resultat is not None:
                prix, prix_revient = resultat.prix_u, resultat.prix_revient
                details.update(resultat.details)
            else:
                # Produit pas encore porté dans produits/pricing.py : ancien comportement,
                # avec un contrôle minimal (voir README_SECURITE.md)
                prix, prix_revient = datas.get('prix'), datas.get('prix_revient')
                if not prix or prix <= 0 or prix_revient is None or prix_revient < 0:
                    raise PrixInvalide("Prix invalide.")
        except PrixInvalide as e:
            messages.error(request, str(e))
        else:
            # Obtenir ou créer le panier de l'utilisateur
            cart, created = Cart.objects.get_or_create(user=request.user)

            # Même produit avec les mêmes détails déjà dans le panier ?
            existing_item = CartItem.objects.filter(cart=cart, produit=product, details=details).first()
            if existing_item:
                existing_item.quantite += quantite
                existing_item.save()
            else:
                CartItem.objects.create(
                    cart=cart,
                    produit=product,
                    details=details,
                    quantite=quantite,
                    prix_u=prix,
                    prix_revient=prix_revient,
                )
            return redirect('panier')

    current_url = '/produits/'
    return render(request, template, {
        'product': product,
        'form': form,
        'current_url':current_url,
        'tarifs': get_tarifs_fer(),
        'constantes': Constante.toutes(),
    })

