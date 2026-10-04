# Replex — website

Marketing site for [Replex](https://apps.apple.com/app/id6476805884), the strength training tracker
for iPhone and Apple Watch. Static HTML served by GitHub Pages at https://alexriakhin.com/Replex/.
This repository is the `ReplexWebsite` submodule of the app repository.

## How the site is built

Every page is generated in every language: English at the site root, other languages in
`/<site>/` (e.g. `/de/`, `/pt-br/`, `/zh-hans/`), with hreflang links, a language picker in the
header that keeps you on the same page, localized app screenshots and a share image per language.

```
src/landing.html               landing page template ({{key}} placeholders)
src/page.html                  shell for the inner pages
src/partials/                  shared header (with the language picker) and footer
src/locales/<site>.json        landing strings for one language (+ lang, dir, languageName,
                               App Store badge); HTML allowed, <span class="v"> = volt keyword
src/pages/<name>.html          English inner pages (faq, support, changelog, privacy, terms);
                               first line is a <!-- {json} --> comment with the page title etc.
src/pages/<site>/<name>.html   translations; a missing translation falls back to English
assets/css/site.css            styles (graphite canvas, volt accent; Archivo plus a companion
                               face per script: Roboto Flex, Cairo, Heebo, Noto Sans JP/KR/SC/TC)
assets/js/site.js              header, reveal-on-scroll, language picker, App Store click events
assets/img/                    English images (US captures, pounds), photos, icon, og-<site>.png
assets/img/<site>/             the same app screens captured in that language (kilograms)
tools/make_assets.py           device renders, UI cards, photos, icon and favicons from the app
                               repo's docs/ASO/screenshots/source; --localized for every language
tools/build_site.py            writes all pages for all languages, share images and sitemap.xml
```

```bash
python3 tools/make_assets.py               # English images, after new app captures
python3 tools/make_assets.py --localized   # every language's images
python3 tools/build_site.py                # every page in every language (+ share images)
python3 -m http.server 8765                # preview at http://localhost:8765
```

**Automatic language:** on a first visit to an English (US) page, a small inline script
(`src/partials/autolang.html`) sends the visitor to their browser language's version when the site
has one (English from the UK, Australia, New Zealand, Ireland and India → English (UK)). A language
picked in the header is remembered in `localStorage` and wins; crawlers and same-site navigation
are never redirected, and translated pages never redirect.

To add a language: capture the app in it (see the app repo's `docs/ASO/screenshots/README.md`),
add it to `SITE_CAPTURES` in `make_assets.py`, then add `src/locales/<site>.json` and
`src/pages/<site>/*.html`. The privacy and terms translations start with a note that the English
version applies. The App Store listing links to the English privacy, terms and support pages, so
keep those paths stable.
