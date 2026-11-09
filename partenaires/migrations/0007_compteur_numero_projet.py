"""Numérotation des projets (année + séquence) : migration manquante.

Le modèle CompteurFactureProj et les champs Projet.annee / Projet.sequence
existaient dans le code sans migration (les tests ne pouvaient pas créer de
projet). Sur une base où ces colonnes existent déjà, appliquer avec --fake.
"""
from django.db import migrations, models


def numeroter_projets_existants(apps, schema_editor):
    """Numéro unique par année, dans l'ordre de création, puis compteur réglé.
    Ne fait rien si les numéros sont déjà tous différents."""
    from django.db.models import Count

    Projet = apps.get_model("partenaires", "Projet")
    Compteur = apps.get_model("partenaires", "CompteurFactureProj")

    doublons = (Projet.objects.values("annee", "sequence")
                .annotate(n=Count("pk")).filter(n__gt=1).exists())
    if not doublons:
        return

    derniers = {}
    for projet in Projet.objects.order_by("created_at", "pk"):
        annee = projet.created_at.year
        derniers[annee] = derniers.get(annee, 0) + 1
        Projet.objects.filter(pk=projet.pk).update(annee=annee, sequence=derniers[annee])
    for annee, dernier in derniers.items():
        Compteur.objects.update_or_create(annee=annee, defaults={"dernier": dernier})


class Migration(migrations.Migration):

    dependencies = [
        ("partenaires", "0006_paiementprojet_montant"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompteurFactureProj",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("annee", models.PositiveIntegerField(unique=True)),
                ("dernier", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name="projet",
            name="annee",
            field=models.PositiveIntegerField(default=2026, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="projet",
            name="sequence",
            field=models.PositiveIntegerField(default=1, editable=False),
            preserve_default=False,
        ),
        migrations.RunPython(numeroter_projets_existants, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="projet",
            constraint=models.UniqueConstraint(fields=("annee", "sequence"), name="orderproj_numero_unique"),
        ),
    ]
