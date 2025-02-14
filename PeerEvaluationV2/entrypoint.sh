#!/bin/bash

set -e  # Exit on any error

echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser..."
python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || {
    echo "Superuser creation failed. It might already exist."
}

echo "Starting development server..."
python manage.py collectstatic --noinput
python manage.py runserver_plus 0.0.0.0:443 --cert-file cert.pem --key-file key.pem