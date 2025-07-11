from django import forms
from .models import *

# '''front'''
class CarreForm(forms.Form):
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
    
    
class EtrierForm(forms.Form):
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
        ('180', '180°'),
    ]
    
    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle de cintrage(degre) ",
        required=True,  # Champ requis
        initial='180°',  # Valeur par défaut
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
            #'value': '5',  # Valeur initiale spécifique
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
            #'value':'5',
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    longueur_Cote = forms.FloatField(
        label=" Longueur du cote(mm)",
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
        label=" Longueur totale du cadre (mm)",
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
    
class EtrierFondRondForm(forms.Form):
    choix_fer = [
        ('bending iron','Bending Iron (Alu)'),
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
            'initial':'le client',
        })
    )
   
    #choix du diametre
    CHOICES2 = [
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20'),
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
   
    hauteur = forms.FloatField(
        label="hauteur(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=30, 
        max_value=580,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '30',  # Valeur initiale spécifique
            'id': 'hauteur'  # Attribut id
        })
    )
    
    largeur = forms.FloatField(
        label="largeur(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=15, 
        max_value=512,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '15',  # Valeur initiale spécifique
            'id': 'largeur'  # Attribut id
        })
    )
    
    hauteur_Filetage = forms.FloatField(
        label="hauteur du Filetage(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=15, 
        max_value=110,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '15',  # Valeur initiale spécifique
            'id': 'hauteurFiletage'  # Attribut id
        })
    )
    
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre(mm)",
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
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
    
class PinceForm(forms.Form):
    choix_fer = [
        ('bending iron','Bending Iron(Fe400)'),
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
        ('135', '135°'),
        ('180', '180°')
    ]
    
    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle de cintrage(degre) ",
        required=True,  # Champ requis
        initial='135°',  # Valeur par défaut
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
        label=" Longueur du cote(mm)",
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
        label=" Longueur totale du cadre (mm)",
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
    
class CrochetForm(forms.Form):
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
        ('135', '135°'),
        ('180', '180°')
    ]
    
    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle de cintrage(degre) ",
        required=True,  # Champ requis
        initial='135°',  # Valeur par défaut
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
    
    #longueur depart et fin
    longueur_Total = forms.FloatField(
        label=" Longueur totale du cadre (mm)",
        # required=True,  # Champ requis
        # initial=0.6,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal'  # Attribut id
        })
    )
    
    longueur_Cote = forms.FloatField(
        label=" Longueur du cote(mm)",
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
     
#cintrage en T
class TForm(forms.Form):
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
        ('6', 'M6'),
        ('8', 'M8')       
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du diametre de fer(mm) ",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
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
            'value': '10',  # Valeur initiale spécifique
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
            'value':'30',
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    
    longueur_Cote = forms.FloatField(
        label=" Longueur du cote(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            'value': '150',  # Valeur initiale spécifique
            'id': 'longueurCote'  # Attribut id
        })
    )
    largeur_Cote = forms.FloatField(
        label=" Largeur du cote(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            'value': '95',  # Valeur initiale spécifique
            'id': 'largeurCote'  # Attribut id
        })
    )
    
    longueur_Total = forms.FloatField(
        label=" Longueur totale du cadre(mm)",
        # required=True,  # Champ requis
        #initial=60,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal',
            #"value":'580'  # Attribut id
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
        label="Quantite de cadre en (u)",
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
    
#cintrage en T economique
class TeconoForm(forms.Form):
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
        ('6', 'M6'),
        ('8', 'M8')       
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du diametre de fer(mm) ",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
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
            'value': '30',  # Valeur initiale spécifique
            'id': 'rayonCourbure'  # Attribut id
        })
    )
    
     
    longueur_Cote = forms.FloatField(
        label=" Longueur du cote(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            'value': '150',  # Valeur initiale spécifique
            'id': 'longueurCote'  # Attribut id
        })
    )
    largeur_Cote = forms.FloatField(
        label=" Largeur du cote(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            'value': '95',  # Valeur initiale spécifique
            'id': 'largeurCote'  # Attribut id
        })
    )
    
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre(mm)",
        # required=True,  # Champ requis
        #initial=60,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal',
             #"value":'500'  # Attribut id
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
        label="Quantite de cadre en (u)",
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
   
#classe des formes U
class UForm(forms.Form):
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
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20')       
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du diametre de fer(mm) ",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
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
    
    hauteur_Gauche = forms.FloatField(
        label=" Hauteur Gauche (mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'hauteurGauche'  # Attribut id
        })
    )
    
    largeur_Fond = forms.FloatField(
        label=" Largeur de fond (mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'largeurFond'  # Attribut id
        })
    )
    
    hauteur_Droite = forms.FloatField(
        label=" Hauteur Droite(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'hauteurDroite'  # Attribut id
        })
    )
    
   
    longueur_Total = forms.FloatField(
        label=" Longueur totale du cadre(mm)",
        # required=True,  # Champ requis
        #initial=60,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal',
             #"value":'580'  # Attribut id
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
        label="Quantite de cadre en (u)",
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        min_value=1, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )
   
class UouvertForm(forms.Form):
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
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20')       
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du diametre de fer(mm) ",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    ) 
    
    #choix angle
    CHOICES = [
        ('90', '90°'),
        ('135', '135°'),
        ('180', '180°')     
    ]
    
    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l'angle de cintrage(degre) ",
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
        label="Rayon de courbure (mm)",
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
        label="Longueur de départ & fin",
        # required=True,  # Champ requis
        #initial=6.5,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            #'value':'30',
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    hauteur_Gauche = forms.FloatField(
        label="Hauteur Gauche (mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'hauteurGauche'  # Attribut id
        })
    )
    
    largeur_Fond = forms.FloatField(
        label="Largeur de fond (mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'largeurFond'  # Attribut id
        })
    )
    
    hauteur_Droite = forms.FloatField(
        label="Hauteur Droite(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'hauteurDroite'  # Attribut id
        })
    )
    
   
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre(mm)/tolerance +-10 mm",
        # required=True,  # Champ requis
        #initial=60,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal',
             #"value":'580'  # Attribut id
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
            'id': 'prixTotal'  # Attribut id
        })
    )
    quantite = forms.FloatField(
        label="Quantite de cadre en (u)",
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        min_value=1, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    )  
   
class UfermeForm(forms.Form):
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
            'initial':'bending iron(Fe400)',
        })
    )
    
    #choix du diametre
    CHOICES2 = [
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20')       
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du diametre de fer(mm) ",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'diametre',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    ) 
    
    #choix angle
    CHOICES = [
        ('90', '90°'),
        ('135', '135°'),
        ('180', '180°')     
    ]
    
    Angle_pliage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l'angle de cintrage(degre) ",
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
        label="Longueur de départ & fin",
        # required=True,  # Champ requis
        #initial=6.5,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            #'value':'30',
            'id': 'longueurDepart'  # Attribut id
        })
    )
    
    hauteur_Gauche = forms.FloatField(
        label="Hauteur Gauche (mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'hauteurGauche'  # Attribut id
        })
    )
    
    largeur_Fond = forms.FloatField(
        label="Largeur de fond (mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'largeurFond'  # Attribut id
        })
    )
    
    hauteur_Droite = forms.FloatField(
        label="Hauteur Droite(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=1, 
        max_value=2000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            # 'value': '20',  # Valeur initiale spécifique
            'id': 'hauteurDroite'  # Attribut id
        })
    )
    
   
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre (mm)",
        # required=True,  # Champ requis
        #initial=60,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control',  # Classe CSS
            'id': 'longueurTotal',
             #"value":'580'  # Attribut id
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
            'id': 'prixTotal'  # Attribut id
        })
    )
    quantite = forms.FloatField(
        label="Quantite de cadre en (u)",
        # required=True,  # Champ requis
        # initial=1,  # Valeur par défaut
        min_value=1, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',  # Classe CSS
            # 'readonly': 'readonly',  # Attribut readonly
            # 'value': '0',  # Valeur initiale
            'id': 'quantite'  # Attribut id
        })
    ) 

class BarreDroiteForm(forms.Form):
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
        ('6', 'M6'),
        ('8', 'M8'),
        ('10', 'M10'),
        ('12', 'M12'),
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('25', 'M25'),
        ('32', 'M32')
    ]
    
    diametre_fer = forms.ChoiceField(
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
    
    longueur_Barre = forms.FloatField(
        label=" Longueur de la barre(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=300, 
        max_value=8000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '300',  # Valeur initiale spécifique
            'id': 'longueurBarre'  # Attribut id
        })
    )
    
    longueur_Total = forms.FloatField(
        label="Longueur totale du cadre(mm)",
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
        label="Quantite de barre(u)",
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
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('25', 'M25'),
        ('32', 'M32')
    ]
    
    diametre_fer = forms.ChoiceField(
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
        ('90', '90°'),
        ('135', '135°'),
        ('180', '180°')
    ]
    
    angle_cintrage = forms.ChoiceField(
        choices=CHOICES,
        label=" Choix de l’angle de cintrage(degre) ",
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
        label=" Longueur de la barre(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=300, 
        max_value=8000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '300',  # Valeur initiale spécifique
            'id': 'longueurBarre'  # Attribut id
        })
    )
    
    
    longueur_Total = forms.FloatField(
        label=" Longueur totale du cadre",
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
        label=" Quantite de barre(u)",
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
        ('14', 'M14'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('25', 'M25'),
        ('32', 'M32')
    ]
    
    diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label="Choix du Diametre du fer en (mm)",
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
        ('90', '90°'),
        ('135', '135°'),
        ('180', '180°')
    ]
    
    angle_cintrage = forms.ChoiceField(
        choices=CHOICES,
        label="Choix de l’angle de cintrage(degre) ",
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
        label="Rayon de courbure (mm)",
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
        label="Longueur de la barre(mm)",
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
        label="Longueur totale du cadre (mm)",
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
        label="Quantite de barre(u)",
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

class AncrageJForm(forms.Form):
 choix_fer = [
        ('bending iron','Bending Iron (Acier) '),
        ('le client','le client'),
    ]

 fer=forms.ChoiceField(
        choices=choix_fer,
        # widget=forms.RadioSelect,
        label = " Qui fourni le fer ?",
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
        ('12', 'M12'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('24', 'M24'),
        ('27', 'M27'),
        ('30', 'M30'),
        ('32', 'M32')
    ]
    
 Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du Diametre du fer en (mm)",
        required=True,  # Champ requis
        initial='M12',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
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
    
 longeur_Ancrage = forms.FloatField(
        label=" Longueur Ancrage(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=300, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
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
    choix_fer = [
        ('bending iron','Bending Iron (Acier) '),
        ('le client','le client'),
    ]

    fer=forms.ChoiceField(
        choices=choix_fer,
        # widget=forms.RadioSelect,
        label = " Qui fourni le fer ?",
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
        ('12', 'M12'),
        ('16', 'M16'),
        ('20', 'M20'),
        ('24', 'M24'),
        ('27', 'M27'),
        ('30', 'M30'),
        ('32', 'M32')
    ]
    
    Diametre_fer = forms.ChoiceField(
        choices=CHOICES2,
        label=" Choix du Diametre du fer en (mm)",
        required=True,  # Champ requis
        initial='M12',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
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
    
    longeur_Ancrage = forms.FloatField(
        label=" Longueur Ancrage(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=300, 
        max_value=1000,
        widget=forms.NumberInput(attrs={
            # 'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
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
    