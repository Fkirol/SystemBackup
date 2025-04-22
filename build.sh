#!/usr/bin/env bash
# Exit on error
set -o errexit
pip install --upgrade drf-yasg
pip install --upgrade drf-yasg[validation]

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt


python manage.py collectstatic --no-input


python manage.py migrate

python database_inizializer.py