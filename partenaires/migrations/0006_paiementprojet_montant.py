from decimal import Decimal

from django.db import migrations, models


def _montant_tranche(projet, tranche):
    """Recopie des calculs de Projet (net_payer, tranche1/2/3) au moment de la
    migration : les modèles historiques n'ont pas les propriétés du modèle."""
    items = list(projet.projetitems.all())
    montant_total = sum(item.prix_u * item.quantite for item in items)
    prix_revient_total = sum(item.prix_revient for item in items)
    apres_remise = round(montant_total - ((prix_revient_total * projet.reduction) / 100))
    tva = round((apres_remise * 19.25) / 100)
    try:
        frais = Decimal(str(projet.frais_ingenieurie or 0))
    except Exception:
        frais = Decimal(0)
    net_payer = round(tva + apres_remise + frais)
    pourcentage = {1: 40, 2: 40, 3: 20}.get(tranche, 0)
    return round((net_payer * pourcentage) / 100)


def figer_montants_existants(apps, schema_editor):
    """Les tranches déjà payées n'avaient pas de montant enregistré : on fige
    le montant calculé sur le total ACTUEL du projet (seule valeur connue)."""
    PaiementProjet = apps.get_model("partenaires", "PaiementProjet")
    for paiement in PaiementProjet.objects.filter(montant__isnull=True).select_related("projet"):
        paiement.montant = _montant_tranche(paiement.projet, paiement.tranche)
        paiement.save(update_fields=["montant"])


class Migration(migrations.Migration):

    dependencies = [
        ("partenaires", "0005_projet_frais_ingenieurie"),
    ]

    operations = [
        migrations.AddField(
            model_name="paiementprojet",
            name="montant",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True,
                                      help_text="Montant de la tranche au moment du paiement (FCFA)"),
        ),
        migrations.RunPython(figer_montants_existants, migrations.RunPython.noop),
    ]
