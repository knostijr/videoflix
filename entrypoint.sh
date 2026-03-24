#!/bin/bash

while ! nc -z db 5432; do
  echo "Warten auf die Datenbank..."
  sleep 1
done

python manage.py migrate

exec "$@"