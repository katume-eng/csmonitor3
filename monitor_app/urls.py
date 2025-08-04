from django.urls import path
from . import views
from .views import DataCreate

urlpatterns = [
    path("", views.index, name="index"),
    path("",DataCreate.as_view(),name="data-create"),
    path("initial/", views.initial, name="initial"),
    path("aggregates_data/", views.aggregates_data, name="aggregates_data"),
    path("display/<int:floor_given>/", views.display, name="display"),
    path("display_json/",views.display_json, name="display_json"),
    # path("displayf/<int:floor>/", views.displayf, name="display"),
    path("make_random_data/", views.make_random_data, name="make_random_data"),
]