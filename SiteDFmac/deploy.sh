#!/bin/bash

# Pull the latest changes
cd  /var/www/bendingiron/
git pull origin main  # Change 'main' to your branch if needed
# Build and start the Docker containers
docker compose up -d

echo "Deployment completed."
