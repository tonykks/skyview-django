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


import json
import os
import re
import urllib.request
import urllib.error
from django.conf import settings
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotFound,
    JsonResponse,
)
from .utils import is_skyview_owner


def _get_github_read_token() -> str:
    return (
        os.environ.get("EMAIL_AGENT_GITHUB_TOKEN")
        or os.environ.get("GITHUB_READ_TOKEN")
        or os.environ.get("GH_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or ""
    ).strip()


def _fetch_github_archive_info() -> tuple[list[str], str | None]:
    token = _get_github_read_token()
    if not token:
        return [], "EMAIL_AGENT_GITHUB_TOKEN 토큰이 설정되지 않았습니다."

    url = "https://api.github.com/repos/tonykks/email-agent/contents/reports/archive"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "Skyview-Django-Portal")
    req.add_header("Accept", "application/vnd.github.v3+json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if isinstance(data, list):
                dates: list[str] = []
                pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})\.html$")
                for item in data:
                    name = item.get("name", "")
                    match = pattern.match(name)
                    if match:
                        dates.append(match.group(1))
                return sorted(dates, reverse=True), None
            return [], "GitHub API 응답 형식이 올바르지 않습니다."
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 404):
            return [], "GitHub API 인증/권한 오류 (Token 설정 및 리포지토리 읽기 권한 확인 필요)"
        return [], f"GitHub API HTTP 오류 ({exc.code})"
    except Exception:
        return [], "GitHub API 통신 연결 오류가 발생했습니다."


def _fetch_github_archive_list() -> list[str]:
    dates, _ = _fetch_github_archive_info()
    return dates


def private_reports(request):
    if not is_skyview_owner(request.user):
        return HttpResponseForbidden("접근 권한이 없습니다. (Owner Only)")

    dates, api_error = _fetch_github_archive_info()
    selected_date = request.GET.get("date", "").strip()
    if not selected_date or selected_date not in dates:
        selected_date = dates[0] if dates else ""

    context = {
        "dates": dates,
        "selected_date": selected_date,
        "api_error": api_error,
        "is_owner": True,
    }
    return render(request, "skyview/private_reports.html", context)


def private_reports_api_list(request):
    if not is_skyview_owner(request.user):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    dates, api_error = _fetch_github_archive_info()
    if api_error:
        return JsonResponse({"ok": False, "error": api_error}, status=502)
    return JsonResponse({"ok": True, "dates": dates})


@xframe_options_sameorigin
def private_reports_api_view(request, date_str):
    if not is_skyview_owner(request.user):
        return HttpResponseForbidden("접근 권한이 없습니다. (Owner Only)")

    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        return HttpResponseBadRequest("올바르지 않은 날짜 형식입니다.")

    token = _get_github_read_token()
    url = f"https://api.github.com/repos/tonykks/email-agent/contents/reports/archive/{date_str}.html"
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "Skyview-Django-Portal")
    req.add_header("Accept", "application/vnd.github.raw+json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html_bytes = resp.read()
            response = HttpResponse(html_bytes, content_type="text/html; charset=utf-8")
            response["Cache-Control"] = "no-store, private, no-cache, must-revalidate"
            response["X-Content-Type-Options"] = "nosniff"
            return response
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return HttpResponseNotFound("해당 날짜의 보고서를 찾을 수 없습니다.")
        return HttpResponse("GitHub API 통신 중 오류가 발생했습니다.", status=502)
    except Exception:
        return HttpResponse("보고서 조회가 실패했습니다.", status=502)
