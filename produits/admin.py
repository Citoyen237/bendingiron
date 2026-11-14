from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Categorie)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ("nom", "sous_categorie", "categorie", "disponible")
    list_editable = ("disponible",)          # geler / dégeler directement depuis la liste
    list_filter = ("disponible", "sous_categorie", "categorie")
    search_fields = ("nom",)
    actions = ["geler", "degeler"]

    @admin.action(description="Geler (indisponible pour le moment)")
    def geler(self, request, queryset):
        n = queryset.update(disponible=False)
        self.message_user(request, f"{n} produit(s) gelé(s).")

    @admin.action(description="Rendre disponible")
    def degeler(self, request, queryset):
        n = queryset.update(disponible=True)
        self.message_user(request, f"{n} produit(s) de nouveau disponible(s).")
admin.site.register(FerPrice)