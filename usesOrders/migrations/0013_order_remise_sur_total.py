from django.db import migrations, models


class Migration(migrations.Migration):
    """La remise du code promo porte désormais sur le total HT de la facture.

    Les commandes déjà enregistrées gardent l'ancienne règle (remise sur le prix
    de revient) : elles reçoivent remise_sur_total=False, pour que leurs
    factures et le solde restant à payer ne changent pas.
    """

    dependencies = [
        ("usesOrders", "0012_payment_plusieurs_par_commande"),
    ]

    operations = [
        # 1. Les lignes existantes reçoivent False (ancienne règle)
        migrations.AddField(
            model_name="order",
            name="remise_sur_total",
            field=models.BooleanField(default=False),
        ),
        # 2. Les nouvelles commandes utilisent la nouvelle règle
        migrations.AlterField(
            model_name="order",
            name="remise_sur_total",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="order",
            name="remise",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
