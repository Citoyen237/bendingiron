# Create your views here.
from django.shortcuts import render,redirect,get_object_or_404
from django.views.generic import ListView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from auth_app.models import *
from django.contrib.auth.decorators import user_passes_test
from .models import *
from .form import *

# Fonction pour vérifier si l'utilisateur appartient au groupe 'admin'
def is_admin(user):
   return user.groups.filter(name='admin').exists() or user.groups.filter(name='superadmin').exists()

@user_passes_test(is_admin)
def get_list_archive(request, type):
   archives = Archives.objects.filter(type=type)
   context = {
      'type':type,
      'archives':archives
   }
   return render(request, "list.html", context )

@user_passes_test(is_admin)
def add_archive(request, type):
    form_class = None

    # Dictionnaire pour choisir la bonne classe de formulaire
    form_mapping = {
        "documents": ArchiveDocumentForm,
        "images": ArchiveImagesForm,
        "videos": ArchiveVideosForm,
    }

    form_class = form_mapping.get(type)
    url =f"/dashboard/archives/{type}"
    if not form_class:
        redirect(url)  # ou erreur 404 si type invalide

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            archive = form.save(commit=False)
            archive.user = request.user
            archive.type = type  # associer à l’utilisateur connecté
            archive.save()
            return redirect(url)
        else:
            print(form.errors)  # debug
    else:
        form = form_class()

    return render(request, "create.html", {"form": form, "type": type})

# @user_passes_test(is_admin)
# def read_devis(request, message_id):
#     message=Contact.objects.filter(id=message_id).first()
#     file_path=os.path.join('medias/' ,message.file.path)
#     # print(file_path)
#     try:
#         # file_path = message.file.url  # Chemin absolu du fichier
#         return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
#     except FileNotFoundError:
#         raise Http404("Fichier introuvable sur le serveur.")