"""
Tests de l'application « boutique » - étape 1 (tables, admin, formules).

Lancer :  python manage.py test boutique
"""
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse

from auth_app.models import CustomUser
from gestion_prix_fer.models import Fournisseur, TypeFer
from produits.models import Categorie, Produit

from .formules import FormuleInvalide, evaluer, noms_utilises, verifier
from .models import (Angle, CoefFaconnage, ConfigProduit, ConstanteSoudure, DimensionProduit,
                     ParametresCalcul, PoidsFer, PrixFerTonne, PrtFer)

EXCLUES = ("Quincaillerie", "Etrier pour bardage et toiture", "boulon d'ancrage a beton")
AUTORISEES = ("Cintrage de cadre", "Cintrage de forme", "cintrage d'extremite", "redressage et decoupage")


def creer_produit(nom="cadre carre", sous_categorie="Cintrage de cadre"):
    cat, _ = Categorie.objects.get_or_create(libelle="Cintrages")
    return Produit.objects.create(categorie=cat, nom=nom, sous_categorie=sous_categorie,
                                  name_page="p", imageshop2d="a.png", imageshop3d="b.png")


# ---------------------------------------------------------------------------
# Évaluateur de formules
# ---------------------------------------------------------------------------
class FormulesTests(TestCase):

    def test_formule_du_cadre_carre(self):
        self.assertEqual(evaluer("ceil(4*Lc + 1.3*d)", {"Lc": 20, "d": 8}), 91)

    def test_operations_et_fonctions(self):
        self.assertEqual(evaluer("2*(Lc+Lb) - 3", {"Lc": 10, "Lb": 5}), 27)
        self.assertEqual(evaluer("max(Lc, 12)", {"Lc": 10}), 12)
        self.assertEqual(evaluer("-Lc + 30", {"Lc": 10}), 20)
        self.assertAlmostEqual(evaluer("sqrt(Lc**2 + Lb**2)", {"Lc": 3, "Lb": 4}), 5)

    def test_angles_en_degres(self):
        self.assertAlmostEqual(evaluer("sin(90)", {}), 1)
        self.assertAlmostEqual(evaluer("cos(angle)", {"angle": 180}), -1)

    def test_noms_utilises(self):
        self.assertEqual(noms_utilises("ceil(4*Lc + 1.3*d) + R"), {"Lc", "d", "R"})

    def test_abreviation_inconnue(self):
        with self.assertRaisesMessage(FormuleInvalide, "Abréviation inconnue : Lx"):
            evaluer("4*Lx", {"Lc": 20})

    def test_code_interdit(self):
        """Rien d'autre que des calculs : pas d'import, d'attribut, de texte…"""
        for formule in ("__import__('os').system('dir')", "Lc.__class__", "'texte'",
                        "[1, 2]", "(lambda: 1)()", "open('x')", "Lc if 1 else 2",
                        "ceil(x=1)", "True + 1", "Lc > 2"):
            with self.subTest(formule=formule):
                with self.assertRaises(FormuleInvalide):
                    evaluer(formule, {"Lc": 1})

    def test_erreurs_de_calcul(self):
        for formule, message in (("Lc/0", "Division par zéro"), ("Lc**100", "Puissance trop grande"),
                                 ("", "vide"), ("4*(Lc", "mal écrite"), ("sqrt(-Lc)", "impossible")):
            with self.subTest(formule=formule):
                with self.assertRaisesMessage(FormuleInvalide, message):
                    evaluer(formule, {"Lc": 1})

    def test_formule_trop_longue(self):
        with self.assertRaisesMessage(FormuleInvalide, "255"):
            evaluer("1+" * 200 + "1", {})

    def test_verifier_refuse_les_resultats_negatifs(self):
        with self.assertRaisesMessage(FormuleInvalide, "Résultat négatif"):
            verifier("Lc - 50", {"Lc"}, [{"Lc": 100}, {"Lc": 8}])

    def test_verifier_refuse_les_abreviations_non_autorisees(self):
        with self.assertRaisesMessage(FormuleInvalide, "Abréviation inconnue : Lb"):
            verifier("Lc + Lb", {"Lc"}, [{"Lc": 1, "Lb": 1}])


# ---------------------------------------------------------------------------
# Tables communes
# ---------------------------------------------------------------------------
class TablesTests(TestCase):

    def setUp(self):
        self.prometal = Fournisseur.objects.create(nom="Prometal")
        self.fe500 = TypeFer.objects.create(fournisseur=self.prometal, nom="FE500")

    def test_pak_et_pvk_avec_prt(self):
        """Exemple du document : PaT 650 000, PvT 750 000, PrT 950."""
        PrtFer.objects.create(marque=self.prometal, diametre=8, prt=950)
        prix = PrixFerTonne.objects.create(type_fer=self.fe500, diametre=8, pat=650000, pvt=750000)
        self.assertEqual(prix.prt, 950)
        self.assertAlmostEqual(float(prix.pak), 684.21, places=2)
        self.assertAlmostEqual(float(prix.pvk), 789.47, places=2)
        self.assertEqual(prix.marque, self.prometal)

    def test_ha6_a_ses_propres_prix(self):
        PrtFer.objects.create(marque=self.prometal, diametre=6, prt=1000)
        PrtFer.objects.create(marque=self.prometal, diametre=8, prt=950)
        PrixFerTonne.objects.create(type_fer=self.fe500, diametre=6, pat=700000, pvt=800000)
        PrixFerTonne.objects.create(type_fer=self.fe500, diametre=8, pat=650000, pvt=750000)
        self.assertNotEqual(PrixFerTonne.objects.get(diametre=6).pvk, PrixFerTonne.objects.get(diametre=8).pvk)

    def test_un_seul_prix_par_marque_type_diametre(self):
        PrixFerTonne.objects.create(type_fer=self.fe500, diametre=8, pat=1, pvt=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            PrixFerTonne.objects.create(type_fer=self.fe500, diametre=8, pat=2, pvt=2)

    def test_prt_nul_refuse(self):
        prt = PrtFer(marque=self.prometal, diametre=8, prt=0)
        with self.assertRaises(ValidationError):
            prt.full_clean()

    def test_prt_meme_valeur_pour_tous_les_types_d_une_marque(self):
        """PrT dépend de la marque et du diamètre, pas du type (FE400 / FE500)."""
        fe400 = TypeFer.objects.create(fournisseur=self.prometal, nom="FE400")
        PrtFer.objects.create(marque=self.prometal, diametre=8, prt=950)
        a = PrixFerTonne.objects.create(type_fer=self.fe500, diametre=8, pat=650000, pvt=750000)
        b = PrixFerTonne.objects.create(type_fer=fe400, diametre=8, pat=600000, pvt=700000)
        self.assertEqual(a.prt, b.prt)

    def test_prt_propre_a_chaque_marque(self):
        autre = Fournisseur.objects.create(nom="autre fer")
        PrtFer.objects.create(marque=self.prometal, diametre=8, prt=950)
        PrtFer.objects.create(marque=autre, diametre=8, prt=980)
        prix = PrixFerTonne.objects.create(type_fer=TypeFer.objects.create(fournisseur=autre, nom="FE500"),
                                           diametre=8, pat=980, pvt=980)
        self.assertEqual((prix.prt, prix.pvk), (980, 1))

    def test_un_seul_prt_par_marque_et_diametre(self):
        PrtFer.objects.create(marque=self.prometal, diametre=8, prt=950)
        with self.assertRaises(IntegrityError), transaction.atomic():
            PrtFer.objects.create(marque=self.prometal, diametre=8, prt=1000)

    def test_prt_manquant(self):
        prix = PrixFerTonne.objects.create(type_fer=self.fe500, diametre=8, pat=1, pvt=1)
        self.assertEqual((prix.prt, prix.pak, prix.pvk), (None, None, None))

    def test_coef_unique_par_marque_et_diametre(self):
        CoefFaconnage.objects.create(marque=self.prometal, diametre=8, coef=51)
        with self.assertRaises(IntegrityError), transaction.atomic():
            CoefFaconnage.objects.create(marque=self.prometal, diametre=8, coef=60)

    def test_poids_et_soudure_uniques_par_diametre(self):
        PoidsFer.objects.create(diametre=8, kg_par_cm=Decimal("0.00395"))
        ConstanteSoudure.objects.create(diametre=8, valeur=Decimal("0.5"))
        with self.assertRaises(IntegrityError), transaction.atomic():
            PoidsFer.objects.create(diametre=8, kg_par_cm=Decimal("0.004"))
        with self.assertRaises(IntegrityError), transaction.atomic():
            ConstanteSoudure.objects.create(diametre=8, valeur=1)

    def test_parametres_une_seule_ligne(self):
        ParametresCalcul.objects.create(constante_ldf_court=Decimal("0.13"), constante_ldf_long=Decimal("0.10"))
        ParametresCalcul.objects.create(constante_ldf_court=Decimal("0.2"), constante_ldf_long=Decimal("0.1"))
        self.assertEqual(ParametresCalcul.objects.count(), 1)
        self.assertEqual(ParametresCalcul.actuels().constante_ldf_court, Decimal("0.2"))
        self.assertEqual(ParametresCalcul.actuels().seuil_ldf, Decimal("100"))

    def test_parametres_formule_r_verifiee(self):
        p = ParametresCalcul(constante_ldf_court=1, constante_ldf_long=1, formule_r="5*x")
        with self.assertRaises(ValidationError):
            p.full_clean()


# ---------------------------------------------------------------------------
# Réglages d'un produit
# ---------------------------------------------------------------------------
class ConfigProduitTests(TestCase):

    def config(self, **extra):
        valeurs = {"diametres": [6, 8], "formule_ltp": "4*Lc"}
        valeurs.update(extra)
        if "produit" not in valeurs:
            valeurs["produit"], _ = Produit.objects.get_or_create(
                nom="cadre carre", sous_categorie="Cintrage de cadre",
                defaults={"categorie": Categorie.objects.get_or_create(libelle="Cintrages")[0],
                          "name_page": "p", "imageshop2d": "a.png", "imageshop3d": "b.png"})
        return ConfigProduit(**valeurs)

    def test_familles_exclues_refusees(self):
        for i, famille in enumerate(EXCLUES + (None,)):
            with self.subTest(famille=famille):
                cfg = self.config(produit=creer_produit(f"p{i}", famille))
                with self.assertRaises(ValidationError) as ctx:
                    cfg.full_clean()
                self.assertIn("produit", ctx.exception.message_dict)

    def test_familles_autorisees_acceptees(self):
        for i, famille in enumerate(AUTORISEES):
            with self.subTest(famille=famille):
                self.config(produit=creer_produit(f"a{i}", famille)).full_clean()

    def test_au_moins_un_diametre(self):
        with self.assertRaises(ValidationError) as ctx:
            self.config(diametres=[]).full_clean()
        self.assertIn("diametres", ctx.exception.message_dict)

    def test_diametre_inconnu(self):
        with self.assertRaises(ValidationError):
            self.config(diametres=[7]).full_clean()

    def test_formule_r_du_produit_verifiee(self):
        with self.assertRaises(ValidationError) as ctx:
            self.config(formule_r="5*Lc").full_clean()
        self.assertIn("formule_r", ctx.exception.message_dict)

    def test_formule_r_par_defaut(self):
        cfg = self.config()
        self.assertEqual(cfg.formule_r_effective(), "5*d/10")
        ParametresCalcul.objects.create(constante_ldf_court=1, constante_ldf_long=1, formule_r="6*d/10")
        self.assertEqual(cfg.formule_r_effective(), "6*d/10")
        cfg.formule_r = "d/2"
        self.assertEqual(cfg.formule_r_effective(), "d/2")

    def test_apercu_ltp_aux_minimums_et_maximums(self):
        a90 = Angle.objects.get(valeur=90)
        lignes = self.config().verifier_formule_ltp([("Lc", Decimal(8), Decimal(100))], angles=[a90])
        self.assertEqual([ltp for _, ltp in lignes], [32, 32, 400, 400])   # HA6, HA8 x min, max
        self.assertEqual(lignes[0][0]["R"], 3.0)                           # R = 5*6/10

    def test_ltp_peut_utiliser_d_angle_ka_et_r(self):
        a135 = Angle.objects.get(valeur=135)
        a135.coefficient = Decimal("1.5")
        lignes = self.config(formule_ltp="2*Lc + R + d/10 + angle/135 + 4*ka").verifier_formule_ltp(
            [("Lc", Decimal(10), Decimal(20))], angles=[a135])
        self.assertAlmostEqual(lignes[0][1], 20 + 3 + 0.6 + 1 + 6)

    def test_verification_sur_chaque_angle_coche(self):
        """La formule doit marcher pour CHAQUE angle coché (ici : -135 rend Ltp négatif)."""
        angles = list(Angle.objects.filter(valeur__in=[90, -135]))
        with self.assertRaisesMessage(FormuleInvalide, "Résultat négatif"):
            self.config(formule_ltp="Lc + angle").verifier_formule_ltp([("Lc", Decimal(8), Decimal(100))],
                                                                       angles=angles)

    def test_sans_angle_coche_tous_les_angles_actifs_sont_verifies(self):
        lignes = self.config().verifier_formule_ltp([("Lc", Decimal(8), Decimal(100))])
        self.assertEqual(len(lignes), 2 * 2 * Angle.objects.filter(actif=True).count())

    def test_ltp_abreviation_non_cochee(self):
        with self.assertRaisesMessage(FormuleInvalide, "Abréviation inconnue : Lb"):
            self.config(formule_ltp="2*(Lc+Lb)").verifier_formule_ltp([("Lc", Decimal(8), Decimal(100))])

    def test_ltp_ne_peut_pas_utiliser_lt(self):
        with self.assertRaises(FormuleInvalide):
            self.config(formule_ltp="Lt + Lc").verifier_formule_ltp([("Lc", Decimal(8), Decimal(100))])


class DimensionTests(TestCase):

    def setUp(self):
        self.cfg = ConfigProduit.objects.create(produit=creer_produit(), diametres=[8], formule_ltp="4*Lc")

    def dimension(self, **extra):
        valeurs = {"config": self.cfg, "libelle": "Longueur du côté", "abreviation": "Lc",
                   "minimum": 8, "maximum": 100}
        valeurs.update(extra)
        return DimensionProduit(**valeurs)

    def test_dimension_valide(self):
        self.dimension().full_clean()

    def test_noms_reserves_refuses(self):
        for nom in ("d", "R", "Ld", "Ltp", "Lt", "angle", "ka"):
            with self.subTest(nom=nom):
                with self.assertRaises(ValidationError):
                    self.dimension(abreviation=nom).full_clean()

    def test_abreviation_mal_ecrite(self):
        for nom in ("1Lc", "L c", "L-c", ""):
            with self.subTest(nom=nom):
                with self.assertRaises(ValidationError):
                    self.dimension(abreviation=nom).full_clean()

    def test_minimum_superieur_au_maximum(self):
        with self.assertRaises(ValidationError) as ctx:
            self.dimension(minimum=100, maximum=8).full_clean()
        self.assertIn("maximum", ctx.exception.message_dict)

    def test_min_max_propres_a_chaque_produit(self):
        autre = ConfigProduit.objects.create(produit=creer_produit("cadre rectangle"), diametres=[8],
                                             formule_ltp="4*Lc")
        self.dimension().save()
        self.dimension(config=autre, minimum=20, maximum=250).save()
        self.assertEqual(DimensionProduit.objects.get(config=autre).maximum, 250)
        self.assertEqual(DimensionProduit.objects.get(config=self.cfg).maximum, 100)


# ---------------------------------------------------------------------------
# Écrans d'administration
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class AdminTests(TestCase):

    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(username="sa@x.cm", email="sa@x.cm",
                                                         password="MotDePasse-Solide-2026")
        Group.objects.get_or_create(name="superadmin")
        self.client.force_login(self.admin)
        self.produit = creer_produit()

    def url(self, modele, action="changelist", *args):
        return reverse(f"admin:boutique_{modele}_{action}", args=args)

    def formulaire(self, **extra):
        data = {
            "produit": self.produit.pk, "diametres": ["6", "8"],
            "angles": [str(Angle.objects.get(valeur=90).pk)],
            "afficher_r": "on", "afficher_ld": "on", "formule_ltp": "4*Lc", "formule_r": "",
            "dimensions-TOTAL_FORMS": "1", "dimensions-INITIAL_FORMS": "0",
            "dimensions-MIN_NUM_FORMS": "0", "dimensions-MAX_NUM_FORMS": "1000",
            "dimensions-0-ordre": "1", "dimensions-0-libelle": "Longueur du côté",
            "dimensions-0-abreviation": "Lc", "dimensions-0-minimum": "8", "dimensions-0-maximum": "100",
        }
        data.update(extra)
        return data

    def test_toutes_les_pages_s_ouvrent(self):
        for modele in ("prixfertonne", "poidsfer", "coeffaconnage", "constantesoudure",
                       "parametrescalcul", "configproduit"):
            with self.subTest(modele=modele):
                self.assertEqual(self.client.get(self.url(modele)).status_code, 200)
                self.assertEqual(self.client.get(self.url(modele, "add")).status_code, 200)

    def test_creer_un_produit_avec_ses_dimensions(self):
        r = self.client.post(self.url("configproduit", "add"), self.formulaire())
        self.assertEqual(r.status_code, 302, getattr(r, "context", None) and r.context["errors"])
        cfg = ConfigProduit.objects.get()
        self.assertEqual((cfg.diametres, cfg.actif), ([6, 8], False))
        self.assertEqual([a.valeur for a in cfg.angles.all()], [90])
        self.assertEqual(cfg.dimensions.get().abreviation, "Lc")

    def test_formule_fausse_refusee_avec_message(self):
        r = self.client.post(self.url("configproduit", "add"), self.formulaire(formule_ltp="4*Lx"))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Abréviation inconnue : Lx")
        self.assertFalse(ConfigProduit.objects.exists())

    def test_abreviation_en_double_refusee(self):
        data = self.formulaire(**{
            "dimensions-TOTAL_FORMS": "2", "dimensions-1-ordre": "2", "dimensions-1-libelle": "Autre",
            "dimensions-1-abreviation": "Lc", "dimensions-1-minimum": "1", "dimensions-1-maximum": "2"})
        r = self.client.post(self.url("configproduit", "add"), data)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "double")     # contrôle d'unicité de Django
        self.assertFalse(ConfigProduit.objects.exists())

    def test_produit_sans_dimension_refuse(self):
        r = self.client.post(self.url("configproduit", "add"),
                             self.formulaire(**{"dimensions-TOTAL_FORMS": "0"}))
        self.assertContains(r, "Ajoutez au moins une dimension")

    def test_familles_exclues_absentes_de_la_liste(self):
        creer_produit("ecrou", "Quincaillerie")
        creer_produit("etrier", "Etrier pour bardage et toiture")
        creer_produit("ancrage", "boulon d'ancrage a beton")
        r = self.client.get(self.url("configproduit", "add"))
        noms = {p.nom for p in r.context["adminform"].form.fields["produit"].queryset}
        self.assertEqual(noms, {"cadre carre"})

    def test_famille_exclue_forcee_refusee(self):
        ecrou = creer_produit("ecrou", "Quincaillerie")
        r = self.client.post(self.url("configproduit", "add"), self.formulaire(produit=ecrou.pk))
        self.assertEqual(r.status_code, 200)
        self.assertFalse(ConfigProduit.objects.exists())

    def test_apercu_dans_la_page_de_modification(self):
        self.client.post(self.url("configproduit", "add"), self.formulaire())
        cfg = ConfigProduit.objects.get()
        r = self.client.get(self.url("configproduit", "change", cfg.pk))
        self.assertContains(r, "Ltp = 32 cm")
        self.assertContains(r, "Ltp = 400 cm")

    def test_parametres_pas_de_deuxieme_ligne(self):
        ParametresCalcul.objects.create(constante_ldf_court=1, constante_ldf_long=1)
        self.assertEqual(self.client.get(self.url("parametrescalcul", "add")).status_code, 403)

    def test_prix_tonne_affiche_pak_pvk(self):
        t = TypeFer.objects.create(fournisseur=Fournisseur.objects.create(nom="Prometal"), nom="FE500")
        PrtFer.objects.create(marque=t.fournisseur, diametre=8, prt=950)
        PrixFerTonne.objects.create(type_fer=t, diametre=8, pat=650000, pvt=750000)
        r = self.client.get(self.url("prixfertonne"))
        self.assertContains(r, "684.21")
        self.assertContains(r, "789.47")

    def test_client_n_a_pas_acces(self):
        client = CustomUser.objects.create_user(username="c@x.cm", email="c@x.cm", password="x-Solide-2026")
        self.client.force_login(client)
        r = self.client.get(self.url("configproduit"))
        self.assertEqual(r.status_code, 302)   # renvoyé vers la connexion de l'admin


# ---------------------------------------------------------------------------
# Angles gérés dans l'admin
# ---------------------------------------------------------------------------
class AnglesTests(TestCase):

    def test_les_4_angles_initiaux_sont_crees(self):
        """Créés par la migration 0002 (ceux utilisés aujourd'hui par les produits)."""
        self.assertEqual(list(Angle.objects.values_list("valeur", flat=True)), [90, 135, -135, 180])
        self.assertTrue(all(a.coefficient == 1 and a.actif for a in Angle.objects.all()))

    def test_valeur_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Angle.objects.create(valeur=90, libelle="doublon")

    def test_coefficient_negatif_refuse(self):
        with self.assertRaises(ValidationError):
            Angle(valeur=45, libelle="45°", coefficient=Decimal("-1")).full_clean()

    def test_variables_de_formule(self):
        angle = Angle(valeur=135, libelle="135°", coefficient=Decimal("1.25"))
        self.assertEqual(angle.variables(), {"angle": 135, "ka": 1.25})

    def test_nouvel_angle_utilisable(self):
        a45 = Angle.objects.create(valeur=45, libelle="45°", coefficient=Decimal("2"))
        cfg = ConfigProduit.objects.create(produit=creer_produit(), diametres=[8], formule_ltp="4*Lc*ka")
        cfg.angles.add(a45)
        lignes = cfg.verifier_formule_ltp([("Lc", Decimal(8), Decimal(100))])
        self.assertEqual([ltp for _, ltp in lignes], [64, 800])


@override_settings(SECURE_SSL_REDIRECT=False)
class AdminAnglesTests(AdminTests):
    """Reprend la base d'AdminTests (super-admin connecté, produit cadre carré)."""

    def test_page_des_angles(self):
        r = self.client.get(self.url("angle"))
        self.assertEqual(r.status_code, 200)
        for libelle in ("90°", "135°", "-135°", "180°"):
            self.assertContains(r, libelle)

    def test_angle_inactif_non_propose(self):
        Angle.objects.filter(valeur=180).update(actif=False)
        r = self.client.get(self.url("configproduit", "add"))
        valeurs = {a.valeur for a in r.context["adminform"].form.fields["angles"].queryset}
        self.assertEqual(valeurs, {90, 135, -135})

    def test_formule_verifiee_avec_les_angles_coches(self):
        """« Lc + angle » : valable avec 90° seul, refusée si -135° est coché (Lc = 8 -> -127)."""
        a90, a135n = Angle.objects.get(valeur=90), Angle.objects.get(valeur=-135)
        r = self.client.post(self.url("configproduit", "add"),
                             self.formulaire(formule_ltp="Lc + angle", angles=[str(a90.pk), str(a135n.pk)]))
        self.assertContains(r, "Résultat négatif")
        self.assertFalse(ConfigProduit.objects.exists())
        r = self.client.post(self.url("configproduit", "add"),
                             self.formulaire(formule_ltp="Lc + angle", angles=[str(a90.pk)]))
        self.assertEqual(r.status_code, 302)

    def test_formule_avec_ka(self):
        Angle.objects.filter(valeur=90).update(coefficient=Decimal("1.5"))
        r = self.client.post(self.url("configproduit", "add"), self.formulaire(formule_ltp="4*Lc*ka"))
        self.assertEqual(r.status_code, 302)
        cfg = ConfigProduit.objects.get()
        self.assertContains(self.client.get(self.url("configproduit", "change", cfg.pk)), "Ltp = 48 cm")
