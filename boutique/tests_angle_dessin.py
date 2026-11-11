"""Angle choisi par le client : dessin, admin, migration, factures (11/11/2026)."""
import importlib

from django.contrib.auth.models import Group
from django.template.loader import render_to_string
from django.test import TestCase

from SiteDFmac.factures import image_dessin

from .admin import ConfigProduitForm
from .dessin import calculer_dessin, forme_utilise_angle, svg_miniature
from .models import Angle, ConfigProduit
from .tests import creer_produit

MIGRATION = importlib.import_module("boutique.migrations.0005_forme_suit_l_angle")
ANCIEN_CARRE, NOUVEAU_CARRE = MIGRATION.FORMES[0]
ANCIEN_RECT, NOUVEAU_RECT = MIGRATION.FORMES[1]
VALEURS = {"Lc": 20, "La": 15, "Lg": 30, "Ldf": 12, "R": 1.2, "d": 8}


def angles_ecrits(forme, angle):
    dessin = calculer_dessin(forme, {**VALEURS, "angle": angle})
    return [c["texte"] for c in dessin["cotes"] if c["type"] == "angle"]


class AngleSurLeDessinTests(TestCase):
    def test_crochets_suivent_l_angle_choisi(self):
        for angle in (90, 135):
            points = calculer_dessin(NOUVEAU_CARRE, {**VALEURS, "angle": angle})["points"]
            # 1er segment = crochet de départ ; 2e = premier côté (vers le bas)
            (x0, y0), (x1, y1), (x2, y2) = points[0], points[1], points[2]
            import math
            cap1 = math.degrees(math.atan2(y1 - y0, x1 - x0))
            cap2 = math.degrees(math.atan2(y2 - y1, x2 - x1))
            self.assertAlmostEqual((cap1 - cap2) % 360, angle, places=3)

    def test_angle_ecrit_une_fois_par_coin(self):
        self.assertEqual(angles_ecrits(NOUVEAU_CARRE, 135), ["135°"])
        self.assertEqual(angles_ecrits(NOUVEAU_CARRE, 90), ["90°"])
        self.assertEqual(angles_ecrits(NOUVEAU_RECT, 135), ["135°"])

    def test_pliages_fixes_non_annotes(self):
        self.assertEqual(angles_ecrits(ANCIEN_CARRE, 90), [])   # forme d'origine : angle en dur

    def test_forme_utilise_angle(self):
        self.assertTrue(forme_utilise_angle(NOUVEAU_CARRE))
        self.assertFalse(forme_utilise_angle(ANCIEN_CARRE))
        self.assertFalse(forme_utilise_angle([]))

    def test_miniature_de_facture_sans_texte(self):
        svg = svg_miniature(calculer_dessin(NOUVEAU_CARRE, {**VALEURS, "angle": 135}))
        self.assertIn('width="90" height="90"', svg)
        self.assertNotIn("<text", svg)   # ni longueurs ni angle sur l'image de la facture


class ImageDessinFactureTests(TestCase):
    def test_dessin_du_site_accepte(self):
        svg = svg_miniature(calculer_dessin(NOUVEAU_CARRE, {**VALEURS, "angle": 135}))
        self.assertTrue(image_dessin({"dessin_svg": svg}).startswith("data:image/svg+xml;base64,"))

    def test_ancien_dessin_70px_accepte(self):
        svg = svg_miniature(calculer_dessin(ANCIEN_CARRE, {**VALEURS, "angle": 135}), taille=70)
        self.assertNotEqual(image_dessin({"dessin_svg": svg}), "")

    def test_faux_dessins_refuses(self):
        vrai = svg_miniature(calculer_dessin(NOUVEAU_CARRE, {**VALEURS, "angle": 135}))
        faux = [
            '<svg xmlns="http://www.w3.org/2000/svg"><image href="http://169.254.169.254/"/></svg>',
            vrai.replace("</svg>", "<script>alert(1)</script></svg>"),
            vrai.replace("</svg>", '<text x="0" y="0">135°</text></svg>'),
            "pas un dessin",
        ]
        for f in faux:
            self.assertEqual(image_dessin({"dessin_svg": f}), "", f[:40])
        self.assertEqual(image_dessin({}), "")
        self.assertEqual(image_dessin(None), "")

    def test_image_sous_le_nom_dans_les_factures(self):
        svg = svg_miniature(calculer_dessin(NOUVEAU_CARRE, {**VALEURS, "angle": 135}))
        ligne = {"produit": "cadre carre", "details": "", "quantite": 1, "prix": 10, "total": 10,
                 "dessin": image_dessin({"dessin_svg": svg})}
        sans = {**ligne, "dessin": ""}
        for modele in ("invoice.html", "invoice2.html", "invoice_pro.html", "bon-livraison-pro.html",
                       "bon_pdf.html", "projet_pdf.html", "invoice-additional.html", "invoice-order-pro.html"):
            html = render_to_string(modele, {"produits": [ligne]})
            self.assertIn("cadre carre", html, modele)
            self.assertIn('<img src="data:image/svg+xml;base64,', html, modele)
            html_sans = render_to_string(modele, {"produits": [sans]})
            self.assertNotIn("data:image/svg+xml", html_sans, modele)


class AdminAngleTests(TestCase):
    def setUp(self):
        self.angle, _ = Angle.objects.update_or_create(valeur=135, defaults={"libelle": "135°", "actif": True})

    def formulaire(self, forme, angles):
        return ConfigProduitForm(data={
            "produit": creer_produit().pk, "diametres": ["8"], "angles": [a.pk for a in angles],
            "formule_ltp": "4*Lc", "forme": __import__("json").dumps(forme)})

    def test_angles_proposes_mais_forme_fixe_refusee(self):
        f = self.formulaire(ANCIEN_CARRE, [self.angle])
        self.assertFalse(f.is_valid())
        self.assertIn("forme", f.errors)
        self.assertIn("ne les utilise pas", str(f.errors["forme"]))

    def test_forme_qui_suit_l_angle_acceptee(self):
        f = self.formulaire(NOUVEAU_CARRE, [self.angle])
        f.is_valid()
        self.assertNotIn("forme", f.errors)

    def test_sans_angle_propose_forme_fixe_acceptee(self):
        f = self.formulaire(ANCIEN_CARRE, [])
        f.is_valid()
        self.assertNotIn("forme", f.errors)


class MigrationFormeTests(TestCase):
    def test_remplace_seulement_les_formes_d_origine(self):
        from django.apps import apps
        carre = ConfigProduit.objects.create(produit=creer_produit("cadre carre"), diametres=[8],
                                             formule_ltp="4*Lc", forme=ANCIEN_CARRE)
        rect = ConfigProduit.objects.create(produit=creer_produit("cadre rectangulaire"), diametres=[8],
                                            formule_ltp="2*La+2*Lg", forme=ANCIEN_RECT)
        retouchee = [dict(s) for s in ANCIEN_CARRE]
        retouchee[2]["angle"] = -91
        autre = ConfigProduit.objects.create(produit=creer_produit("autre cadre"), diametres=[8],
                                             formule_ltp="4*Lc", forme=retouchee)
        MIGRATION.aller(apps, None)
        for cfg in (carre, rect, autre):
            cfg.refresh_from_db()
        self.assertEqual(carre.forme, NOUVEAU_CARRE)
        self.assertEqual(rect.forme, NOUVEAU_RECT)
        self.assertEqual(autre.forme, retouchee)          # retouchée à la main : pas écrasée
        MIGRATION.retour(apps, None)
        carre.refresh_from_db()
        self.assertEqual(carre.forme, ANCIEN_CARRE)
