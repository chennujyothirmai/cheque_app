#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Create static files
python manage.py collectstatic --noinput
