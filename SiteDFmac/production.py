"""Réglages de production : tout vient du .env, DEBUG toujours désactivé."""
from .settings import *  # noqa

DEBUG = False
PAIEMENT_SIMULATION = False  # jamais de faux paiements en production

# Protections HTTPS / cookies imposées ici aussi : settings.py ne les active que
# si DEBUG vaut False dans le .env. Sans ces lignes, un DEBUG=True oublié dans le
# .env du serveur les désactiverait en silence (DEBUG étant remis à False ci-dessus).
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Si le cookie CSRF doit être partagé entre bending-iron.com et www.bending-iron.com
CSRF_COOKIE_DOMAIN = config('CSRF_COOKIE_DOMAIN', default=None)
