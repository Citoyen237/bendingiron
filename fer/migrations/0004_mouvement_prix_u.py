# Generated by Django 5.0.6 on 2025-06-12 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fer', '0003_fer_unique_diametre_categorie'),
    ]

    operations = [
        migrations.AddField(
            model_name='mouvement',
            name='prix_u',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
