from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView
import os
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

# Create your views here.
# Mixin personnalisé pour vérifier si l'utilisateur appartient aux groupes 'admin' ou 'superadmin'
class AdminOrSuperAdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.groups.filter(name='admin').exists() or request.user.groups.filter(name='superadmin').exists()):
            return HttpResponseForbidden("Vous n'avez pas accès à cette page.")
        return super().dispatch(request, *args, **kwargs)

# Fonction pour vérifier si l'utilisateur appartient au groupe 'admin'
def is_admin(user):
   return user.groups.filter(name='admin').exists() or user.groups.filter(name='superadmin').exists()

@user_passes_test(is_admin)
def indexA(request):
    return render(request, 'indexA.html')


# produits en stock
class ListProduits(ListView):
    model=Produit
    context_object_name = 'produits'
    template_name = "stocks/list.html"
# stock gestion du fer
class ListFer(ListView):
    model=Fer
    context_object_name = 'fers'
    template_name = "fer/list.html"


class CreateFer(CreateView):
   model = Fer
   form_class = FerForm
   template_name = "fer/create.html"
   success_url="../stocks/"

   def form_valid(self, form):
        form.instance.user = self.request.user  # 👤 lier l'utilisateur connecté
        response = super().form_valid(form)
        messages.success(self.request, "Fer ajouté avec succès !")
        return response
 
@user_passes_test(is_admin)
def get_suivis(request, fer_id):
    fer=get_object_or_404(Fer, id=fer_id)
    mouvements = Mouvement.objects.filter(fer=fer_id).order_by('-date')
    context = {
        'mouvements': mouvements,
        'fer':fer
     }
    return render(request, "fer/suivis.html", context)

class ListMouvement(ListView):
    model=Mouvement
    context_object_name = 'mouvements'
    template_name = "fer/mouvement.html"
   
class CreateMouvement(CreateView):
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
@user_passes_test(is_admin)
def mark_message_as_read(request, message_id):
    message = get_object_or_404(Contact, id=message_id)
    message.is_read = 1
    message.save()
    return redirect('contact.list')

@user_passes_test(is_admin)
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
         for field in form.errors:
            print(field)
         return render(request, 'contact/reponse.html', context)
   else:
      form = ReponseForm()
      context ={
            'current_url':current_url,
            'message':message,
            'form':form,
         }
      return render(request, 'contact/reponse.html', context)

class DeleteMessage(DeleteView):
   model = Contact
   template_name = "contact/delete.html"
   success_url="../../contact"

   def delete(self, request, *args, **kwargs):
      response = super().delete(request, *args, **kwargs)
      message = messages.success(self.request, "Le message a été supprimé avec succès")
      reponses = [response,message]
      return reponses

@user_passes_test(is_admin)
def read_devis(request, message_id):
    message=Contact.objects.filter(id=message_id).first()
    file_path=os.path.join('medias/' ,message.file.path)
    # print(file_path)
    try:
        # file_path = message.file.url  # Chemin absolu du fichier
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404("Fichier introuvable sur le serveur.")
    
@user_passes_test(is_admin)  
def read_devis_response(request, message_id):
    message=Contact.objects.filter(id=message_id).first()
    file_path=os.path.join('medias/' ,message.file_response.path)
    # print(file_path)
    try:
        # file_path = message.file.url  # Chemin absolu du fichier
        return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404("Fichier introuvable sur le serveur.")
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
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        if user.is_active:
            # Bloquer l'utilisateur
            user.is_active = 0
            status_message = "Votre compte chez a été bloqué."
            admin_message = f"L'utilisateur {user.first_name} a été bloqué."
        else:
            # Débloquer l'utilisateur
            user.is_active = 1
            status_message = "Votre compte a été réactivé."
            admin_message = f"L'utilisateur {user.first_name} a été débloqué."
        
        # Sauvegarder le changement
        user.save()

        # Envoyer l'email
        send_mail(
            subject='Mise à jour de votre compte',
            message=f"Bonjour {user.first_name},\n\n{status_message}\n\nCordialement, L'équipe DFMAC.",
            from_email=settings.DEFAULT_FROM_EMAIL,  # Remplacez par votre adresse d'expéditeur
            recipient_list=[user.email],
            fail_silently=False,
        )

        # Message de confirmation pour l'admin
        messages.success(request, admin_message)
    except CustomUser.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
    return redirect('user.list')  # Redirigez vers la liste des utilisateurs

@user_passes_test(is_admin)
def change_user_role(request, user_id, group_name):
    try:
# Trouver l'utilisateur par ID
        user = CustomUser.objects.get(id=user_id)
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

@user_passes_test(is_admin)
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
    return render(request, 'order/detail.html',context)

@user_passes_test(is_admin)
def suivis_commande(request, order_id):
    commande = get_object_or_404(Order, id=order_id)
    traitements = Traiment.objects.filter(order=order_id).order_by('-created_at')
    context = {
        'traitements':traitements,
        'order':commande
    }
    return render(request, 'order/suivis.html',context)

@user_passes_test(is_admin)
def change_statut(request, order_id):
   user=request.user
    #   Récupérer l'objet
   order = get_object_or_404(Order, id=order_id)
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
      # Mettre à jour le statut
   Traiment.objects.create(
        order=order,
        user=user,
        statut=new_status
    )

    #   Rediriger (par exemple, vers la page des commandes)
   return redirect('order.list')  # Modifie selon le nom de ta vue cible


# partenariats
class ListPartenariats(ListView):
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

@user_passes_test(is_admin)
def get_detail_partenariat(request, partenariat_id):
    partenariat = get_object_or_404(Partenariats, id=partenariat_id)
    projets=Projet.objects.filter(partenariat=partenariat_id)
    context = {
        'partenariat': partenariat,
        'projets':projets

    }
    return render(request, 'partenaires/detail-partenariat.html',context)

@user_passes_test(is_admin)
def get_detail_projet(request, projet_id):
     # Récupérer la commande avec son ID
    projet = get_object_or_404(Projet, id=projet_id)

     # Récupérer les produits associés à ce projet
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
    # 'totals':commande.get_prix_total,
    # 'status':commande.get_statut_actuel,
    'projet':projet
    }
    return render(request,'partenaires/detail-projet.html', context)