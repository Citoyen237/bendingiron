from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Partenariats)
class PartenariatsAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "soumis_tva", "date_fin")
    list_editable = ("soumis_tva",)          # TVA appliquée ou non, partenaire par partenaire
    list_filter = ("soumis_tva",)
    search_fields = ("name", "email")
admin.site.register(Projet)
admin.site.register(ProjetOrder)
