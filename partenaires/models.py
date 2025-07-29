from django.db import models
from auth_app.models import CustomUser as User
from django.utils import timezone
from produits.models import *
# Create your models here.
class Partenariats(models.Model):
    # interimaire
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
    reduction=models.IntegerField(default=15)
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
        return sum(item.prix_u * item.quantite for item in self.projetitems.all())
    
    @property
    def montant_apres_remise(self):
        return round(self.montant_total-((self.montant_total*self.reduction)/100))
    
    @property
    def montant_tva(self):
        return round((self.montant_apres_remise*19.25)/100)

    @property
    def net_payer(self):
        return round(self.montant_tva + self.montant_apres_remise)
    
    @property
    def tranche1(self):
        return round((self.net_payer*40)/100)
    
    @property
    def tranche2(self):
        return round((self.net_payer*40)/100)
    
    @property
    def tranche3(self):
        return round((self.net_payer*20)/100)
    
    # @property
    # def paiement_termine(self):
    #     return self.paiements.filter(approuve=True).count() >= 3

class ProjetItem(models.Model):
    projet = models.ForeignKey(Projet,related_name='projetitems', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    details = models.JSONField()  # Détails du produit (dimensions, choix d'angle, etc.)
    quantite = models.PositiveIntegerField(default=1)
    prix_u = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_prix_total(self):
        return self.prix_u*self.quantite
    
    @property
    def quantite_commande(self):
        return self.orders.aggregate(
            total=models.Sum('quantite')
        )['total'] or 0

    @property
    def quantite_restant(self):
        return self.quantite-self.quantite_commande
    
    # affiche ds json files
    def details_to_text(self):
        if not self.details:
            return ""
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items())


class PaiementProjet(models.Model):
    TRANCHES = (
        (1, '1ère tranche'),
        (2, '2ème tranche'),
        (3, '3ème tranche'),
    )

    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='paiements')
    tranche = models.PositiveSmallIntegerField(choices=TRANCHES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date_paiement = models.DateTimeField(default=timezone.now)
    approuve = models.BooleanField(default=False)
    mode_paiement = models.CharField(max_length=100, blank=True, null=True)  # Mobile money, virement, etc.

    class Meta:
        unique_together = ('projet', 'tranche')  # Une tranche ne peut être payée qu'une fois

    def __str__(self):
        return f"{self.projet.name} - Tranche {self.tranche} : {self.montant} FCFA"


class ProjetOrder(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    projet_item = models.ForeignKey(ProjetItem,related_name='orders', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.projet_item}-({self.quantite})'