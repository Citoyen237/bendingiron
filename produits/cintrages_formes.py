from django import forms
from .models import *

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
        label="Longueur totale du cadre(mm)",
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
    