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
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote

KST = timezone(timedelta(hours=9))


def _filter_dates_by_period(
    dates: list[str],
    period: str,
    start_date_str: str = "",
    end_date_str: str = ""
) -> tuple[list[str], str, str, str]:
    today = datetime.now(KST).date()
    period = period.strip().lower() if period else "all"

    if period == "1day":
        start_date = today
        end_date = today
    elif period == "3days":
        start_date = today - timedelta(days=2)
        end_date = today
    elif period == "30days":
        start_date = today - timedelta(days=29)
        end_date = today
    elif period == "all":
        start_date = None
        end_date = None
    elif period == "custom":
        try:
            start_date = datetime.strptime(start_date_str.strip(), "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str.strip(), "%Y-%m-%d").date()
            if start_date > end_date:
                start_date, end_date = end_date, start_date
        except Exception:
            period = "7days"
            start_date = today - timedelta(days=6)
            end_date = today
    else:
        period = "7days"
        start_date = today - timedelta(days=6)
        end_date = today

    filtered: list[str] = []
    for d_str in dates:
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
            if (start_date is None or start_date <= d) and (end_date is None or d <= end_date):
                filtered.append(d_str)
        except ValueError:
            continue

    filtered_sorted = sorted(filtered, reverse=True)
    start_fmt = start_date.strftime("%Y-%m-%d") if start_date else (filtered_sorted[-1] if filtered_sorted else today.strftime("%Y-%m-%d"))
    end_fmt = end_date.strftime("%Y-%m-%d") if end_date else (filtered_sorted[0] if filtered_sorted else today.strftime("%Y-%m-%d"))

    return filtered_sorted, period, start_fmt, end_fmt
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

    all_dates, api_error = _fetch_github_archive_info()
    
    period = request.GET.get("period", "all").strip()
    start_date_req = request.GET.get("start_date", "").strip()
    end_date_req = request.GET.get("end_date", "").strip()
    selected_date_req = request.GET.get("date", "").strip()

    filtered_dates, active_period, start_date, end_date = _filter_dates_by_period(
        all_dates, period, start_date_req, end_date_req
    )

    if selected_date_req and selected_date_req in filtered_dates:
        selected_date = selected_date_req
    elif filtered_dates:
        selected_date = filtered_dates[0]
    else:
        selected_date = ""

    has_no_reports_in_period = (not api_error) and bool(all_dates) and (not filtered_dates)

    context = {
        "all_dates": all_dates,
        "dates": filtered_dates,
        "selected_date": selected_date,
        "api_error": api_error,
        "is_owner": True,
        "active_period": active_period,
        "start_date": start_date,
        "end_date": end_date,
        "has_no_reports_in_period": has_no_reports_in_period,
    }
    return render(request, "skyview/private_reports.html", context)


def private_reports_api_list(request):
    if not is_skyview_owner(request.user):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    all_dates, api_error = _fetch_github_archive_info()
    if api_error:
        return JsonResponse({"ok": False, "error": api_error}, status=502)

    period = request.GET.get("period", "all").strip()
    start_date_req = request.GET.get("start_date", "").strip()
    end_date_req = request.GET.get("end_date", "").strip()

    filtered_dates, active_period, start_date, end_date = _filter_dates_by_period(
        all_dates, period, start_date_req, end_date_req
    )

    return JsonResponse({
        "ok": True,
        "dates": filtered_dates,
        "all_dates": all_dates,
        "period": active_period,
        "start_date": start_date,
        "end_date": end_date,
    })


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


TOSS_ARCHIVE_API_URL = (
    "https://api.github.com/repos/tonykks/Toss_Invest_Agent/contents/"
    "premarket/github/reports/archive"
)


def _get_toss_token() -> str:
    return (os.environ.get("TOSS_AGENT_GITHUB_TOKEN") or _get_github_read_token()).strip()


def _get_toss_local_archive_dir() -> Path | None:
    configured = os.environ.get("TOSS_REPORTS_LOCAL_PATH")
    archive_dir = Path(configured).expanduser() if configured else Path(
        r"c:\Users\김광수\Desktop\Toss_Invest_Agent\premarket\github\reports\archive"
    )
    return archive_dir if (archive_dir / "manifest.json").is_file() else None


def _toss_github_request(relative_path: str):
    req = urllib.request.Request(f"{TOSS_ARCHIVE_API_URL}/{quote(relative_path, safe='/')}")
    token = _get_toss_token()
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    req.add_header("User-Agent", "Skyview-Django-Portal")
    req.add_header("Accept", "application/vnd.github.raw+json")
    return req


def _fetch_toss_archive_info() -> tuple[dict, list[str], str | None]:
    local_dir = _get_toss_local_archive_dir()
    try:
        if local_dir:
            manifest_data = json.loads((local_dir / "manifest.json").read_text(encoding="utf-8-sig"))
        else:
            if not _get_toss_token():
                return {}, [], "TOSS_AGENT_GITHUB_TOKEN 또는 GitHub 읽기 토큰이 설정되지 않았습니다."
            with urllib.request.urlopen(_toss_github_request("manifest.json"), timeout=10) as resp:
                manifest_data = json.loads(resp.read().decode("utf-8-sig"))

        if (
            not isinstance(manifest_data, dict)
            or not isinstance(manifest_data.get("date_list", []), list)
            or not all(isinstance(d, str) for d in manifest_data.get("date_list", []))
            or not isinstance(manifest_data.get("dates", []), list)
        ):
            raise ValueError("Invalid manifest")
        for entry in manifest_data.get("dates", []):
            if (
                not isinstance(entry, dict)
                or not isinstance(entry.get("date"), str)
                or not isinstance(entry.get("runs", []), list)
                or not all(isinstance(run, dict) for run in entry.get("runs", []))
            ):
                raise ValueError("Invalid date entry")
        return manifest_data, manifest_data.get("date_list", []), None
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 404):
            return {}, [], "GitHub API 인증/권한 오류 (Token 설정 및 리포지토리 읽기 권한 확인 필요)"
        return {}, [], f"GitHub API HTTP 오류 ({exc.code})"
    except (ValueError, UnicodeError):
        return {}, [], "Toss 보고서 보관 목록 형식이 올바르지 않습니다."
    except OSError:
        return {}, [], "Toss 보고서 보관 목록을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."


def _get_toss_date_entry(manifest: dict, date_str: str) -> dict:
    return next((entry for entry in manifest.get("dates", []) if entry.get("date") == date_str), {})


def _get_toss_run(entry: dict, run_id: str | None = None) -> dict:
    runs = entry.get("runs", [])
    target_id = run_id or entry.get("default_run_id")
    if target_id:
        return next((run for run in runs if run.get("run_id") == target_id), {})
    return next((run for run in runs if run.get("is_default")), runs[-1] if runs else {})


def toss_reports(request):
    if not is_skyview_owner(request.user):
        return HttpResponseForbidden("접근 권한이 없습니다. (Owner Only)")

    manifest_data, all_dates, api_error = _fetch_toss_archive_info()
    filtered_dates, active_period, start_date, end_date = _filter_dates_by_period(
        all_dates,
        request.GET.get("period", "all"),
        request.GET.get("start_date", ""),
        request.GET.get("end_date", ""),
    )
    selected_date = request.GET.get("date", "").strip()
    if selected_date not in filtered_dates:
        selected_date = filtered_dates[0] if filtered_dates else ""
    selected_date_entry = _get_toss_date_entry(manifest_data, selected_date)
    selected_run = _get_toss_run(selected_date_entry, request.GET.get("run_id", "").strip())
    if not selected_run:
        selected_run = _get_toss_run(selected_date_entry)

    context = {
        "manifest": manifest_data,
        "all_dates": all_dates,
        "dates": filtered_dates,
        "date_entries": [
            {"date": d, "run_count": len(_get_toss_date_entry(manifest_data, d).get("runs", []))}
            for d in filtered_dates
        ],
        "selected_date": selected_date,
        "selected_date_entry": selected_date_entry,
        "runs": selected_date_entry.get("runs", []),
        "selected_run_id": selected_run.get("run_id", ""),
        "selected_run": selected_run,
        "api_error": api_error,
        "is_owner": True,
        "active_period": active_period,
        "start_date": start_date,
        "end_date": end_date,
        "has_no_reports_in_period": not api_error and bool(all_dates) and not filtered_dates,
    }
    return render(request, "skyview/toss_reports.html", context)


def toss_reports_api_list(request):
    if not is_skyview_owner(request.user):
        return JsonResponse({"ok": False, "error": "Forbidden"}, status=403)

    manifest_data, all_dates, api_error = _fetch_toss_archive_info()
    if api_error:
        return JsonResponse({"ok": False, "error": api_error}, status=502)
    filtered_dates, _, _, _ = _filter_dates_by_period(
        all_dates,
        request.GET.get("period", "all"),
        request.GET.get("start_date", ""),
        request.GET.get("end_date", ""),
    )
    return JsonResponse({"ok": True, "dates": filtered_dates, "all_dates": all_dates, "manifest": manifest_data})


@xframe_options_sameorigin
def toss_reports_api_view(request, date_str, run_id=None):
    if not is_skyview_owner(request.user):
        return HttpResponseForbidden("접근 권한이 없습니다. (Owner Only)")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_str):
        return HttpResponseBadRequest("올바르지 않은 날짜 형식입니다.")
    if date_str in ("2026-08-07", "2026-08-25"):
        return HttpResponseNotFound("해당 날짜에는 보고서가 발행되지 않았습니다.")

    manifest_data, _, api_error = _fetch_toss_archive_info()
    if api_error:
        return HttpResponse(api_error, status=502)
    entry = _get_toss_date_entry(manifest_data, date_str)
    run = _get_toss_run(entry, run_id)
    if not run:
        return HttpResponseNotFound("해당 날짜 또는 실행의 보고서를 찾을 수 없습니다.")

    # Manifest paths are relative to reports/, while the local root is archive/.
    rel_html_path = run.get("rel_html_path", "")
    if not isinstance(rel_html_path, str) or not re.fullmatch(
        r"archive/(?:[A-Za-z0-9_-]+/)*[A-Za-z0-9_.-]+\.html", rel_html_path
    ):
        return HttpResponseBadRequest("올바르지 않은 보고서 경로입니다.")
    relative_path = PurePosixPath(rel_html_path).relative_to("archive")
    local_dir = _get_toss_local_archive_dir()
    try:
        html_bytes = None
        if local_dir:
            archive_root = local_dir.resolve()
            html_path = (archive_root / relative_path).resolve()
            if not html_path.is_relative_to(archive_root):
                return HttpResponseBadRequest("올바르지 않은 보고서 경로입니다.")
            if html_path.is_file():
                html_bytes = html_path.read_bytes()
        if html_bytes is None:
            with urllib.request.urlopen(_toss_github_request(relative_path.as_posix()), timeout=10) as resp:
                html_bytes = resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return HttpResponseNotFound("해당 날짜 또는 실행의 보고서를 찾을 수 없습니다.")
        return HttpResponse("GitHub API 통신 중 오류가 발생했습니다.", status=502)
    except OSError:
        return HttpResponse("보고서 조회가 실패했습니다.", status=502)

    response = HttpResponse(html_bytes, content_type="text/html; charset=utf-8")
    response["Cache-Control"] = "no-store, private, no-cache, must-revalidate"
    response["X-Content-Type-Options"] = "nosniff"
    return response
