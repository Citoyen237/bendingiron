from django.contrib import admin
from .models import CustomUser

# Register your models here.



@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "soumis_tva", "is_active")
    list_editable = ("soumis_tva",)          # TVA appliquée ou non, client par client
    list_filter = ("soumis_tva", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")