"""Écrans d'administration de l'application « boutique » (admin Django : /larue/)."""
from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html, format_html_join

from gestion_prix_fer.models import DIAMETRES
from produits.models import Produit

from .formules import FormuleInvalide
from .models import (SOUS_CATEGORIES_AUTORISEES, Angle, CoefFaconnage, ConfigProduit,
                     ConstanteSoudure, DimensionProduit, ParametresCalcul, PoidsFer, PrixFerTonne, PrtFer)


def _ha(diametre):
    return f"HA{diametre}"


# ---------------------------------------------------------------------------
# Données communes à tous les produits
# ---------------------------------------------------------------------------
@admin.register(PrixFerTonne)
class PrixFerTonneAdmin(admin.ModelAdmin):
    """Prix du fer à la tonne : modifiables directement dans la liste."""

    list_display = ("diametre_lib", "type_fer", "pat", "pvt", "prt_affiche", "pak_affiche", "pvk_affiche",
                    "modifie_le")
    list_display_links = ("diametre_lib",)
    list_editable = ("pat", "pvt")
    list_filter = ("type_fer__fournisseur", "type_fer__nom", "diametre")
    list_select_related = ("type_fer__fournisseur",)

    @admin.display(description="Diamètre", ordering="diametre")
    def diametre_lib(self, obj):
        return _ha(obj.diametre)

    @admin.display(description="PrT (marque + diamètre)")
    def prt_affiche(self, obj):
        return obj.prt if obj.prt is not None else "à renseigner"

    @admin.display(description="Pak (achat / kg)")
    def pak_affiche(self, obj):
        return f"{obj.pak:.2f}" if obj.pak is not None else "PrT manquant"

    @admin.display(description="Pvk (vente / kg)")
    def pvk_affiche(self, obj):
        return f"{obj.pvk:.2f}" if obj.pvk is not None else "PrT manquant"


@admin.register(PrtFer)
class PrtFerAdmin(admin.ModelAdmin):
    """PrT (poids réel d'une tonne) par marque et diamètre : modifiable dans la liste."""

    list_display = ("diametre_lib", "marque", "prt", "modifie_le")
    list_display_links = ("diametre_lib",)
    list_editable = ("prt",)
    list_filter = ("marque", "diametre")

    @admin.display(description="Diamètre", ordering="diametre")
    def diametre_lib(self, obj):
        return _ha(obj.diametre)


@admin.register(PoidsFer)
class PoidsFerAdmin(admin.ModelAdmin):
    list_display = ("diametre_lib", "kg_par_cm")
    list_display_links = ("diametre_lib",)
    list_editable = ("kg_par_cm",)

    @admin.display(description="Diamètre", ordering="diametre")
    def diametre_lib(self, obj):
        return _ha(obj.diametre)


@admin.register(CoefFaconnage)
class CoefFaconnageAdmin(admin.ModelAdmin):
    list_display = ("diametre_lib", "marque", "coef")
    list_display_links = ("diametre_lib",)
    list_editable = ("coef",)
    list_filter = ("marque", "diametre")

    @admin.display(description="Diamètre", ordering="diametre")
    def diametre_lib(self, obj):
        return _ha(obj.diametre)


@admin.register(ConstanteSoudure)
class ConstanteSoudureAdmin(admin.ModelAdmin):
    list_display = ("diametre_lib", "valeur")
    list_display_links = ("diametre_lib",)
    list_editable = ("valeur",)

    @admin.display(description="Diamètre", ordering="diametre")
    def diametre_lib(self, obj):
        return _ha(obj.diametre)


@admin.register(Angle)
class AngleAdmin(admin.ModelAdmin):
    list_display = ("libelle", "valeur", "coefficient", "actif", "ordre", "nb_produits")
    list_display_links = ("libelle",)
    list_editable = ("coefficient", "actif", "ordre")

    @admin.display(description="Produits qui le proposent")
    def nb_produits(self, obj):
        return obj.produits.count()


@admin.register(ParametresCalcul)
class ParametresCalculAdmin(admin.ModelAdmin):
    """Une seule ligne de paramètres : pas d'ajout s'il en existe déjà une, pas de suppression."""

    list_display = ("__str__", "seuil_ldf", "constante_ldf_court", "constante_ldf_long", "formule_r")

    def has_add_permission(self, request):
        return not ParametresCalcul.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Réglages de chaque produit
# ---------------------------------------------------------------------------
class ConfigProduitForm(forms.ModelForm):
    diametres = forms.TypedMultipleChoiceField(
        label="Diamètres proposés", choices=DIAMETRES, coerce=int,
        widget=forms.CheckboxSelectMultiple)
    angles = forms.ModelMultipleChoiceField(
        label="Angles proposés", queryset=Angle.objects.filter(actif=True), required=False,
        widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = ConfigProduit
        fields = ["produit", "diametres", "angles", "afficher_r", "afficher_ld",
                  "formule_ltp", "formule_r", "forme", "actif"]

    def clean_forme(self):
        return self.cleaned_data.get("forme") or []   # champ vide = pas de dessin

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Seules les familles du gabarit universel sont proposées
        self.fields["produit"].queryset = Produit.objects.filter(
            sous_categorie__in=SOUS_CATEGORIES_AUTORISEES).order_by("sous_categorie", "nom")


class DimensionFormSet(BaseInlineFormSet):
    """Vérifie la formule de Ltp avec les dimensions ET les angles saisis sur la même page."""

    def __init__(self, *args, angles=None, **kwargs):
        self.angles_coches = angles
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        dimensions, vues = [], set()
        for form in self.forms:
            data = getattr(form, "cleaned_data", None)
            if not data or data.get("DELETE"):
                continue
            abr = data["abreviation"]
            if abr in vues:
                raise ValidationError(f"L'abréviation « {abr} » est utilisée deux fois.")
            vues.add(abr)
            dimensions.append((abr, data["minimum"], data["maximum"]))
        if not dimensions:
            raise ValidationError("Ajoutez au moins une dimension.")
        if not self.instance.formule_ltp or not self.instance.diametres:
            return   # l'erreur est déjà affichée sur le champ concerné
        try:
            self.instance.verifier_formule_ltp(dimensions, angles=self.angles_coches)
        except FormuleInvalide as exc:
            message = str(exc)
            raise ValidationError(message if message.startswith("Forme") else f"Formule de Ltp : {message}")


class DimensionInline(admin.TabularInline):
    model = DimensionProduit
    formset = DimensionFormSet
    extra = 1
    fields = ("ordre", "libelle", "abreviation", "minimum", "maximum")


@admin.register(ConfigProduit)
class ConfigProduitAdmin(admin.ModelAdmin):
    form = ConfigProduitForm
    inlines = [DimensionInline]
    list_display = ("produit", "famille", "diametres_lib", "formule_ltp", "actif", "modifie_le")
    list_filter = ("actif", "produit__sous_categorie")
    list_select_related = ("produit",)
    search_fields = ("produit__nom",)
    readonly_fields = ("apercu",)

    def get_formset_kwargs(self, request, obj, inline, prefix):
        """Transmet aux dimensions les angles cochés dans le formulaire envoyé."""
        kwargs = super().get_formset_kwargs(request, obj, inline, prefix)
        if isinstance(inline, DimensionInline) and request.method == "POST":
            ids = [i for i in request.POST.getlist("angles") if i.isdigit()]
            kwargs["angles"] = list(Angle.objects.filter(pk__in=ids, actif=True))
        return kwargs
    fieldsets = (
        (None, {"fields": ("produit", "actif")}),
        ("Choix proposés au client", {"fields": ("diametres", "angles", "afficher_r", "afficher_ld")}),
        ("Formules et dessin", {"fields": ("formule_ltp", "formule_r", "forme", "apercu"),
                      "description": "Variables : abréviations des dimensions, d (diamètre), "
                                     "angle (degrés), ka (coefficient de l'angle), R. "
                                     "Fonctions : ceil, floor, round, min, max, sqrt, sin, cos, tan "
                                     "(angles en degrés)."}),
    )

    @admin.display(description="Famille", ordering="produit__sous_categorie")
    def famille(self, obj):
        return obj.produit.sous_categorie

    @admin.display(description="Diamètres")
    def diametres_lib(self, obj):
        return ", ".join(_ha(d) for d in obj.diametres)

    @admin.display(description="Aperçu de Ltp (aux minimums puis aux maximums)")
    def apercu(self, obj):
        if not obj or not obj.pk:
            return "Enregistrez d'abord le produit et ses dimensions."
        dimensions = [(x.abreviation, x.minimum, x.maximum) for x in obj.dimensions.all()]
        if not dimensions:
            return "Aucune dimension."
        try:
            lignes = obj.verifier_formule_ltp(dimensions)
        except FormuleInvalide as exc:
            return format_html('<span style="color:#b00">{}</span>', exc)
        return format_html_join(
            "", "<div>{} → <b>Ltp = {} cm</b></div>",
            ((", ".join(f"{k} = {v:g}" for k, v in valeurs.items()), f"{ltp:g}") for valeurs, ltp in lignes),
        )
