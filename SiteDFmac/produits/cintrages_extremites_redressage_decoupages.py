from django import forms
from .models import *

# '''front'''   
class BarreDroiteForm(forms.Form):
    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    choix_fer = [
        ('bending iron','Bending Iron (Fe400)'),
        ('le client','le client'),
    ]

    fer=forms.ChoiceField(
        choices=choix_fer,
        # widget=forms.RadioSelect,
        label = "Qui fourni le fer ?",
        required=True,
         widget=forms.RadioSelect(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            # 'class': 'form-radio',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'fer' , # Attribut id
            'initial':'bending iron',
        })
    )
   
    #choix du diametre
    CHOICES2 = [
        ('6', 'Fer 6'),
        ('8', 'Fer 8'),
        ('10', 'Fer 10'),
        ('12', 'Fer 12'),
        ('14', 'Fer 14'),
        ('16', 'Fer 16'),
        ('20', 'Fer 20'),
        ('25', 'Fer 25'),
        ('32', 'Fer 32')
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du fer",
        required=True,  # Champ requis
        initial='Fer 6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    longueur_Barre = forms.FloatField(
        label=" Longueur de la barre (cm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=30, 
        max_value=600,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '300',  # Valeur initiale spécifique
            'id': 'longueurBarre'  # Attribut id
        })
    )
    
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre (cm)",
        required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        #min_value=1,
        #max_value=1000,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
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
    quantite = forms.FloatField(
        label="Quantite",
        required=True,  # Champ requis
        min_value=1,
        max_value=10000,
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
   
class BarreCouUneExForm(forms.Form):
    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    choix_fer = [
        ('bending iron','Bending Iron'),
        ('le client','le client'),
    ]

    fer=forms.ChoiceField(
        choices=choix_fer,
        # widget=forms.RadioSelect,
        label = "Qui fournit le fer ?",
        required=True,
         widget=forms.RadioSelect(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            # 'class': 'form-radio',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'fer' , # Attribut id
            'initial':'bending iron',
        })
    )
   
    #choix du diametre
    CHOICES2 = [
        ('6', 'Fer 6'),
        ('8', 'Fer 8'),
        ('10', 'Fer 10'),
        ('12', 'Fer 12'),
        ('14', 'Fer 14'),
        ('16', 'Fer 16'),
        ('20', 'Fer 20'),
        ('25', 'Fer 25'),
        ('32', 'Fer 32')
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du fer ",
        required=True,  # Champ requis
        initial='Fer 6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    # choix angle de cintrage
    CHOICES = [
        ('90', '90'),
        ('135', '135'),
        ('-135', '-135'),
        ('180', '180')
    ]
    
    angle_cintrage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle (degre) ",
        required=True,  # Champ requis
        initial='135',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'angle',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )   
    
    #rayon de courbure
    rayon_Courbure = forms.FloatField(
        label=" Rayon de courbure (cm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        #min_value=300, 
        #max_value=6000,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '300',  # Valeur initiale spécifique
            'id': 'rayonCourbure'  # Attribut id
        })
    )
    

    longueur_Barre = forms.FloatField(
        label=" Longueur de la barre(cm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=30, 
        max_value=600,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '300',  # Valeur initiale spécifique
            'id': 'longueurBarre'  # Attribut id
        })
    )
    
    
    longueur_Total = forms.FloatField(
        label=" Longueur totale du cadre (cm)",
        required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        #min_value=1,
        #max_value=1000,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
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
    quantite = forms.FloatField(
        label=" Quantite ",
        required=True,  # Champ requis
        min_value=1,
        max_value=10000,
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )

class BarreCouDeuxExForm(forms.Form):
    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    choix_fer = [
        ('bending iron','Bending Iron'),
        ('le client','le client'),
    ]

    fer=forms.ChoiceField(
        choices=choix_fer,
        # widget=forms.RadioSelect,
        label = "Qui fournit le fer ?",
        required=True,
         widget=forms.RadioSelect(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            # 'class': 'form-radio',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'fer' , # Attribut id
            'initial':'bending iron',
        })
    )
   
    #choix du diametre
    CHOICES2 = [
        ('6', 'Fer 6'),
        ('8', 'Fer 8'),
        ('10', 'Fer 10'),
        ('12', 'Fer 12'),
        ('14', 'Fer 14'),
        ('16', 'Fer 16'),
        ('20', 'Fer 20'),
        ('25', 'Fer 25'),
        ('32', 'Fer 32')
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label="Choix du fer",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    # choix angle de cintrage
    CHOICES = [
        ('90', '90'),
        ('135', '135'),
        ('-135', '-135'),
        ('180', '180')
    ]
    
    angle_cintrage = forms.ChoiceField(
        choices=CHOICES,
        label="Choix de l’angle (degre) ",
        required=True,  # Champ requis
        initial='135',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'angle',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )   
    
    #rayon de courbure
    rayon_Courbure = forms.FloatField(
        label="Rayon de courbure (cm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        #min_value=300, 
        #max_value=6000,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '300',  # Valeur initiale spécifique
            'id': 'rayonCourbure'  # Attribut id
        })
    )
    
    longueur_Barre = forms.FloatField(
        label="Longueur de la barre (cm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=30, 
        max_value=6000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '300',  # Valeur initiale spécifique
            'id': 'longueurBarre'  # Attribut id
        })
    )
       
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre (cm)",
        required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        #min_value=1,
        #max_value=1000,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
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
    quantite = forms.FloatField(
        label="Quantite",
        required=True,  # Champ requis
        min_value=1,
        max_value=10000,
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )

