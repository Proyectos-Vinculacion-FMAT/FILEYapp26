#!/bin/bash
set -e

echo "Iniciando PostgreSQL interno..."
# Iniciar el servicio de Postgres en segundo plano
/etc/init.d/postgresql start

# Esperar a que Postgres esté levantado y aceptando conexiones
echo "Esperando a que Postgres acepte conexiones..."
until sudo -u postgres psql -c '\q' > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL está listo."

# Crear usuario y base de datos si no existen
echo "Configurando base de datos..."
sudo -u postgres psql -c "CREATE USER filey_user WITH PASSWORD 'filey_password';" || true
sudo -u postgres psql -c "CREATE DATABASE filey_db OWNER filey_user;" || true

# Configurar la variable de entorno para que Django sepa a dónde conectarse
# Como Postgres y Django viven en el mismo contenedor, se usa 127.0.0.1
export DATABASE_URL="postgres://filey_user:filey_password@127.0.0.1:5432/filey_db"

echo "Aplicando migraciones..."
python manage.py migrate --noinput

# ---------------------------------------------------------
# OPCIONAL: Aquí puedes agregar tu comando para sembrar datos
# python manage.py loaddata qa_data.json
# python manage.py tu_comando_de_qa
# ---------------------------------------------------------

echo "Iniciando Gunicorn..."
# Reemplazar el proceso actual por gunicorn (buena práctica para Docker)
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
