from django.contrib import admin

# Register your models here.

from .models import Collected, Location

admin.site.register(Collected)
admin.site.register(Location)