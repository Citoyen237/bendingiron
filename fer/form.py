from django import forms
from .models import *

# from tinymce.widgets import TinyMCE

DIAMETRE_CHOICES = [
    ('6', '6'),
    ('8', '8'),
    ('10', '10'),
    ('12', '12'),
    ('14', '14'),
    ('16', '16'),
    ('20', '20'),
    ('25', '25'),
    ('30', '30'),
    ('32', '32'),
]

class FerForm(forms.ModelForm):
    diametre = forms.ChoiceField(choices=DIAMETRE_CHOICES)  # Champ select

    class Meta:
        model = Fer
        fields = ['diametre', 'categorie','longueur_critique']
    
    
    def __init__(self, *args, **kwargs):
        super(FerForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-select'})
    
    def clean(self):
        cleaned_data = super().clean()
        diametre = cleaned_data.get('diametre')
        categorie = cleaned_data.get('categorie')

        if diametre and categorie:
            if Fer.objects.filter(diametre=diametre, categorie=categorie).exists():
                raise forms.ValidationError("Un fer avec ce diamètre et cette catégorie existe déjà.")
        return cleaned_data
    
class MouvementForm(forms.ModelForm):
    class Meta:
        model = Mouvement
        fields = ['fer', 'quantite', 'prix_u', 'longueur_m']

    def __init__(self, *args, **kwargs):
        super(MouvementForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
 
# class Fer(forms.ModelForm):
#     # desc = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 30, 'class':'form-control'}))
#     class Meta:
#         model = Fer
#         fiels = ['longueur','prix', 'fournisseur','produit']
#         exclude = ['created_at','updated_at']
#         labels= {
#             'longueur':'Longueur',
#             'prix':'Prix Total',
#             'fournisseur':'Fournisseur',
#             'produit':'Produit',
#         }
#         widgets={
#             'longueur':forms.NumberInput(attrs={'class':'form-control'}),
#             'prix':forms.NumberInput(attrs={'class':'form-control'}),
#             'fournisseur':forms.TextInput(attrs={'class':'form-control'}),
#             'produit':forms.Select(attrs={'class':'form-select'}),
#         }

