from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='partenaire.index'),
    path('detail-sur-le-projet/', detail_projet, name='partenaire.detail'),
]
