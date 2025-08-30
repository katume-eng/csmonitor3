from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('master/', admin.site.urls),
    path("" , include("monitor_app.urls")),
]
