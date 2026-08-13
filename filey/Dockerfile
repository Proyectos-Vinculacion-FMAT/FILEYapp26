# Usa una imagen oficial de Python ligera
FROM python:3.12-slim

# Evita que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python haga buffer de stdout/stderr
ENV PYTHONUNBUFFERED=1

# Configura el directorio de trabajo
WORKDIR /app

# Instala el servidor de PostgreSQL local, dependencias y sudo
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc libpq-dev postgresql postgresql-contrib sudo \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requerimientos e instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el proyecto al contenedor
COPY . .

# Da permisos de ejecución al script de arranque
RUN chmod +x start.sh

# Recolecta los archivos estáticos de Django (Pasamos una llave temporal para que pase la validación de settings.py)
RUN DJANGO_SECRET_KEY=dummy-para-build python manage.py collectstatic --noinput

# Expone el puerto 8000
EXPOSE 8000

# Usaremos un script de Bash para arrancar tanto Postgres como Django
CMD ["./start.sh"]
