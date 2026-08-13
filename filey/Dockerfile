# Usa una imagen oficial de Python ligera
FROM python:3.12-slim

# Evita que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python haga buffer de stdout/stderr (útil para logs)
ENV PYTHONUNBUFFERED=1

# Configura el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema requeridas para Postgres
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requerimientos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el proyecto al contenedor
COPY . .

# Recolecta los archivos estáticos de Django
RUN python manage.py collectstatic --noinput

# Expone el puerto 8000
EXPOSE 8000

# Comando para arrancar la aplicación con Gunicorn en producción
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
