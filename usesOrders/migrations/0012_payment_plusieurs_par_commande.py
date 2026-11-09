# Une commande peut recevoir plusieurs paiements (acompte puis solde) :
# Payment.order passe de OneToOneField à ForeignKey(related_name="payments").
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usesOrders", "0011_codepromo_user_alter_codepromo_client"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to="usesOrders.order",
            ),
        ),
    ]
