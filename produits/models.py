from django.db import models
# from anonces.models import *
# from sympy import symbols, sympify
from django.core.exceptions import ValidationError


#classe categorie
class Categorie(models.Model):
    libelle = models.CharField(max_length=255)
    image = models.ImageField(upload_to='produits/images',null=True,blank=True)
    
    def __str__(self):
        return f'{self.libelle}'
    
# produit    
class Produit(models.Model):
    SOUS_CATEGORIE = [
        ('Etrier pour bardage et toiture','Etrier pour bardage et toiture'),
        ('boulon d\'ancrage a beton','boulon d\'ancrage a beton'),
        ('cintrage d\'extremite','Cintrage d extremite'),
        ('redressage et decoupage','Redressage et decoupage'),
        ('Cintrage de cadre','Cintrage de Cadre'),
        ('Cintrage de forme','Cintrage de Forme'),
        ('Quincaillerie','Quincaillerie'),
    ]
    
    categorie=models.ForeignKey(Categorie, related_name='categorie',on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    sous_categorie = models.CharField(max_length=255,choices=SOUS_CATEGORIE,null=True,blank=True)#valeur facultative
    imageshop3d=models.ImageField(upload_to='produits/images')
    imageshop2d=models.ImageField(upload_to='produits/images')
    image_sous_categorie = models.ImageField(upload_to='produits/images',null=True,blank=True)
    name_page = models.CharField(max_length=255)
    Description = models.TextField(max_length=400,null=True,blank=True)#valeur facultative
    
    #
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sous_categorie','nom'],name='unique_sous_categorie_nom')
        ]
    # compte le nombre de produits dans les differents commandes
    @property
    def get_quantite_order(self):
        pass
    
    #retourner le nom du produit
    def __str__(self):
        return f'{self.nom}'

class FerPrice(models.Model):
    DIAMETRE_CHOISES = [
        ('m6','M6'),
        ('m8','M8'),
        ('m10','M10'),
        ('m12','M12'),
        ('m14','M14'),
        ('m16','M16'),
        ('m20','M20' ),
        ('m24','M24'),
        ('m27','M27'),
        ('m30','M30'),
        ('m32','M32'),
        ('taux','Taux transaction'),
        ('taxe','Taxe de l\'etat'),
    ]
    diametre = models.CharField(max_length=255,choices=DIAMETRE_CHOISES,unique=True)
    prixRevient= models.FloatField(null=True,blank=True)
    prix= models.FloatField()

    def __str__(self):
        return self.diametre

    @property
    def prix_utile(self):
        return self.prix/12000