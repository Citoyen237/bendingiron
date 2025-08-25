from django import forms
from .models import *

class CarreForm(forms.Form):
    # form
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
        label = "Qui fourni le fer ?",
        required=True,
         widget=forms.RadioSelect(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            # 'class': 'form-radio',  # Classe CSS
            'value': 'bending iron',  # Valeur initiale spécifique
            'id': 'fer' , # Attribut id
            'initial':'bending iron',
        })
    )
    choix_fer = [
        ('bending iron','Bending Iron'),
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

    longueur_Cote = forms.FloatField(
        label=" Longueur du cote",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=80, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'longueurCote'  # Attribut id
        })
    )
  
     #longueur depart et fin
    longueur_Depart_et_Fin = forms.FloatField(
        label=" Longueur de départ & fin",
        # required=True,  # Champ requis
        #initial=6.5,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            # 'value':'30',
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    #rayon de courbure
    rayon_Courbure = forms.FloatField(
        label=" Rayon de courbure (mm)",
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

    longueur_Total = forms.FloatField(
        label=" Longueur totale du cadre(mm)",
        # required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'value':'0',
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
        label="Quantite de barre(u)",
         required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
         min_value=1, 
         max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            #'value': '1',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    CHOICES = [
        ('90', '90°'),
        ('135', '135°'),
    ]

    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label="Choix de l’angle",
        required=True,  # Champ requis
        initial='90°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'angle',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    CHOICES2 = [
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
    ]
    
    Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label="Choix du diametre du fer (mm)",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
class RectangleForm(forms.Form):
    choix_fer = [
        ('bending iron','Bending Iron'),
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
    rayon_Courbure = forms.FloatField(
        label=" Rayon de courbure",
        #required=True,  # Champ requis
        # initial,  # Valeur par défaut
        #min_value=8, 
        #max_value=50,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '30',  # Valeur initiale spécifique
            'id': 'rayonCourbure'  # Attribut id
        })
    )
    
    longueur_Depart_et_Fin = forms.FloatField(
        label=" longueur Depart & Fin",
        #required=True,  # Champ requis
        # initial,  # Valeur par défaut
        #min_value=8, 
        #max_value=50,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '30',  # Valeur initiale spécifique
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre(mm)",
        # required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
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
        label="Quantite de barre(u)",
         required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
         min_value=1, 
         max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            'value': '1',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    CHOICES = [
        ('90', '90°'),
        ('135', '135°'),
    ]

    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle",
        required=True,  # Champ requis
        initial='90°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'angle',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    CHOICES2 = [
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
    ] 
     
    Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du Diametre du fer en (mm)",
        required=True,  # Champ requis
        #initial='90°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    largeur_Cote = forms.FloatField(
        label=" Largeur du cote(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=800,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'largeurCote'  # Attribut id
        })
    )
    
    longueur_Cote = forms.FloatField(
        label="Longueur du cote(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'longueurCote'  # Attribut id
        })
    )
      
class TriangleForm(forms.Form):
    choix_fer = [
        ('bending iron','Bending Iron'),
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
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
    ]
    
    Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du Diametre du fer en (mm)",
        required=True,  # Champ requis
        initial='M6°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
    
    # choix angle de cintrage
    CHOICES = [
        ('120', '120°'),
        ('135', '135°'),
    ]
    
    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle ",
        required=True,  # Champ requis
        initial='90°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'angle',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )   
    
    #rayon de courbure
    rayon_Courbure = forms.FloatField(
        label=" Rayon de courbure (mm)",
        #required=True,  # Champ requis
        # initial,  # Valeur par défaut
        #min_value=8, 
        #max_value=50,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '30',  # Valeur initiale spécifique
            'id': 'rayonCourbure'  # Attribut id
        })
    )
    
    #longueur depart et fin
    longueur_Depart_et_Fin = forms.FloatField(
        label=" Longueur de départ & fin",
        # required=True,  # Champ requis
        #initial=6.5,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            #'value':'30',
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    longueur_Cote = forms.FloatField(
        label=" Longueur du cote",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'longueurCote'  # Attribut id
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
        label="Quantite de barre(u)",
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
     
class HexagonaleForm(forms.Form):
    choix_fer = [
        ('bending iron','Bending Iron'),
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
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
    ]
    
    Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du Diametre du fer en (mm)",
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
        ('60', '60°'),
        ('120', '120°'),
    ]
    
    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle de cintrage(degre) ",
        required=True,  # Champ requis
        initial='60°',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'angle',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )   
    
    #rayon de courbure
    rayon_Courbure = forms.FloatField(
        label=" Rayon de courbure (mm)",
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
    
    #longueur depart et fin
    longueur_Depart_et_Fin = forms.FloatField(
        label=" Longueur de départ & fin",
        # required=True,  # Champ requis
        #initial=6.5,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
           # 'value':'30',
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    diametre = forms.FloatField(
        label=" Diametre de cintrage(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            #'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'diametreCin'  # Attribut id
        })
    )
        
    longueur_Total = forms.FloatField(
        label=" Longueur totale du cadre",
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
        label="Quantite de barre(u)",
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    