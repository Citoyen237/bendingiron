from django.db import models, transaction
from auth_app.models import CustomUser
from produits.models import *
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.db.models import Sum

class CompteurFacturePro(models.Model):
    annee = models.PositiveIntegerField(unique=True)
    dernier = models.PositiveIntegerField(default=0)

# Create your models here.
class OrderPro(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    annee = models.PositiveIntegerField(editable=False)
    sequence = models.PositiveIntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["annee", "sequence"],
                name="orderpro_numero_unique",
            )
        ]

    @property
    def numero(self):
        return f"{self.sequence:03d}"   # ex. 00001

    def save(self, *args, **kwargs):
        if self.pk:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            annee = timezone.localdate().year
            compteur, _ = (
                CompteurFacturePro.objects.select_for_update()
                .get_or_create(annee=annee)
            )
            compteur.dernier += 1
            compteur.save(update_fields=["dernier"])

            self.annee = annee
            self.sequence = compteur.dernier
            super().save(*args, **kwargs)

    @property
    def prix_revient_total(self):
        return sum(item.prix_revient for item in self.orderitempro_set.all())
    
    def montant_remise(self):
        return (self.prix_revient_total*self.remise)/100

    @property
    def get_prix_total(self):
        total =sum(item.prix_u * item.quantite for item in self.orderitempro_set.all())
        return round(Decimal(total) - self.montant_remise())

    @property
    def montant_tva(self):
        return round((Decimal(self.get_prix_total)*Decimal(19.25))/100)
    
    @property
    def net_payer(self):
        return round(self.montant_tva + self.get_prix_total)

    @property
    def total_paye(self):
        return self.payments.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")

    @property
    def reste_a_payer(self):
        return max(Decimal(self.net_payer) - self.total_paye, Decimal("0"))

    @property
    def est_solde(self):
        return self.reste_a_payer <= 0

    # @property
    # def get_prix_total(self):
    #     total=sum(item.prix_u * item.quantite for item in self.orderitem_set.all())
    #     return total
    
    # @property
    # def montant_tva(self):
    #     return round((Decimal(self.get_prix_total)*Decimal(19.25))/100)
    
    @property
    def est_supprimable(self):
        dernier = self.traimentpro_set.order_by("-created_at", "-pk").first()
        statut_ok = dernier is None or dernier.statut == "en_attente"
        a_paiement = PaymentPro.objects.filter(order=self).exists()
        return statut_ok and not a_paiement
    
    @property
    def get_tranche1(self):
        return round((self.net_payer*30)/100)
    
    @property
    def get_tranche2(self):
        return round((self.net_payer*70)/100)
    
    @property
    def get_statut_actuel(self):
        dernier_traiment = self.traimentpro_set.order_by('-created_at').first()
        return dernier_traiment.statut if dernier_traiment else "Aucun traitement"
    
    @property
    def est_termine(self):
        return self.get_statut_actuel == "termine"
    
    @property
    def infoclient(self):
        try:
            return self.orderuserinfopro_set.first()  # si OneToOneField
        except OrderUserInfo.DoesNotExist:
            return None
    
    @property
    def statut_final(self):
        if self.get_statut_actuel == "annule":
            return "Annulée"
        if self.est_termine and self.est_solde:
            return "Terminée et soldée"
        if self.est_termine:
            return "Terminée, reste à payer"
        if self.est_solde:
            return "Soldée, production en cours"
        return "En cours"
    
    def __str__(self):
        return f"{self.user} - {self.get_prix_total}"

class OrderItemPro(models.Model):
    order = models.ForeignKey(OrderPro, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    details = models.JSONField()  # Détails du produit (dimensions, choix d'angle, etc.)
    quantite = models.PositiveIntegerField(default=1)
    prix_revient=models.DecimalField(max_digits=10, decimal_places=2)
    prix_u = models.DecimalField(max_digits=10, decimal_places=2)

    def details_to_text(self):
        if not self.details:
            return ""
        # « dessin_svg » : dessin 70 x 70 px du gabarit universel, affiché en image, pas en texte
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items()
                          if key != "dessin_svg")

    @property
    def get_prix_total(self):
        return self.prix_u*self.quantite
    

    def __str__(self):
        return f"{self.produit.nom} - Quantité: {self.quantite}"

class TraimentPro(models.Model):
    order = models.ForeignKey(OrderPro, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('en_production', 'En production'),
        ('pret_pour_livraison', 'Pret pour livraison'),
        ('termine', 'Livraison termine'),
        ('annule', 'Annulée'),
    ], default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)  # ➕ important pour trier
    
    def __str__(self):
        return f"{self.order}-{self.statut}"
    
class OrderUserInfoPro(models.Model):
    '''retrait en usine, livraison sur chantier'''
    order = models.ForeignKey(OrderPro, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    telephone = models.CharField(max_length=255)
    mode_livraison= models.CharField(max_length=255, default="livraison sur chantier")
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class PaymentPro(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderPro, on_delete=models.CASCADE, related_name="payments")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, help_text="Montant payé")
    mode_paid = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement - Commande {self.order_id} : {self.amount_paid} fcfa"