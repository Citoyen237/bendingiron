from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Order)
admin.site.register(Traiment)
admin.site.register(OrderUserInfo)
admin.site.register(CodePromo)

@admin.register(ReglageCommande)
class ReglageCommandeAdmin(admin.ModelAdmin):
    """Une seule ligne de réglages : on la modifie, on n'en crée pas d'autre."""
    list_display = ("__str__", "annulation_jusqu_a")

    def has_add_permission(self, request):
        return not ReglageCommande.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Annulation)
class AnnulationAdmin(admin.ModelAdmin):
    list_display = ("created_at", "type_commande", "numero", "statut_avant", "montant_commande", "montant_paye",
                    "montant_rembourse", "rembourse_le", "user")
    list_filter = ("type_commande", "statut_avant", ("rembourse_le", admin.EmptyFieldListFilter))
    search_fields = ("numero", "motif")
    readonly_fields = ("type_commande", "commande_id", "numero", "statut_avant", "montant_commande",
                       "montant_paye", "user", "created_at")
