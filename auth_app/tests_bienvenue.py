"""« Bienvenue … » affiché sur l'accueil sous le logo, et plus sur la page Paramétrage (14/11/2026)."""
from django.test import TestCase
from django.urls import reverse

from auth_app.models import CustomUser


class BienvenueAccueilTests(TestCase):
    def test_bienvenue_sous_le_logo_puis_consomme(self):
        CustomUser.objects.create_user(username="n@x.cm", email="n@x.cm", password="MotDePasse-Solide-2026",
                                       first_name="Nana")
        reponse = self.client.post(reverse("login"), {"email": "n@x.cm", "password": "MotDePasse-Solide-2026"},
                                   follow=True, secure=True)
        self.assertEqual(reponse.request["PATH_INFO"], reverse("font.index"))
        html = reponse.content.decode()
        self.assertIn('class="message-accueil message-success"', html)
        self.assertIn("Bienvenue Nana!", html)
        self.assertLess(html.index("logoiron.png"), html.index("Bienvenue Nana!"))   # sous le logo

        # affiché une seule fois : la page suivante ne le montre plus
        accueil = self.client.get(reverse("font.index"), secure=True).content.decode()
        self.assertNotIn("Bienvenue Nana!", accueil)
