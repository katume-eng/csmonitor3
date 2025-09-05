from django.urls import path
from . import views

urlpatterns = [
    path("", views.con_form_view, name="vote_index"),
    path("vote/", views.con_form_view, name="vote"),
    path("aggregates_data/", views.aggregates_data, name="aggregates_data"),
    path("display/<int:floor_given>/", views.display, name="display"),
    path("display_json_api/",views.display_json_api, name="display_json_api"),
    path("food_cs_api/", views.food_cs_api, name="zero_api"),
    # path("make_random_data/", views.make_random_data, name="make_random_data"),
]