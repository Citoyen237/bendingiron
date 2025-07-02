from django.db import models
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from auth_app.models import CustomUser as User

# Create your models here.
# class Fer(models.Model):
#     nom=models.CharField(max_length=255)
#     # longueur=models.IntegerField(null=True, blank=True)
#     description=models.TextField()
#     created_at=models.DateTimeField(auto_now_add=True)
#     updated_at=models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.nom

# class BonCommande(models.Model):
#     fournisseur= models.CharField(max_length=200, null=True)
#     produit=models.ForeignKey(Fer, on_delete=models.CASCADE)
#     longueur=models.IntegerField()
#     prix=models.IntegerField()
#     created_at=models.DateTimeField(auto_now_add=True)
#     updated_at=models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.longueur

# alert

class Fer(models.Model):
    TYPE_CHOICES = [
        ('barre', 'Barre de fer'),
        ('rouleau', 'Rouleau de fer'),
    ]

    # type_fer = models.CharField(max_length=10, choices=TYPE_CHOICES)
    diametre = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
    categorie = models.CharField(max_length=10, choices=TYPE_CHOICES)
    longueur_critique =  models.PositiveIntegerField(null=True, blank=True, default=500) 
    created_at = models.DateTimeField(auto_now_add=True)
          
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['diametre', 'categorie'], name='unique_diametre_categorie')
        ]

    def __str__(self):
        return f"{self.categorie}-{self.diametre}"
    
    @property
    def quantite_totale(self):
        return self.mouvement_set.filter(quantite__isnull=False).aggregate(total=models.Sum('quantite'))['total'] or 0

    @property
    def longueur_totale(self):

        # On multiplie longueur_m * quantite pour chaque mouvement et on fait la somme
        total = self.mouvement_set.annotate(
            total_longueur=ExpressionWrapper(F('longueur_m') * F('quantite'), output_field=DecimalField())
        ).aggregate(longueur_totale=Sum('total_longueur'))['longueur_totale']

        return total or 0
    
    @property
    def sueil_atteint(self):
       if self.longueur_totale < self.longueur_critique :
           return True
       else :
           return False


class Mouvement(models.Model):
    fer = models.ForeignKey(Fer, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) 
    date = models.DateTimeField(auto_now_add=True)
    quantite = models.PositiveIntegerField(null=True, blank=True)     # Pour les barres
    prix_u = models.PositiveIntegerField(null=True, blank=True) 
    longueur_m = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Pour les rouleaux
    type_mouvement = models.CharField(max_length=10, choices=[('entree', 'Entrée'), ('sortie', 'Sortie')], default="entree")

    @property
    def longueur_total(self):
        # return self.prix_u * self.quantite
        return self.longueur_m * self.quantite


    @property
    def prix_total(self):
        return self.prix_u * self.quantite
    

