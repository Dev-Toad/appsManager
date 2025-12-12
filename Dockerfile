# Imagen base
FROM python:3.11-slim

# Variables de entorno básicas
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema que pueda necesitar (psycopg2, etc)
RUN apt-get update && \
    apt-get install -y build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalarlos
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . /app

# Exponer puerto interno
EXPOSE 8000

# Comando por defecto: ejecutar con gunicorn
# wsgi:app -> el archivo wsgi.py y el objeto "app"
# CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app"]
CMD ["gunicorn", "-b", "0.0.0.0:8000", "run:app"]
