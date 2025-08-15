from django import forms
from .models import *

class OrderUserInfoForm(forms.ModelForm):

    class Meta:
        model = OrderUserInfo
        fields = ['nom', 'telephone','adresse']
        labels = {
            'nom': "Nom complet du client",
            'telephone': "Numero de telephone",
            'adresse': "Adresse de livraison"
        }
    
    
    def __init__(self, *args, **kwargs):
        super(OrderUserInfoForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})