# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Instala dependencias del sistema necesarias para GDAL y compilación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libxml2-dev \
    libexpat1-dev \
    libxerces-c-dev \
    zlib1g-dev \
    libpng-dev \
    libjpeg-dev \
    libsqlite3-dev \
    libpq-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    libspatialite-dev \
    && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto
COPY . /app/

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# Comando para correr la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Establece la variable de entorno GDAL_LIBRARY_PATH
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
