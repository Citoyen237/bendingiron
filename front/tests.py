"""Tests du site public.

Lancer :  python manage.py test front
"""
from django.test import TestCase, override_settings


@override_settings(SECURE_SSL_REDIRECT=False)
class SitemapTests(TestCase):
    """Régression : sans « django.contrib.sitemaps » dans INSTALLED_APPS,
    /sitemap.xml renvoyait une erreur 500 (gabarit sitemap.xml introuvable)."""

    def test_sitemap_accessible(self):
        r = self.client.get("/sitemap.xml")
        self.assertEqual(r.status_code, 200)
        self.assertIn("<urlset", r.content.decode())
