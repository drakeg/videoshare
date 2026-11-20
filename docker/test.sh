#!/bin/sh
set -eu

python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test --parallel "${DJANGO_TEST_PROCESSES:-4}"
