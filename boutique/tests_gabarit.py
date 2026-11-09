"""
Tests du gabarit universel (étape 4) : page produit, calcul en direct,
dessin, ajout au panier, aperçu administrateur.

Lancer :  python manage.py test boutique
"""
from decimal import Decimal

from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.urls import reverse

from auth_app.models import CustomUser
from usesOrders.models import CartItem
from usesOrders.promo import erreur_conditions

from .dessin import calculer_dessin, verifier_structure
from .formules import FormuleInvalide
from .models import Angle, ConfigProduit
from .tests_calcul import CalculBase

CARRE = [{"longueur": "Lc", "angle": 90}, {"longueur": "Lc", "angle": 90},
         {"longueur": "Lc", "angle": 90}, {"longueur": "Lc"}]


def creer_user(email, groupe="simple"):
    user = CustomUser.objects.create_user(username=email, email=email, password="MotDePasse-Solide-2026",
                                          first_name="Paul", last_name="Mbarga", email_verified=True)
    g, _ = Group.objects.get_or_create(name=groupe)
    user.groups.add(g)
    return user


# ---------------------------------------------------------------------------
# Dessin
# ---------------------------------------------------------------------------
class DessinTests(TestCase):

    def test_carre_ferme(self):
        d = calculer_dessin(CARRE, {"Lc": 20})
        self.assertEqual(d["points"], [[0, 0], [20, 0], [20, 20], [0, 20], [0, 0]])
        self.assertEqual([c["texte"] for c in d["cotes"]], ["20", "20", "20", "20"])

    def test_rectangle_avec_formules(self):
        rect = [{"longueur": "La", "angle": 90}, {"longueur": "Lb", "angle": 90},
                {"longueur": "La", "angle": 90}, {"longueur": "Lb"}]
        d = calculer_dessin(rect, {"La": 30, "Lb": 10})
        self.assertEqual(d["points"][2], [30, 10])

    def test_angle_choisi_par_le_client(self):
        """Un crochet qui suit l'angle choisi : « angle » dans la forme."""
        forme = [{"longueur": "Lc", "angle": "angle"}, {"longueur": "5*d/10"}]
        d = calculer_dessin(forme, {"Lc": 10, "d": 8, "angle": 90})
        self.assertEqual(d["points"][-1], [10, 4])

    def test_structure_refusee(self):
        for forme in ({"longueur": "Lc"}, [{"angle": 90}], [{"longueur": "Lc", "couleur": "rouge"}],
                      ["Lc"], [{"longueur": "Lc"}] * 41):
            with self.subTest(forme=str(forme)[:40]):
                with self.assertRaises(FormuleInvalide):
                    verifier_structure(forme)

    def test_longueur_negative_refusee(self):
        with self.assertRaisesMessage(FormuleInvalide, "longueur négative"):
            calculer_dessin([{"longueur": "Lc - 50"}], {"Lc": 10})

    def test_forme_verifiee_a_l_enregistrement(self):
        """La forme utilise les mêmes abréviations que la formule de Ltp."""
        cfg = ConfigProduit(diametres=[8], formule_ltp="4*Lc", forme=[{"longueur": "Lx"}])
        with self.assertRaisesMessage(FormuleInvalide, "Forme, segment 1 : abréviation inconnue : Lx"):
            cfg.verifier_formule_ltp([("Lc", Decimal(8), Decimal(100))])


# ---------------------------------------------------------------------------
# Choix de la page : gabarit universel ou ancienne page
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class ChoixDeLaPageTests(CalculBase):

    def url(self):
        return reverse("produit.detail", args=[self.produit.id])

    def test_case_non_cochee_ancienne_page(self):
        r = self.client.get(self.url())
        self.assertTemplateUsed(r, "produits/cintrages_cadres/cadre-carre.html")
        self.assertTemplateNotUsed(r, "boutique/gabarit/produit.html")

    def test_case_cochee_gabarit_universel(self):
        self.config.actif = True
        self.config.save()
        r = self.client.get(self.url())
        self.assertTemplateUsed(r, "boutique/gabarit/produit.html")
        self.assertNotContains(r, "Aperçu administrateur")

    def test_famille_exclue_jamais_basculee(self):
        """Même avec la case cochée en base, une famille exclue garde son ancienne page."""
        self.config.actif = True
        self.config.save()
        self.produit.sous_categorie = "Quincaillerie"
        self.produit.save()
        r = self.client.get(self.url())
        self.assertTemplateNotUsed(r, "boutique/gabarit/produit.html")


# ---------------------------------------------------------------------------
# Contenu de la page
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class ContenuDeLaPageTests(CalculBase):

    def setUp(self):
        super().setUp()
        self.config.actif = True
        self.config.forme = CARRE
        self.config.save()

    def page(self):
        return self.client.get(reverse("produit.detail", args=[self.produit.id]))

    def test_dimensions_cochees_seulement(self):
        r = self.page()
        self.assertContains(r, 'name="dim_Lc"')
        self.assertContains(r, "Longueur du côté Lc (cm)")
        self.assertContains(r, 'min="8"')
        self.assertContains(r, 'max="100"')
        self.assertNotContains(r, 'name="dim_Lb"')

    def test_diametres_et_angles_coches_seulement(self):
        r = self.page()
        self.assertContains(r, 'name="diametre" value="8"')
        self.assertNotContains(r, 'name="diametre" value="10"')
        self.assertContains(r, 'name="angle" value="90"')
        self.assertContains(r, 'name="angle" value="135"')
        self.assertNotContains(r, 'name="angle" value="180"')

    def test_marques_et_types_avec_un_prix(self):
        r = self.page()
        self.assertContains(r, 'name="marque_fer" value="prometal"')
        self.assertContains(r, 'name="type_fer" value="fe500"')
        self.assertNotContains(r, 'value="fe400"')     # pas de prix FE400 dans les données de test

    def test_r_et_ld_selon_les_cases(self):
        self.assertContains(self.page(), 'id="calc-r"')
        self.config.afficher_r = False
        self.config.afficher_ld = False
        self.config.save()
        r = self.page()
        self.assertNotContains(r, 'id="calc-r"')
        self.assertNotContains(r, 'id="calc-ldf"')
        self.assertContains(r, 'id="calc-lt"')

    def test_pas_de_bouton_angle_sans_angle(self):
        self.config.angles.clear()
        self.assertNotContains(self.page(), 'data-panneau="p-angle"')

    def test_images_et_espace_dessin(self):
        r = self.page()
        self.assertContains(r, "a.png")                # image 2D
        self.assertContains(r, 'id="dessin"')          # espace pour le dessin
        self.config.forme = []
        self.config.save()
        self.assertNotContains(self.page(), 'id="dessin"')

    def test_aucune_formule_dans_la_page(self):
        """Le calcul est fait par le serveur : ni formule, ni coefficient envoyés au navigateur."""
        r = self.page()
        self.assertNotContains(r, "4*Lc")
        self.assertNotContains(r, "COEF_PS")
        self.assertContains(r, reverse("boutique.calcul", args=[self.produit.id]))


# ---------------------------------------------------------------------------
# Calcul en direct (calcul.json)
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class CalculEnDirectTests(CalculBase):

    def setUp(self):
        super().setUp()
        self.config.actif = True
        self.config.forme = CARRE
        self.config.save()
        self.url = reverse("boutique.calcul", args=[self.produit.id])

    def post(self, **extra):
        data = {"fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500", "diametre": "8",
                "angle": "90", "dim_Lc": "20", "quantite": "50"}
        data.update(extra)
        return self.client.post(self.url, data).json()

    def test_resultat_de_l_exemple(self):
        data = self.post()
        self.assertTrue(data["ok"])
        self.assertEqual((data["lt"], data["pu"], data["total"]), (91, 430, 21500))
        self.assertEqual((data["ltp"], data["ldf"], data["r"]), (80, 10.4, 4))

    def test_dessin_renvoye(self):
        self.assertEqual(self.post()["dessin"]["points"][2], [20, 20])

    def test_erreur_lisible(self):
        data = self.post(dim_Lc="200")
        self.assertFalse(data["ok"])
        self.assertIn("entre 8 et 100 cm", data["erreur"])

    def test_quantite_trop_grande(self):
        self.assertIn("10000", self.post(quantite="20000")["erreur"])

    def test_prix_du_navigateur_ignore(self):
        self.assertEqual(self.post(prix="1", pu="1", total="1")["pu"], 430)

    def test_get_refuse(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_produit_non_bascule_invisible_pour_un_client(self):
        self.config.actif = False
        self.config.save()
        self.assertEqual(self.client.post(self.url, {}).status_code, 404)


# ---------------------------------------------------------------------------
# Ajout au panier (le serveur fait foi)
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class AjoutPanierTests(CalculBase):

    def setUp(self):
        super().setUp()
        self.config.actif = True
        self.config.save()
        self.client_a = creer_user("a@x.cm")
        self.url = reverse("produit.detail", args=[self.produit.id])

    def post(self, **extra):
        data = {"fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500", "diametre": "8",
                "angle": "90", "dim_Lc": "20", "quantite": "10"}
        data.update(extra)
        return self.client.post(self.url, data)

    def test_anonyme_doit_se_connecter(self):
        r = self.post()
        self.assertEqual(r.status_code, 302)
        self.assertIn("/auth/login/", r["Location"])
        self.assertFalse(CartItem.objects.exists())

    def test_ajout_avec_le_prix_du_serveur(self):
        self.client.force_login(self.client_a)
        r = self.post(prix="1", prix_revient="0", prix_Total="1")
        self.assertRedirects(r, reverse("panier"), fetch_redirect_response=False)
        item = CartItem.objects.get()
        self.assertEqual((item.prix_u, item.prix_revient, item.quantite), (430, Decimal("46.41"), 10))
        self.assertEqual(item.details["longueur_Total"], 91)
        self.assertEqual(item.details["Longueur du côté"], "20 cm")

    def test_meme_article_deux_fois_quantites_additionnees(self):
        self.client.force_login(self.client_a)
        self.post()
        self.post(quantite="5")
        self.assertEqual(CartItem.objects.get().quantite, 15)

    def test_saisie_invalide_rien_ajoute_et_saisies_conservees(self):
        self.client.force_login(self.client_a)
        r = self.post(dim_Lc="500")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "entre 8 et 100 cm")
        self.assertContains(r, 'value="500"')
        self.assertFalse(CartItem.objects.exists())

    def test_compatible_code_promo(self):
        """Le fer « bending iron » reste reconnu par les règles du code promo."""
        self.client.force_login(self.client_a)
        self.post()
        self.assertIsNone(erreur_conditions(CartItem.objects.get().cart))


# ---------------------------------------------------------------------------
# Aperçu administrateur (avant la bascule)
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class ApercuAdminTests(CalculBase):

    def setUp(self):
        super().setUp()
        self.admin = creer_user("admin@x.cm", "admin")
        self.url = reverse("boutique.apercu", args=[self.produit.id])

    def test_admin_voit_l_apercu_avant_la_bascule(self):
        self.client.force_login(self.admin)
        r = self.client.get(self.url)
        self.assertTemplateUsed(r, "boutique/gabarit/produit.html")
        self.assertContains(r, "Aperçu administrateur")
        self.assertNotContains(r, 'id="bouton-panier"')

    def test_admin_peut_calculer_avant_la_bascule(self):
        self.client.force_login(self.admin)
        data = self.client.post(reverse("boutique.calcul", args=[self.produit.id]), {
            "fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500", "diametre": "8",
            "angle": "90", "dim_Lc": "20"}).json()
        self.assertEqual(data["pu"], 430)

    def test_apercu_n_ajoute_rien_au_panier(self):
        self.client.force_login(self.admin)
        self.client.post(self.url, {"fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500",
                                    "diametre": "8", "angle": "90", "dim_Lc": "20"})
        self.assertFalse(CartItem.objects.exists())

    def test_client_refuse(self):
        self.client.force_login(creer_user("c@x.cm"))
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_famille_exclue_pas_d_apercu(self):
        self.client.force_login(self.admin)
        self.produit.sous_categorie = "boulon d'ancrage a beton"
        self.produit.save()
        self.assertEqual(self.client.get(self.url).status_code, 404)
