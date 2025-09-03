from .settings import *
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT')
    }
}




# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# addresse acepter en production
CSRF_TRUSTED_ORIGINS = [
    'https://www.bending-iron.com',  
    'http://www.bending-iron.com',
    'http://localhost',
]

CSRF_COOKIE_DOMAIN = '.bending-iron.com'