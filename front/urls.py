from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='font.index'),
    path('nos-services/', services , name='services'),
    path('a-propos/', about, name='about'),
    path('condition-generale-de-vente/', cgv, name='cgv'),
    path('politique-de-confidentialite/', get_politique, name='politique'),
    path('domaine-expertise/engenerie-de-projet', get_domaine_expertise, name='domaine.expertise'),
    path('domaine-expertise/boutique-en-ligne', get_boutique_expertise, name='domaine.boutique'), 
    path('domaine-expertise/fabrication-d-armatures', get_fa_armature_expertise, name='domaine.faarmature'), 
    path('domaine-expertise/pose-d-armatures', get_pose_armature_expertise, name='domaine.pose.armature'), 
]
