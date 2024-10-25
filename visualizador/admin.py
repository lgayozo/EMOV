from django.contrib import admin

# Register your models here.
from .models import TimedLocation, Polygon

admin.site.register(TimedLocation)
admin.site.register(Polygon)
