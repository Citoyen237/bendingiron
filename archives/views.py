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

from django.http import Http404, FileResponse
from auth_app.permissions import admin_required

@admin_required
def get_list_archive(request, type):
   archives = Archives.objects.filter(type=type)
   context = {
      'type':type,
      'archives':archives
   }
   return render(request, "list.html", context )

@admin_required
def add_archive(request, type):
    form_class = None

    # Dictionnaire pour choisir la bonne classe de formulaire
    form_mapping = {
        "documents": ArchiveDocumentForm,
        "images": ArchiveImagesForm,
        "videos": ArchiveVideosForm,
    }

    form_class = form_mapping.get(type)
    if not form_class:
        raise Http404("Type d'archive inconnu")
    url = f"/dashboard/archives/{type}/"

    if request.method == "POST":
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            archive = form.save(commit=False)
            archive.user = request.user
            archive.type = type  # associer à l’utilisateur connecté
            archive.save()
            return redirect(url)
    else:
        form = form_class()

    return render(request, "create.html", {"form": form, "type": type})

# @admin_required
# def read_devis(request, message_id):
#     message=Contact.objects.filter(id=message_id).first()
#     file_path=os.path.join('medias/' ,message.file.path)
#     # print(file_path)
#     try:
#         # file_path = message.file.url  # Chemin absolu du fichier
#         return FileResponse(open(file_path, 'rb'), content_type='application/pdf')
#     except FileNotFoundError:
#         raise Http404("Fichier introuvable sur le serveur.")

@admin_required
def download_archive(request, archive_id):
    """Les archives ne sont plus servies directement par Nginx : on passe par cette vue."""
    archive = get_object_or_404(Archives, id=archive_id)
    if not archive.file:
        raise Http404
    return FileResponse(archive.file.open('rb'), as_attachment=False,
                        filename=archive.file.name.rsplit('/', 1)[-1])
