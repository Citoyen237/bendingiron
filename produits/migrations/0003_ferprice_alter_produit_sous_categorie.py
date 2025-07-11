# Generated by Django 5.0.6 on 2025-06-28 11:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('produits', '0002_alter_produit_sous_categorie'),
    ]

    operations = [
        migrations.CreateModel(
            name='FerPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diametre', models.CharField(choices=[('m6', 'M6'), ('m8', 'M8'), ('m10', 'M10'), ('m14', 'M14'), ('m16', 'M16'), ('m20', 'M20'), ('m24', 'M24'), ('m27', 'M27'), ('m30', 'M30'), ('m32', 'M32')], max_length=255, unique=True)),
                ('prix', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AlterField(
            model_name='produit',
            name='sous_categorie',
            field=models.CharField(blank=True, choices=[('Etrier pour bardage et toiture', 'Etrier pour bardage et toiture'), ("boulon d'ancrage a beton", "boulon d'ancrage a beton"), ("cintrage d'extremite", 'Cintrage d extremite'), ('redressage et decoupage', 'Redressage et decoupage'), ('Cintrage de cadre', 'Cintrage de Cadre'), ('Cintrage de forme', 'Cintrage de Forme'), ('Quincaillerie', 'Quincaillerie')], max_length=255, null=True),
        ),
    ]
