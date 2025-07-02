from django.db import models
# from auth_app.models import *
from auth_app.models import CustomUser
from produits.models import *

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
        #  reduction
        # tva
        return sum(item.prix_u * item.quantite for item in self.orderitem_set.all())
    
    @property
    def get_statut_actuel(self):
        dernier_traiment = self.traiment_set.order_by('-created_at').first()
        return dernier_traiment.statut if dernier_traiment else "Aucun traitement"
    
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
    
# class Payment(models.Model):
#     order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
#     amount_paid = models.FloatField(help_text="Montant payé par l'utilisateur")
#     payment_method = models.CharField(max_length=50, choices=[
#         ('full', 'Paiement intégral'),
#         ('partial', 'Paiement partiel (35%)')
#     ])
#     is_completed = models.BooleanField(default=False, help_text="Indique si le paiement est validé")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Paiement - Commande {self.order.id} : {self.amount_paid} fcfa"
