#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations (IMPORTANT for fixing Internal Server Error)
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create static files
python manage.py collectstatic --noinput
