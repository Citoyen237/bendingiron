from django import forms
from .models import *

class AncrageJForm(forms.Form):
 
 prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

 fer = forms.CharField(
        # Valeur par défaut
        widget=forms.HiddenInput(attrs={
            'id': 'fer',
        })
    )


    #choix du diametre
 CHOICES2 = [
        ('12', 'M12'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('24', 'M24'),
        ('27', 'M27'),
        ('30', 'M30'),
        ('33', 'M32'),
        ('36', 'M36')
    ]
    
 Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du Diametre du fer en (mm)",
        required=True,  # Champ requis
        initial='M12',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':'form-select',  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
 longeur_Filetage = forms.FloatField(
        label=" Longueur filtetage(mm)",
        #required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '3',  # Valeur initiale spécifique
            'id': 'longeurFiletage'  # Attribut id
        })
    )
    
    #longueur d'antrage
 CHOICES3 = [
        (200, 200),
        (300, 300),
        (400, 400),
        (500, 500),
        (600, 600),
    ]
 longeur_Ancrage = forms.ChoiceField(
        choices=CHOICES3,
        label=" Longueur Ancrage(mm)",
        required=True,  # Champ requis
        initial=200,
        # initial,  # Valeur par défaut
        widget=forms.Select(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-select',  # Classe CSS
             #'value': '300',  # Valeur initiale spécifique
            'id': 'longeurAncrage'  # Attribut id
        })
    )
    
    #rayon de courbure
 rayon_Courbure = forms.FloatField(
        label=" Rayon de Courbure (mm)",
        #required=True,  # Champ requis
        # initial,  # Valeur par défaut
        #min_value=8, 
        #max_value=50,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '30',  # Valeur initiale spécifique
            'id': 'rayonCourbure'  # Attribut id
        })
    )
    
 hauteur_Cintrage = forms.FloatField(
        label=" Hauteur de cintrage(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '3',  # Valeur initiale spécifique
            'id': 'hauteurCintrage'  # Attribut id
        })
    )
    
 longueur_Total = forms.FloatField(
        label="Longueur totale du cadre",
        # required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal'  # Attribut id
        })
    )
    
 prix = forms.FloatField(
        label=" Prix unitaire",
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
        label=" Prix Total",
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
        label=" Quantite de barre(u)",
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )

class AncrageCrossForm(forms.Form):
    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    fer = forms.CharField(
        # required=True,  # Champ requis
        widget=forms.HiddenInput(attrs={
            'id': 'fer',
        })
    )
   
    #choix du diametre
    CHOICES2 = [
        ('12', 'M12'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('24', 'M24'),
        ('27', 'M27'),
        ('30', 'M30'),
        ('33', 'M32'),
        ('36', 'M36')
        ]
    
    Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du Diametre du fer en (mm)",
        required=True,  # Champ requis
        initial='M12',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':'form-select',  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    
    longeur_Filetage = forms.FloatField(
        label="Longueur filtetage(mm)",
        #required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '3',  # Valeur initiale spécifique
            'id': 'longeurFiletage'  # Attribut id
        })
    )
    
       #longueur d'antrage
    CHOICES3 = [
        (200, 200),
        (300, 300),
        (400, 400),
        (500, 500),
        (600, 600),
    ]
    longeur_Ancrage = forms.ChoiceField(
        choices=CHOICES3,
        label=" Longueur Ancrage(mm)",
        required=True,  # Champ requis
        initial=200,
        # initial,  # Valeur par défaut
        widget=forms.Select(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-select',  # Classe CSS
             #'value': '300',  # Valeur initiale spécifique
            'id': 'longeurAncrage'  # Attribut id
        })
    )
    
    
    #rayon de courbure
    diametre_Cintrage = forms.FloatField(
        label=" Diametre (mm)",
        #required=True,  # Champ requis
        # initial,  # Valeur par défaut
        #min_value=8, 
        #max_value=50,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '30',  # Valeur initiale spécifique
            'id': 'diametreCin'  # Attribut id
        })
    )
    
    hauteur_Cintrage = forms.FloatField(
        label=" Hauteur de cintrage(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '3',  # Valeur initiale spécifique
            'id': 'hauteurCintrage'  # Attribut id
        })
    )
    
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre",
        # required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal'  # Attribut id
        })
    )
    
    prix = forms.FloatField(
        label=" Prix unitaire",
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
        label=" Prix Total",
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
        label=" Quantite de barre(u)",
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    