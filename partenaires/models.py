from django.db import models
from auth_app.models import CustomUser as User
from django.utils import timezone
from produits.models import *
# Create your models here.
class Partenariats(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    adresse=models.CharField(max_length=255)
    telephone = models.CharField(max_length=200)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()

    def __str__(self):
        return self.name

    @property
    def is_expired(self):
        return timezone.now()>self.date_fin

class Projet(models.Model):
    partenariat=models.ForeignKey(Partenariats, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=255, unique=True)
    statut=models.CharField(max_length=255, default='en cours') 
    created_at= models.DateTimeField(auto_now_add=True)
    update_at= models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','partenariat'],name='unique_name_partenariat')
        ]

    def __str__(self):
        return self.name
    
    @property
    def is_solde(self):
        pass

    @property
    def montant_total(self):
        pass

    @property
    def montant_recu():
        pass

    @property
    def montant_restant():
        pass

class ProjetItem(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    details = models.JSONField()  # Détails du produit (dimensions, choix d'angle, etc.)
    quantite = models.PositiveIntegerField(default=1)
    prix_u = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_prix_total(self):
        return self.prix_u*self.quantite
    
    @property
    def quantite_commande(self):
        pass

    @property
    def quantite_restant(self):
        pass
    
    # affiche ds json files
    def details_to_text(self):
        if not self.details:
            return ""
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items())
    
    class PaimenentProjet(models.Model):
        # date
        pass