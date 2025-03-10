from django.contrib import admin

# Register your models here.

from .models import Collected, Location, CongestionLevel

admin.site.register(Collected)
admin.site.register(Location)
admin.site.register(CongestionLevel)