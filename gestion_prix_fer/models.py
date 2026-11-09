from django.core.validators import MinValueValidator
from django.db import models

# Types de fer proposés par chaque fournisseur
TYPES_FER = [
    ("FE400", "FE400"),
    ("FE500", "FE500"),
]

# Diamètres disponibles (en mm)
DIAMETRES = [
    (6, "HA6"), (8, "HA8"), (10, "HA10"), (12, "HA12"), (14, "HA14"),
    (16, "HA16"), (20, "HA20"), (22, "HA22"), (25, "HA25"), (32, "HA32"),
]


class Fournisseur(models.Model):
    """Un fournisseur de fer (Prometal, Metafrique...)."""

    nom = models.CharField(max_length=100, unique=True)
    actif = models.BooleanField(
        default=True, help_text="Décoche pour ne plus proposer ce fournisseur aux clients."
    )

    class Meta:
        ordering = ["nom"]
        verbose_name = "fournisseur"
        verbose_name_plural = "fournisseurs"

    def __str__(self):
        return self.nom


class TypeFer(models.Model):
    """Un type de fer (FE400, FE500) vendu par un fournisseur."""

    fournisseur = models.ForeignKey(
        Fournisseur, on_delete=models.CASCADE, related_name="types"
    )
    nom = models.CharField(max_length=10, choices=TYPES_FER)

    class Meta:
        ordering = ["fournisseur__nom", "nom"]
        verbose_name = "type de fer"
        verbose_name_plural = "types de fer"
        constraints = [
            models.UniqueConstraint(
                fields=["fournisseur", "nom"], name="un_seul_type_par_fournisseur"
            )
        ]

    def __str__(self):
        return f"{self.fournisseur} – {self.nom}"


class PrixFerQuerySet(models.QuerySet):
    def disponibles(self):
        """Prix que l'on peut proposer aux clients."""
        return self.filter(
            disponible=True, type_fer__fournisseur__actif=True, prix_vente__gt=0
        )

    def catalogue(self):
        """
        Catalogue prêt à être envoyé au navigateur (en JSON) :
        {fournisseur: {type: {diamètre: {"achat": ..., "vente": ...}}}}
        """
        resultat = {}
        for p in self.disponibles().select_related("type_fer__fournisseur"):
            fournisseur = p.type_fer.fournisseur.nom
            resultat.setdefault(fournisseur, {}).setdefault(p.type_fer.nom, {})[str(p.diametre)] = {
                "achat": float(p.prix_achat),
                "vente": float(p.prix_vente),
            }
        return resultat

class Constante(models.Model):
    """Constantes de calcul des prix (modifiables dans l'admin)."""

    cle = models.CharField(
        max_length=50, unique=True,
        help_text="Identifiant utilisé dans le code (ex : taux_majoration).",
    )
    valeur = models.DecimalField(max_digits=14, decimal_places=4)
    description = models.CharField(max_length=200, blank=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["cle"]
        verbose_name = "constante"
        verbose_name_plural = "constantes"

    def __str__(self):
        return f"{self.cle} = {self.valeur}"

    @classmethod
    def toutes(cls):
        """Dictionnaire {cle: valeur} prêt à être envoyé au navigateur."""
        return {c.cle: float(c.valeur) for c in cls.objects.all()}

class PrixFer(models.Model):
    """Prix d'achat et de vente d'un diamètre, pour un type de fer d'un fournisseur."""

    type_fer = models.ForeignKey(TypeFer, on_delete=models.CASCADE, related_name="prix")
    diametre = models.PositiveSmallIntegerField(choices=DIAMETRES)
    prix_achat = models.DecimalField(
        max_digits=14, decimal_places=3, default=0, validators=[MinValueValidator(0)],
        help_text="Ce que coûte le fer à l'entreprise (FCFA).",
    )
    prix_vente = models.DecimalField(
        max_digits=14, decimal_places=3, default=0, validators=[MinValueValidator(0)],
        help_text="Ce que paie le client (FCFA). Modifiable à tout moment.",
    )
    disponible = models.BooleanField(
        default=True, help_text="Décoche pour retirer ce diamètre de l'offre."
    )
    modifie_le = models.DateTimeField(auto_now=True)

    objects = PrixFerQuerySet.as_manager()

    class Meta:
        ordering = ["type_fer__fournisseur__nom", "type_fer__nom", "diametre"]
        verbose_name = "prix du fer"
        verbose_name_plural = "prix des fers"
        constraints = [
            models.UniqueConstraint(
                fields=["type_fer", "diametre"], name="un_seul_prix_par_diametre"
            )
        ]

    def __str__(self):
        return f"{self.type_fer} – HA{self.diametre}"

    @property
    def fournisseur(self):
        return self.type_fer.fournisseur

    @property
    def marge(self):
        """Gain par unité : prix de vente moins prix d'achat."""
        return self.prix_vente - self.prix_achat

    @property
    def taux_marge(self):
        """Marge en pourcentage du prix d'achat (None si le prix d'achat est nul)."""
        if not self.prix_achat:
            return None
        return round(self.marge / self.prix_achat * 100, 1)