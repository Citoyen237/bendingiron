from django import forms
from .models import *

class EtrierFondRondForm(forms.Form):
    fer = forms.CharField(
        # Valeur par défaut
        widget=forms.HiddenInput(attrs={
            'id': 'fer',
        })
    )
    # choix_materiel = [
    #     ('acier','Acier'),
    #     ('alu','Alu'),
    # ]

    # materiaux=forms.ChoiceField(
    #     choices=choix_materiel,
    #     # widget=forms.RadioSelect,
    #     label = "Type de materiaux ?",
    #     required=True,
    #      widget=forms.RadioSelect(attrs={
    #         # 'readonly': 'readonly',  # Attribut readonly
    #         # 'class': 'form-radio',  # Classe CSS
    #         # 'value': '20',  # Valeur initiale spécifique
    #         'id': 'materiaux' , # Attribut id
    #         'initial':'a lu',
    #     })
    # )
    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    #designation
    designation = [
        ('1', '1'),
        ('1 1/4', '1 1/4'),
        ('1 1/2', '1 1/2'),
        ('2', '2'),
        ('2 1/2', '2 1/2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('8', '8'),
        ('10', '10'),
        ('12', '12'),
        ('14','14'),
        ('16','16'),
        ('18','18'),
        ('20','20'),
    ]

    tube_etrier = forms.ChoiceField(
        choices=designation,
        label="Tube pour etrier (pouce)",
        required=True,  # Champ requis
        initial='1/4',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'tube_etrier',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    #choix du diametre 
    Diametre_fer = forms.CharField(
        label="Diametre du fer (mm)",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.TextInput(attrs={
            'class':'form-control',  # Classe CSS
            'id': 'diametre',  # Attribut id
            'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    hauteur = forms.FloatField(
        label="hauteur(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=30, 
        max_value=580,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
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
            'readonly': 'readonly',  # Attribut readonly
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
            'readonly': 'readonly',  # Attribut readonly
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

class EtrierFondDroitForm(forms.Form):
    fer = forms.CharField(
        # Valeur par défaut
        widget=forms.HiddenInput(attrs={
            'id': 'fer',
        })
    )
    # choix_materiel = [
    #     ('acier','Acier'),
    #     ('alu','Alu'),
    # ]

    # materiaux=forms.ChoiceField(
    #     choices=choix_materiel,
    #     # widget=forms.RadioSelect,
    #     label = "Type de materiaux ?",
    #     required=True,
    #      widget=forms.RadioSelect(attrs={
    #         # 'readonly': 'readonly',  # Attribut readonly
    #         # 'class': 'form-radio',  # Classe CSS
    #         # 'value': '20',  # Valeur initiale spécifique
    #         'id': 'materiaux' , # Attribut id
    #         'initial':'a lu',
    #     })
    # )
    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    #designation
    designation = [
        ('40X40', '40X40'),
        ('45X45', '45X45'),
        ('50X50', '50X50'),
        ('60X60', '60X60'),
        ('70X70', '70X70'),
        ('80X80', '80X80'),
        ('100X100', '100X100'),
        ('120X120', '120X120'),
        ('135X135', '135X135'),
        ('150X150', '150X150'),
        ('160X160', '160X160'),
        ('180X180', '180X180'),
        ('200X200', '200X200'),
        ('220X220', '220X220'),
        ('250X250', '250X250'),
    ]

    tube_etrier = forms.ChoiceField(
        choices=designation,
        label="Tube pour etrier (pouce)",
        required=True,  # Champ requis
        initial='1/4',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'tube_etrier',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    #choix du diametre 
    Diametre_fer = forms.CharField(
        label="Diametre du fer (mm)",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.TextInput(attrs={
            'class':'form-control',  # Classe CSS
            'id': 'diametre',  # Attribut id
            'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    hauteur = forms.FloatField(
        label="hauteur(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=30, 
        max_value=580,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
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
            'readonly': 'readonly',  # Attribut readonly
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
            'readonly': 'readonly',  # Attribut readonly
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

class EtrierFondDroitUneBrancheForm(forms.Form):
    fer = forms.CharField(
        # Valeur par défaut
        widget=forms.HiddenInput(attrs={
            'id': 'fer',
        })
    )

    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    #designation
    designation = [
        ('40X40', '40X40'),
        ('45X45', '45X45'),
        ('50X50', '50X50'),
        ('60X60', '60X60'),
        ('70X70', '70X70'),
        ('80X80', '80X80'),
        ('100X100', '100X100'),
        ('120X120', '120X120'),
        ('135X135', '135X135'),
    ]

    tube_etrier = forms.ChoiceField(
        choices=designation,
        label="Tube pour etrier (pouce)",
        required=True,  # Champ requis
        initial='1/4',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'tube_etrier',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    #choix du diametre 
    Diametre_fer = forms.CharField(
        label="Diametre du fer (mm)",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.TextInput(attrs={
            'class':'form-control',  # Classe CSS
            'id': 'diametre',  # Attribut id
            'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    hauteur = forms.FloatField(
        label="hauteur(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '30',  # Valeur initiale spécifique
            'id': 'hauteur'  # Attribut id
        })
    )

    demi_branche = forms.FloatField(
        label="Demi branche(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '30',  # Valeur initiale spécifique
            'id': 'demi_branche'  # Attribut id
        })
    )
    
    largeur = forms.FloatField(
        label="largeur(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '15',  # Valeur initiale spécifique
            'id': 'largeur'  # Attribut id
        })
    )
    
    hauteur_Filetage = forms.FloatField(
        label="hauteur du Filetage(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
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

class EtrierUnPiedFondRondForm(forms.Form):
    fer = forms.CharField(
        # Valeur par défaut
        widget=forms.HiddenInput(attrs={
            'id': 'fer',
        })
    )
    
    prix_revient = forms.FloatField(
        widget=forms.HiddenInput(attrs={
            'id': 'prix_revient'  # Attribut id
        })
    )

    #designation
    designation = [
        ('1', '1'),
        ('1 1/4', '1 1/4'),
        ('1 1/2', '1 1/2'),
        ('2', '2'),
        ('2 1/2', '2 1/2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    ]

    tube_etrier = forms.ChoiceField(
        choices=designation,
        label="Tube pour etrier (pouce)",
        required=True,  # Champ requis
        initial='1/4',  # Valeur par défaut
        widget=forms.Select(attrs={
            'class':{ 'form-select','mt-4'},  # Classe CSS
            'id': 'tube_etrier',  # Attribut id
            # 'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    #choix du diametre 
    Diametre_fer = forms.CharField(
        label="Diametre du fer (mm)",
        required=True,  # Champ requis
        initial='M6',  # Valeur par défaut
        widget=forms.TextInput(attrs={
            'class':'form-control',  # Classe CSS
            'id': 'diametre',  # Attribut id
            'readonly': 'readonly',  # Attribut readonly (facultatif)
        })
    )
   
    hauteur = forms.FloatField(
        label="hauteur(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        min_value=30, 
        max_value=580,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
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
            'readonly': 'readonly',  # Attribut readonly
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
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '15',  # Valeur initiale spécifique
            'id': 'hauteurFiletage'  # Attribut id
        })
    )

    demi_branche = forms.FloatField(
        label="Demi branche(mm)",
        required=True,  # Champ requis
        # initial,  # Valeur par défaut
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly',  # Attribut readonly
            'class': 'form-control',  # Classe CSS
            #'value': '30',  # Valeur initiale spécifique
            'id': 'demi_branche'  # Attribut id
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
    