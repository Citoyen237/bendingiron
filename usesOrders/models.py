from django.db import models
# from auth_app.models import *
from auth_app.models import CustomUser
from produits.models import *
from decimal import Decimal

# # Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # total_prix = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_prix_total(self):
        #  reduction
        # tva
        return sum(item.prix_u * item.quantite for item in self.cartitem_set.all())

    @property
    def montant_tva(self):
        return round((Decimal(self.get_prix_total)*Decimal(19.25))/100)
    @property
    def net_payer(self):
        return round(self.montant_tva + self.get_prix_total)
    
    @property
    def get_tranche1(self):
        return round((self.net_payer*30)/100)
    
    @property
    def get_tranche2(self):
        return round((self.net_payer*70)/100)
        
    
    def __str__(self):
        return self.get_prix_total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    details = models.JSONField()  # Détails du produit (dimensions, choix d'angle, etc.)
    quantite = models.PositiveIntegerField(default=1)
    prix_u = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def get_prix_total(self):
        return self.prix_u*self.quantite
    
    # affiche ds json files
    def details_to_text(self):
        if not self.details:
            return ""
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items())
    
    


    def __str__(self):
        return f"{self.produit.nom} - Quantité: {self.quantite}"

# # Create your models here.
class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def get_prix_total(self):
        return sum(item.prix_u * item.quantite for item in self.orderitem_set.all())
    
    @property
    def montant_tva(self):
        return round((Decimal(self.get_prix_total)*Decimal(19.25))/100)
    
    @property
    def net_payer(self):
        return round(self.montant_tva + self.get_prix_total)
    
    @property
    def get_tranche1(self):
        return round((self.net_payer*30)/100)
    
    @property
    def get_tranche2(self):
        return round((self.net_payer*70)/100)
    
    @property
    def get_statut_actuel(self):
        dernier_traiment = self.traiment_set.order_by('-created_at').first()
        return dernier_traiment.statut if dernier_traiment else "Aucun traitement"
    
    @property
    def infoclient(self):
        try:
            return self.orderuserinfo_set.first()  # si OneToOneField
        except OrderUserInfo.DoesNotExist:
            return None
    
    def __str__(self):
        return f"{self.user} - {self.get_prix_total}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    details = models.JSONField()  # Détails du produit (dimensions, choix d'angle, etc.)
    quantite = models.PositiveIntegerField(default=1)
    prix_u = models.DecimalField(max_digits=10, decimal_places=2)

    def details_to_text(self):
        if not self.details:
            return ""
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items())

    @property
    def get_prix_total(self):
        return self.prix_u*self.quantite
    

    def __str__(self):
        return f"{self.produit.nom} - Quantité: {self.quantite}"

class Traiment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('en_production', 'En production'),
        ('pret_pour_livraison', 'Pret pour livraison'),
        ('solde_facture', 'Solde ma facture'),
        ('termine', 'Livraison termine'),
    ], default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)  # ➕ important pour trier
    
    def __str__(self):
        return f"{self.order}-{self.statut}"
    
class OrderUserInfo(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=255)
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount_paid = models.FloatField(help_text="Montant payé par l'utilisateur")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement - Commande {self.order.id} : {self.amount_paid} fcfa"

class CodePromo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client')
    remise = models.DecimalField(max_digits=10, decimal_places=2)
    code = models.CharField(max_length=255)
    expiration = models.CharField(max_length=255)
