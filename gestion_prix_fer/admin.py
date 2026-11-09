from django.contrib import admin

from .models import Fournisseur, PrixFer, TypeFer


class TypeFerInline(admin.TabularInline):
    model = TypeFer
    extra = 0
    show_change_link = True  # le lien « Modifier » ouvre le type avec ses prix par diamètre


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ("nom", "actif")
    list_editable = ("actif",)
    inlines = [TypeFerInline]


class PrixFerInline(admin.TabularInline):
    model = PrixFer
    extra = 0
    fields = ("diametre", "prix_achat", "prix_vente", "disponible")


@admin.register(TypeFer)
class TypeFerAdmin(admin.ModelAdmin):
    list_display = ("__str__", "fournisseur", "nom")
    list_filter = ("fournisseur",)
    inlines = [PrixFerInline]  # tous les diamètres et leurs prix sur la même page


@admin.register(PrixFer)
class PrixFerAdmin(admin.ModelAdmin):
    """Tableau de tous les prix : on modifie les prix directement dans la liste."""

    list_display = ("diametre_lib", "type_fer", "prix_achat", "prix_vente", "marge_affichee", "disponible", "modifie_le")
    list_display_links = ("diametre_lib",)
    list_editable = ("prix_achat", "prix_vente", "disponible")
    list_filter = ("type_fer__fournisseur", "type_fer__nom", "disponible")
    ordering = ("type_fer__fournisseur__nom", "type_fer__nom", "diametre")
    list_select_related = ("type_fer__fournisseur",)

    @admin.display(description="Diamètre", ordering="diametre")
    def diametre_lib(self, prix):
        return f"HA{prix.diametre}"

    @admin.display(description="Marge")
    def marge_affichee(self, prix):
        taux = prix.taux_marge
        return f"{prix.marge:g} ({taux:g} %)" if taux is not None else f"{prix.marge:g}"

from django.contrib import admin
from .models import Constante

@admin.register(Constante)
class ConstanteAdmin(admin.ModelAdmin):
    list_display = ("cle", "valeur", "description", "modifie_le")
    search_fields = ("cle", "description")