from django.urls import path, register_converter

from . import views
from .converters import UnicodeSlugConverter

register_converter(UnicodeSlugConverter, "uslug")

urlpatterns = [
    path("", views.home, name="home"),
    path("places/all/", views.place_all, name="place_all"),
    path("places/", views.place_list, name="place_list"),
    path("places/<uslug:slug>/epilogue/popup/", views.place_epilogue_popup, name="place_epilogue_popup"),
    path("places/<uslug:slug>/epilogue/", views.place_epilogue, name="place_epilogue"),
    path("places/<uslug:slug>/", views.place_detail, name="place_detail"),
    path("maps/", views.maps_view, name="maps"),
    path("videos/", views.landscape_videos, name="landscape_videos"),
    path("shorts/", views.shorts_videos, name="shorts_videos"),
    path("about/", views.about, name="about"),
    path("private-reports/", views.private_reports, name="private_reports"),
    path("private-reports/api/list/", views.private_reports_api_list, name="private_reports_api_list"),
    path("private-reports/api/view/<str:date_str>/", views.private_reports_api_view, name="private_reports_api_view"),
]
