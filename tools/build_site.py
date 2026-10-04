#!/usr/bin/env python3
"""Build every page of the site in every language.

Languages are the files in src/locales/: <site>.json, where <site> is the folder the language is
published in (en at the site root, others at /<site>/ — e.g. de, pt-br, zh-hans). Each file holds
the landing page strings plus "lang" (BCP 47, e.g. pt-BR), "dir" and "languageName" (the
language's own name, shown in the header language picker).

Pages:
- the landing page: src/landing.html + the locale strings → index.html / <site>/index.html
- inner pages (faq, support, changelog, privacy, terms): src/page.html (shell) + the page body in
  src/pages/<name>.html (English) or src/pages/<site>/<name>.html (a translation). The body starts
  with a <!-- {json} --> comment holding pageTitle, pageDescription, pageEyebrow, pageHeading and
  pageLead. A language without a translation of a page gets the English body.

Both templates pull the shared header and footer from src/partials/ ({{>header}}, {{>footer}}).
App screenshots come from assets/img/<site>/ when tools/make_assets.py made localized ones, else
from assets/img/ (English). Each language also gets a 1200 x 630 share image (og-<site>.png).

    python3 tools/build_site.py            # everything
    python3 tools/build_site.py --no-og    # skip the share images
"""
import hashlib
import html
import json
import re
import subprocess
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent
PARTIALS = {path.stem: path.read_text() for path in (SITE / "src/partials").glob("*.html")}
ORIGIN = "https://alexriakhin.com/Replex/"
APP_STORE = "https://apps.apple.com/app/id6476805884"
DEFAULT = "en"
PAGES = ["faq", "support", "changelog", "privacy", "terms"]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FONTS = "https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,500..900"
# Archivo is Latin-only: each script gets a heavy companion face (see site.css › Scripts).
SCRIPT_FONTS = {
    "ru": "Roboto+Flex:opsz,wdth,wght@8..144,25..151,400..1000",
    "uk": "Roboto+Flex:opsz,wdth,wght@8..144,25..151,400..1000",
    "ar": "Cairo:wght@500..1000",
    "he": "Heebo:wght@500..900",
    "ja": "Noto+Sans+JP:wght@500..900",
    "ko": "Noto+Sans+KR:wght@500..900",
    "zh-hans": "Noto+Sans+SC:wght@500..900",
    "zh-hant": "Noto+Sans+TC:wght@500..900",
}


def expand(template: str) -> str:
    return re.sub(r"\{\{>(\w+)\}\}\n?", lambda m: PARTIALS[m.group(1)], template)


def asset_version(*paths: str) -> str:
    """Short content hash for cache-busting ?v= on the stylesheet and script."""
    digest = hashlib.sha1()
    for path in paths:
        digest.update((SITE / path).read_bytes())
    return digest.hexdigest()[:8]


LANDING = expand((SITE / "src/landing.html").read_text())
SHELL = expand((SITE / "src/page.html").read_text())


def load_locales() -> dict:
    locales = {path.stem: json.loads(path.read_text()) for path in (SITE / "src/locales").glob("*.json")}
    english = locales[DEFAULT]
    for site, strings in locales.items():
        missing = [key for key in english if key not in strings]
        if missing:
            print(f"warning: {site} is missing {len(missing)} strings, using English: {', '.join(missing[:6])}…")
            locales[site] = {**english, **strings}
    # English (US) first, then other English variants, then everything else alphabetically.
    return dict(sorted(locales.items(), key=lambda item: (item[0] != DEFAULT, not item[0].startswith("en"), item[0])))


def folder(site: str) -> str:
    return "" if site == DEFAULT else f"{site}/"


def page_url(site: str, filename: str = "") -> str:
    return f"{ORIGIN}{folder(site)}{filename}"


def alternates(locales: dict, filename: str) -> str:
    # A locale can stand for several regions ("hreflangs", e.g. English (UK) for GB, AU, NZ, IE, IN).
    lines = [
        f'  <link rel="alternate" hreflang="{code}" href="{page_url(site, filename)}">'
        for site, strings in locales.items()
        for code in strings.get("hreflangs", [strings["lang"]])
    ]
    lines.append(f'  <link rel="alternate" hreflang="x-default" href="{page_url(DEFAULT, filename)}">')
    return "\n".join(lines)


GLOBE = (
    '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9.5" '
    'fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M2.5 12h19M12 2.5c2.6 2.8 3.9 6 3.9 9.5s'
    '-1.3 6.7-3.9 9.5c-2.6-2.8-3.9-6-3.9-9.5s1.3-6.7 3.9-9.5z" fill="none" stroke="currentColor" '
    'stroke-width="1.8"/></svg>'
)


def language_picker(locales: dict, current: str, filename: str) -> str:
    """Header dropdown linking to the same page in every language."""
    base = "" if current == DEFAULT else "../"
    items = []
    for site, strings in locales.items():
        href = f"{base}{folder(site)}{filename}" or "./"
        current_attr = ' aria-current="page"' if site == current else ""
        items.append(
            f'          <li><a href="{href}" hreflang="{strings["lang"]}" lang="{strings["lang"]}"{current_attr}>'
            f'{strings["languageName"]}</a></li>'
        )
    strings = locales[current]
    code = strings["lang"].split("-")[0].upper()
    return (
        '      <details class="lang">\n'
        f'        <summary aria-label="{html.escape(strings["footerLanguage"])}">{GLOBE}'
        f'<span class="lang-name">{strings["languageName"]}</span><span class="lang-code">{code}</span></summary>\n'
        '        <ul>\n' + "\n".join(items) + "\n        </ul>\n      </details>"
    )


def fill(template: str, values: dict, where: str) -> str:
    def value(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"{where}: missing string {key!r}")
        return values[key]

    page = re.sub(r"\{\{(\w+)\}\}", value, template)
    # Attributes can't carry markup: strip tags inside alt="…", content="…" and aria-label="…".
    return re.sub(
        r'((?:alt|content|aria-label)=")([^"]*)(")',
        lambda m: m.group(1) + re.sub(r"<[^>]+>", "", m.group(2)) + m.group(3),
        page,
    )


def common_values(site: str, locales: dict, filename: str) -> dict:
    base = "" if site == DEFAULT else "../"
    localized_shots = (SITE / "assets/img" / site / "phone-log.webp").exists()
    values = dict(locales[site])
    values.update(
        site=site,
        base=base,
        root="",
        home="./",
        appStore=APP_STORE,
        shots=f"{base}assets/img/{site}/" if localized_shots else f"{base}assets/img/",
        assetVersion=asset_version("assets/css/site.css", "assets/js/site.js"),
        fontsHref=FONTS + (f"&family={SCRIPT_FONTS[site]}" if site in SCRIPT_FONTS else "") + "&display=swap",
        canonical=page_url(site, filename),
        alternates=alternates(locales, filename),
        languagePicker=language_picker(locales, site, filename),
        # Only English (US) pages pick the visitor's language; translated pages never redirect.
        autoLanguage=PARTIALS["autolang"] if site == DEFAULT else "",
    )
    return values


def render_landing(site: str, locales: dict) -> str:
    values = common_values(site, locales, "")
    values["navBase"] = ""
    return fill(LANDING, values, f"{site}/index")


BRITISH = [("colors", "colours"), ("Colors", "Colours"), ("color", "colour"), ("canceled", "cancelled"),
           ("Canceled", "Cancelled"), ("favorite", "favourite"), ("personalized", "personalised"),
           ("organize", "organise"), ("optimized", "optimised"), ("center", "centre")]


def british(text: str) -> str:
    """US → British spelling for English (UK) pages built from the English source."""
    for us, uk in BRITISH:
        text = re.sub(rf"\b{us}\b", uk, text)
    return text


def page_source(site: str, name: str) -> tuple[Path, bool]:
    translated = SITE / "src/pages" / site / f"{name}.html"
    if site != DEFAULT and translated.exists():
        return translated, True
    return SITE / "src/pages" / f"{name}.html", site == DEFAULT


def render_page(site: str, name: str, locales: dict) -> str:
    source, translated = page_source(site, name)
    text = source.read_text()
    meta = re.match(r"<!--\s*(\{.*?\})\s*-->\n", text, re.S)
    if not meta:
        raise ValueError(f"{source}: first line must be a <!-- {{json}} --> metadata comment")
    values = common_values(site, locales, f"{name}.html")
    values.update(json.loads(meta.group(1)))
    body = text[meta.end():].rstrip()
    if locales[site].get("spelling") == "british" and not (SITE / "src/pages" / site / f"{name}.html").exists():
        body, translated = british(body), True
        values.update({key: british(value) for key, value in json.loads(meta.group(1)).items()})
    if not translated:
        body = f'<div lang="en" dir="ltr">\n{body}\n</div>'
    values.update(navBase="./", content=body)
    return fill(SHELL, values, f"{site}/{name}")


def share_image(site: str, strings: dict, shots: str):
    """1200 x 630 share card: headline left, the logging phone and record card right."""
    page = SITE / f"assets/img/_og-{site}.html"
    page.write_text(f"""<!doctype html><html lang="{strings['lang']}" dir="{strings.get('dir', 'ltr')}"><head><meta charset="utf-8">
<link href="{FONTS}{'&family=' + SCRIPT_FONTS[site] if site in SCRIPT_FONTS else ''}&display=block" rel="stylesheet">
<link rel="stylesheet" href="../css/site.css">
<style>
body {{ margin: 0; width: 1200px; height: 630px; overflow: hidden; background: #0B0B0C; }}
.og {{ position: relative; width: 1200px; height: 630px; overflow: hidden; }}
.og-photo {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 30% 35%; opacity: .45; }}
.og::after {{ content: ""; position: absolute; inset: 0; background: linear-gradient(90deg, rgba(11,11,12,.97) 0%, rgba(11,11,12,.8) 55%, rgba(11,11,12,.35) 100%); }}
[dir="rtl"] .og::after {{ background: linear-gradient(270deg, rgba(11,11,12,.97) 0%, rgba(11,11,12,.8) 55%, rgba(11,11,12,.35) 100%); }}
.og-copy {{ position: absolute; z-index: 1; inset-inline-start: 70px; top: 70px; width: 640px; }}
.og-copy .headline {{ font-size: 118px; }}
.og-brand {{ display: flex; gap: 14px; align-items: center; margin-top: 40px; }}
.og-brand img {{ width: 64px; border-radius: 15px; }}
.og-brand span {{ font-family: Archivo; font-stretch: 125%; font-variation-settings: "wdth" 125; font-weight: 900; font-size: 34px; text-transform: uppercase; color: #F4F3EF; }}
.og-phone {{ position: absolute; z-index: 1; width: 330px; inset-inline-end: 90px; top: 60px; transform: rotate(5deg); filter: drop-shadow(0 30px 40px rgba(0,0,0,.7)); }}
.og-card {{ position: absolute; z-index: 2; width: 380px; inset-inline-end: 200px; top: 360px; transform: rotate(-4deg); filter: drop-shadow(0 0 40px rgba(255,200,61,.3)) drop-shadow(0 20px 30px rgba(0,0,0,.8)); }}
</style></head><body><div class="og">
<img class="og-photo" src="photo-bench-spotter.webp">
<div class="og-copy"><h1 class="headline">{strings['heroTitle']}</h1>
<div class="og-brand"><img src="app-icon.webp"><span>Replex</span></div></div>
<img class="og-phone" src="{shots}phone-log.webp"><img class="og-card" src="{shots}card-pr-record.webp">
</div></body></html>""")
    out = SITE / f"assets/img/og-{site}.png"
    subprocess.run([
        CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,630",
        "--virtual-time-budget=4000", f"--screenshot={out}", f"file://{page}",
    ], check=True, capture_output=True)
    page.unlink()


def sitemap(locales: dict):
    urls = []
    for site in locales:
        urls.append((page_url(site), "weekly", "1.0" if site == DEFAULT else "0.9"))
        for name in PAGES:
            priority = "0.5" if name in ("privacy", "terms") else "0.7"
            urls.append((page_url(site, f"{name}.html"), "monthly", priority))
    body = "".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{priority}</priority>\n  </url>\n"
        for loc, freq, priority in urls
    )
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + body + "</urlset>\n"
    )


def main():
    locales = load_locales()
    for site, strings in locales.items():
        out_dir = SITE / folder(site)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(render_landing(site, locales))
        for name in PAGES:
            (out_dir / f"{name}.html").write_text(render_page(site, name, locales))
        if "--no-og" not in sys.argv:
            shots = f"{site}/" if (SITE / "assets/img" / site / "phone-log.webp").exists() else ""
            share_image(site, strings, shots)
        print(f"{site}: index + {len(PAGES)} pages")
    sitemap(locales)


if __name__ == "__main__":
    main()
