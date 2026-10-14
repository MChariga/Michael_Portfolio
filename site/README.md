# Michael Chariga portfolio (v2)

Static site. Edit `content.json`, then run:

    python3 make_cv.py     # rebuilds the CV PDF from content.json
    python3 make_images.py # (only if you change card images) designs the framed card images
    python3 build.py       # rebuilds dist/ (minifies CSS and JS, converts photos to WebP)
    cd dist && python3 -m http.server 8000

Needs: pip install pillow rcssmin rjsmin reportlab

Deploy by uploading the `dist/` folder to Cloudflare Pages, Netlify or GitHub Pages. `dist/_headers` sets caching and security headers on Cloudflare Pages and Netlify.

## Before you go live
- `site.url` in content.json: set your real domain (used for canonical links, the sitemap and social previews)
- Submit `https://your-domain/sitemap.xml` in Google Search Console
- `cv.experience[].period`: add real start dates
- `booking.endpoint` (Formspree URL) or `booking.calcom` (Cal.com link) for real bookings

## Prices (hidden)
Prices are not shown on the site. The earlier packages, hourly rates and payment terms are kept in `content.json` under `pricing_archive` in case you want them back.
`tools/quote-estimator.html` is a private calculator for your own quotes. It is not published.

## Photos
Put originals in `assets/` and `assets/gallery/`; the build creates the WebP versions in `dist/`.
