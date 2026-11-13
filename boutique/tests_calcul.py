"""
Tests du moteur de calcul (étape 2).

Les valeurs reprennent l'EXEMPLE CHIFFRÉ de LOGIQUE_CALCUL_PRIX.txt (section 5) :
cadre carré, Lc = 20 cm, HA8, Prometal FE500 -> 430 FCFA (fer Bending Iron)
et 160 FCFA (fer du client).

Lancer :  python manage.py test boutique
"""
from decimal import Decimal

from django.test import TestCase

from gestion_prix_fer.models import Constante, Fournisseur, TypeFer
from produits.models import Categorie, Produit

from .calcul import CalculImpossible, calculer
from .models import (Angle, CoefFaconnage, ConfigProduit, ConstanteSoudure, DimensionProduit,
                     ParametresCalcul, PoidsFer, PrixFerTonne, PrtFer, ToleranceDiametre)


class CalculBase(TestCase):
    def setUp(self):
        prometal = Fournisseur.objects.create(nom="prometal")
        self.fe500 = TypeFer.objects.create(fournisseur=prometal, nom="FE500")
        PrtFer.objects.create(marque=prometal, diametre=8, prt=950)
        PrixFerTonne.objects.create(type_fer=self.fe500, diametre=8, pat=650000, pvt=750000)
        PoidsFer.objects.create(diametre=8, kg_par_cm=Decimal("0.00395"))
        CoefFaconnage.objects.create(marque=prometal, diametre=8, coef=51)
        ConstanteSoudure.objects.create(diametre=8, valeur=Decimal("0.5"))
        ParametresCalcul.objects.create(seuil_ldf=100, constante_ldf_court=Decimal("0.13"),
                                        constante_ldf_long=Decimal("0.10"), formule_r="5*d/10")
        for cle, valeur in (("tolerance", 10), ("taxe", 5), ("taux", Decimal("0.1"))):
            Constante.objects.create(cle=cle, valeur=valeur)

        cat = Categorie.objects.create(libelle="Cintrages")
        self.produit = Produit.objects.create(categorie=cat, nom="cadre carre", sous_categorie="Cintrage de cadre",
                                              name_page="p", imageshop2d="a.png", imageshop3d="b.png")
        self.config = ConfigProduit.objects.create(produit=self.produit, diametres=[8], formule_ltp="4*Lc")
        self.config.angles.set(Angle.objects.filter(valeur__in=[90, 135]))
        DimensionProduit.objects.create(config=self.config, libelle="Longueur du côté", abreviation="Lc",
                                        minimum=8, maximum=100)

    def saisies(self, **extra):
        valeurs = {"fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500", "diametre": "8",
                   "angle": "90", "dimensions": {"Lc": "20"}, "quantite": "1"}
        valeurs.update(extra)
        return valeurs


# ---------------------------------------------------------------------------
# L'exemple chiffré du document
# ---------------------------------------------------------------------------
class ExempleDuDocumentTests(CalculBase):

    def test_fer_bending_iron_430(self):
        r = calculer(self.config, self.saisies())
        self.assertEqual(r.ltp, Decimal("80"))
        self.assertEqual(r.ldf, Decimal("10.4"))
        self.assertEqual(r.lt, 91)
        self.assertEqual(r.poids, Decimal("0.35945"))
        self.assertAlmostEqual(float(r.pak), 684.21, places=2)
        self.assertAlmostEqual(float(r.pvk), 789.47, places=2)
        self.assertAlmostEqual(float(r.pv), 283.78, places=2)
        self.assertEqual(r.ps, Decimal("46.41"))
        self.assertEqual(r.pd, Decimal("45.5"))
        self.assertEqual(r.pu, 430)

    def test_fer_du_client_160(self):
        r = calculer(self.config, self.saisies(fer="le client"))
        self.assertAlmostEqual(float(r.pv), 37.84, places=2)     # Poids × (Pvk − Pak)
        self.assertEqual(r.pu, 160)

    def test_grand_cadre_constante_au_dela_de_100(self):
        r = calculer(self.config, self.saisies(dimensions={"Lc": "30"}))
        self.assertEqual((r.ltp, r.ldf, r.lt), (Decimal("120"), Decimal("12.0"), 132))

    def test_seuil_exactement_100_utilise_la_premiere_constante(self):
        r = calculer(self.config, self.saisies(dimensions={"Lc": "25"}))   # Ltp = 100
        self.assertEqual(r.ldf, Decimal("13.00"))
        self.assertEqual(r.lt, 113)                                       # pas 114

    def test_total_selon_la_quantite(self):
        r = calculer(self.config, self.saisies(quantite="50"))
        self.assertEqual(r.total, 430 * 50)

    def test_details_pour_le_panier(self):
        r = calculer(self.config, self.saisies())
        self.assertEqual(r.details["longueur_Total"], 91)
        self.assertEqual(r.details["Longueur du côté"], "20 cm")
        self.assertEqual(r.details["rayon_Courbure"], 4.0)          # R = 5*8/10
        self.assertEqual(r.details["angle"], "90°")
        self.assertEqual((r.details["marque_fer"], r.details["type_fer"]), ("prometal", "FE500"))

    def test_r_et_ld_masques_si_non_coches(self):
        self.config.afficher_r = self.config.afficher_ld = False
        self.config.save()
        details = calculer(self.config, self.saisies()).details
        self.assertNotIn("rayon_Courbure", details)
        self.assertNotIn("longueur_Depart_et_Fin", details)

    def test_le_prix_du_navigateur_est_ignore(self):
        r = calculer(self.config, self.saisies(prix="1", prix_Total="1", prix_revient="0"))
        self.assertEqual(r.pu, 430)


# ---------------------------------------------------------------------------
# Paramètres qui changent le résultat
# ---------------------------------------------------------------------------
class VariationsTests(CalculBase):

    def test_prt_change_le_prix_au_kg(self):
        PrtFer.objects.filter(diametre=8).update(prt=1000)
        r = calculer(self.config, self.saisies())
        self.assertEqual((r.pak, r.pvk), (Decimal("650"), Decimal("750")))

    def test_prt_commun_aux_types_d_une_marque(self):
        """FE400 utilise le même PrT (950) que FE500 pour prometal HA8."""
        fe400 = TypeFer.objects.create(fournisseur=self.fe500.fournisseur, nom="FE400")
        PrixFerTonne.objects.create(type_fer=fe400, diametre=8, pat=600000, pvt=700000)
        r = calculer(self.config, self.saisies(type_fer="fe400"))
        self.assertAlmostEqual(float(r.pvk), 700000 / 950, places=4)

    def test_type_de_fer_change_le_prix(self):
        fe400 = TypeFer.objects.create(fournisseur=self.fe500.fournisseur, nom="FE400")
        PrixFerTonne.objects.create(type_fer=fe400, diametre=8, pat=600000, pvt=700000)
        self.assertLess(calculer(self.config, self.saisies(type_fer="fe400")).pu,
                        calculer(self.config, self.saisies()).pu)

    def test_majuscules_ignorees(self):
        r = calculer(self.config, self.saisies(type_fer="FE500", marque_fer="Prometal", fer="Bending Iron"))
        self.assertEqual(r.pu, 430)

    def test_coefficient_de_l_angle(self):
        """ka utilisable dans la formule : Ltp = 4*Lc*ka avec ka = 1,5 pour 135°."""
        Angle.objects.filter(valeur=135).update(coefficient=Decimal("1.5"))
        self.config.formule_ltp = "4*Lc*ka"
        self.config.save()
        self.assertEqual(calculer(self.config, self.saisies(angle="135")).ltp, Decimal("120"))
        self.assertEqual(calculer(self.config, self.saisies(angle="90")).ltp, Decimal("80"))

    def test_produit_sans_angle(self):
        self.config.angles.clear()
        r = calculer(self.config, self.saisies(angle=None))
        self.assertEqual(r.pu, 430)
        self.assertNotIn("angle", r.details)

    def test_formule_r_du_produit(self):
        self.config.formule_r = "d/2"
        self.config.save()
        self.assertEqual(calculer(self.config, self.saisies()).r, Decimal("4.0"))

    def test_virgule_acceptee(self):
        self.assertEqual(calculer(self.config, self.saisies(dimensions={"Lc": "20,5"})).ltp, Decimal("82"))

    def test_imprecision_des_decimaux_ne_fausse_pas_l_arrondi(self):
        """0,1 × 3 = 0,30000000000000004 en flottant : Lt ne doit pas monter d'un cm."""
        self.config.formule_ltp = "0.1*Lc*3*10/3"     # = Lc, avec des flottants
        self.config.save()
        ParametresCalcul.objects.update(constante_ldf_court=0)
        self.assertEqual(calculer(self.config, self.saisies(dimensions={"Lc": "30"})).lt, 30)


# ---------------------------------------------------------------------------
# Saisies refusées
# ---------------------------------------------------------------------------
class SaisiesRefuseesTests(CalculBase):

    def refuse(self, message, **extra):
        with self.assertRaisesMessage(CalculImpossible, message):
            calculer(self.config, self.saisies(**extra))

    def test_dimension_hors_limites(self):
        self.refuse("entre 8 et 100 cm", dimensions={"Lc": "7"})
        self.refuse("entre 8 et 100 cm", dimensions={"Lc": "100.5"})

    def test_dimensions_limites_acceptees(self):
        calculer(self.config, self.saisies(dimensions={"Lc": "8"}))
        calculer(self.config, self.saisies(dimensions={"Lc": "100"}))

    def test_dimension_manquante_ou_invalide(self):
        self.refuse("valeur manquante", dimensions={})
        self.refuse("valeur invalide", dimensions={"Lc": "abc"})
        self.refuse("valeur invalide", dimensions={"Lc": "NaN"})

    def test_diametre_non_propose(self):
        self.refuse("HA10 n'est pas proposé", diametre="10")
        self.refuse("Choisissez un diamètre", diametre="")

    def test_angle_non_propose_ou_manquant(self):
        self.refuse("Choisissez un angle", angle="180")
        self.refuse("Choisissez un angle", angle=None)

    def test_angle_desactive(self):
        Angle.objects.filter(valeur=90).update(actif=False)
        self.refuse("Choisissez un angle", angle="90")

    def test_fournisseur_du_fer(self):
        self.refuse("qui fournit le fer", fer="")
        self.refuse("qui fournit le fer", fer="un voisin")

    def test_quantite(self):
        self.refuse("au moins 1", quantite="0")
        self.refuse("Quantité invalide", quantite="deux")

    def test_famille_exclue(self):
        self.produit.sous_categorie = "Quincaillerie"
        self.produit.save()
        self.refuse("n'utilise pas le gabarit universel")


# ---------------------------------------------------------------------------
# Données manquantes dans l'admin : message clair, jamais de prix faux
# ---------------------------------------------------------------------------
class DonneesManquantesTests(CalculBase):

    def refuse(self, message):
        with self.assertRaisesMessage(CalculImpossible, message):
            calculer(self.config, self.saisies())

    def test_prix_tonne_absent(self):
        PrixFerTonne.objects.all().delete()
        self.refuse("Prix du fer prometal FE500 HA8 non renseigné")

    def test_prt_absent(self):
        PrtFer.objects.all().delete()
        self.refuse("PrT prometal HA8 non renseigné dans l'admin")

    def test_poids_absent(self):
        PoidsFer.objects.all().delete()
        self.refuse("Poids au cm du HA8")

    def test_coef_absent(self):
        CoefFaconnage.objects.all().delete()
        self.refuse("Coefficient de façonnage")

    def test_soudure_absente(self):
        ConstanteSoudure.objects.all().delete()
        self.refuse("Constante de soudure du HA8")

    def test_parametres_absents(self):
        ParametresCalcul.objects.all().delete()
        self.refuse("Paramètres de calcul non renseignés")

    def test_constantes_absentes(self):
        Constante.objects.filter(cle="taux").delete()
        self.refuse("Constantes manquantes dans l'admin : taux")

    def test_formule_devenue_invalide(self):
        ConfigProduit.objects.filter(pk=self.config.pk).update(formule_ltp="4*Lx")
        self.config.refresh_from_db()
        self.refuse("Formule du produit invalide")

    def test_marque_inconnue(self):
        with self.assertRaisesMessage(CalculImpossible, "Prix du fer"):
            calculer(self.config, self.saisies(marque_fer="inconnue"))



class ToleranceParDiametreTests(CalculBase):
    """La tolérance fixée pour un diamètre remplace la constante commune (13/11/2026)."""

    def test_tolerance_du_diametre(self):
        ToleranceDiametre.objects.create(diametre=8, valeur=20)
        # (283,78 + 46,41 + 20 + 5 + 45,5) × 1,1 = 440,76 -> 441 (au lieu de 430 avec 10)
        self.assertEqual(calculer(self.config, self.saisies()).pu, 441)

    def test_autre_diametre_garde_la_constante_commune(self):
        ToleranceDiametre.objects.create(diametre=10, valeur=500)
        self.assertEqual(calculer(self.config, self.saisies()).pu, 430)

    def test_constante_commune_inutile_si_le_diametre_a_sa_tolerance(self):
        Constante.objects.filter(cle="tolerance").delete()
        ToleranceDiametre.objects.create(diametre=8, valeur=10)
        self.assertEqual(calculer(self.config, self.saisies()).pu, 430)
        ToleranceDiametre.objects.all().delete()
        with self.assertRaises(CalculImpossible):
            calculer(self.config, self.saisies())
