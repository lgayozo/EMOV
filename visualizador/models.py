# models.py
from django.contrib.gis.db import models

class TimedLocation(models.Model):
    participant = models.CharField(max_length=255)
    viaje = models.IntegerField()
    agrupacion = models.IntegerField()
    timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    velocidad = models.FloatField()
    distancia_acumulada = models.FloatField()
    emocion = models.CharField(max_length=255)
    id_poligono = models.IntegerField()
    contexto_1 = models.CharField(max_length=255)
    contexto_2 = models.CharField(max_length=255)
    contexto_3 = models.CharField(max_length=255)
    SCL = models.FloatField()
    SCR = models.FloatField()
    SKT = models.FloatField()
    MOS = models.FloatField(null=True, blank=True)
    Peak_SCR = models.FloatField()


class Polygon(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = models.PolygonField(srid=4326)

