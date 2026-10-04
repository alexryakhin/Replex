#!/usr/bin/env python3
"""Build the landing page for every language in src/locales/, and the inner pages.

src/landing.html is the one template; src/locales/<lang>.json holds that language's strings
(HTML allowed: <span class="v"> marks the volt keyword). English is written to index.html at the
site root, every other language to <lang>/index.html, with hreflang links between them, a language
switcher in the footer, and a 1200 x 630 share image per language (assets/img/og-<lang>.png,
rendered with headless Chrome).

Inner pages (faq, support, privacy, terms, changelog) are English: src/pages/<name>.html holds
the page body after a first-line comment with its metadata as JSON (pageTitle, pageDescription,
pageEyebrow, pageHeading, pageLead); src/page.html is their shell. Both templates pull the shared
header and footer from src/partials/ with {{>header}} / {{>footer}}.

    python3 tools/build_site.py            # every language
    python3 tools/build_site.py --no-og    # skip the share images
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
PARTIALS = {path.stem: path.read_text() for path in (SITE / "src/partials").glob("*.html")}


def expand(template: str) -> str:
    return re.sub(r"\{\{>(\w+)\}\}\n?", lambda m: PARTIALS[m.group(1)], template)


TEMPLATE = expand((SITE / "src/landing.html").read_text())
PAGE = expand((SITE / "src/page.html").read_text())
ORIGIN = "https://alexriakhin.com/Replex/"
APP_STORE = "https://apps.apple.com/app/id6476805884"
DEFAULT = "en"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def load_locales() -> dict:
    locales = {}
    for path in sorted((SITE / "src/locales").glob("*.json")):
        locales[path.stem] = json.loads(path.read_text())
    return dict(sorted(locales.items(), key=lambda item: (item[0] != DEFAULT, item[0])))


def page_url(lang: str) -> str:
    return ORIGIN if lang == DEFAULT else f"{ORIGIN}{lang}/"


def alternates(locales: dict) -> str:
    lines = [f'  <link rel="alternate" hreflang="{lang}" href="{page_url(lang)}">' for lang in locales]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{page_url(DEFAULT)}">')
    return "\n".join(lines)


def switcher(locales: dict, current: str, base: str) -> str:
    if len(locales) < 2:
        return ""
    options = []
    for lang, strings in locales.items():
        href = base if lang == DEFAULT else f"{base}{lang}/"
        selected = " selected" if lang == current else ""
        options.append(f'          <option value="{href}" lang="{lang}"{selected}>{strings["languageName"]}</option>')
    label = html.escape(locales[current]["footerLanguage"])
    return (
        '      <label class="lang-switch">\n'
        f'        <span class="visually-hidden">{label}</span>\n'
        f'        <select aria-label="{label}">\n' + "\n".join(options) + "\n        </select>\n      </label>"
    )


def fill(template: str, values: dict, where: str) -> str:
    def value(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"{where}: missing string {key!r}")
        return values[key]

    page = re.sub(r"\{\{(\w+)\}\}", value, template)
    # Attributes can't carry markup: strip tags/entities inside alt="…" and content="…".
    return re.sub(
        r'((?:alt|content|aria-label)=")([^"]*)(")',
        lambda m: m.group(1) + re.sub(r"<[^>]+>", "", m.group(2)) + m.group(3),
        page,
    )


def render(lang: str, locales: dict) -> str:
    strings = locales[lang]
    base = "" if lang == DEFAULT else "../"
    values = dict(strings)
    values.update(
        base=base,
        root=base,
        home="./",
        navBase="",
        canonical=page_url(lang),
        appStore=APP_STORE,
        alternates=alternates(locales),
        languageSwitcher=switcher(locales, lang, base),
    )
    return fill(TEMPLATE, values, lang)


def render_page(source: Path, locales: dict) -> str:
    """An inner page (English, at the site root) from src/pages/<name>.html."""
    text = source.read_text()
    meta_match = re.match(r"<!--\s*(\{.*?\})\s*-->\n", text, re.S)
    if not meta_match:
        raise ValueError(f"{source.name}: first line must be a <!-- {{json}} --> metadata comment")
    values = dict(locales[DEFAULT])
    values.update(json.loads(meta_match.group(1)))
    values.update(
        base="",
        root="",
        home="./",
        navBase="./",
        canonical=f"{ORIGIN}{source.name}",
        appStore=APP_STORE,
        content=text[meta_match.end():].rstrip(),
        languageSwitcher="",
    )
    return fill(PAGE, values, source.name)


def share_image(lang: str, strings: dict):
    """1200 x 630 share card: headline left, the logging phone and record card right."""
    page = SITE / f"assets/img/_og-{lang}.html"
    page.write_text(f"""<!doctype html><html lang="{lang}" dir="{strings.get('dir', 'ltr')}"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..900&display=block" rel="stylesheet">
<link rel="stylesheet" href="../css/site.css">
<style>
body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #0B0B0C; }}
.og {{ position: relative; width: 1200px; height: 630px; overflow: hidden; }}
.og-photo {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 30% 35%; opacity: .45; }}
.og::after {{ content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(11,11,12,.97) 0%, rgba(11,11,12,.8) 55%, rgba(11,11,12,.35) 100%); }}
.og-copy {{ position: absolute; z-index: 1; left: 70px; top: 70px; width: 640px; }}
.og-copy .headline {{ font-size: 124px; }}
.og-brand {{ display: flex; gap: 14px; align-items: center; margin-top: 40px; }}
.og-brand img {{ width: 64px; border-radius: 15px; }}
.og-brand span {{ font-family: Archivo; font-stretch: 125%; font-variation-settings: "wdth" 125; font-weight: 900; font-size: 34px; text-transform: uppercase; color: #F4F3EF; }}
.og-phone {{ position: absolute; z-index: 1; width: 330px; right: 90px; top: 60px; transform: rotate(5deg); filter: drop-shadow(0 30px 40px rgba(0,0,0,.7)); }}
.og-card {{ position: absolute; z-index: 2; width: 380px; right: 200px; top: 360px; transform: rotate(-4deg); filter: drop-shadow(0 0 40px rgba(255,200,61,.3)) drop-shadow(0 20px 30px rgba(0,0,0,.8)); }}
</style></head><body><div class="og">
<img class="og-photo" src="photo-bench-spotter.webp">
<div class="og-copy"><h1 class="headline">{strings['heroTitle']}</h1>
<div class="og-brand"><img src="app-icon.webp"><span>Replex</span></div></div>
<img class="og-phone" src="phone-log.webp"><img class="og-card" src="card-pr-record.webp">
</div></body></html>""")
    out = SITE / f"assets/img/og-{lang}.png"
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,630",
        "--virtual-time-budget=4000", f"--screenshot={out}", f"file://{page}",
    ], check=True, capture_output=True)
    page.unlink()
    print(f"assets/img/og-{lang}.png")


def sitemap(locales: dict):
    path = SITE / "sitemap.xml"
    text = path.read_text()
    text = re.sub(r"\s*<url>\s*<loc>https://alexriakhin\.com/Replex/[a-z]{2}(?:-[A-Za-z]+)?/</loc>.*?</url>", "", text, flags=re.S)
    extra = "".join(
        f"\n  <url>\n    <loc>{page_url(lang)}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.9</priority>\n  </url>"
        for lang in locales if lang != DEFAULT
    )
    text = text.replace("</urlset>", extra.lstrip("\n") + ("\n" if extra else "") + "</urlset>") if extra else text
    path.write_text(text)


def main():
    locales = load_locales()
    for lang, strings in locales.items():
        out = SITE / ("index.html" if lang == DEFAULT else f"{lang}/index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(lang, locales))
        print(out.relative_to(SITE))
        if "--no-og" not in sys.argv:
            share_image(lang, strings)
    for source in sorted((SITE / "src/pages").glob("*.html")):
        (SITE / source.name).write_text(render_page(source, locales))
        print(source.name)
    sitemap(locales)


if __name__ == "__main__":
    main()
