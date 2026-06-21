import re

from django.http import Http404


def extract_youtube_id(url):
    if not url:
        return ""

    patterns = [
        r"(?:youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def shorten_title(title):
    if not title:
        return title

    original = str(title).strip()
    result = original

    match_4k = re.search(r"\[4[Kk]\]", result)
    if match_4k:
        result = result[: match_4k.start()].strip()
    else:
        match_latin = re.search(r"[A-Za-z]", result)
        if match_latin:
            result = result[: match_latin.start()].strip()
            result = re.sub(r"[\s—\-]+$", "", result).strip()

    result = re.sub(r"\([^)]*\)", "", result).strip()
    result = re.sub(r"\[[^\]]*\]", "", result).strip()
    result = result.strip()

    return result or original


def convert_video_type(raw_type):
    if not raw_type:
        return VideoType.LANDSCAPE

    normalized = str(raw_type).strip().lower()
    if normalized == "shorts":
        return VideoType.SHORTS
    return VideoType.LANDSCAPE


class VideoType:
    LANDSCAPE = "L"
    SHORTS = "S"


def get_place_by_slug(slug):
    from .models import Place

    for place in Place.objects.filter(is_active=True):
        if place.slug == slug:
            return place
    raise Http404("Place not found")


def sorted_places(queryset=None):
    from .models import Place

    places = list((queryset or Place.objects.filter(is_active=True)).order_by("name"))
    places.sort(key=lambda place: (place.name == "기타", place.name))
    return places


def priority_places():
    from .models import Place

    return Place.objects.filter(
        is_active=True,
        priority__isnull=False,
        priority__gte=1,
        priority__lte=7,
    ).order_by("priority", "name")


def default_place():
    from .models import Place

    place = priority_places().first()
    if place:
        return place
    return Place.objects.filter(is_active=True).order_by("name").first()


def places_for_map(queryset=None):
    from .models import Place

    places = queryset or Place.objects.filter(is_active=True)
    result = []
    for place in places:
        if place.latitude is None or place.longitude is None:
            continue
        result.append(
            {
                "name": place.name,
                "lat": place.latitude,
                "lng": place.longitude,
                "slug": place.slug,
                "introUrl": place.intro_url or "",
            }
        )
    return result


def chunk_place_videos(videos, max_per_row=3, max_landscape=2, max_shorts_mixed=2):
    from .models import Video

    videos = list(videos)
    rows = []
    index = 0
    total = len(videos)

    while index < total:
        row = []
        landscape_count = 0
        shorts_count = 0

        while index < total:
            video = videos[index]
            is_shorts = video.video_type == Video.VIDEO_TYPE_SHORTS

            if len(row) >= max_per_row:
                break

            if is_shorts:
                max_shorts = 3 if landscape_count == 0 else max_shorts_mixed
                if shorts_count >= max_shorts:
                    break
            elif landscape_count >= max_landscape:
                break

            row.append(video)
            if is_shorts:
                shorts_count += 1
            else:
                landscape_count += 1
            index += 1

        if row:
            rows.append(row)

    return rows


def place_row_layout(row):
    from .models import Video

    landscape_count = sum(
        1 for video in row if video.video_type == Video.VIDEO_TYPE_LANDSCAPE
    )
    shorts_count = len(row) - landscape_count

    if len(row) == 3 and landscape_count == 2 and shorts_count == 1:
        return "full"
    if len(row) == 3:
        return "count-3"
    return f"count-{len(row)}"
