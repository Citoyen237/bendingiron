"""Tolérances par diamètre PROVISOIRES (13/11/2026), à corriger par l'admin dans
« larue » → Boutique → Tolérances par diamètre.

Ne crée une ligne que si le diamètre n'en a pas encore : une valeur déjà saisie
par l'admin n'est jamais écrasée.
"""
from decimal import Decimal

from django.db import migrations

VALEURS = {6: "3", 8: "4.5", 10: "6", 12: "7.5", 14: "9", 16: "10.5", 20: "12", 22: "13.5", 25: "15", 32: "16.5"}


def ajouter(apps, schema_editor):
    ToleranceDiametre = apps.get_model("boutique", "ToleranceDiametre")
    for diametre, valeur in VALEURS.items():
        ToleranceDiametre.objects.get_or_create(diametre=diametre, defaults={"valeur": Decimal(valeur)})


def retirer(apps, schema_editor):
    """Retire seulement les valeurs provisoires restées telles quelles."""
    ToleranceDiametre = apps.get_model("boutique", "ToleranceDiametre")
    for diametre, valeur in VALEURS.items():
        ToleranceDiametre.objects.filter(diametre=diametre, valeur=Decimal(valeur)).delete()


class Migration(migrations.Migration):
    dependencies = [("boutique", "0006_tolerance_par_diametre")]
    operations = [migrations.RunPython(ajouter, retirer)]
