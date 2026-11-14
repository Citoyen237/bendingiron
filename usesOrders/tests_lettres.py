"""Montants en lettres (factures, e-mail d'annulation) — 14/11/2026."""
from decimal import Decimal

from django.template.loader import render_to_string
from django.test import SimpleTestCase

from usesOrders.lettres import en_lettres


class EnLettresTests(SimpleTestCase):
    def test_regles_du_francais(self):
        cas = {
            0: "zéro", 1: "un", 17: "dix-sept", 21: "vingt et un", 71: "soixante et onze",
            77: "soixante-dix-sept", 80: "quatre-vingts", 81: "quatre-vingt-un", 91: "quatre-vingt-onze",
            100: "cent", 200: "deux cents", 201: "deux cent un", 1000: "mille", 2000: "deux mille",
            80000: "quatre-vingt mille", 200000: "deux cent mille", 1000000: "un million",
            200000000: "deux cents millions", 1000000000: "un milliard",
            5149261: "cinq millions cent quarante-neuf mille deux cent soixante et un",
        }
        for nombre, attendu in cas.items():
            self.assertEqual(en_lettres(nombre), attendu, nombre)

    def test_decimal_arrondi_au_franc(self):
        self.assertEqual(en_lettres(Decimal("2385.50")), "deux mille trois cent quatre-vingt-six")

    def test_sous_le_tableau_des_factures(self):
        contexte = {"net_payer": 2385, "produits": [], "order": None}
        for gabarit in ("invoice.html", "invoice2.html", "invoice-additional.html", "invoice_pro.html"):
            html = render_to_string(gabarit, contexte)
            self.assertIn(">Deux mille trois cent quatre-vingt-cinq francs CFA<", html, gabarit)
            self.assertIn("à la somme TTC de", html, gabarit)
            self.assertLess(html.index("</table>"), html.index("Arrêté la présente"), gabarit)
