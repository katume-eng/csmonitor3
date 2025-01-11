from django.contrib import admin

# Register your models here.

from .models import Monitor, Location

admin.site.register(Monitor)
admin.site.register(Location)