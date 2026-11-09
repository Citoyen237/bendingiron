"""Réglages de production : tout vient du .env, DEBUG toujours désactivé."""
from .settings import *  # noqa

DEBUG = False
PAIEMENT_SIMULATION = False  # jamais de faux paiements en production

# Si le cookie CSRF doit être partagé entre bending-iron.com et www.bending-iron.com
CSRF_COOKIE_DOMAIN = config('CSRF_COOKIE_DOMAIN', default=None)
