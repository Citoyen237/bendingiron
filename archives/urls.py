from django.urls import path
from .views import *

urlpatterns = [
    path('<str:type>/',get_list_archive, name='archive.list'),
    path('ajouter/<str:type>/',add_archive, name='archive.add'),
]
