from django.urls import path

from . import views

urlpatterns = [
    path("<int:product_id>/calcul.json", views.calcul_json, name="boutique.calcul"),
    path("<int:product_id>/apercu/", views.apercu, name="boutique.apercu"),
]
