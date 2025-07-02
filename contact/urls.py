from django.urls import path
from .views import *

urlpatterns = [
    path('', SendMessage.as_view(), name='contact.index'),
]
