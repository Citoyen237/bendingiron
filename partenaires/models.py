from django.db import models , transaction
from auth_app.models import CustomUser as User
from django.utils import timezone
from produits.models import *
from django.db.models import Sum
from decimal import Decimal


def commandes_projet_annulees():
    """Identifiants des commandes projet annulées (sous-requête)."""
    from usesOrders.models import Annulation
    return Annulation.objects.filter(type_commande="projet").values("commande_id")
# Create your models here.
class CompteurFactureProj(models.Model):
    annee = models.PositiveIntegerField(unique=True)
    dernier = models.PositiveIntegerField(default=0) 

class Partenariats(models.Model):
    # referent
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    adresse=models.CharField(max_length=255)
    telephone = models.CharField(max_length=200)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    # TVA décidée par l'admin pour ce partenaire (14/11/2026) ; figée sur chaque projet
    soumis_tva = models.BooleanField("Appliquer la TVA", default=True,
                                     help_text="Décocher pour ne pas facturer la TVA à ce partenaire "
                                               "(projets et travaux additionnels créés ensuite).")

    class Meta:
        verbose_name = "partenariat"
        verbose_name_plural = "Partenariats"

    @property
    def is_expired(self):
        return timezone.now()>self.date_fin
    
    
    @property
    def nb_projet(self):
        return self.projet_set.count()
    
    @property
    def montant(self):
        total =sum(item.net_payer for item in self.projet_set.all())
        return round(total)

    def __str__(self):
        return self.name

class Projet(models.Model):
    partenariat=models.ForeignKey(Partenariats, on_delete=models.CASCADE)
    # TVA figée à la création (19,25 ou 0 = exonéré), décidée par l'admin (usesOrders/tva.py)
    taux_tva = models.DecimalField("Taux de TVA (%)", max_digits=5, decimal_places=2, default=Decimal("19.25"),
                                   help_text="19,25 ou 0 (exonéré). Figé à la création de la commande.")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=255, unique=True)
    annee = models.PositiveIntegerField(editable=False)
    sequence = models.PositiveIntegerField(editable=False)
    statut=models.CharField(max_length=255, default='en cours') 
    reduction=models.IntegerField(default=15)
    frais_ingenieurie=models.CharField(max_length=255, default=5000)
    created_at= models.DateTimeField(auto_now_add=True)
    update_at= models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name','partenariat'],name='unique_name_partenariat'),
             models.UniqueConstraint(
                fields=["annee", "sequence"],
                name="orderproj_numero_unique",
            )
        ]
    
    def save(self, *args, **kwargs):
        if self.pk:
            return super().save(*args, **kwargs)

        with transaction.atomic():
            annee = timezone.localdate().year
            compteur, _ = (
                CompteurFactureProj.objects.select_for_update()
                .get_or_create(annee=annee)
            )
            compteur.dernier += 1
            compteur.save(update_fields=["dernier"])

            self.annee = annee
            self.sequence = compteur.dernier
            super().save(*args, **kwargs)

    @property
    def numero(self):
        return f"{self.sequence:03d}"   # ex. 00001

    def __str__(self):
        return self.name
    
    @property
    def prix_revient_total(self):
        return sum(item.prix_revient for item in self.projetitems.all())
    
    @property
    def montant_total(self):
        return sum(item.prix_u * item.quantite for item in self.projetitems.all())
    
    @property
    def montant_apres_remise(self):
        return round(self.montant_total-((self.prix_revient_total*self.reduction)/100))
    
    @property
    def montant_tva(self):
        from usesOrders.tva import calculer_tva
        return calculer_tva(self.montant_apres_remise, self.taux_tva)

    @property
    def net_payer(self):
        # frais_ingenieurie est stocké en texte (CharField) : conversion avant le calcul
        return round(self.montant_tva + self.montant_apres_remise + self.frais_ingenieurie_montant)

    @property
    def frais_ingenieurie_montant(self):
        try:
            return Decimal(str(self.frais_ingenieurie or 0))
        except Exception:
            return Decimal(0)
    
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
        ).exclude(projet_order_id__in=commandes_projet_annulees()).aggregate(
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
    
    # Livraisons partielles (règle du 13/11/2026) : chaque tranche payée ouvre un
    # PLAFOND, vérifié en comptant la demande en cours (avant : seul le déjà
    # livré était regardé, et une seule demande pouvait prendre 100 % du projet).
    #   aucune tranche -> 0 %   1re -> 50 %   1re + 2e -> 90 %   les 3 -> 100 %
    # Pourcentage = pièces demandées / pièces prévues (demandes annulées exclues).
    PLAFONDS_LIVRAISON = {0: 0, 1: 50, 2: 90, 3: 100}

    @staticmethod
    def libelle_tranche(numero):
        return "1re" if numero == 1 else f"{numero}e"

    @property
    def tranches_payees(self):
        """Nombre de tranches payées dans l'ordre (1, puis 2, puis 3)."""
        payees = set(self.paiements.values_list("tranche", flat=True))
        n = 0
        while n + 1 in payees:
            n += 1
        return n

    @property
    def plafond_livraison(self):
        """Pourcentage maximal du projet livrable avec les tranches payées."""
        return self.PLAFONDS_LIVRAISON[self.tranches_payees]

    @property
    def quantite_max_livrable(self):
        """Pièces livrables au plus (plafond, arrondi à la pièce inférieure)."""
        return self.quantite_totale_commandee * self.plafond_livraison // 100

    @property
    def marge_plafond(self):
        """Part du projet (en %) encore demandable avec les tranches payées (barre d'avancement)."""
        return max(round(self.plafond_livraison - self.pourcentage_realisation, 2), 0)

    @property
    def quantite_encore_demandable(self):
        return max(self.quantite_max_livrable - self.quantite_commande_totale, 0)

    @property
    def peut_commander(self):
        return self.quantite_encore_demandable > 0

    def erreur_plafond(self, quantite_demandee):
        """Message si la demande dépasse le plafond des tranches payées, sinon None."""
        if quantite_demandee <= self.quantite_encore_demandable:
            return None
        n = self.tranches_payees
        if n == 0:
            return "La 1re tranche n'est pas encore payée : aucune livraison possible."
        message = (f"Avec {'les ' + str(n) + ' premières tranches payées' if n > 1 else 'la 1re tranche payée'}, "
                   f"vous pouvez vous faire livrer jusqu'à {self.plafond_livraison} % du projet "
                   f"({self.quantite_max_livrable} pièce(s)). Vous pouvez encore demander "
                   f"{self.quantite_encore_demandable} pièce(s).")
        if n < 3:
            message += f" Payez la {self.libelle_tranche(n + 1)} tranche pour aller plus loin."
        return message

    @property
    def message_etape_suivante(self):
        if self.peut_commander or not self.quantite_totale_commandee:
            return ""
        n = self.tranches_payees
        if n >= 3 or self.quantite_commande_totale >= self.quantite_totale_commandee:
            return ""        # tout est payé ou tout est déjà demandé
        suivante = self.libelle_tranche(n + 1)
        if n == 0:
            return f"La {suivante} tranche n'est pas encore payée."
        return f"Plafond de {self.plafond_livraison} % atteint : la {suivante} tranche n'est pas encore payée."
    
    @property
    def toutes_commandes_terminees(self):
        # Les commandes annulées ne comptent pas
        orders = self.projetorder_set.exclude(id__in=commandes_projet_annulees())
        if not orders.exists():
            return False  # pas de commandes → pas terminé
        return all(order.get_statut_actuel == "termine" for order in orders)
    
    @property
    def get_statut(self):
        statut = "en cours"
        if self.is_solde and self.pourcentage_realisation == 100:
            if self.toutes_commandes_terminees:
                statut = "termine"
        return statut
    
    @classmethod
    def montant_total_projets_solde(cls):
        total = Decimal(0)
        for projet in cls.objects.all():
            if projet.is_solde:
                total += projet.net_payer
        return total
    
    @property
    def benefice(self):
        return (self.prix_revient_total*self.reduction)/100
    
    @classmethod
    def benefice_total(cls):
        total = Decimal(0)
        for projet in cls.objects.all():
            total += projet.benefice
        return total

class ProjetItem(models.Model):
    projet = models.ForeignKey(Projet,related_name='projetitems', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    details = models.JSONField()  # Détails du produit (dimensions, choix d'angle, etc.)
    prix_revient=models.DecimalField(max_digits=10, decimal_places=2)
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
        # Une commande projet annulée rend ses quantités au « restant »
        return self.orders_items.filter(
                projet_order__projet=self.projet
            ).exclude(projet_order_id__in=commandes_projet_annulees()).aggregate(
                total=Sum('quantite')
            )['total'] or 0

    @property
    def quantite_restant(self):
        return self.quantite-self.quantite_commande
    
    # affiche ds json files
    def details_to_text(self):
        if not self.details:
            return ""
        # « dessin_svg » : dessin 70 x 70 px du gabarit universel, affiché en image, pas en texte
        return " | ".join(f"{key.capitalize()} : {value}" for key, value in self.details.items()
                          if key != "dessin_svg")
    
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
    # Montant figé au moment du paiement : il ne change plus si le projet est
    # modifié ensuite (articles, réduction, frais d'ingénierie).
    montant = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True,
                                  help_text="Montant de la tranche au moment du paiement (FCFA)")
    date_paiement = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paiements_enregistres')
    mode_paiement = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('projet', 'tranche')  # On ne paie une tranche qu'une seule fois
        ordering = ['tranche']

    def __str__(self):
        return f"{self.projet.name} - Tranche {self.tranche}"

    @staticmethod
    def montant_prevu(projet, tranche):
        """Montant de la tranche selon le total ACTUEL du projet (40 % / 40 % / 20 %)."""
        return {1: projet.tranche1, 2: projet.tranche2, 3: projet.tranche3}.get(tranche, 0)

    @staticmethod
    def prochaine_tranche(projet):
        """Tranches payées dans l'ordre 1 -> 2 -> 3 : renvoie la suivante, ou None si tout est payé."""
        payees = set(projet.paiements.values_list('tranche', flat=True))
        for numero, _ in PaiementProjet.TRANCHES:
            if numero not in payees:
                return numero
        return None

    def save(self, *args, **kwargs):
        if self.montant is None:
            self.montant = self.montant_prevu(self.projet, self.tranche)
        super().save(*args, **kwargs)

class ProjetOrder(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    STATUTS_AFFICHES = {   # statut -> (libellé pour le partenaire, couleur du badge)
        "en_attente": ("En attente", "bg-warning text-dark"),
        "en_production": ("En production", "bg-primary"),
        "pret_pour_livraison": ("Prête pour livraison", "bg-info text-dark"),
        "termine": ("Livrée", "bg-success"),
        "annule": ("Annulée", "bg-danger"),
    }

    @property
    def statut_affiche(self):
        return self.STATUTS_AFFICHES.get(self.get_statut_actuel, ("Aucun traitement", "bg-secondary"))

    @property
    def annulation(self):
        """Annulation enregistrée (date, motif), ou None."""
        from usesOrders.models import Annulation
        return Annulation.objects.filter(type_commande="projet", commande_id=self.id).first()

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
        ('annule', 'Annulée'),
    ], default='en_attente')
    created_at = models.DateTimeField(auto_now_add=True)  # ➕ important pour trier
    
    def __str__(self):
        return f"{self.projet_order}-{self.statut}"


class CompteurFactureAdd(models.Model):
    annee = models.PositiveIntegerField(unique=True)
    dernier = models.PositiveIntegerField(default=0)

# Create your models here.
class OrderAdd(models.Model):
    projet_order= models.ForeignKey(Projet,related_name='projet_add', on_delete=models.CASCADE)
    # TVA figée à la création (19,25 ou 0 = exonéré), décidée par l'admin (usesOrders/tva.py)
    taux_tva = models.DecimalField("Taux de TVA (%)", max_digits=5, decimal_places=2, default=Decimal("19.25"),
                                   help_text="19,25 ou 0 (exonéré). Figé à la création de la commande.")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    annee = models.PositiveIntegerField(editable=False)
    sequence = models.PositiveIntegerField(editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["annee", "sequence"],
                name="orderadd_numero_unique",
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
                CompteurFactureAdd.objects.select_for_update()
                .get_or_create(annee=annee)
            )
            compteur.dernier += 1
            compteur.save(update_fields=["dernier"])

            self.annee = annee
            self.sequence = compteur.dernier
            super().save(*args, **kwargs)

    @property
    def prix_revient_total(self):
        return sum(item.prix_revient for item in self.orderitemadd_set.all())
    
    #def montant_remise(self):
        #return (self.prix_revient_total*self.remise)/100

    @property
    def get_prix_total(self):
        total =sum(item.prix_u * item.quantite for item in self.orderitemadd_set.all())
        return round(Decimal(total))

    @property
    def montant_tva(self):
        from usesOrders.tva import calculer_tva
        return calculer_tva(self.get_prix_total, self.taux_tva)
    
    @property
    def get_statut_actuel(self):
        dernier_traiment = self.traimentadd_set.order_by('-created_at').first()
        return dernier_traiment.statut if dernier_traiment else "Aucun traitement"

    @property
    def net_payer(self):
        return round(self.montant_tva + self.get_prix_total)  
    
    @property
    def total_paye(self):
        return self.payments_add.aggregate(total=Sum("amount_paid"))["total"] or Decimal("0")

    @property
    def reste_a_payer(self):
        return max(Decimal(self.net_payer) - self.total_paye, Decimal("0"))  
    
    def __str__(self):
        return f"{self.user} - {self.get_prix_total}"

class OrderItemAdd(models.Model):
    order = models.ForeignKey(OrderAdd, on_delete=models.CASCADE)
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

class TraimentAdd(models.Model):
    order = models.ForeignKey(OrderAdd, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

class PaymentAdd(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(OrderAdd, on_delete=models.CASCADE, related_name="payments_add")
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, help_text="Montant payé")
    mode_paid = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement - Commande {self.order_id} : {self.amount_paid} fcfa" 