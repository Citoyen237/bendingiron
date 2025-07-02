from django.shortcuts import render,redirect
from .models import *
from .form import *
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .utils import *
from django.conf import settings
import traceback
from django.http import HttpResponse

class SendMessage(SuccessMessageMixin, CreateView):
   model = Contact
   form_class = ContactForm
   template_name = "contact.html"
   success_url = reverse_lazy('contact.index')  # Redirige vers la liste des messages après envoi
   success_message = "Votre message a été envoyé avec succès !"  # Message de confirmation

   def get_context_data(self, **kwargs):
      context = super().get_context_data(**kwargs)
      context['current_url'] = self.request.path
      return context 