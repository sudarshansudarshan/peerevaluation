#!/bin/bash

set -e  # Exit on any error

echo "Running database migrations..."
python manage.py migrate

echo "Creating superuser..."
python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || {
    echo "Superuser creation failed. It might already exist."
}

echo "Starting development server..."
python manage.py runserver 0.0.0.0:8000