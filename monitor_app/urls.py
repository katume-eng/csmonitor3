from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("vote/", views.con_form_view, name="vote"),
    # path("initial/", views.initial, name="initial"),
    path("aggregates_data/", views.aggregates_data, name="aggregates_data"),
    path("display/<int:floor_given>/", views.display, name="display"),
    # path("display_json/",views.display_json, name="display_json"),
    path("display_json_api/",views.display_json_api, name="display_json_api"),
    path("food_cs_api/", views.food_cs_api, name="zero_api"),
    # path("displayf/<int:floor>/", views.displayf, name="display"),
    path("make_random_data/", views.make_random_data, name="make_random_data"),
    # path("test/", views.test, name="test"),
]