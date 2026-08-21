#!/bin/bash
set -e

echo "Iniciando Gunicorn..."
# Reemplazar el proceso actual por gunicorn (buena práctica para Docker)
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
