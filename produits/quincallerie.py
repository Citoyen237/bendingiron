from django import forms
from .models import *

class EcrouForm(forms.Form):

    prix = forms.FloatField(
        label="Prix unitaire",
        # required=True,  # Champ requis
        # initial=0,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            'readonly': 'readonly',  # Attribut readonly
            'value': '0',  # Valeur initiale
            'id': 'prix-id'  # Attribut id
        })
    )
    prix_Total = forms.FloatField(
        label="Prix Total",
        # required=True,  # Champ requis
        # initial=0,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            'readonly': 'readonly',  # Attribut readonly
            'value': '0',  # Valeur initiale
            'id': 'prix-total'  # Attribut id
        })
    )
    quantite = forms.FloatField(
        label="Quantite d'ecrou (u)",
         required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
         min_value=1, 
         max_value=10000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            #'value': '1',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    
    CHOICES2 = [
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('24', 'M24'),
        ('27', 'M27'),
        ('30', 'M30'),
        ('32', 'M32')
    ]
    
    Diametre_ecrou = forms.ChoiceField(
        choices=CHOICES2,
        label="Choix de l'ecrou",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
class FerABetonForm(forms.Form):

    prix = forms.FloatField(
        label="Prix unitaire",
        # required=True,  # Champ requis
        # initial=0,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            'readonly': 'readonly',  # Attribut readonly
            'value': '0',  # Valeur initiale
            'id': 'prix-id'  # Attribut id
        })
    )
    prix_Total = forms.FloatField(
        label="Prix Total",
        # required=True,  # Champ requis
        # initial=0,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            'readonly': 'readonly',  # Attribut readonly
            'value': '0',  # Valeur initiale
            'id': 'prix-total'  # Attribut id
        })
    )
    
    longueur_Barre = forms.FloatField(
        label="Longueur de la barre (m)",
        required=False,  # Champ requis
        # initial,  # Valeur par défaut
        # min_value=80, 
        # max_value=1000,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            'value': '12',  # Valeur initiale spécifique
            'id': 'longueurBarre'  # Attribut id
        })
    )
    
    quantite = forms.FloatField(
        label="Quantite de barre de fer (u)",
         required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
         min_value=1, 
         max_value=10000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            #'value': '1',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    
    CHOICES2 = [
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('24', 'M24'),
        ('27', 'M27'),
        ('32', 'M32')
    ]
    
    Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label="Choix du diametre",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    CHOICES = [
        ('Fe400', 'Fe E400'),
        ('Fe500', 'Fe E500')
    ]
    
    type_de_fer = forms.ChoiceField(
        choices=CHOICES,
        label="Choix du type de fer",
        required=True,  # Champ requis
        initial='Fe400',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'typeFer',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
class FilForm(forms.Form):


    longueur_Total = forms.FloatField(
        label="Longueur totale d'un anneau (mm)",
        # required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'value':'110',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal'  # Attribut id
        })
    )
    prix = forms.FloatField(
        label="Prix unitaire",
        # required=True,  # Champ requis
        # initial=0,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            'readonly': 'readonly',  # Attribut readonly
            'value': '0',  # Valeur initiale
            'id': 'prix-id'  # Attribut id
        })
    )
    prix_Total = forms.FloatField(
        label="Prix Total",
        # required=True,  # Champ requis
        # initial=0,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            'readonly': 'readonly',  # Attribut readonly
            'value': '0',  # Valeur initiale
            'id': 'prix-total'  # Attribut id
        })
    )
    
    poids_Anneau = forms.FloatField(
        label="Poids d'un anneau  (Kg)",
        required=False,  # Champ requis
        # initial,  # Valeur par défaut
        # min_value=80, 
        # max_value=1000,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'value':'0.5',
            'class': 'form-control',  # Classe CSS
            'id': 'poidsAnneau'  # Attribut id
        })
    )
    
    quantite = forms.FloatField(
        label="Quantite d'anneau (u)",
         required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
         min_value=1, 
         max_value=10000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            #'value': '1',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    
    CHOICES2 = [
        ('fil_noire', 'fil noire'),
        ('fil_galvanise', 'fil galvanise')
    ]
    
    type_de_fil = forms.ChoiceField(
        choices=CHOICES2,
        label="Choix du materiaux du fil",
        required=True,  # Champ requis
        initial='fil noire',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'fil',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    