#!/bin/sh
set -e

echo "Application des migrations..."
# Les migrations sont générées en développement et versionnées ; on ne fait que les appliquer ici.
python manage.py migrate --noinput

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Démarrage de Gunicorn (${GUNICORN_WORKERS:-4} workers)"
exec gunicorn SiteDFmac.wsgi:application \
    -b 0.0.0.0:8000 \
    -w "${GUNICORN_WORKERS:-4}" \
    --threads 4 \
    --timeout 60 \
    --log-level info \
    --access-logfile -
