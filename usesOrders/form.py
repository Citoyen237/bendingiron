from django import forms
from .models import *

class OrderUserInfoForm(forms.ModelForm):
    class Meta:
        model = OrderUserInfo
        fields = ['nom', 'telephone','adresse']
        labels = {
            'nom': "Nom complet du client",
            'telephone': "Numero de telephone",
            'adresse': "Adresse de livraison",
        }
    CHOICES2 = [
        ('', ''),
        ('livraison sur chantier', 'Livraison sur chantier'),
        ('retrait en usine', 'Retrait en usine'),
    ] 
     
    mode_livraison = forms.ChoiceField(
        choices=CHOICES2,
        label=" Mode de livraison",
        required=True,  # Champ requis
            #initial='90°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
                # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    def __init__(self, *args, **kwargs):
        super(OrderUserInfoForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class DistributeurForm(forms.ModelForm):
    class Meta:
        model = CodePromo
        fields = ['client', 'remise','expiration']
        labels = {
            'client': "Nom complet du client :",
            'remise': "Remise :",
            'expiration': "Expiration (en Mois) :"
        }
    
    def __init__(self, *args, **kwargs):
        super(DistributeurForm, self).__init__(*args, **kwargs)
        from django.db.models import Exists, OuterRef

        self.fields['client'].queryset = CustomUser.objects.annotate(
            has_code=Exists(CodePromo.objects.filter(client=OuterRef('pk')))
        ).filter(has_code=False)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})