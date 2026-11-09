"""
Tests des retours du 08/11/2026 sur le gabarit universel :
  1. erreur affichée sous le champ concerné (limites, quantité…) ;
  2. qui fournit le fer, la marque et le type ne sont pas présélectionnés ;
  3. dessin comme l'image de référence : coins arrondis au rayon R,
     crochets (Ldf) dessinés sans valeur ;
  4. miniature 70 x 70 px enregistrée avec l'article, pour la facture.

Lancer :  python manage.py test boutique
"""
from django.test import TestCase, override_settings
from django.urls import reverse

from usesOrders.models import CartItem

from .calcul import CalculImpossible, calculer
from .dessin import calculer_dessin, svg_miniature, verifier_structure
from .formules import FormuleInvalide
from .models import PoidsFer
from .tests_calcul import CalculBase
from .tests_gabarit import CARRE, creer_user

CADRE_AVEC_CROCHETS = [
    {"longueur": 0, "angle": 45, "cote": False},              # oriente le départ
    {"longueur": "Ldf/2", "angle": -135, "cote": False},      # crochet de départ
    {"longueur": "Lc", "angle": -90}, {"longueur": "Lc", "angle": -90},
    {"longueur": "Lc", "angle": -90}, {"longueur": "Lc", "angle": -135},
    {"longueur": "Ldf/2", "cote": False},                     # crochet de fin
]


# ---------------------------------------------------------------------------
# 1. Chaque erreur indique son champ
# ---------------------------------------------------------------------------
class ChampDeLErreurTests(CalculBase):

    def champ(self, **extra):
        with self.assertRaises(CalculImpossible) as ctx:
            calculer(self.config, self.saisies(**extra))
        return ctx.exception.champ

    def test_champs(self):
        self.assertEqual(self.champ(fer=""), "fer")
        self.assertEqual(self.champ(marque_fer=""), "marque_fer")
        self.assertEqual(self.champ(type_fer=""), "type_fer")
        self.assertEqual(self.champ(diametre="10"), "diametre")
        self.assertEqual(self.champ(angle="180"), "angle")
        self.assertEqual(self.champ(dimensions={"Lc": "500"}), "dim_Lc")
        self.assertEqual(self.champ(dimensions={"Lc": "abc"}), "dim_Lc")
        self.assertEqual(self.champ(quantite="0"), "quantite")

    def test_marque_et_type_vides_messages_clairs(self):
        with self.assertRaisesMessage(CalculImpossible, "Choisissez la marque du fer"):
            calculer(self.config, self.saisies(marque_fer=""))
        with self.assertRaisesMessage(CalculImpossible, "Choisissez le type de fer"):
            calculer(self.config, self.saisies(type_fer=""))

    def test_donnee_admin_manquante_sans_champ(self):
        PoidsFer.objects.all().delete()
        self.assertIsNone(self.champ())

    def test_variables_pour_le_dessin(self):
        v = calculer(self.config, self.saisies()).variables
        self.assertEqual((v["Ltp"], v["Ldf"], v["Lt"]), (80.0, 10.4, 91))


# ---------------------------------------------------------------------------
# 3. et 4. Dessin arrondi, crochets sans valeur, miniature
# ---------------------------------------------------------------------------
class DessinArrondiTests(TestCase):
    VARIABLES = {"Lc": 20, "d": 8, "R": 4, "Ldf": 10.4}

    def test_coins_arrondis_au_rayon(self):
        d = calculer_dessin(CARRE, {"Lc": 20, "R": 4})
        self.assertEqual(d["chemin"].count("A4 4"), 3)          # 3 coins intérieurs, rayon 4

    def test_sans_rayon_coins_droits(self):
        self.assertNotIn("A", calculer_dessin(CARRE, {"Lc": 20, "R": 0})["chemin"])

    def test_crochets_sans_valeur(self):
        d = calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES)
        self.assertEqual([c["texte"] for c in d["cotes"]], ["20", "20", "20", "20"])   # pas de « 5.2 »

    def test_crochets_dans_l_angle_vers_l_interieur(self):
        p = calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES)["points"]
        coin = p[1]                                              # le segment d'orientation (0) n'a pas de point
        self.assertEqual(p[-2], coin)                            # on revient au même coin
        self.assertAlmostEqual(p[0][0], p[-1][0], places=2)      # les deux bouts se superposent
        self.assertAlmostEqual(p[0][1], p[-1][1], places=2)
        self.assertLess(p[-1][0], coin[0])                       # vers l'intérieur du cadre
        self.assertLess(p[-1][1], coin[1])

    def test_rayon_entier_au_debut_et_a_la_fin_du_pliage(self):
        """Les 2 pliages des crochets (135°) gardent le rayon R = 4 en entier, comme les 3 autres coins."""
        chemin = calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES)["chemin"]
        self.assertEqual(chemin.count("A4 4"), 5)

    def test_ldf_droit_apres_l_arc(self):
        """Crochet = arc de rayon R, puis Ldf/2 en ligne droite (au début et à la fin du pliage)."""
        import math
        import re
        chemin = calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES)["chemin"]
        nombres = [float(n) for n in re.findall(r"-?[\d.]+", chemin)]
        # début : M0 0 puis L x y = crochet de départ
        self.assertAlmostEqual(math.dist((0, 0), (nombres[2], nombres[3])), 5.2, places=2)
        # fin : fin du dernier arc (A … x y) puis L x y = crochet de fin
        self.assertAlmostEqual(math.dist((nombres[-4], nombres[-3]), (nombres[-2], nombres[-1])), 5.2, places=2)

    def test_coin_des_crochets_arrondi_comme_les_autres(self):
        """Les 2 crochets suivent l'arrondi du coin : le tracé atteint le coin réel (x max et y max)."""
        d = calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES)
        x, y, largeur, hauteur = d["cadre"]
        self.assertAlmostEqual(largeur, 20, places=1)            # le carré garde sa taille : 20 x 20
        self.assertAlmostEqual(hauteur, 20, places=1)

    def test_sans_rayon_crochet_egal_a_ldf(self):
        import math
        p = calculer_dessin(CADRE_AVEC_CROCHETS, {**self.VARIABLES, "R": 0})["points"]
        self.assertAlmostEqual(math.dist(p[0], p[1]), 5.2, places=2)

    def test_rayon_reduit_si_segment_trop_court(self):
        d = calculer_dessin(CADRE_AVEC_CROCHETS, {**self.VARIABLES, "R": 50})
        self.assertNotIn("A50", d["chemin"])

    def test_cle_cote_verifiee(self):
        with self.assertRaises(FormuleInvalide):
            verifier_structure([{"longueur": "Lc", "cote": "non"}])

    def test_miniature_70_pixels_sans_texte(self):
        svg = svg_miniature(calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES))
        self.assertIn('width="70" height="70"', svg)
        self.assertIn("<path", svg)
        self.assertIn("#f2a900", svg)
        self.assertNotIn("<text", svg)

    def test_miniature_vide_sans_forme(self):
        self.assertEqual(svg_miniature(None), "")


# ---------------------------------------------------------------------------
# Page produit
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class RetoursPageTests(CalculBase):

    def setUp(self):
        super().setUp()
        self.config.actif = True
        self.config.forme = CADRE_AVEC_CROCHETS
        self.config.save()
        self.url = reverse("produit.detail", args=[self.produit.id])
        self.client_a = creer_user("a@x.cm")

    def post(self, **extra):
        data = {"fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500", "diametre": "8",
                "angle": "90", "dim_Lc": "20", "quantite": "10"}
        data.update(extra)
        return self.client.post(self.url, data)

    @staticmethod
    def zone(html, champ):
        """Contenu de la zone d'erreur d'un champ (balise ouvrante comprise)."""
        debut = html.index(f'data-champ="{champ}"')
        return html[debut:html.index("</div>", debut)]

    def test_fer_marque_type_non_preselectionnes(self):
        html = self.client.get(self.url).content.decode()
        for nom in ("fer", "marque_fer", "type_fer"):
            with self.subTest(champ=nom):
                debut = 0
                while True:
                    debut = html.find(f'name="{nom}"', debut + 1)
                    if debut == -1:
                        break
                    balise = html[html.rindex("<input", 0, debut):html.index(">", debut)]
                    self.assertNotIn("checked", balise)

    def test_pas_d_erreur_a_l_ouverture(self):
        html = self.client.get(self.url).content.decode()
        for champ in ("fer", "marque_fer", "type_fer", "dim_Lc", "quantite"):
            self.assertIn("hidden", self.zone(html, champ))

    def test_erreur_sous_le_champ_concerne(self):
        self.client.force_login(self.client_a)
        html = self.post(dim_Lc="500").content.decode()
        zone = self.zone(html, "dim_Lc")
        self.assertNotIn("hidden", zone)
        self.assertIn("entre 8 et 100 cm", zone)
        self.assertIn("hidden", self.zone(html, "fer"))          # les autres champs n'affichent rien
        self.assertIn("hidden", self.zone(html, "quantite"))

    def test_erreur_quantite_sous_la_quantite(self):
        self.client.force_login(self.client_a)
        zone = self.zone(self.post(quantite="20000").content.decode(), "quantite")
        self.assertIn("10000", zone)

    def test_fer_non_choisi_erreur_sous_le_choix(self):
        self.client.force_login(self.client_a)
        zone = self.zone(self.post(fer="").content.decode(), "fer")
        self.assertIn("Précisez qui fournit le fer", zone)
        self.assertFalse(CartItem.objects.exists())

    def test_calcul_json_indique_le_champ(self):
        data = self.client.post(reverse("boutique.calcul", args=[self.produit.id]), {
            "fer": "bending iron", "marque_fer": "", "type_fer": "fe500", "diametre": "8",
            "angle": "90", "dim_Lc": "20"}).json()
        self.assertEqual((data["ok"], data["champ"]), (False, "marque_fer"))

    def test_dessin_renvoye_avec_crochets_et_arrondis(self):
        data = self.client.post(reverse("boutique.calcul", args=[self.produit.id]), {
            "fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500", "diametre": "8",
            "angle": "90", "dim_Lc": "20"}).json()
        self.assertIn(" A", data["dessin"]["chemin"])
        self.assertEqual(len(data["dessin"]["cotes"]), 4)

    def test_miniature_enregistree_avec_l_article(self):
        self.client.force_login(self.client_a)
        self.post()
        item = CartItem.objects.get()
        self.assertIn('width="70" height="70"', item.details["dessin_svg"])
        self.assertNotIn("dessin_svg", item.details_to_text())
        self.assertNotIn("<svg", item.details_to_text())

    def test_meme_article_deux_fois_toujours_additionne(self):
        """La miniature est identique pour les mêmes choix : la quantité s'additionne."""
        self.client.force_login(self.client_a)
        self.post()
        self.post(quantite="5")
        self.assertEqual(CartItem.objects.get().quantite, 15)


class SensDesArcsTests(TestCase):
    """Régression : les arcs doivent tourner dans le sens du pliage (sinon coins « creusés »)."""

    def test_virage_a_droite_horaire_a_l_ecran(self):
        # carré parcouru dans le sens horaire (virages à droite, -90°)
        horaire = [{"longueur": "Lc", "angle": -90}] * 3 + [{"longueur": "Lc"}]
        self.assertIn("A4 4 0 0 1", calculer_dessin(horaire, {"Lc": 20, "R": 4})["chemin"])
        self.assertNotIn("A4 4 0 0 0", calculer_dessin(horaire, {"Lc": 20, "R": 4})["chemin"])

    def test_virage_a_gauche_antihoraire_a_l_ecran(self):
        self.assertIn("A4 4 0 0 0", calculer_dessin(CARRE, {"Lc": 20, "R": 4})["chemin"])

    def test_cadre_garde_sa_taille_dans_les_deux_sens(self):
        horaire = [{"longueur": "Lc", "angle": -90}] * 3 + [{"longueur": "Lc"}]
        for forme in (CARRE, horaire):
            _, _, largeur, hauteur = calculer_dessin(forme, {"Lc": 20, "R": 4})["cadre"]
            self.assertAlmostEqual(largeur, 20, places=1)
            self.assertAlmostEqual(hauteur, 20, places=1)


# ---------------------------------------------------------------------------
# Valeur des crochets (Ldf) écrite sur le dessin
# ---------------------------------------------------------------------------
CADRE_CROCHETS_AFFICHES = [
    {"longueur": 0, "angle": 45, "cote": False},
    {"longueur": "Ldf/2", "angle": -135, "crochet": True},
    {"longueur": "Lc", "angle": -90}, {"longueur": "Lc", "angle": -90},
    {"longueur": "Lc", "angle": -90}, {"longueur": "Lc", "angle": -135},
    {"longueur": "Ldf/2", "crochet": True},
]


class ValeurLdfSurLeDessinTests(TestCase):
    VARIABLES = {"Lc": 20, "d": 8, "R": 4, "Ldf": 10.4}

    def test_valeur_des_crochets_affichee(self):
        cotes = calculer_dessin(CADRE_CROCHETS_AFFICHES, self.VARIABLES)["cotes"]
        self.assertEqual([(c["type"], c["texte"]) for c in cotes],
                         [("ldf", "5.2"), ("cote", "20"), ("cote", "20"), ("cote", "20"), ("cote", "20"),
                          ("ldf", "5.2")])

    def test_meme_trace_que_l_ancienne_ecriture(self):
        """« crochet »: true et l'ancien « cote »: false donnent le même tracé."""
        self.assertEqual(calculer_dessin(CADRE_CROCHETS_AFFICHES, self.VARIABLES)["chemin"],
                         calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES)["chemin"])

    def test_ancienne_ecriture_sans_valeur(self):
        types = {c["type"] for c in calculer_dessin(CADRE_AVEC_CROCHETS, self.VARIABLES)["cotes"]}
        self.assertEqual(types, {"cote"})

    def test_crochet_sans_valeur_possible(self):
        forme = [dict(s, cote=False) if s.get("crochet") else s for s in CADRE_CROCHETS_AFFICHES]
        types = {c["type"] for c in calculer_dessin(forme, self.VARIABLES)["cotes"]}
        self.assertEqual(types, {"cote"})

    def test_cle_crochet_verifiee(self):
        with self.assertRaises(FormuleInvalide):
            verifier_structure([{"longueur": "Lc", "crochet": "oui"}])

    def test_miniature_toujours_sans_texte(self):
        svg = svg_miniature(calculer_dessin(CADRE_CROCHETS_AFFICHES, self.VARIABLES))
        self.assertNotIn("<text", svg)
        self.assertNotIn("5.2", svg)


# ---------------------------------------------------------------------------
# Poids d'une pièce et poids total affichés sur la page
# ---------------------------------------------------------------------------
@override_settings(SECURE_SSL_REDIRECT=False)
class PoidsAfficheTests(CalculBase):

    def setUp(self):
        super().setUp()
        self.config.actif = True
        self.config.save()

    def test_poids_total_calcule(self):
        r = calculer(self.config, self.saisies(quantite="50"))
        self.assertEqual(r.poids, r.poids_total / 50)
        self.assertAlmostEqual(float(r.poids_total), 0.35945 * 50, places=4)    # Lt 91 cm x 0,00395 kg/cm

    def test_lignes_poids_sur_la_page(self):
        html = self.client.get(reverse("produit.detail", args=[self.produit.id])).content.decode()
        self.assertIn("Poids d'une pièce (kg)", html.replace("&#x27;", "'"))
        self.assertIn('id="calc-poids"', html)
        self.assertIn('id="calc-poids_total"', html)
        # les poids viennent après la longueur totale et avant les prix
        self.assertLess(html.index('id="calc-lt"'), html.index('id="calc-poids"'))
        self.assertLess(html.index('id="calc-poids_total"'), html.index('id="calc-pu"'))

    def test_poids_dans_le_calcul_en_direct(self):
        data = self.client.post(reverse("boutique.calcul", args=[self.produit.id]), {
            "fer": "bending iron", "marque_fer": "prometal", "type_fer": "fe500", "diametre": "8",
            "angle": "90", "dim_Lc": "20", "quantite": "50"}).json()
        self.assertEqual(data["poids"], 0.359)
        self.assertEqual(data["poids_total"], 17.97)
