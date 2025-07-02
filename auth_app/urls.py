from django.urls import path
from .views import *

urlpatterns = [
    path('login/', loginPage, name='login'),
    path('deconnexion/', logoutPage, name='logout'),
    path('creer-un-compte/', register, name='register'),
    path('mot-de-passe-oublier/', resetpass, name='resetpass'),
]
