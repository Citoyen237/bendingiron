from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView
import os
from datetime import datetime
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from contact.form import *
from usesOrders.models import *
from fer.models import *
from fer.form import *
from produits.models import *
from produits.form import *
from contact.models import *
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from auth_app.models import *
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.views.generic import TemplateView
from django.db.models.functions import Coalesce
from django.http import FileResponse, Http404
from partenaires.models import *
from partenaires.form import *
from django.urls import reverse_lazy
from collections import defaultdict
from auth_app.utils import *
from usesOrders.form import *
import random
import string
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from proforma.models import *
from django.views.decorators.http import require_POST
from proforma.form import *


# Les règles d'accès sont centralisées dans auth_app/permissions.py
from auth_app.permissions import (
    AdminOrSuperAdminRequiredMixin, AdminRequiredMixin, admin_required,
    superadmin_required, is_admin, is_superadmin,
)
from django.db import transaction

from decimal import Decimal
from django.db.models import OuterRef, Subquery
from usesOrders import annulation as annulation_cmd

def montant_total_ventes_terminees():
    # Dernier statut par commande
    dernier_statut = Traiment.objects.filter(
    order=OuterRef("pk")
     ).order_by("-created_at").values("statut")[:1]

     # Filtrer seulement les orders terminés
    orders_terminees = Order.objects.annotate(
    dernier_statut=Subquery(dernier_statut)
    ).filter(dernier_statut="termine")
     # Calcul du montant total
    return sum(order.net_payer for order in orders_terminees)

def montant_total_revenue():
    # Dernier statut par commande
    dernier_statut = Traiment.objects.filter(
    order=OuterRef("pk")
     ).order_by("-created_at").values("statut")[:1]
     # Filtrer seulement les orders terminés
    orders_terminees = Order.objects.annotate(
    dernier_statut=Subquery(dernier_statut)
    ).filter(dernier_statut="termine")
     # Calcul du montant total
    return sum(order.prix_revient_total for order in orders_terminees)
@admin_required
def indexA(request):
    total_vente_client = montant_total_ventes_terminees()
    montant_total_revenue_client = montant_total_revenue() 
    total_projet = Projet.montant_total_projets_solde()
    # benefice_total=Projet.benefice()

    orders = Order.objects.order_by('-created_at')[:5]
    projets = Projet.objects.order_by('-created_at')[:5]
    users = User.objects.all()
    distributeurs = CodePromo.objects.all()
    valid_count = sum(1 for code in distributeurs if not code.is_expired)  # nombre valides
    userStaff=User.objects.filter(is_staff=1)
    partenaires=Partenariats.objects.all()
    valid_partenaires = sum(1 for code in partenaires if not code.is_expired)  # en cours
    produits = Produit.objects.all()
    fersRouleau = Fer.objects.filter(categorie="rouleau")
    fersBarre = Fer.objects.filter(categorie="barre")

    projetOrders = ProjetOrder.objects.order_by('-created_at')[:5]
    context = {
        'orders':orders,
        'projets':projets,
        'projetsOrders':projetOrders,
        'users':users,
        'userStaff':userStaff,
        'distributeurs':distributeurs,
        "valid_count": valid_count,
        'partenaires':partenaires,
        'valid_partenaires':valid_partenaires,
        'produits':produits,
        'fersRouleau':fersRouleau,
        'fersBarre':fersBarre,
        'total_vente_client':total_vente_client,
        'montant_total_revenue_client':montant_total_revenue_client,
        'total_projet':total_projet,
        # 'benefice_total':benefice_total
    }
    return render(request, 'indexA.html', context)


# produits en stock
class ListProduits(AdminRequiredMixin, ListView):
    model=Produit
    context_object_name = 'produits'
    template_name = "stocks/list.html"
# stock gestion du fer
class ListFer(AdminRequiredMixin, ListView):
    model=Fer
    context_object_name = 'fers'
    template_name = "fer/list.html"

class CreateFer(AdminRequiredMixin, CreateView):
   model = Fer
   form_class = FerForm
   template_name = "fer/create.html"
   success_url="../stocks/"

   def form_valid(self, form):
        form.instance.user = self.request.user  # 👤 lier l'utilisateur connecté
        response = super().form_valid(form)
        messages.success(self.request, "Fer ajouté avec succès !")
        return response
 
@admin_required
def get_suivis(request, fer_id):
    fer=get_object_or_404(Fer, id=fer_id)
    mouvements = Mouvement.objects.filter(fer=fer_id).order_by('-date')
    context = {
        'mouvements': mouvements,
        'fer':fer
     }
    return render(request, "fer/suivis.html", context)

class ListMouvement(AdminRequiredMixin, ListView):
    model=Mouvement
    context_object_name = 'mouvements'
    template_name = "fer/mouvement.html"
   
class CreateMouvement(AdminRequiredMixin, CreateView):
   model = Mouvement
   form_class = MouvementForm
   template_name = "fer/new-entrer.html"
   success_url="../mouvements"

   def form_valid(self, form):
        form.instance.user = self.request.user  # 👤 lier l'utilisateur connecté
        response = super().form_valid(form)
        messages.success(self.request, "Entree effectue succès !")
        return response
   
# contact
class ListMessage(AdminOrSuperAdminRequiredMixin,ListView):
    model=Contact
    context_object_name = 'messages'
    template_name = "contact/list.html"

    def get_queryset(self):
        # Trier par date de création croissante (plus ancien au plus récent)
      return Contact.objects.order_by('-created_at')

# contact
@admin_required
def mark_message_as_read(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    message.is_read = 1
    message.save()
    return redirect('contact.list')

@admin_required
def send_response(request, message_id):
   message=get_object_or_404(Contact, id=message_id)
   message.is_read = True
   message.save()
   current_url = request.get_full_path()
   if request.method == 'POST':
      form = ReponseForm(request.POST,request.FILES,instance=message, )
      if form.is_valid():
         response = form.cleaned_data['reponse']
        #  file_response = form.cleaned_data['file_response']
         message.is_read = 1
         message.reponse=response
         form.save()
         messages.success(request, 'Votre reponse a ete envoyer succès.')
        #  send_mail(
        #         'Réponse à votre message',
        #         f'Vous: {message.message}\n\nbendingironinfo@gmail.com: {response}',  
        #         settings.DEFAULT_FROM_EMAIL,# From email
        #         [message.email],  # To email
        #         fail_silently=False,
        #     )

         file_path = os.path.join('medias', message.file_response.path)

         email = EmailMessage(
            subject='Réponse à votre message',
            body=f'Vous: {message.message}\n\nbending.info@gmail.com\n: {response}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[message.email],
            )

        # # Joindre le fichier
         email.attach_file(file_path)

        # # Envoyer le mail
         email.send(fail_silently=False)

         return redirect('contact.list')   
      else :
         context ={
         'current_url':current_url,
         'message':message,
         'form':form,
          }
         return render(request, 'contact/reponse.html', context)
   else:
      form = ReponseForm()
      context ={
            'current_url':current_url,
            'message':message,
            'form':form,
         }
      return render(request, 'contact/reponse.html', context)

class DeleteMessage(AdminRequiredMixin, DeleteView):
   model = Contact
   template_name = "contact/delete.html"
   success_url="../../contact"

   def delete(self, request, *args, **kwargs):
      response = super().delete(request, *args, **kwargs)
      message = messages.success(self.request, "Le message a été supprimé avec succès")
      reponses = [response,message]
      return reponses

def _servir_pdf(fichier):
    if not fichier:
        raise Http404("Aucun fichier.")
    try:
        return FileResponse(fichier.open('rb'), content_type='application/pdf',
                            filename=fichier.name.rsplit('/', 1)[-1])
    except FileNotFoundError:
        raise Http404("Fichier introuvable sur le serveur.")

@admin_required
def read_devis(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    return _servir_pdf(message.file)

@admin_required
def read_devis_response(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    return _servir_pdf(message.file_response)

# users

# Mixin pour vérifier si l'utilisateur est un superadmin
class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
class ListUser(AdminOrSuperAdminRequiredMixin,ListView):
    model=CustomUser
    context_object_name = 'users'
    template_name = "users/list.html"

# Vérifier si l'utilisateur connecté est superadmin
@require_POST
@admin_required
def toggle_user_status(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.pk == request.user.pk:
            messages.error(request, "Vous ne pouvez pas bloquer votre propre compte.")
            return redirect('user.list')
        if is_superadmin(user) and not is_superadmin(request.user):
            messages.error(request, "Seul un superadmin peut bloquer un autre superadmin.")
            return redirect('user.list')
        objet = ""
        template = ""
        if user.is_active:
            # Bloquer l'utilisateur
            user.is_active = 0
            # status_message = "Votre compte chez a été bloqué."
            admin_message = f"L'utilisateur {user.first_name} a été bloqué."
            template = 'users/mail_bloque.html'
            objet = "Votre compte a été temporairement bloqué."
        else:
            # Débloquer l'utilisateur
            user.is_active = 1
            # status_message = "Votre compte a été réactivé."
            admin_message = f"L'utilisateur {user.first_name} a été débloqué."
            template = 'users/mail_debloque.html'
            objet = "Votre compte a été réactivé"
        
        # Sauvegarder le changement
        user.save()

        # Envoyer l'email
        context = {'user': user}
        send_custom_email(
            objet,
            template,
            context,
            [user.email]
        )
        # subject=objet,
        #     message=f"Bonjour {user.first_name},\n\n{status_message}\n\nCordialement, L'équipe DFMAC.",
        #     from_email=settings.DEFAULT_FROM_EMAIL,  # Remplacez par votre adresse d'expéditeur
        #     recipient_list=[user.email],
        #     fail_silently=False,
        # Message de confirmation pour l'admin
        messages.success(request, admin_message)
    except CustomUser.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    return redirect('user.list')  # Redirigez vers la liste des utilisateurs

ROLES_AUTORISES = ('simple', 'partenaire', 'admin', 'superadmin')

@require_POST
@admin_required
def change_user_role(request, user_id, group_name):
    if group_name not in ROLES_AUTORISES:
        messages.error(request, "Rôle inconnu.")
        return redirect('user.list')
    if user_id == request.user.id:
        messages.error(request, "Vous ne pouvez pas modifier votre propre rôle.")
        return redirect('user.list')
    try:
        # Trouver l'utilisateur par ID
        user = CustomUser.objects.get(id=user_id)
        touche_un_role_admin = group_name in ('admin', 'superadmin') or is_admin(user)
        if touche_un_role_admin and not is_superadmin(request.user):
            messages.error(request, "Seul un superadmin peut attribuer ou retirer un rôle d'administrateur.")
            return redirect('user.list')
        if group_name == 'partenaire' : 
            user.is_partenaire = 1
        else :
        # Trouver le groupe auquel vous voulez assigner l'utilisateur
            group = Group.objects.get(name=group_name)

            if group_name == 'admin':
                user.is_staff = 1
                user.is_superuser = 0

            if group_name == 'superadmin': 
                user.is_superuser = 1
                user.is_staff = 1
            
            if group_name == 'simple': 
                user.is_superuser = 0
                user.is_staff = 0
                                
            # Changer le rôle de l'utilisateur
            user.groups.clear()  # Efface les groupes existants
            user.groups.add(group)  # Assigne le nouvel groupe
            messages.success(request, f"Le rôle de {user.username} a été changé avec succès en {group.name}.")


        user.save()

    except CustomUser.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    except Group.DoesNotExist:
        messages.error(request, "Groupe introuvable.")

    return redirect('user.list')  # Redirigez vers la liste des utilisateurs ou ailleurs

# orderUser
class ListOrder(AdminOrSuperAdminRequiredMixin,ListView):
   model=Order
   context_object_name = 'orders'
   template_name = 'order/list.html'

   def get_queryset(self):
        # Récupérer les commandes de l'utilisateur connecté, triées par date de création décroissante
        return Order.objects.order_by('-created_at')

@admin_required
def detail_commande(request, order_id):
     # Récupérer la commande avec son ID
    commande = get_object_or_404(Order, id=order_id)

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
    context = {
        'produits':produits_details,
        'totals':commande.get_prix_total,
        'status':commande.get_statut_actuel,
        'orderId':commande.id,
        'order':commande
    }
    context.update(annulation_cmd.contexte("client", commande))
    return render(request, 'order/detail.html',context)

@admin_required
def suivis_commande(request, order_id):
    commande = get_object_or_404(Order, id=order_id)
    traitements = Traiment.objects.filter(order=order_id).order_by('-created_at')
    context = {
        'traitements':traitements,
        'order':commande
    }
    return render(request, 'order/suivis.html',context)

@require_POST
@admin_required
def change_statut(request, order_id):
   user=request.user
    #   Récupérer l'objet
   order = get_object_or_404(Order, id=order_id)
   if order.get_statut_actuel == annulation_cmd.ANNULE:
      messages.error(request, "Commande annulée : son statut ne change plus.")
      return redirect('order.detail', order.id)
   new_status=order.get_statut_actuel
  
   if (order.get_statut_actuel == "en_attente" ):
      new_status = "en_production"
   elif (order.get_statut_actuel == "en_production" ):
      new_status = "pret_pour_livraison"
   if (order.get_statut_actuel == "pret_pour_livraison" ):
      new_status = "solde_facture"
   elif (order.get_statut_actuel == "solde_facture" ):
      new_status = "termine"
   elif (order.get_statut_actuel == "termine" ):
      new_status = "termine"
   Traiment.objects.create(
        order=order,
        user=user,
        statut=new_status
    )
   template="mail-statut.html"
   objet="le statut de votre commande"
   context = {
       'user': user,
       'order':order
              }
   send_custom_email(
            objet,
            template,
            context,
            [order.user.email]
    )
    #   Rediriger (par exemple, vers la page des commandes)
   return redirect('order.list')  # Modifie selon le nom de ta vue cible


# partenariats
class ListPartenariats(AdminRequiredMixin, ListView):
    model=Partenariats
    context_object_name = 'partenariats'
    template_name = "partenaires/partenariats.html"

class CreatePartenariat(AdminOrSuperAdminRequiredMixin, CreateView):
   model = Partenariats
   form_class = ParteriatForm
   template_name = "partenaires/create.html"
   success_url=".."

   def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Fer ajouté avec succès !")
        return response

class UpdatePartenriat(AdminOrSuperAdminRequiredMixin, UpdateView):
    model = Partenariats
    form_class = ParteriatForm
    template_name = 'partenaires/update.html'  # ou ton chemin réel
    success_url = reverse_lazy('partenariat.list')

class ListProjets(AdminOrSuperAdminRequiredMixin, ListView):
    model=Projet
    context_object_name = 'projets'
    template_name = "partenaires/projet.html"

@admin_required
def get_detail_partenariat(request, partenariat_id):
    partenariat = get_object_or_404(Partenariats, id=partenariat_id)
    projets=Projet.objects.filter(partenariat=partenariat_id)
    context = {
        'partenariat': partenariat,
        'projets':projets

    }
    return render(request, 'partenaires/detail-partenariat.html',context)

@admin_required
def get_detail_projet(request, projet_id):
     # Récupérer la commande avec son ID
    projet = get_object_or_404(Projet, id=projet_id)

     # Récupérer les produits associés à ce projet
    produits = ProjetItem.objects.filter(projet=projet_id)

    
    if request.method == 'POST':
        form = PaiementProjetForm(request.POST, projet=projet)
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.user = request.user  # on attribue l'admin qui enregistre
            paiement.save()
            messages.success(request, f"Tranche {paiement.tranche} enregistrée : {paiement.montant} FCFA.")
            # Redirection : un rafraîchissement de la page ne renvoie pas le paiement
            return redirect(request.path)
    else :
        form = PaiementProjetForm(projet=projet)

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
    'form':form,
    # 'status':commande.get_statut_actuel,
    'projet':projet
    }
    return render(request,'partenaires/detail-projet.html', context)

@admin_required
def get_commandes(request):
    orders = ProjetOrder.objects.order_by('-created_at')
    context = {
        'orders': orders
    }
    return render(request, "partenaires/order.html", context)

@admin_required
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
    context.update(annulation_cmd.contexte("projet", commande))
    return render(request, "partenaires/detail-order.html", context)

@require_POST
@admin_required
def change_statut_order(request, order_id):
    user=request.user
    #   Récupérer l'objet
    order = get_object_or_404(ProjetOrder, id=order_id)
    if order.get_statut_actuel == annulation_cmd.ANNULE:
        messages.error(request, "Commande annulée : son statut ne change plus.")
        return redirect('partenariat.orders.details', order.id)
    new_status=order.get_statut_actuel
 
    if (order.get_statut_actuel == "en_attente" ):
      new_status = "en_production"
    elif (order.get_statut_actuel == "en_production" ):
      new_status = "pret_pour_livraison"
    if (order.get_statut_actuel == "pret_pour_livraison" ):
      new_status = "termine"
    elif (order.get_statut_actuel == "termine" ):
      new_status = "termine"
        # Mettre à jour le statut
    TraimentOrder.objects.create(
            projet_order=order,
            user=user,
            statut=new_status
        )
    userIn = order.projet.partenariat.user
    template="mail-statut.html"
    objet="le statut de votre demande de livraison partielle"
    context = {
       'user': userIn,
       'order':order
              }
    send_custom_email(
            objet,
            template,
            context,
            [order.projet.partenariat.user.email]
    )
    #   Rediriger (par exemple, vers la page des commandes)
    return redirect('partenariat.orders')  # Modifie selon le nom de ta vue cible 

@admin_required
def suivis_order(request, order_id):
    commande = get_object_or_404(ProjetOrder, id=order_id)
    traitements = TraimentOrder.objects.filter(projet_order=order_id).order_by('-created_at')
    context = {
        'traitements':traitements,
        'order':commande
    }
    return render(request, 'partenaires/suivis-order.html',context)

@admin_required
def historique_projet(request, projet_id):
    projet = get_object_or_404(Projet, id=projet_id)
    orders = ProjetOrder.objects.filter(projet=projet_id).order_by('-created_at')
    paiements =PaiementProjet.objects.filter(projet=projet_id).all() 
    context = {
        'orders':orders,
        'projet':projet,
        'paiements':paiements
    }
    return render(request, 'partenaires/historique.html',context)

SUIVANT_ADD = {
    "en_attente": "en_production",
    "en_production": "pret_pour_livraison",
    "pret_pour_livraison": "termine",
    "termine": "termine",
}

@require_POST
@admin_required
def change_statut_order_add(request, order_id):
    order = get_object_or_404(OrderAdd, id=order_id)
    if order.get_statut_actuel == annulation_cmd.ANNULE:
        messages.error(request, "Commande annulée : son statut ne change plus.")
        return redirect('partenariat.detail.order.additional', order.id)
    nouveau = SUIVANT_ADD.get(order.get_statut_actuel, "en_attente")
    TraimentAdd.objects.create(order=order, user=request.user, statut=nouveau)
    messages.success(request, "Statut mis à jour.")
    return redirect('partenariat.detail.order.additional', order.id)

@admin_required
def get_detail_order_additional(request, order_id):
     # Récupérer la commande avec son ID
    commande = get_object_or_404(OrderAdd, id=order_id)

    # Récupérer les produits associés à cette commande
    produits = OrderItemAdd.objects.filter(order=commande)

    with transaction.atomic():
        order = get_object_or_404(OrderAdd.objects.select_for_update(), id=order_id)
        form = PaymentAddForm(request.POST or None, order=order)

        if request.method == "POST" and order.get_statut_actuel == annulation_cmd.ANNULE:
            messages.error(request, "Commande annulée : aucun paiement ne peut être enregistré.")
            return redirect(request.path)
        if request.method == "POST" and form.is_valid():
            paiement = form.save(commit=False)
            paiement.order = order
            paiement.user = request.user
            paiement.mode_paid = form.cleaned_data["mode_paid"]
            paiement.save()
            messages.success(request, "Paiement enregistré.")
            return redirect(request.path)
            #return redirect("detail.proforma", order=order_id)

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
    context = {
        'produits':produits_details,
        'totals':commande.get_prix_total,
        'status':commande.get_statut_actuel,
        'orderId':commande.id,
        'order':commande,
        'form':form
    }
    context.update(annulation_cmd.contexte("additionnel", commande))
    return render(request, 'partenaires/detail-commande-additional.html',context)

class ListCodeRevendeur(AdminRequiredMixin, ListView):
    model=CodePromo
    context_object_name = 'codes'
    template_name = "codepromo/list.html"

def generate_random_code(length=8):
    """Code distributeur imprévisible (module secrets, et non random)."""
    import secrets
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))
        if not CodePromo.objects.filter(code=code).exists():
            return code

@admin_required
def add_distributeur(request):
    if request.method == "POST":
        form=DistributeurForm(request.POST)
        if form.is_valid():
            user = request.user
            code =generate_random_code()
            CodePromo.objects.create(
                user=user,
                client =form.cleaned_data.get('client'),
                remise=form.cleaned_data.get('remise'),
                code=code,
                nb_utilidation=form.cleaned_data.get('nb_utilidation'),
                expiration =form.cleaned_data.get('expiration')
            )
            messages.success(request, f'le code ce distributeur est {code}!')
            return redirect('code.revendeur')
    else :
        form=DistributeurForm()

    return render(request, "codepromo/create.html", {'form':form})


@admin_required
def get_portefeuille_client(request):
    users=CustomUser.objects.all()
    context = {
        'users':users
    }
    return render(request, 'order/porte-feuille-client.html', context)

@admin_required
def get_order_user(request, id_user):
    orders=Order.objects.filter(user=id_user).all()
    user=get_object_or_404(CustomUser, id=id_user)
    context = {
     'orders':orders,
     'user':user
    }
    return render(request, 'order/order-client.html', context)

@admin_required
def get_portefeuille_partenaire(request):
    partenariats = Partenariats.objects.all()
    context = {
       'partenariats':partenariats,
    }
    return render(request, 'partenaires/portefeuille.html', context)


@admin_required
def get_order_additional(request):
    orders = OrderAdd.objects.order_by('created_at')
    context = {
        'orders': orders
    }
    return render(request, "partenaires/list-order-additional.html", context)

STATUTS_TRAVAUX = {
    "en_attente": ("En attente", "bg-warning text-dark"),
    "en_production": ("En production", "bg-primary"),
    "pret_pour_livraison": ("Prêt pour livraison", "bg-info text-dark"),
    "termine": ("Livraison terminée", "bg-success"),
    "annule": ("Annulée", "bg-danger"),
}


@admin_required
def get_order_additional_projet(request, projet_id):
    """Travaux additionnels d'UN projet (avant : filtrait par numéro de commande = numéro de projet)."""
    projet = get_object_or_404(Projet, id=projet_id)
    commandes = (OrderAdd.objects.filter(projet_order=projet).order_by("-created_at")
                 .prefetch_related("orderitemadd_set", "payments_add", "traimentadd_set"))
    lignes = []
    for commande in commandes:
        net, paye = commande.net_payer, commande.total_paye
        statut = commande.get_statut_actuel
        libelle, couleur = STATUTS_TRAVAUX.get(statut, ("Aucun traitement", "bg-secondary"))
        lignes.append({"commande": commande, "net": net, "paye": paye, "reste": commande.reste_a_payer,
                       "articles": commande.orderitemadd_set.count(),
                       "statut": libelle, "couleur": couleur})
    context = {
        "projet": projet,
        "lignes": lignes,
        "total_net": sum(l["net"] for l in lignes),
        "total_paye": sum(l["paye"] for l in lignes),
        "total_reste": sum(l["reste"] for l in lignes),
    }
    return render(request, "partenaires/travaux-add-projet.html", context)
#proforma
@admin_required
def get_order_pro(request):
    commandes = OrderPro.objects.filter(user=request.user).order_by('-created_at')
    current_url = request.get_full_path()
    context = {
        'orders': commandes,
        'current_url':current_url,
    }
    return render(request, 'proforma/liste-commande-pro.html',context)

@admin_required
def detail_order_pro(request, order_id):
     # Récupérer la commande avec son ID
    commande = get_object_or_404(OrderPro, id=order_id)

    # Récupérer les produits associés à cette commande
    produits = OrderItemPro.objects.filter(order=commande)

    with transaction.atomic():
        order = get_object_or_404(OrderPro.objects.select_for_update(), id=order_id)
        form = PaymentProForm(request.POST or None, order=order)

        if request.method == "POST" and order.get_statut_actuel == annulation_cmd.ANNULE:
            messages.error(request, "Commande annulée : aucun paiement ne peut être enregistré.")
            return redirect(request.path)
        if request.method == "POST" and form.is_valid():
            paiement = form.save(commit=False)
            paiement.order = order
            paiement.user = request.user
            paiement.mode_paid = form.cleaned_data["mode_paid"]
            paiement.save()
            messages.success(request, "Paiement enregistré.")
            return redirect(request.path)
            #return redirect("detail.proforma", order=order_id)

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
    context = {
        'produits':produits_details,
        'totals':commande.get_prix_total,
        'status':commande.get_statut_actuel,
        'orderId':commande.id,
        'order':commande,
        'form':form
    }
    context.update(annulation_cmd.contexte("proforma", commande))
    return render(request, 'proforma/detail-commande-pro.html',context)

@admin_required
def suivis_commande_pro(request, order_id):
    commande = get_object_or_404(OrderPro, id=order_id)
    traitements = TraimentPro.objects.filter(order=order_id).order_by('-created_at')
    context = {
        'traitements':traitements,
        'order':commande
    }
    return render(request, 'proforma/suivis-pro.html',context)

@require_POST
@admin_required
def change_statut_pro(request, order_id):
   user=request.user
    #   Récupérer l'objet
   order = get_object_or_404(OrderPro, id=order_id)
   if order.get_statut_actuel == annulation_cmd.ANNULE:
      messages.error(request, "Commande annulée : son statut ne change plus.")
      return redirect('detail.proforma', order.id)
   new_status=order.get_statut_actuel
  
   if (order.get_statut_actuel == "en_attente" ):
      new_status = "en_production"
   elif (order.get_statut_actuel == "en_production" ):
      new_status = "pret_pour_livraison"
   if (order.get_statut_actuel == "pret_pour_livraison" ):
      new_status = "termine"
   elif (order.get_statut_actuel == "termine" ):
      new_status = "termine"
   TraimentPro.objects.create(
        order=order,
        user=user,
        statut=new_status
    )
  
    #   Rediriger (par exemple, vers la page des commandes)
   return redirect('detail.proforma', order_id)  # Modifie selon le nom de ta vue cible

@require_POST
@admin_required
def supprimer_order_pro(request, pk):
    order = get_object_or_404(OrderPro, pk=pk, user=request.user)
    date=order.created_at.strftime("%y%m%d")
    numero = f'{order.numero}BI{date}'
    order.delete()
    messages.success(request, f"La commande n° {numero} a été supprimée.")
    return redirect("liste-order-pro")

@admin_required
def get_historique_paiement_pro(request, order_id):
    commande = get_object_or_404(OrderPro, id=order_id)
    paiements = PaymentPro.objects.filter(order=order_id).order_by('-created_at')
    context = {
        'paiements':paiements,
        'order':commande
    }
    return render(request, 'proforma/historique-paiement-pro.html',context)


# --- Statistiques annuelles (proposition D, 12/11/2026) ---
@admin_required
def statistiques_annuelles(request):
    from .statistiques import annees_disponibles, statistiques
    annees = annees_disponibles()
    try:
        annee = int(request.GET.get("annee") or annees[0])
    except (TypeError, ValueError):
        annee = annees[0]
    if annee not in annees:
        annee = annees[0]
    stats = statistiques(annee)
    graphiques = {   # données des graphiques (lues par Chart.js via json_script)
        "mois": stats["mois"],
        "ca_par_type": [{"libelle": lib, "valeurs": stats["ca"]["par_mois"][cle]} for cle, lib in stats["types"]],
        "encaisse": stats["encaissements"]["par_mois"],
        "commandes": [{"libelle": lib, "valeurs": stats["commandes"]["par_mois"][cle]} for cle, lib in stats["types"]],
        "nouveaux_clients": stats["clients"]["nouveaux_par_mois"],
        "modes": [{"libelle": m, "valeur": v} for m, v in stats["encaissements"]["modes"]],
        "diametres": [{"libelle": d, "valeur": q} for d, q in stats["produits"]["diametres"]],
    }
    return render(request, "statistiques.html", {
        "s": stats, "annees": annees, "graphiques": graphiques,
        "current_url": request.get_full_path(),
    })


# --- Annulation d'une commande (13/11/2026) ---
@require_POST
@admin_required
def annuler_commande(request, type_commande, order_id):
    if type_commande not in ("client", "proforma", "projet", "additionnel"):
        raise Http404
    try:
        annulation = annulation_cmd.annuler(type_commande, order_id, request.user, request.POST.get("motif"))
    except annulation_cmd.AnnulationImpossible as erreur:
        messages.error(request, str(erreur))
    except (Order.DoesNotExist, OrderPro.DoesNotExist, ProjetOrder.DoesNotExist, OrderAdd.DoesNotExist):
        raise Http404
    else:
        messages.success(request, f"La commande n° {annulation.numero} est annulée.")
    return redirect(annulation_cmd.url_detail(type_commande, order_id))
