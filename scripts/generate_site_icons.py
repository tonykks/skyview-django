"""Generate favicon and touch icons from the SkyView logo master image."""
from pathlib import Path

from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE = BASE_DIR / "skyview" / "static" / "skyview" / "images" / "icons" / "skyview-icon-master.png"
OUTPUT_DIR = SOURCE.parent

SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "apple-touch-icon.png": 180,
    "icon-192x192.png": 192,
    "icon-512x512.png": 512,
}


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"Master icon not found: {SOURCE}")

    image = Image.open(SOURCE)
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for filename, size in SIZES.items():
        resized = image.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(OUTPUT_DIR / filename, format="PNG")

    ico_images = [
        image.resize((size, size), Image.Resampling.LANCZOS) for size in (16, 32, 48)
    ]
    ico_images[0].save(
        OUTPUT_DIR / "favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=ico_images[1:],
    )

    print(f"Generated icons in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
