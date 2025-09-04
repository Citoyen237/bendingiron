#!/bin/bash
#set -e
cat << EOF
  _____ _____.__ .__ 
_/ __ \ __\   __\| |/ ___\\__ \ | | / ___/
\ ___/| | | | | \ \ \ ___ / __ \| |__\___ \
\___ >__| |__| |__|\___ >____ /____/____ >
\/ \/ \/ \/ \/
EOF

echo "Running the project"
echo "Installing requirements..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py makemigrations --merge
python manage.py migrate

echo "  "
echo "============================"
echo "Running Test and Sonar..."
echo "============================"
python manage.py test

if [ $? -ne 0 ]; then
  echo " "
  echo "❌ Test step failed, please fix before pushing."
  exit 1
fi

echo "Collection statics?yes/or pass"
echo 'yes' | python manage.py collectstatic --noinput

sleep 5

echo "** Number of workers ${GUNICORN_WORKERS}"
echo "** Version ${VERSION}"
echo "** Starting gunicorn on multiple ports..."

# Starting Gunicorn 
gunicorn django_invoice.wsgi:application -b 0:8000 -w "${GUNICORN_WORKERS}" --log-level DEBUG --reload --threads=10 --timeout=3600 &

# Wait for all background jobs to finish
wait
