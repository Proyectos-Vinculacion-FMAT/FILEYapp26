# syntax=docker/dockerfile:1
FROM python:3.14-slim

# Keep Python lean and predictable inside the container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Build deps for psycopg2 (in case no wheel is available for this Python).
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project.
COPY fileyapp/ ./fileyapp/

WORKDIR /app/fileyapp

# Collect static files (admin + DRF) so WhiteNoise can serve them.
# A dummy SECRET_KEY is fine here; collectstatic doesn't need the real one.
RUN DJANGO_SECRET_KEY=build-time DJANGO_DEBUG=False \
    python manage.py collectstatic --noinput

EXPOSE 8000

# On start: apply migrations, then run gunicorn.
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn filey_back.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60"]
