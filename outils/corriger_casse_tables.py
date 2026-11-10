"""Remet les noms de tables à la casse attendue par Django.

Pourquoi : WAMP/MariaDB sous Windows enregistre les tables en minuscules
(usesorders_cart). MySQL sous Linux distingue les majuscules, et Django
cherche usesOrders_cart : le site plante (erreur 500 « Table ... doesn't
exist ») après l'import d'une base venant de Windows.

Utilisation sur le VPS (faire une sauvegarde mysqldump avant) :
  1. Voir la liste, sans rien modifier :
       docker-compose exec -T web python manage.py shell < outils/corriger_casse_tables.py
  2. Appliquer le renommage :
       docker-compose exec -T -e APPLIQUER=1 web python manage.py shell < outils/corriger_casse_tables.py
  3. Relancer la commande 1 : « A renommer : 0 | Introuvables : aucune ».
"""
import os

from django.apps import apps
from django.db import connection

with connection.cursor() as c:
    existantes = set(connection.introspection.table_names(c))
    minus = {t.lower(): t for t in existantes}
    attendues = sorted({m._meta.db_table for m in apps.get_models(include_auto_created=True)})
    a_renommer = [(minus[t.lower()], t) for t in attendues
                  if t not in existantes and t.lower() in minus]
    absentes = [t for t in attendues if t.lower() not in minus]

    for ancien, nouveau in a_renommer:
        print(f"{ancien}  ->  {nouveau}")
    print(f"A renommer : {len(a_renommer)} | Introuvables : {absentes or 'aucune'}")

    if os.environ.get("APPLIQUER") == "1":
        for ancien, nouveau in a_renommer:
            c.execute(f"RENAME TABLE `{ancien}` TO `{nouveau}`")
        print("RENOMMAGE FAIT")
