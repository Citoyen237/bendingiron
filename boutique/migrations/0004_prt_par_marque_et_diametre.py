"""PrT (poids réel d'une tonne) dépend de la MARQUE et du DIAMÈTRE, pas du type.

Avant : un PrT sur chaque ligne de prix (marque × type × diamètre).
Après : une table PrtFer (marque × diamètre) ; les prix à la tonne ne gardent
que PaT et PvT.

La migration reprend le PrT existant. Si deux types d'une même marque ont un
PrT différent pour le même diamètre, elle S'ARRÊTE (rien n'est changé) au lieu
de choisir à la place de l'administrateur.
"""
from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class PrtIncoherent(Exception):
    pass


def verifier_coherence(apps, schema_editor):
    """Lancée AVANT toute modification de tables (MySQL ne peut pas les annuler)."""
    _valeurs_par_marque_diametre(apps)


def _valeurs_par_marque_diametre(apps):
    PrixFerTonne = apps.get_model("boutique", "PrixFerTonne")
    valeurs = {}
    for prix in PrixFerTonne.objects.select_related("type_fer__fournisseur"):
        cle = (prix.type_fer.fournisseur_id, prix.diametre)
        valeurs.setdefault(cle, set()).add(prix.prt)
    incoherents = {cle: v for cle, v in valeurs.items() if len(v) > 1}
    if incoherents:
        Fournisseur = apps.get_model("gestion_prix_fer", "Fournisseur")
        noms = {f.id: f.nom for f in Fournisseur.objects.all()}
        detail = "; ".join(f"{noms.get(m, m)} HA{d} : {sorted(v)}" for (m, d), v in incoherents.items())
        raise PrtIncoherent("PrT différents selon le type pour une même marque et un même diamètre : "
                            + detail + ". Harmonisez-les dans l'admin puis relancez la migration.")
    return valeurs


def copier_prt(apps, schema_editor):
    PrtFer = apps.get_model("boutique", "PrtFer")
    for (marque_id, diametre), v in _valeurs_par_marque_diametre(apps).items():
        PrtFer.objects.create(marque_id=marque_id, diametre=diametre, prt=v.pop())


def restaurer_prt(apps, schema_editor):
    PrixFerTonne = apps.get_model("boutique", "PrixFerTonne")
    PrtFer = apps.get_model("boutique", "PrtFer")
    for prix in PrixFerTonne.objects.select_related("type_fer"):
        ligne = PrtFer.objects.filter(marque_id=prix.type_fer.fournisseur_id, diametre=prix.diametre).first()
        prix.prt = ligne.prt if ligne else Decimal("1000")
        prix.save(update_fields=["prt"])


class Migration(migrations.Migration):

    dependencies = [
        ("gestion_prix_fer", "0001_initial"),
        ("boutique", "0003_aide_forme_crochet"),
    ]

    operations = [
        migrations.RunPython(verifier_coherence, migrations.RunPython.noop),
        migrations.CreateModel(
            name="PrtFer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("diametre", models.PositiveSmallIntegerField(
                    choices=[(6, "HA6"), (8, "HA8"), (10, "HA10"), (12, "HA12"), (14, "HA14"), (16, "HA16"),
                             (20, "HA20"), (22, "HA22"), (25, "HA25"), (32, "HA32")],
                    verbose_name="diamètre")),
                ("prt", models.DecimalField(
                    decimal_places=3, max_digits=10,
                    help_text="Remplace le 1000 : Pak = PaT / PrT et Pvk = PvT / PrT.",
                    validators=[django.core.validators.MinValueValidator(Decimal("0.000001"))],
                    verbose_name="PrT - poids réel d'une tonne (kg)")),
                ("modifie_le", models.DateTimeField(auto_now=True)),
                ("marque", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="prt",
                                             to="gestion_prix_fer.fournisseur")),
            ],
            options={
                "verbose_name": "PrT (poids réel d'une tonne)",
                "verbose_name_plural": "PrT (poids réel d'une tonne)",
                "ordering": ["marque__nom", "diametre"],
            },
        ),
        migrations.AddConstraint(
            model_name="prtfer",
            constraint=models.UniqueConstraint(fields=("marque", "diametre"), name="boutique_un_prt_par_marque_diametre"),
        ),
        # valeur par défaut le temps de la migration (utile seulement pour revenir en arrière)
        migrations.AlterField(
            model_name="prixfertonne",
            name="prt",
            field=models.DecimalField(decimal_places=3, default=Decimal("1000"), max_digits=10,
                                      verbose_name="PrT - poids réel d'une tonne (kg)"),
        ),
        migrations.RunPython(copier_prt, restaurer_prt),
        migrations.RemoveField(model_name="prixfertonne", name="prt"),
    ]
