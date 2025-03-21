from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("monitor/" , include("monitor_app.urls")),
]
