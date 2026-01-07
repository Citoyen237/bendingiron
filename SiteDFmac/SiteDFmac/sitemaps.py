from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return [
            'font.index',
            'about',
            'contact.index',
            'services',
            'domaine.expertise',
            'domaine.boutique',
            'domaine.faarmature',
            'domaine.pose.armature'
        ]

    def location(self, item):
        return reverse(item)
