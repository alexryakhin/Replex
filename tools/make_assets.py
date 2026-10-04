#!/usr/bin/env python3
"""Build the landing page images from the app repo's screenshot sources.

Runs from the Replex-App checkout (this site is its ReplexWebsite submodule) and reads
docs/ASO/screenshots/source: real app captures (US set, pounds), the floating UI cut-outs,
the graded gym photos and the device frames. Writes WebP files to assets/img/.

    python3 tools/make_assets.py
"""
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

SITE = Path(__file__).resolve().parent.parent
APP = SITE.parent
SRC = APP / "docs/ASO/screenshots/source"
CAPTURES = SRC / "captures-lb"
CUTOUTS = SRC / "cutouts-lb"
OUT = SITE / "assets/img"
OUT.mkdir(parents=True, exist_ok=True)


def save(image: Image.Image, name: str, width: int, quality: int = 84):
    if image.width > width:
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
    image.save(OUT / f"{name}.webp", "WEBP", quality=quality, method=6)
    print(f"{name}.webp {image.width}x{image.height}")


def rounded_mask(size, radius, scale=4):
    w, h = size
    mask = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w * scale - 1, h * scale - 1), radius * scale, fill=255)
    return mask.resize(size, Image.LANCZOS)


def phone(capture: str, name: str, width: int = 760):
    """iPhone 17 Pro frame (978 x 2000, opening x 54-923, y 51-1948) around a capture."""
    frame = Image.open(SRC / "app/iphone-17-frame.png").convert("RGBA")
    box = (54, 51, 923, 1948)
    size = (box[2] - box[0], box[3] - box[1])
    screen = Image.open(CAPTURES / f"{capture}.png").convert("RGBA").resize(size, Image.LANCZOS)
    canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    canvas.paste(Image.new("RGBA", size, (0, 0, 0, 255)), box[:2], rounded_mask(size, 120))
    canvas.paste(screen, box[:2], rounded_mask(size, 110))
    canvas.alpha_composite(frame)
    save(canvas, name, width)


def watch(capture: Path, name: str, width: int = 520):
    """Apple Watch frame (840 x 1320, opening x 109-730, y 289-1030) around a capture."""
    frame = Image.open(SRC / "app/apple-watch-frame.png").convert("RGBA")
    box = (109, 289, 731, 1031)
    size = (box[2] - box[0], box[3] - box[1])
    shot = Image.open(capture).convert("RGBA")
    # Cover the opening, anchored a little above centre like the store layout.
    scale = max(size[0] / shot.width, size[1] / shot.height)
    shot = shot.resize((round(shot.width * scale), round(shot.height * scale)), Image.LANCZOS)
    left = (shot.width - size[0]) // 2
    top = round((shot.height - size[1]) * 0.3)
    shot = shot.crop((left, top, left + size[0], top + size[1]))
    canvas = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    canvas.paste(shot, box[:2], rounded_mask(size, 95))
    canvas.alpha_composite(frame)
    save(canvas, name, width)


def cutout(name: str, width: int = 900):
    save(Image.open(CUTOUTS / f"{name}.png").convert("RGBA"), f"card-{name}", width, quality=88)


def photo(name: str, width: int = 1600):
    save(Image.open(SRC / f"photos/graded/{name}.jpg").convert("RGB"), f"photo-{name}", width, quality=78)


def app_icon():
    """The light (volt) app icon from the Icon Composer glyph, rendered with headless Chrome."""
    svg = (APP / "Shared/Resources/Replex-Icon.icon/Assets/Layer-2.svg").read_text()
    svg = re.sub(r'fill="[^"]*"', 'fill="#0B0B0C"', svg)
    # Icon Composer draws the glyph at ~62% of the canvas, nudged right, on a soft volt gradient.
    svg = re.sub(r'width="\d+" height="\d+"', 'width="640" height="592"', svg, count=1)
    html = f"""<html><body style="margin:0;background:transparent">
<div style="width:1024px;height:1024px;border-radius:230px;background:linear-gradient(180deg,#DBFF3D,#C4F200);
display:flex;align-items:center;justify-content:center;overflow:hidden">
<div style="transform:translate(22px,6px);line-height:0">{svg}</div>
</div></body></html>"""
    page = OUT / "_icon.html"
    page.write_text(html)
    png = OUT / "_icon.png"
    subprocess.run([
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--headless=new", "--disable-gpu",
        "--hide-scrollbars", "--default-background-color=00000000", "--window-size=1024,1024",
        f"--screenshot={png}", f"file://{page}",
    ], check=True, capture_output=True)
    icon = Image.open(png).convert("RGBA")
    save(icon, "app-icon", 256, quality=90)
    icon.resize((180, 180), Image.LANCZOS).save(SITE / "favicons/apple-touch-icon.png")
    for size in (16, 32, 96):
        icon.resize((size, size), Image.LANCZOS).save(SITE / f"favicons/favicon-{size}x{size}.png")
    icon.resize((192, 192), Image.LANCZOS).save(SITE / "favicons/android-chrome-192x192.png")
    icon.resize((512, 512), Image.LANCZOS).save(SITE / "favicons/android-chrome-512x512.png")
    icon.save(SITE / "favicons/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    page.unlink()
    png.unlink()


if __name__ == "__main__":
    for capture, name in [
        ("02-log", "phone-log"), ("01-today", "phone-today"), ("04-lift-bench", "phone-lift"),
        ("05-coach-top", "phone-coach"), ("06-plan", "phone-plan"), ("07-completion-records", "phone-records"),
        ("04-progress", "phone-progress"),
    ]:
        phone(capture, name)
    watch(CAPTURES / "03-watch-log.png", "watch-log")
    watch(CAPTURES / "watch/02-rest.png", "watch-rest")
    for name in ["pr-record", "plate-loader", "volume-chart", "proposal-card", "share-card", "template-card",
                 "exercise-illustration", "records-list"]:
        cutout(name)
    for name in ["bench-spotter", "deadlift-man", "pull-up", "overhead-woman", "chalk-woman", "deadlift-woman"]:
        photo(name)
    app_icon()
