"""
Test de la migration 0004 : PrT passe des prix à la tonne (marque × type × diamètre)
à une table par marque et diamètre.

Lancer :  python manage.py test boutique
"""
from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

AVANT = [("boutique", "0003_aide_forme_crochet")]
APRES = [("boutique", "0004_prt_par_marque_et_diametre")]


class MigrationPrtTests(TransactionTestCase):

    def migrer(self, cible):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(cible)
        return executor.loader.project_state(cible).apps

    def preparer(self, prt_fe400, prt_fe500):
        apps = self.migrer(AVANT)
        Fournisseur = apps.get_model("gestion_prix_fer", "Fournisseur")
        TypeFer = apps.get_model("gestion_prix_fer", "TypeFer")
        PrixFerTonne = apps.get_model("boutique", "PrixFerTonne")
        prometal = Fournisseur.objects.create(nom="prometal")
        for nom, prt in (("FE400", prt_fe400), ("FE500", prt_fe500)):
            t = TypeFer.objects.create(fournisseur=prometal, nom=nom)
            PrixFerTonne.objects.create(type_fer=t, diametre=8, pat=1, pvt=1, prt=prt)

    def tearDown(self):
        self.migrer(APRES)   # remet la base de test dans son état final

    def test_prt_repris_par_marque_et_diametre(self):
        self.preparer(Decimal("950"), Decimal("950"))
        apps = self.migrer(APRES)
        PrtFer = apps.get_model("boutique", "PrtFer")
        self.assertEqual([(p.marque.nom, p.diametre, p.prt) for p in PrtFer.objects.all()],
                         [("prometal", 8, Decimal("950.000"))])

    def test_prt_differents_selon_le_type_migration_arretee(self):
        self.preparer(Decimal("950"), Decimal("1000"))
        with self.assertRaisesMessage(Exception, "PrT différents selon le type"):
            self.migrer(APRES)
        # la migration n'est pas appliquée : on est toujours avant 0004
        self.migrer(AVANT)
        from django.apps import apps as _  # noqa: F401
        apps = MigrationExecutor(connection).loader.project_state(AVANT).apps
        PrixFerTonne = apps.get_model("boutique", "PrixFerTonne")
        self.assertEqual(sorted(p.prt for p in PrixFerTonne.objects.all()), [Decimal("950.000"), Decimal("1000.000")])
        PrixFerTonne.objects.update(prt=950)   # harmonisé, pour que tearDown puisse migrer
