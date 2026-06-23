from dataclasses import dataclass
from pathlib import Path
import re

from django.conf import settings
from django.utils.html import escape, linebreaks

from .models import Place

_NUMBERED_SECTION_RE = re.compile(r"^(\d+\.\s.+)$", re.MULTILINE)


@dataclass(frozen=True)
class EpilogueContent:
    title: str
    body_html: str
    source_name: str


@dataclass(frozen=True)
class RelatedVideo:
    title: str
    youtube_url: str
    video_type: str = "L"

    @property
    def youtube_id(self) -> str:
        from .utils import extract_youtube_id

        return extract_youtube_id(self.youtube_url)


RELATED_VIDEOS_BY_SLUG: dict[str, list[RelatedVideo]] = {
    "섶섬": [
        RelatedVideo(
            title="아슬아슬한 자동복귀(RTH) - 섶섬",
            youtube_url="https://youtu.be/oG825uQxReY",
        ),
    ],
}


def related_videos_for_place(place: Place) -> list[RelatedVideo]:
    return RELATED_VIDEOS_BY_SLUG.get(place.slug, [])


def epilogue_place_for_hero(hero_video, featured_place):
    if hero_video and hero_video.place_id:
        return hero_video.place
    return featured_place


def epilogue_url_for_place(place: Place | None) -> str | None:
    if not place or not load_epilogue(place):
        return None

    from django.urls import reverse

    return reverse("place_epilogue", kwargs={"slug": place.slug})


def epilogue_absolute_url_for_place(request, place: Place | None) -> str | None:
    path = epilogue_url_for_place(place)
    if not path:
        return None

    return request.build_absolute_uri(path)


def epilogue_static_html_path(place: Place) -> Path | None:
    static_path = (
        Path(settings.BASE_DIR)
        / "skyview"
        / "static"
        / "skyview"
        / "epilogues"
        / f"{place.slug}.html"
    )
    if static_path.is_file():
        return static_path
    return None


def epilogue_popup_available(place: Place | None) -> bool:
    if not place or not load_epilogue(place):
        return False
    return epilogue_static_html_path(place) is not None


def epilogue_popup_url_for_place(place: Place | None) -> str | None:
    if not epilogue_popup_available(place):
        return None

    from django.urls import reverse

    return reverse("place_epilogue_popup", kwargs={"slug": place.slug})


def epilogue_popup_absolute_url_for_place(request, place: Place | None) -> str | None:
    path = epilogue_popup_url_for_place(place)
    if not path:
        return None

    return request.build_absolute_uri(path)


def epilogue_content_dir() -> Path:
    return Path(getattr(settings, "EPILOGUE_CONTENT_DIR", settings.BASE_DIR / "content" / "epilogues"))


def _epilogue_source_path(place: Place) -> Path | None:
    content_dir = epilogue_content_dir()
    if not content_dir.is_dir():
        return None

    slug = place.slug
    candidates = [
        content_dir / f"{slug}.md",
        content_dir / f"{slug}.txt",
    ]
    for path in candidates:
        if path.is_file():
            return path

    matches = sorted(content_dir.glob(f"{slug}.*"))
    for path in matches:
        if path.is_file() and path.suffix.lower() in {".md", ".txt"}:
            return path

    return None


def _split_title_and_body(text: str) -> tuple[str, str]:
    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return "", ""

    parts = normalized.split("\n\n", 1)
    title = parts[0].strip()
    body = parts[1].strip() if len(parts) > 1 else ""
    return title, body


def _promote_numbered_sections(body: str) -> str:
    return _NUMBERED_SECTION_RE.sub(r"## \1", body)


def _external_links_new_tab(html: str) -> str:
    return re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a href="\1" target="_blank" rel="noopener noreferrer"',
        html,
    )


def _render_body(body: str, source_suffix: str) -> str:
    if not body:
        return ""

    body = _promote_numbered_sections(body)

    if source_suffix == ".md":
        try:
            import markdown

            html = markdown.markdown(
                body,
                extensions=["extra", "nl2br", "sane_lists"],
                output_format="html5",
            )
            return _external_links_new_tab(html)
        except ImportError:
            pass

    return linebreaks(escape(body))


def load_epilogue(place: Place) -> EpilogueContent | None:
    source_path = _epilogue_source_path(place)
    if not source_path:
        return None

    text = source_path.read_text(encoding="utf-8")
    title, body = _split_title_and_body(text)
    if not title and not body:
        return None

    if not title:
        title = f"{place.name} 에필로그"

    return EpilogueContent(
        title=title,
        body_html=_render_body(body, source_path.suffix.lower()),
        source_name=source_path.name,
    )
