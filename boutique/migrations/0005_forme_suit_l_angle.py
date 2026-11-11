"""Cadre carré et cadre rectangulaire : les crochets suivent l'angle choisi.

Avant, l'angle des crochets était écrit en dur (45 / -135) : le dessin montrait
toujours 135°, même quand le client choisissait 90°. Désormais :
  orientation de départ « angle-90 », crochets « -angle ».

Seules les formes EXACTEMENT identiques à celles d'origine sont modifiées :
une forme déjà retouchée dans l'admin n'est pas écrasée (message dans le journal).
"""
from django.db import migrations


def _cadre(cotes, depart, crochet):
    """cotes : les 4 côtés dans l'ordre ; depart / crochet : angles d'orientation et des crochets."""
    a, b, c, d = cotes
    return [{"longueur": 0, "angle": depart, "cote": False},
            {"longueur": "Ldf/2", "angle": crochet, "crochet": True},
            {"longueur": a, "angle": -90},
            {"longueur": b, "angle": -90},
            {"longueur": c, "angle": -90},
            {"longueur": d, "angle": crochet},
            {"longueur": "Ldf/2", "crochet": True}]


FORMES = [   # (ancienne, nouvelle)
    (_cadre(("Lc", "Lc", "Lc", "Lc"), 45, -135), _cadre(("Lc", "Lc", "Lc", "Lc"), "angle-90", "-angle")),
    (_cadre(("La", "Lg", "La", "Lg"), 45, -135), _cadre(("La", "Lg", "La", "Lg"), "angle-90", "-angle")),
]


def _remplacer(apps, sens):
    ConfigProduit = apps.get_model("boutique", "ConfigProduit")
    for config in ConfigProduit.objects.select_related("produit"):
        for ancienne, nouvelle in FORMES:
            avant, apres = (ancienne, nouvelle) if sens == "aller" else (nouvelle, ancienne)
            if config.forme == avant:
                config.forme = apres
                config.save(update_fields=["forme"])
                print(f"\n  Forme de « {config.produit.nom} » : les crochets suivent l'angle choisi"
                      if sens == "aller" else f"\n  Forme de « {config.produit.nom} » : angle fixe remis")
                break


def aller(apps, schema_editor):
    _remplacer(apps, "aller")


def retour(apps, schema_editor):
    _remplacer(apps, "retour")


class Migration(migrations.Migration):

    dependencies = [
        ("boutique", "0004_prt_par_marque_et_diametre"),
    ]

    operations = [
        migrations.RunPython(aller, retour),
    ]
