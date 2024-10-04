#!/bin/bash

# Ensure pip is installed for Python 3.9
echo "Installing pip for Python 3.9"
python3.9 -m ensurepip --upgrade

# Upgrade pip to the latest version
python3.9 -m pip install --upgrade pip

# Install project dependencies
echo "Installing dependencies"
python3.9 -m pip install -r requirements.txt

# Run migrations
echo "Running migrations"
python3.9 manage.py makemigrations --noinput
python3.9 manage.py migrate --noinput

# Collect static files
echo "Collecting static files"
python3.9 manage.py collectstatic --noinput --clear
