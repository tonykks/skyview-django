"""Generate static epilogue HTML from md source. Run: python scripts/generate_epilogue_static.py"""
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "skyview_project.settings")

import django

django.setup()

from skyview.epilogue import load_epilogue, related_videos_for_place
from skyview.utils import get_place_by_slug

SLUG = "섶섬"
OUTPUT = BASE_DIR / "skyview" / "static" / "skyview" / "epilogues" / f"{SLUG}.html"


def main():
    place = get_place_by_slug(SLUG)
    epilogue = load_epilogue(place)
    if not epilogue:
        raise SystemExit(f"No epilogue for {SLUG}")

    related = related_videos_for_place(place)
    related_html = ""
    if related:
        video = related[0]
        related_html = f"""
        <div class="epilogue-page__related">
          <a class="card card--link card--landscape epilogue-related-card" href="{video.youtube_url}" target="_blank" rel="noopener noreferrer">
            <img src="https://img.youtube.com/vi/{video.youtube_id}/hqdefault.jpg" alt="{video.title} 썸네일" width="400" height="225" />
            <h3>{video.title}</h3>
          </a>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{epilogue.title} | {place.name} Epilogue</title>
    <link rel="stylesheet" href="/static/skyview/css/styles.css" />
  </head>
  <body class="epilogue-page">
    <div class="epilogue-page__wrap">
      <header class="epilogue-page__header">
        <p class="epilogue-page__place">{place.name}</p>
        <h1 class="epilogue-page__title">{epilogue.title}</h1>
      </header>
      <article class="epilogue-page__body">
        {epilogue.body_html}
        {related_html}
      </article>
    </div>
  </body>
</html>
"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
