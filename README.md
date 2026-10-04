# Replex — website

Marketing site for [Replex](https://apps.apple.com/app/id6476805884), the strength training tracker
for iPhone and Apple Watch. Static HTML served by GitHub Pages at https://alexriakhin.com/Replex/.
This repository is the `ReplexWebsite` submodule of the app repository.

## Landing page (5.0, "Chalk & Iron")

The landing page is generated, one page per language:

```
src/landing.html          the template ({{key}} placeholders)
src/locales/<lang>.json   strings for one language (HTML allowed; <span class="v"> = volt keyword)
assets/css/site.css       styles (graphite canvas, volt accent, Archivo from Google Fonts)
assets/js/site.js         header, reveal-on-scroll, language switcher, App Store click events
assets/img/               WebP images and og-<lang>.png share cards
tools/make_assets.py      device renders, UI cards, photos and the app icon/favicons, built from
                          the app repo's docs/ASO/screenshots/source (US captures, pounds)
tools/build_site.py       writes index.html (English) and <lang>/index.html for every other
                          language (hreflang links, footer language switcher, share images,
                          sitemap entries), then the inner pages from src/pages/
```

```bash
python3 tools/make_assets.py   # after new app captures
python3 tools/build_site.py    # after editing the template or strings
python3 -m http.server 8765    # preview at http://localhost:8765
```

To add a language, copy `src/locales/en.json` to `src/locales/<lang>.json`, translate the values
(keep the keys and the `<span class="v">` markup), and run `build_site.py`.

## Inner pages

`faq.html`, `support.html`, `privacy.html`, `terms.html` and `changelog.html` are generated too (English):
`src/pages/<name>.html` holds the page body after a first-line `<!-- {json} -->` metadata comment, and
`src/page.html` is their shell. The header and footer of every page come from `src/partials/`.
The App Store listing links to the privacy, terms and support pages, so keep those paths stable.
