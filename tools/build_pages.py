#!/usr/bin/env python3
"""Make a copy of index.html for each section so it has its own address,
title and sharing details (mazomoon.com/shop/, /journals/ ...).

Run this after every change to index.html:  python3 tools/build_pages.py
"""
import html, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://mazomoon.com'
IMG = SITE + '/img/og-image.jpg'

PAGES = {
    'journals': ('Journals & colouring books | Mazo Moon',
                 'Keepsake journals for kids, parents and grown-ups, and cosy colouring books for adults. Made in Yorkshire, delivered by Amazon.'),
    'shop': ('Shop stickers, pens, journals and more | Mazo Moon',
             'Stickers, gel and brush pens, sleep masks, journals and colouring books from Mazo Moon. Buy on Amazon with Prime delivery.'),
    'reading': ('The Reading Corner | Mazo Moon',
                'Rebecca\'s bookshelf: romantasy and fantasy series she has read, with honest reviews on the way.'),
    'little-things': ('Little Things I Love | Mazo Moon',
                      'Small comforts for slower days: the little things the Mazo Moon family loves.'),
    'our-story': ('Our story and contact | Mazo Moon',
                  'Mazo Moon is a Yorkshire family business making journals, colouring books and stationery. Say hello at hello@mazomoon.com.'),
}


def meta(title, desc, url):
    t, d = html.escape(title, quote=True), html.escape(desc, quote=True)
    return f'''<!--meta-start-->
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Mazo Moon">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<!--meta-end-->'''


def main():
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    assert '<!--meta-start-->' in src and '<!--title-end-->' in src
    urls = [SITE + '/']
    for path, (title, desc) in PAGES.items():
        url = f'{SITE}/{path}/'
        out = re.sub(r'<!--meta-start-->.*?<!--meta-end-->', lambda m: meta(title, desc, url), src, flags=re.S)
        out = re.sub(r'<title>.*?</title><!--title-end-->', f'<title>{html.escape(title)}</title><!--title-end-->', out, flags=re.S)
        d = os.path.join(ROOT, path)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
        urls.append(url)
    # unknown addresses fall back to the home page
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(src)
    for p in ('privacy', 'cookies', 'terms'):
        urls.append(f'{SITE}/{p}/')
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    print('built', ', '.join(PAGES))


if __name__ == '__main__':
    main()
