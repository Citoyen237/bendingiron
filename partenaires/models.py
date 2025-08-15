from django.db import models
from auth_app.models import CustomUser as User
from django.utils import timezone
from produits.models import *
from django.db.models import Sum
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
    
    @property
    def tranche1_payee(self):
        return self.paiements.filter(tranche=1).exists()

    @property
    def tranche2_payee(self):
        return self.paiements.filter(tranche=2).exists()

    @property
    def tranche3_payee(self):
        return self.paiements.filter(tranche=3).exists()
    
    @property
    def is_solde(self):
        return self.tranche1_payee and self.tranche2_payee and self.tranche3_payee
    
    @property
    def quantite_totale_commandee(self):
        # somme la quantité de tous les items liés à ce projet
        return self.projetitems.aggregate(total=models.Sum('quantite'))['total'] or 0 
        # return ProjetItem.objects.filter(
        #    projetitems=self
        # ).aggregate(
        #     total=Sum('quantite')
        # )['total'] or 0
   
    # @property
    # def quantite_commande_totale(self):
    #     # On récupère la somme des quantités commandées de chaque ProjetItem lié au sous commande
    #     total = self.projetitems.annotate(
    #         total_commande=Sum('orders__quantite')
    #     ).aggregate(
    #         somme=Sum('total_commande')
    #     )['somme']

    #     return total or 0
       
    @property
    def quantite_commande_totale(self):
        # On récupère la somme des quantités commandées de chaque ProjetItem lié au sous commande
        total = ProjetOrderItem.objects.filter(
            projet_item__projet=self
        ).aggregate(
            somme=Sum('quantite')
        )['somme']
        return total or 0
    
    @property
    def pourcentage_realisation(self):
        quantite_prevue = self.quantite_totale_commandee
        quantite_commandee = self.quantite_commande_totale

        if quantite_prevue == 0:
            return 0  # éviter division par zéro

        pourcentage = (quantite_commandee / quantite_prevue) * 100
        return round(pourcentage, 2)  # arrondi à 2 décimales
    
    @property
    def peut_passer_a_etape_suivante1(self):
        return self.pourcentage_realisation >= 50 and self.tranche2_payee

    @property
    def peut_passer_a_etape_suivante2(self):
        return self.pourcentage_realisation >= 90 and self.tranche3_payee
    
    # Si réalisation < 50 %, seule la 1ʳᵉ tranche suffit.
    # Si 50 % ≤ réalisation < 90 %, il faut la 2ᵉ tranche.
    # Si réalisation ≥ 90 %, il faut la 3ᵉ tranche.
    @property
    def peut_commander(self):
        if self.pourcentage_realisation < 50:
            return self.tranche1_payee
        elif 50 <= self.pourcentage_realisation < 90:
            return self.tranche2_payee
        elif self.pourcentage_realisation >= 90:
            return self.tranche3_payee
        return False

    @property
    def message_etape_suivante(self):
        if self.peut_commander:
            return ""
        elif self.pourcentage_realisation < 50 and not self.tranche1_payee:
            return "La 1er tranche n'est pas encore payée."
        elif 50 <= self.pourcentage_realisation < 90 and not self.tranche2_payee:
            return "La 2e tranche n'est pas encore payée."
        elif self.pourcentage_realisation >= 90 and not self.tranche3_payee:
            return "La 3e tranche n'est pas encore payée."
        return "Conditions non remplies."
    
    @property
    def get_statut(self):
        statut ="en cours"
        if self.is_solde and self.pourcentage_realisation == 100:
            statut = "termine"
        return statut


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
        """
        Retourne la quantité commandée pour cet item dans les commandes du projet lié.
        """
        return self.orders_items.filter(
                projet_order__projet=self.projet
            ).aggregate(
                total=Sum('quantite')
            )['total'] or 0

    @property
    def quantite_restant(self):
        return self.quantite-self.quantite_commande
    
    # affiche ds json files
    def details_to_text(self):
        if not self.details:
            return ""
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items())
    
    def __str__(self):
        return f'{self.details_to_text()}'


class PaiementProjet(models.Model):
    TRANCHES = (
        (1, '1ère tranche'),
        (2, '2ème tranche'),
        (3, '3ème tranche'),
    )

    projet = models.ForeignKey('Projet', on_delete=models.CASCADE, related_name='paiements')
    tranche = models.PositiveSmallIntegerField(choices=TRANCHES)
    date_paiement = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paiements_enregistres')
    mode_paiement = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('projet', 'tranche')  # On ne paie une tranche qu'une seule fois
        ordering = ['tranche']

    def __str__(self):
        return f"{self.projet.name} - Tranche {self.tranche}"

    @property
    def montant(self):
        if self.tranche == 1:
            return self.projet.tranche1
        elif self.tranche == 2:
            return self.projet.tranche2
        elif self.tranche == 3:
            return self.projet.tranche3
        return 0



class ProjetOrder(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def get_statut_actuel(self):
        dernier_traiment = self.projet_order_name.order_by('-created_at').first()
        return dernier_traiment.statut if dernier_traiment else "Aucun traitement"
    
class ProjetOrderItem(models.Model):
    projet_order= models.ForeignKey(ProjetOrder,related_name='projet_order', on_delete=models.CASCADE)
    projet_item = models.ForeignKey(ProjetItem, related_name='orders_items', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

class TraimentOrder(models.Model):
    projet_order= models.ForeignKey(ProjetOrder,related_name='projet_order_name', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('en_production', 'En production'),
        ('pret_pour_livraison', 'Pret pour livraison'),
        ('termine', 'Livraison termine'),
    ], default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)  # ➕ important pour trier
    
    def __str__(self):
        return f"{self.projet_order}-{self.statut}"