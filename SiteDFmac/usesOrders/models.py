from django.db import models
from auth_app.models import CustomUser
from produits.models import *
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def prix_revient_total(self):
        return sum(item.prix_revient for item in self.items.all())
    
    def montant_remise(self):
        return (self.prix_revient_total*self.remise)/100

    @property
    def get_prix_total(self):
        total =sum(item.prix_u * item.quantite for item in self.items.all())
        return round(Decimal(total) - self.montant_remise())

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
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    details = models.JSONField()  # Détails du produit (dimensions, choix d'angle, etc.)
    quantite = models.PositiveIntegerField(default=1)
    prix_revient=models.DecimalField(max_digits=10, decimal_places=2)
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
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def prix_revient_total(self):
        return sum(item.prix_revient for item in self.orderitem_set.all())
    
    def montant_remise(self):
        return (self.prix_revient_total*self.remise)/100

    @property
    def get_prix_total(self):
        total =sum(item.prix_u * item.quantite for item in self.orderitem_set.all())
        return round(Decimal(total) - self.montant_remise())

    @property
    def montant_tva(self):
        return round((Decimal(self.get_prix_total)*Decimal(19.25))/100)
    
    @property
    def net_payer(self):
        return round(self.montant_tva + self.get_prix_total)

    # @property
    # def get_prix_total(self):
    #     total=sum(item.prix_u * item.quantite for item in self.orderitem_set.all())
    #     return total
    
    # @property
    # def montant_tva(self):
    #     return round((Decimal(self.get_prix_total)*Decimal(19.25))/100)
    
    # @property
    # def net_payer(self):
    #     return round(self.montant_tva + self.get_prix_total)
    
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
    prix_revient=models.DecimalField(max_digits=10, decimal_places=2)
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
    '''retrait en usine, livraison sur chantier'''
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=255)
    mode_livraison= models.CharField(max_length=255, default="livraison sur chantier")
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
    expiration = models.PositiveIntegerField(default=0)
    nb_utilidation = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def expiration_date(self):
        """Date exacte d’expiration du code promo"""
        return self.created_at + relativedelta(months=self.expiration)

    @property
    def is_expired(self):
        """Retourne True si le code est expiré"""
        return timezone.now() > self.expiration_date

    def is_valid_for(self, client):
        """Vérifie que le code est pour ce client et valide"""
        return self.client == client and not self.is_expired
    
    # Nombre total d'utilisations (grâce au 2ème modèle)
    @property
    def total_uses(self):
        return self.codesuses.count()
    
    # controle si le nombre d'utilisation est atteint
    @property 
    def nb_uses_atteint(self):
        if self.total_uses >= self.nb_utilidation :
            # il ne peut plus utiliser le code
            return True
        else : 
            # il peut utiliser le code 
            return False
    
    @property
    def statut(self):
        if self.expiration == 0 :
            return self.nb_uses_atteint
        if self.nb_utilidation == 0 :
            return self.is_expired


    # # Nombre d'utilisations par un utilisateur précis
    # def user_uses(self, user):
    #     return self.codesuses.filter(user=user).count()



class CodePromoUse(models.Model):
    promo_code = models.ForeignKey(CodePromo, on_delete=models.CASCADE, related_name="codesuses")
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.promo_code.code}"
