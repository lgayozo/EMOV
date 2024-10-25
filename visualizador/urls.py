from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "visualizador"

urlpatterns = [
    path("", views.home, name="home"),
    path("mapa/", views.map, name="map"),
    path("upload/", views.upload_file, name="upload_file"),  
    path('get_locations_by_agrupacion/', views.get_locations_by_agrupacion, name='get_locations_by_agrupacion'),  # La URL para la vista AJAX
    path('get_polygons/', views.get_polygons, name='get_polygons'),
    path('get_stats_by_polygon/', views.get_stats_by_polygon, name='get_stats_by_polygon'),
]
