#!/bin/bash
set -e
cd /var/www/bendingiron/
# Les fichiers ont été copiés par la CI : on reconstruit et on relance.
docker compose up -d --build
docker image prune -f
echo "Deployment completed."
