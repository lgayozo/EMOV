import csv
import os
import zipfile
import geopandas as gpd
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.gis.geos import GEOSGeometry
from .forms import UploadFileForm
from .models import TimedLocation, Polygon
from datetime import datetime
from io import BytesIO
from django.db.models import Avg, Max, Min


def load_shapefile_from_zip(zip_file, shapefile_name):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("temp_shapefile")

    shapefile_path = os.path.join("temp_shapefile", shapefile_name)
    gdf = gpd.read_file(shapefile_path)

    for root, dirs, files in os.walk("temp_shapefile"):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir("temp_shapefile")

    return gdf


def handle_uploaded_file(f):
    # Leer el archivo completo en memoria
    file_data = f.read()

    # Intentar leer el archivo con UTF-8 primero
    try:
        file_content = file_data.decode('utf-8')
        print("Archivo leído con codificación UTF-8")
    except UnicodeDecodeError:
        # Si UTF-8 falla, intentar con ISO-8859-1
        try:
            file_content = file_data.decode('ISO-8859-1')
            print("Archivo leído con codificación ISO-8859-1")
        except UnicodeDecodeError:
            raise ValueError("El archivo CSV tiene una codificación no soportada.")

    # Verificar contenido del archivo
    print("Contenido del archivo:\n", file_content[:1000])  # Imprimir los primeros 1000 caracteres para evitar demasiada salida

    # Asegurarse de que no hay líneas vacías inesperadas
    lines = file_content.splitlines()
    print(f"Total de líneas en el archivo: {len(lines)}")
    if len(lines) > 0:
        print(f"Primera línea (encabezados): {lines[0]}")

    reader = csv.DictReader(lines, delimiter=';')

    # Asegurarse de que el lector esté leyendo las filas
    rows = list(reader)
    print(f"Total de filas leídas: {len(rows)}")

    if len(rows) > 0:
        print(f"Encabezados: {rows[0].keys()}")  # Imprimir los encabezados

    for row in rows:
        try:
            row['latitude'] = float(row['latitude']) if row['latitude'] else None
            row['longitude'] = float(row['longitude']) if row['longitude'] else None
            row['velocidad'] = float(row['velocidad']) if row['velocidad'] else None
            row['distancia_acumulada'] = float(row['distancia_acumulada']) if row['distancia_acumulada'] else None
            row['SCL'] = float(row['SCL']) if row['SCL'] else None
            row['SCR'] = float(row['SCR']) if row['SCR'] else None
            row['SKT'] = float(row['SKT']) if row['SKT'] else None
            row['MOS'] = float(row['MOS']) if row['MOS'] else None
            row['Peak_SCR'] = float(row['Peak_SCR']) if row['Peak_SCR'] else None
            row['timestamp'] = datetime.strptime(row['timestamp'], "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            print(f"Procesando fila: {row}")  # Mensaje de depuración para cada fila
            TimedLocation.objects.create(
                participant=row['participant'],
                viaje=int(row['viaje']),
                agrupacion=int(row['agrupacion']),
                timestamp=row['timestamp'],
                latitude=row['latitude'],
                longitude=row['longitude'],
                velocidad=row['velocidad'],
                distancia_acumulada=row['distancia_acumulada'],
                emocion=row['emocion'],
                id_poligono=int(row['id_poligono']),
                contexto_1=row['contexto_1'],
                contexto_2=row['contexto_2'],
                contexto_3=row['contexto_3'],
                SCL=row['SCL'],
                SCR=row['SCR'],
                SKT=row['SKT'],
                MOS=row['MOS'],
                Peak_SCR=row['Peak_SCR'],
            )
        except Exception as e:
            print(f"Error al crear TimedLocation para la fila {row}: {e}")


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if 'zip_file' in request.FILES:
                zip_file = request.FILES['zip_file']
                zip_file = BytesIO(zip_file.read())
                shapefile_name = 'POLIGONOS_2019_100M.shp'  # Asegúrate de especificar el nombre correcto del shapefile dentro del ZIP

                gdf = load_shapefile_from_zip(zip_file, shapefile_name)
                for _, row in gdf.iterrows():
                    # Convertir la geometría a WKT y luego a GEOSGeometry
                    geom_wkt = row['geometry'].wkt
                    geom_geos = GEOSGeometry(geom_wkt)
                    polygon = Polygon(id=row['fid'], geom=geom_geos)
                    polygon.save()

            if 'csv_file' in request.FILES:
                try:
                    handle_uploaded_file(request.FILES['csv_file'])
                    return redirect('visualizador:home')
                except Exception as e:
                    print(f"Error al manejar el archivo subido: {e}")

    else:
        form = UploadFileForm()
    return render(request, 'visualizador/upload.html', {'form': form})


def home(request):
    return render(request, 'visualizador/base.html')

def map(request):
    # Obtener todos los datos de TimedLocation
    locations = TimedLocation.objects.all()

    # Obtener valores distintos de agrupacion
    agrupaciones = TimedLocation.objects.values_list('agrupacion', flat=True).distinct()

    # Convertir los datos de ubicaciones a un formato adecuado para usar en el template
    locations_data = [
        {
            'latitude': loc.latitude,
            'longitude': loc.longitude,
        }
        for loc in locations
    ]

    if locations and agrupaciones:
        return render(request, 'visualizador/mapa.html', {'locations': locations_data, 'agrupaciones': agrupaciones})
    
    else: 
        return render(request, 'visualizador/mapa.html')
def get_polygons(request):
    polygons = Polygon.objects.all()
    polygons_data = [
        {
            'id': polygon.id,
            'coordinates': list(polygon.geom.coords)  # Obtener coordenadas del polígono
        }
        for polygon in polygons
    ]
    return JsonResponse({'polygons': polygons_data})

def get_locations_by_agrupacion(request):
    agrupacion = request.GET.get('agrupacion', 'todas')

    if agrupacion == 'todas':
        locations = TimedLocation.objects.all()
    else:
        locations = TimedLocation.objects.filter(agrupacion=agrupacion)

    locations_data = [
        {
            'latitude': loc.latitude,
            'longitude': loc.longitude,
        }
        for loc in locations
    ]

    return JsonResponse({'locations': locations_data})

def get_stats_by_polygon(request):
    polygon_id = request.GET.get('polygon_id', None)
    if polygon_id is None:
        return JsonResponse({'error': 'No se proporcionó un ID de polígono.'}, status=400)
    
    points = TimedLocation.objects.filter(id_poligono=polygon_id)
    
    stats = [
        {'name': 'Puntos totales del polígono', 'value': points.count()},
        {'name': 'Máx SCL', 'value': points.aggregate(Max('SCL'))['SCL__max']},
        {'name': 'Mín SCL', 'value': points.aggregate(Min('SCL'))['SCL__min']},
        {'name': 'Promedio SCL', 'value': points.aggregate(Avg('SCL'))['SCL__avg']},
        {'name': 'Máx SCR', 'value': points.aggregate(Max('SCR'))['SCR__max']},
        {'name': 'Mín SCR', 'value': points.aggregate(Min('SCR'))['SCR__min']},
        {'name': 'Promedio SCR', 'value': points.aggregate(Avg('SCR'))['SCR__avg']},
        {'name': 'Máx SKT', 'value': points.aggregate(Max('SKT'))['SKT__max']},
        {'name': 'Mín SKT', 'value': points.aggregate(Min('SKT'))['SKT__min']},
        {'name': 'Promedio SKT', 'value': points.aggregate(Avg('SKT'))['SKT__avg']}
    ]
    print(points)
    
    return JsonResponse({'stats': stats})