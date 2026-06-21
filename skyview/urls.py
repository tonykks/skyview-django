from django.urls import path, register_converter

from . import views
from .converters import UnicodeSlugConverter

register_converter(UnicodeSlugConverter, "uslug")

urlpatterns = [
    path("", views.home, name="home"),
    path("places/all/", views.place_all, name="place_all"),
    path("places/", views.place_list, name="place_list"),
    path("places/<uslug:slug>/", views.place_detail, name="place_detail"),
    path("maps/", views.maps_view, name="maps"),
    path("videos/", views.landscape_videos, name="landscape_videos"),
    path("shorts/", views.shorts_videos, name="shorts_videos"),
    path("about/", views.about, name="about"),
]
