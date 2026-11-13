"""
Application « boutique » - étape 1 : tables saisies dans l'admin.

Voir LOGIQUE_CALCUL_PRIX.txt à la racine du projet. Rien ici ne modifie
encore les prix affichés aux clients : ces tables seront utilisées par le
moteur de calcul (étape 2) puis par le gabarit universel (étape 4).
"""
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from gestion_prix_fer.models import DIAMETRES, Fournisseur, TypeFer
from produits.models import Produit

from .formules import FormuleInvalide, verifier

# Familles concernées par le gabarit universel (valeurs de Produit.sous_categorie).
# NON concernées : Quincaillerie, Étrier pour bardage et toiture, Boulon d'ancrage à béton.
SOUS_CATEGORIES_AUTORISEES = (
    "Cintrage de cadre",
    "Cintrage de forme",
    "cintrage d'extremite",
    "redressage et decoupage",
)

VALEURS_DIAMETRES = [d for d, _ in DIAMETRES]

# Noms réservés : ils ne peuvent pas servir d'abréviation de dimension
NOMS_RESERVES = {"d", "angle", "ka", "R", "Ld", "Ldf", "Ltp", "Lt", "poids", "coef"}

POSITIF = [MinValueValidator(Decimal("0"))]
STRICTEMENT_POSITIF = [MinValueValidator(Decimal("0.000001"))]


# ---------------------------------------------------------------------------
# 2.1 Prix du fer à la tonne (marque + type + diamètre)
# ---------------------------------------------------------------------------
class PrixFerTonne(models.Model):
    type_fer = models.ForeignKey(TypeFer, on_delete=models.CASCADE, related_name="prix_tonne",
                                 verbose_name="marque et type")
    diametre = models.PositiveSmallIntegerField(choices=DIAMETRES, verbose_name="diamètre")
    pat = models.DecimalField("PaT - prix d'achat par tonne", max_digits=14, decimal_places=2,
                              validators=POSITIF)
    pvt = models.DecimalField("PvT - prix de vente par tonne", max_digits=14, decimal_places=2,
                              validators=POSITIF)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "prix du fer à la tonne"
        verbose_name_plural = "prix du fer à la tonne"
        ordering = ["type_fer__fournisseur__nom", "type_fer__nom", "diametre"]
        constraints = [models.UniqueConstraint(fields=["type_fer", "diametre"],
                                               name="boutique_un_prix_tonne_par_diametre")]

    def __str__(self):
        return f"{self.type_fer} – HA{self.diametre}"

    @property
    def marque(self):
        return self.type_fer.fournisseur

    @property
    def prt(self):
        """PrT de la marque et du diamètre (table « PrT »), ou None s'il n'est pas renseigné."""
        ligne = PrtFer.objects.filter(marque_id=self.type_fer.fournisseur_id, diametre=self.diametre).first()
        return ligne.prt if ligne else None

    @property
    def pak(self):
        """Prix d'achat au kg = PaT / PrT (None si PrT manque)."""
        prt = self.prt
        return self.pat / prt if prt else None

    @property
    def pvk(self):
        """Prix de vente au kg = PvT / PrT (None si PrT manque)."""
        prt = self.prt
        return self.pvt / prt if prt else None


# ---------------------------------------------------------------------------
# 2.1 bis PrT : poids réel d'une tonne (marque + diamètre)
# ---------------------------------------------------------------------------
class PrtFer(models.Model):
    marque = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name="prt")
    diametre = models.PositiveSmallIntegerField(choices=DIAMETRES, verbose_name="diamètre")
    prt = models.DecimalField("PrT - poids réel d'une tonne (kg)", max_digits=10, decimal_places=3,
                              validators=STRICTEMENT_POSITIF,
                              help_text="Remplace le 1000 : Pak = PaT / PrT et Pvk = PvT / PrT.")
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "PrT (poids réel d'une tonne)"
        verbose_name_plural = "PrT (poids réel d'une tonne)"
        ordering = ["marque__nom", "diametre"]
        constraints = [models.UniqueConstraint(fields=["marque", "diametre"],
                                               name="boutique_un_prt_par_marque_diametre")]

    def __str__(self):
        return f"{self.marque} – HA{self.diametre} : {self.prt} kg"


# ---------------------------------------------------------------------------
# 2.2 Poids au cm (diamètre)
# ---------------------------------------------------------------------------
class PoidsFer(models.Model):
    diametre = models.PositiveSmallIntegerField(choices=DIAMETRES, unique=True, verbose_name="diamètre")
    kg_par_cm = models.DecimalField("poids au cm (kg/cm)", max_digits=12, decimal_places=6,
                                    validators=STRICTEMENT_POSITIF)

    class Meta:
        verbose_name = "poids du fer au cm"
        verbose_name_plural = "poids du fer au cm"
        ordering = ["diametre"]

    def __str__(self):
        return f"HA{self.diametre} : {self.kg_par_cm} kg/cm"


# ---------------------------------------------------------------------------
# 2.3 Coefficient de façonnage (marque + diamètre), pour tous les produits
# ---------------------------------------------------------------------------
class CoefFaconnage(models.Model):
    marque = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name="coefs_faconnage")
    diametre = models.PositiveSmallIntegerField(choices=DIAMETRES, verbose_name="diamètre")
    coef = models.DecimalField("coefficient", max_digits=10, decimal_places=3, validators=POSITIF,
                               help_text="Ps = coef × Lt / 100")

    class Meta:
        verbose_name = "coefficient de façonnage"
        verbose_name_plural = "coefficients de façonnage"
        ordering = ["marque__nom", "diametre"]
        constraints = [models.UniqueConstraint(fields=["marque", "diametre"],
                                               name="boutique_un_coef_par_marque_diametre")]

    def __str__(self):
        return f"{self.marque} – HA{self.diametre} : {self.coef}"


# ---------------------------------------------------------------------------
# 2.4 Constante de soudure (diamètre)
# ---------------------------------------------------------------------------
class ConstanteSoudure(models.Model):
    diametre = models.PositiveSmallIntegerField(choices=DIAMETRES, unique=True, verbose_name="diamètre")
    valeur = models.DecimalField("constante de soudure", max_digits=10, decimal_places=4,
                                 validators=POSITIF, help_text="Pd = constante × Lt")

    class Meta:
        verbose_name = "constante de soudure"
        verbose_name_plural = "constantes de soudure"
        ordering = ["diametre"]

    def __str__(self):
        return f"HA{self.diametre} : {self.valeur}"


# ---------------------------------------------------------------------------
# 2.4 ter Tolérance du prix (diamètre) — 13/11/2026
# ---------------------------------------------------------------------------
class ToleranceDiametre(models.Model):
    diametre = models.PositiveSmallIntegerField(choices=DIAMETRES, unique=True, verbose_name="diamètre")
    valeur = models.DecimalField("tolérance (FCFA)", max_digits=10, decimal_places=4, validators=POSITIF,
                                 help_text="Ajoutée au prix unitaire : Pu = (Pv + Ps + tolérance + taxe + Pd) × (1 + taux). "
                                           "Sans ligne pour un diamètre, la constante commune « tolerance » s'applique.")

    class Meta:
        verbose_name = "tolérance par diamètre"
        verbose_name_plural = "tolérances par diamètre"
        ordering = ["diametre"]

    def __str__(self):
        return f"HA{self.diametre} : {self.valeur} FCFA"


# ---------------------------------------------------------------------------
# 2.4 bis Angles de pliage (gérés dans l'admin)
# ---------------------------------------------------------------------------
class Angle(models.Model):
    valeur = models.IntegerField("valeur (degrés)", unique=True, help_text="Ex. : 90, 135, -135, 180")
    libelle = models.CharField("libellé", max_length=50, help_text="Affiché au client. Ex. : 90°")
    coefficient = models.DecimalField(
        "coefficient (ka)", max_digits=10, decimal_places=4, default=Decimal("1"), validators=POSITIF,
        help_text="Utilisable dans les formules sous le nom « ka » (l'angle en degrés : « angle »).")
    actif = models.BooleanField(default=True, help_text="Décoché : n'est plus proposé.")
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "angle"
        verbose_name_plural = "angles"
        ordering = ["ordre", "valeur"]

    def __str__(self):
        return self.libelle

    def variables(self):
        """Variables de formule apportées par cet angle."""
        return {"angle": self.valeur, "ka": float(self.coefficient)}


# ---------------------------------------------------------------------------
# 2.5 Paramètres généraux (une seule ligne)
# ---------------------------------------------------------------------------
class ParametresCalcul(models.Model):
    seuil_ldf = models.DecimalField("seuil Ltp (cm)", max_digits=8, decimal_places=2,
                                    default=Decimal("100"), validators=STRICTEMENT_POSITIF)
    constante_ldf_court = models.DecimalField("constante Ldf si Ltp ≤ seuil", max_digits=8,
                                              decimal_places=4, validators=POSITIF)
    constante_ldf_long = models.DecimalField("constante Ldf si Ltp > seuil", max_digits=8,
                                             decimal_places=4, validators=POSITIF)
    formule_r = models.CharField("formule de R par défaut", max_length=255, default="5*d/10",
                                 help_text="Rayon de courbure selon le diamètre d. "
                                           "Chaque produit peut la remplacer.")

    class Meta:
        verbose_name = "paramètres de calcul"
        verbose_name_plural = "paramètres de calcul"

    def __str__(self):
        return "Paramètres de calcul"

    def clean(self):
        try:
            verifier(self.formule_r, {"d"}, [{"d": d} for d in VALEURS_DIAMETRES])
        except FormuleInvalide as exc:
            raise ValidationError({"formule_r": str(exc)})

    def save(self, *args, **kwargs):
        self.pk = 1   # une seule ligne de paramètres : une 2e création remplace la 1re
        if ParametresCalcul.objects.filter(pk=1).exists():
            kwargs["force_insert"] = False
            self._state.adding = False
        super().save(*args, **kwargs)

    @classmethod
    def actuels(cls):
        return cls.objects.filter(pk=1).first()


# ---------------------------------------------------------------------------
# 3. Réglages de chaque produit
# ---------------------------------------------------------------------------
class ConfigProduit(models.Model):
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE, related_name="config_boutique")
    diametres = models.JSONField("diamètres proposés", default=list)
    angles = models.ManyToManyField(Angle, verbose_name="angles proposés", blank=True,
                                    related_name="produits")
    afficher_r = models.BooleanField("afficher R (rayon de courbure)", default=True)
    afficher_ld = models.BooleanField("afficher Ld (départ et fin)", default=True)
    formule_ltp = models.CharField("formule de Ltp", max_length=255,
                                   help_text="Longueur totale partielle, avec les abréviations des "
                                             "dimensions, d, angle, ka et R. Ex. : 4*Lc")
    formule_r = models.CharField("formule de R (facultatif)", max_length=255, blank=True,
                                 help_text="Laisser vide pour utiliser la formule par défaut.")
    forme = models.JSONField(
        "forme (pour le dessin)", default=list, blank=True,
        help_text='Liste de segments : [{"longueur": "Lc", "angle": 90}, …]. « longueur » est une '
                  'formule ; « angle » (degrés ou formule, ex. "angle") est le virage après le segment ; '
                  '"crochet": true pour un crochet Ldf (valeur affichée) ; "cote": false pour ne pas '
                  'écrire la valeur. Vide = pas de dessin.')
    actif = models.BooleanField("utiliser le gabarit universel", default=False,
                                help_text="Reste décoché tant que le produit n'est pas basculé (étape 5).")
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "configuration produit"
        verbose_name_plural = "configurations produit"
        ordering = ["produit__sous_categorie", "produit__nom"]

    def __str__(self):
        return f"Configuration – {self.produit}"

    def clean(self):
        erreurs = {}
        if self.produit_id and self.produit.sous_categorie not in SOUS_CATEGORIES_AUTORISEES:
            erreurs["produit"] = ("Cette famille n'utilise pas le gabarit universel "
                                  "(Quincaillerie, étriers pour bardage et boulons d'ancrage exclus).")
        if not self.diametres:
            erreurs["diametres"] = "Cochez au moins un diamètre."
        elif any(d not in VALEURS_DIAMETRES for d in self.diametres):
            erreurs["diametres"] = "Diamètre inconnu."
        if self.formule_r:
            try:
                verifier(self.formule_r, {"d"}, [{"d": d} for d in (self.diametres or VALEURS_DIAMETRES)])
            except FormuleInvalide as exc:
                erreurs["formule_r"] = str(exc)
        try:
            from .dessin import verifier_structure
            verifier_structure(self.forme)
        except FormuleInvalide as exc:
            erreurs["forme"] = str(exc)
        if erreurs:
            raise ValidationError(erreurs)

    def formule_r_effective(self):
        if self.formule_r:
            return self.formule_r
        parametres = ParametresCalcul.actuels()
        return parametres.formule_r if parametres else "5*d/10"

    def verifier_formule_ltp(self, dimensions, angles=None):
        """dimensions : liste de (abreviation, minimum, maximum).
        angles : angles cochés ; par défaut ceux du produit enregistré, sinon
        tous les angles actifs (produit pas encore enregistré).
        Calcule Ltp aux minimums et aux maximums, pour chaque diamètre et
        chaque angle. Renvoie l'aperçu ; lève FormuleInvalide."""
        from .formules import evaluer

        if angles is None:
            angles = list(self.angles.all()) if self.pk else []
        if not angles:
            angles = list(Angle.objects.filter(actif=True)) or [Angle(valeur=90, libelle="90°")]

        autorisees = {abr for abr, _, _ in dimensions} | {"d", "angle", "ka", "R"}
        jeux = []
        for aux_maximums in (False, True):
            for d in (self.diametres or [8]):
                for angle in angles:
                    valeurs = {abr: float(maxi if aux_maximums else mini) for abr, mini, maxi in dimensions}
                    valeurs.update({"d": d, **angle.variables(),
                                    "R": evaluer(self.formule_r_effective(), {"d": d})})
                    jeux.append(valeurs)
        resultats = verifier(self.formule_ltp, autorisees, jeux)
        if self.forme:
            # La forme doit se dessiner avec les mêmes valeurs (min, max, chaque diamètre et angle) ;
            # elle peut aussi utiliser Ltp, Ldf (= Ld) et Lt.
            import math

            from .dessin import calculer_dessin
            from .formules import noms_utilises
            autorisees_forme = autorisees | {"Ltp", "Ldf", "Ld", "Lt"}
            for i, segment in enumerate(self.forme, start=1):
                for cle in ("longueur", "angle"):
                    if isinstance(segment.get(cle), str):
                        inconnues = noms_utilises(segment[cle]) - autorisees_forme
                        if inconnues:
                            raise FormuleInvalide(f"Forme, segment {i} : abréviation inconnue : "
                                                  + ", ".join(sorted(inconnues)))
            parametres = ParametresCalcul.actuels()
            for valeurs, ltp in zip(jeux, resultats):
                constante = 0
                if parametres:
                    constante = float(parametres.constante_ldf_court if ltp <= parametres.seuil_ldf
                                      else parametres.constante_ldf_long)
                ldf = ltp * constante
                calculer_dessin(self.forme, {**valeurs, "Ltp": ltp, "Ldf": ldf, "Ld": ldf,
                                             "Lt": math.ceil(ltp + ldf)})
        return list(zip(jeux, resultats))


class DimensionProduit(models.Model):
    config = models.ForeignKey(ConfigProduit, on_delete=models.CASCADE, related_name="dimensions")
    libelle = models.CharField("libellé", max_length=100, help_text="Ex. : Longueur du côté")
    abreviation = models.CharField(
        "abréviation", max_length=10,
        validators=[RegexValidator(r"^[A-Za-z][A-Za-z0-9_]*$",
                                   "Lettres, chiffres et _ ; commence par une lettre (ex. Lc).")],
        help_text="Nom utilisé dans la formule. Ex. : Lc")
    minimum = models.DecimalField("minimum (cm)", max_digits=8, decimal_places=2, validators=POSITIF)
    maximum = models.DecimalField("maximum (cm)", max_digits=8, decimal_places=2, validators=POSITIF)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "dimension"
        verbose_name_plural = "dimensions"
        ordering = ["ordre", "id"]
        constraints = [models.UniqueConstraint(fields=["config", "abreviation"],
                                               name="boutique_abreviation_unique_par_produit")]

    def __str__(self):
        return f"{self.libelle} ({self.abreviation})"

    def clean(self):
        erreurs = {}
        if self.abreviation in NOMS_RESERVES:
            erreurs["abreviation"] = f"« {self.abreviation} » est réservé ({', '.join(sorted(NOMS_RESERVES))})."
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            erreurs["maximum"] = "Le maximum doit être supérieur ou égal au minimum."
        if erreurs:
            raise ValidationError(erreurs)
