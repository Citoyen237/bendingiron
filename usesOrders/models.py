from django.db import models, transaction
from auth_app.models import CustomUser
from produits.models import *
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta

# Create your models here.
class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    @property
    def taux_tva(self):
        """Taux du client propriétaire du panier (case « Appliquer la TVA » de son compte)."""
        from .tva import taux_pour
        return taux_pour(getattr(self.user, "soumis_tva", True))
    created_at = models.DateTimeField(auto_now_add=True)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def prix_revient_total(self):
        return sum(item.prix_revient for item in self.items.all())

    @property
    def montant_ht_brut(self):
        """Total HT avant remise."""
        return Decimal(sum(item.prix_u * item.quantite for item in self.items.all()))

    def montant_remise(self):
        """La remise du code promo s'applique sur le total HT de la facture."""
        return (self.montant_ht_brut * Decimal(self.remise or 0)) / 100

    @property
    def get_prix_total(self):
        return round(self.montant_ht_brut - self.montant_remise())

    @property
    def montant_tva(self):
        from .tva import calculer_tva
        return calculer_tva(self.get_prix_total, self.taux_tva)
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
        # « dessin_svg » : dessin 70 x 70 px du gabarit universel, affiché en image, pas en texte
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items()
                          if key != "dessin_svg")
   
    def __str__(self):
        return f"{self.produit.nom} - Quantité: {self.quantite}"
# # Create your models here.

class CompteurFacture(models.Model):
    annee = models.PositiveIntegerField(unique=True)
    dernier = models.PositiveIntegerField(default=0)


class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # True : la remise porte sur le total HT de la facture (règle actuelle).
    # False : ancienne règle (remise sur le prix de revient) — conservée pour
    # les commandes existantes afin que leurs factures ne changent pas.
    remise_sur_total = models.BooleanField(default=True)
    # TVA figée à la création (19,25 ou 0 = exonéré), décidée par l'admin (usesOrders/tva.py)
    taux_tva = models.DecimalField("Taux de TVA (%)", max_digits=5, decimal_places=2, default=Decimal("19.25"),
                                   help_text="19,25 ou 0 (exonéré). Figé à la création de la commande.")
    annee = models.PositiveIntegerField(editable=False)
    sequence = models.PositiveIntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def prix_revient_total(self):
        return sum(item.prix_revient for item in self.orderitem_set.all())

    @property
    def montant_ht_brut(self):
        """Total HT avant remise."""
        return Decimal(sum(item.prix_u * item.quantite for item in self.orderitem_set.all()))

    def montant_remise(self):
        base = self.montant_ht_brut if self.remise_sur_total else Decimal(self.prix_revient_total)
        return (base * Decimal(self.remise or 0)) / 100

    @property
    def get_prix_total(self):
        return round(self.montant_ht_brut - self.montant_remise())

    @property
    def montant_tva(self):
        from .tva import calculer_tva
        return calculer_tva(self.get_prix_total, self.taux_tva)
    
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
    def annulation(self):
        """Annulation enregistrée (date, motif, remboursement), ou None."""
        return Annulation.objects.filter(type_commande="client", commande_id=self.id).first()

    @property
    def infoclient(self):
        try:
            return self.orderuserinfo_set.first()  # si OneToOneField
        except OrderUserInfo.DoesNotExist:
            return None

    @property
    def paiment_recu(self):
        pass

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["annee", "sequence"],
                name="facture_numero_unique",
            )
        ]

    @property
    def numero(self):
        return f"{self.sequence:05d}"   # ex. 00001

    def save(self, *args, **kwargs):
        if self.pk:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            annee = timezone.localdate().year
            compteur, _ = (
                CompteurFacture.objects.select_for_update()
                .get_or_create(annee=annee)
            )
            compteur.dernier += 1
            compteur.save(update_fields=["dernier"])

            self.annee = annee
            self.sequence = compteur.dernier
            super().save(*args, **kwargs)
    
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
        # « dessin_svg » : dessin 70 x 70 px du gabarit universel, affiché en image, pas en texte
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items()
                          if key != "dessin_svg")

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
        ('annule', 'Annulée'),
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
    # ForeignKey (et non OneToOne) : une commande peut recevoir un acompte PUIS le solde
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
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


# --- Annulation des commandes (13/11/2026) ---
STATUTS_ANNULABLES = [   # dans l'ordre d'avancement
    ("en_attente", "En attente"),
    ("en_production", "En production"),
    ("pret_pour_livraison", "Prêt pour livraison"),
    ("solde_facture", "Facture soldée"),
]


class ReglageCommande(models.Model):
    """Réglages des commandes, modifiables par l'admin dans « larue » (une seule ligne)."""
    annulation_jusqu_a = models.CharField(
        "Annulation permise jusqu'au statut", max_length=20,
        choices=STATUTS_ANNULABLES, default="pret_pour_livraison",
        help_text="Une commande peut être annulée tant que son statut ne dépasse pas celui-ci. "
                  "Une commande « Livraison terminée » ne peut jamais être annulée.")

    class Meta:
        verbose_name = "Réglage des commandes"
        verbose_name_plural = "Réglages des commandes"

    def __str__(self):
        return "Réglages des commandes"

    @classmethod
    def actuel(cls):
        return cls.objects.first() or cls()


class Annulation(models.Model):
    """Trace d'une commande annulée (client, proforma, projet ou travaux additionnels).

    montant_rembourse et montant_retenu sont prévus pour la proposition G
    (partie remboursable / non remboursable) : vides tant qu'elle n'est pas faite.
    """
    TYPES = [
        ("client", "Commande client"),
        ("proforma", "Proforma"),
        ("projet", "Demande de livraison partielle"),
        ("additionnel", "Travaux additionnels"),
    ]
    STATUTS_AVANT = STATUTS_ANNULABLES + [("aucun", "Aucun traitement")]

    type_commande = models.CharField(max_length=20, choices=TYPES)
    commande_id = models.PositiveIntegerField()
    numero = models.CharField(max_length=50, blank=True)
    statut_avant = models.CharField("Statut au moment de l'annulation", max_length=20, choices=STATUTS_AVANT)
    motif = models.TextField(max_length=500)
    montant_commande = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    montant_paye = models.DecimalField("Déjà payé", max_digits=14, decimal_places=2, default=0)
    montant_rembourse = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    montant_retenu = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Remboursement fait hors du site (à la direction), enregistré par l'admin (14/11/2026)
    rembourse_le = models.DateTimeField("Remboursé le", null=True, blank=True)
    rembourse_par = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="remboursements_enregistres")
    mode_remboursement = models.CharField("Mode de remboursement", max_length=50, blank=True)
    reference_remboursement = models.CharField("Référence", max_length=100, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["type_commande", "commande_id"],
                                               name="annulation_unique_par_commande")]
        ordering = ["-created_at"]

    @property
    def montant_a_rembourser(self):
        """Montant rendu au client : saisi par l'admin (proposition G), sinon tout ce
        qui a été payé moins une éventuelle retenue."""
        if self.montant_rembourse is not None:
            return self.montant_rembourse
        return max(self.montant_paye - (self.montant_retenu or 0), 0)

    @property
    def est_rembourse(self):
        return self.rembourse_le is not None

    def __str__(self):
        return f"{self.get_type_commande_display()} {self.numero or self.commande_id} annulée"
