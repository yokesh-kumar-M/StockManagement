#!/usr/bin/env bash
# Build script for Render deployment
set -o errexit

pip install --upgrade pip
pip install -r requirements/prod.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Seed initial stock data (safe to run multiple times)
python manage.py seed_stocks
