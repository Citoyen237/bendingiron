"""Angles gérés dans l'admin (table Angle) au lieu d'une liste fixe.

1. crée la table Angle et les 4 angles utilisés aujourd'hui ;
2. reporte les angles déjà cochés (ancienne liste JSON) sur la nouvelle table ;
3. supprime l'ancienne liste.
"""
from decimal import Decimal

import django.core.validators
from django.db import migrations, models

ANGLES_INITIAUX = [(90, "90°", 1), (135, "135°", 2), (-135, "-135°", 3), (180, "180°", 4)]


def creer_angles_et_reporter(apps, schema_editor):
    Angle = apps.get_model("boutique", "Angle")
    ConfigProduit = apps.get_model("boutique", "ConfigProduit")
    for valeur, libelle, ordre in ANGLES_INITIAUX:
        Angle.objects.get_or_create(valeur=valeur, defaults={"libelle": libelle, "ordre": ordre})
    for config in ConfigProduit.objects.all():
        valeurs = config.angles_json or []
        for valeur in valeurs:
            angle, _ = Angle.objects.get_or_create(valeur=valeur, defaults={"libelle": f"{valeur}°"})
            config.angles_proposes.add(angle)


def revenir_a_la_liste(apps, schema_editor):
    ConfigProduit = apps.get_model("boutique", "ConfigProduit")
    for config in ConfigProduit.objects.all():
        config.angles_json = [a.valeur for a in config.angles_proposes.all()]
        config.save(update_fields=["angles_json"])


class Migration(migrations.Migration):

    dependencies = [
        ("boutique", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Angle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("valeur", models.IntegerField(help_text="Ex. : 90, 135, -135, 180", unique=True,
                                               verbose_name="valeur (degrés)")),
                ("libelle", models.CharField(help_text="Affiché au client. Ex. : 90°", max_length=50,
                                             verbose_name="libellé")),
                ("coefficient", models.DecimalField(
                    decimal_places=4, default=Decimal("1"), max_digits=10,
                    help_text="Utilisable dans les formules sous le nom « ka » (l'angle en degrés : « angle »).",
                    validators=[django.core.validators.MinValueValidator(Decimal("0"))],
                    verbose_name="coefficient (ka)")),
                ("actif", models.BooleanField(default=True, help_text="Décoché : n'est plus proposé.")),
                ("ordre", models.PositiveSmallIntegerField(default=0)),
            ],
            options={"verbose_name": "angle", "verbose_name_plural": "angles", "ordering": ["ordre", "valeur"]},
        ),
        # L'ancienne liste est renommée le temps de la conversion
        migrations.RenameField(model_name="configproduit", old_name="angles", new_name="angles_json"),
        migrations.AddField(
            model_name="configproduit",
            name="angles_proposes",
            field=models.ManyToManyField(blank=True, related_name="produits", to="boutique.angle",
                                         verbose_name="angles proposés"),
        ),
        migrations.RunPython(creer_angles_et_reporter, revenir_a_la_liste),
        migrations.RemoveField(model_name="configproduit", name="angles_json"),
        migrations.RenameField(model_name="configproduit", old_name="angles_proposes", new_name="angles"),
        migrations.AlterField(
            model_name="configproduit",
            name="formule_ltp",
            field=models.CharField(help_text="Longueur totale partielle, avec les abréviations des dimensions, "
                                             "d, angle, ka et R. Ex. : 4*Lc",
                                   max_length=255, verbose_name="formule de Ltp"),
        ),
    ]
