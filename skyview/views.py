import json

from django.core.serializers.json import DjangoJSONEncoder
from django.http import FileResponse, Http404
from django.shortcuts import redirect, render
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .epilogue import (
    epilogue_place_for_hero,
    epilogue_popup_absolute_url_for_place,
    epilogue_static_html_path,
    load_epilogue,
    related_videos_for_place,
)
from .models import FamilySite, Place, Video
from .utils import (
    chunk_place_videos,
    default_place,
    get_place_by_slug,
    places_for_map,
    place_row_layout,
    priority_places,
    sorted_places,
)


def _family_sites():
    return FamilySite.objects.filter(is_active=True)


def _recommended_videos(video_type, max_rank):
    return (
        Video.objects.filter(
            is_active=True,
            video_type=video_type,
            display_rank__gte=1,
            display_rank__lte=max_rank,
        )
        .exclude(youtube_id="")
        .order_by("display_rank")
    )


def _latest_videos(video_type, limit=5):
    return (
        Video.objects.filter(
            is_active=True,
            video_type=video_type,
        )
        .exclude(youtube_id="")
        .order_by("-published_date", "title")[:limit]
    )


def _all_videos(video_type):
    return (
        Video.objects.filter(
            is_active=True,
            video_type=video_type,
        )
        .exclude(youtube_id="")
        .order_by("-published_date", "title")
    )


def _place_landscape_videos(place, limit=5):
    if not place:
        return Video.objects.none()

    return (
        Video.objects.filter(
            place=place,
            is_active=True,
            video_type=Video.VIDEO_TYPE_LANDSCAPE,
        )
        .exclude(youtube_id="")
        .order_by("-published_date", "title")[:limit]
    )


def home(request):
    hero_video = (
        Video.objects.filter(
            is_active=True,
            video_type=Video.VIDEO_TYPE_LANDSCAPE,
            display_rank=0,
        )
        .exclude(youtube_id="")
        .select_related("place")
        .first()
    )
    featured_place = default_place()
    hero_epilogue_place = epilogue_place_for_hero(hero_video, featured_place)
    hero_epilogue_url = epilogue_popup_absolute_url_for_place(request, hero_epilogue_place)

    return render(
        request,
        "skyview/index.html",
        {
            "hero_video": hero_video,
            "hero_epilogue_place": hero_epilogue_place,
            "hero_epilogue_url": hero_epilogue_url,
            "featured_place": featured_place,
            "featured_place_videos": _place_landscape_videos(featured_place),
            "place_nav_places": priority_places(),
            "recommended_landscape": _recommended_videos(
                Video.VIDEO_TYPE_LANDSCAPE, 5
            )[:5],
            "recommended_shorts": _recommended_videos(Video.VIDEO_TYPE_SHORTS, 7)[:7],
            "latest_landscape": _latest_videos(Video.VIDEO_TYPE_LANDSCAPE),
            "latest_shorts": _latest_videos(Video.VIDEO_TYPE_SHORTS, 7),
            "family_sites": _family_sites(),
        },
    )


def landscape_videos(request):
    return render(
        request,
        "skyview/video_list.html",
        {
            "page_title": "16:9 Videos",
            "section_title": "16:9 Landscape",
            "videos": _all_videos(Video.VIDEO_TYPE_LANDSCAPE),
            "card_type": "landscape",
            "cols_class": "cards--cols-5",
            "family_sites": _family_sites(),
        },
    )


def shorts_videos(request):
    return render(
        request,
        "skyview/video_list.html",
        {
            "page_title": "9:16 Shorts",
            "section_title": "9:16 Shorts",
            "videos": _all_videos(Video.VIDEO_TYPE_SHORTS),
            "card_type": "shorts",
            "cols_class": "cards--cols-7",
            "family_sites": _family_sites(),
        },
    )


def _place_videos(place):
    return (
        Video.objects.filter(place=place, is_active=True)
        .exclude(youtube_id="")
        .order_by("-published_date", "title")
    )


def place_list(request):
    place = default_place()
    if place:
        return redirect("place_detail", slug=place.slug)

    return render(
        request,
        "skyview/place_empty.html",
        {"family_sites": _family_sites()},
    )


def place_detail(request, slug):
    place = get_place_by_slug(slug)
    has_location = place.latitude is not None and place.longitude is not None
    videos = _place_videos(place)

    return render(
        request,
        "skyview/place_detail.html",
        {
            "place": place,
            "videos": videos,
            "video_rows": [
                {"videos": row, "layout": place_row_layout(row)}
                for row in chunk_place_videos(videos)
            ],
            "nav_places": priority_places(),
            "has_location": has_location,
            "family_sites": _family_sites(),
        },
    )


def place_epilogue(request, slug):
    place = get_place_by_slug(slug)
    epilogue = load_epilogue(place)
    if not epilogue:
        raise Http404("Epilogue not found")

    return render(
        request,
        "skyview/epilogue.html",
        {
            "place": place,
            "epilogue": epilogue,
            "related_videos": related_videos_for_place(place),
        },
    )


@xframe_options_sameorigin
def place_epilogue_popup(request, slug):
    place = get_place_by_slug(slug)
    static_path = epilogue_static_html_path(place)
    if not static_path:
        raise Http404("Epilogue popup not found")

    return FileResponse(static_path.open("rb"), content_type="text/html; charset=utf-8")


def place_all(request):
    map_places = places_for_map()
    return render(
        request,
        "skyview/place_all.html",
        {
            "places": sorted_places(),
            "places_for_map": map_places,
            "family_sites": _family_sites(),
        },
    )


def maps_view(request):
    places = Place.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False,
    ).order_by("name")
    places_data = [
        {
            "name": place.name,
            "introUrl": place.intro_url or "",
            "lat": place.latitude,
            "lng": place.longitude,
        }
        for place in places
    ]

    return render(
        request,
        "skyview/maps.html",
        {
            "places_json": json.dumps(places_data, cls=DjangoJSONEncoder),
        },
    )


def about(request):
    return render(
        request,
        "skyview/about.html",
        {"family_sites": _family_sites()},
    )
