from django.urls import path
from . import views
from .views import DataCreate

urlpatterns = [
    path("create/",DataCreate.as_view(),name="data-create"),
    path("initial/", views.initial, name="initial"),
    path("aggregates_data/", views.aggregates_data, name="aggregates_data"),
    path("display/", views.display, name="display"),
    path("displayf/<int:floor>/", views.displayf, name="display"),
    path("make_random_data/", views.make_random_data, name="make_random_data"),
]