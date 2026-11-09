"""Réglages de développement local (MySQL local, DEBUG actif)."""
from .settings import *  # noqa

DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']

if config('DB_ENGINE', default='mysql') != 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': config('DB_NAME', default='bendingiron_db'),
            'USER': config('DB_USER', default='root'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='127.0.0.1'),
            'PORT': config('DB_PORT', default='3306'),
            # Voir settings.py : nouvelles tables en InnoDB
            'OPTIONS': {'init_command': "SET default_storage_engine=INNODB"},
        }
    }
