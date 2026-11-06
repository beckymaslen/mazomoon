#!/usr/bin/env python3
"""Build the site.

The home page (index.html) is the interactive desk: src/desk-body.html plus the head made here,
with its scripts and pictures in /desk/. Each section (mazomoon.com/shop/, /journals/ ...) is a copy
of src/site.html with its own address, title and sharing details.

Book reviews and blog posts (content/reviews/*.md, written in Pages CMS, see .pages.yml) are
built by tools/blog.py: their pages, previews, the blog and category pages, feed and checks.

Run this after every change to src/site.html or src/desk-body.html:  python3 tools/build_pages.py
(GitHub runs it too on every push, see .github/workflows/pages.yml.)
"""
import hashlib
import html
import re, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blog  # noqa: E402  the reviews and blog posts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.mazomoon.com'
IMG = SITE + '/img/og-image.jpg'

PAGES = {
    'journals': ('Journals & colouring books | Mazo Moon',
                 'Keepsake journals for kids, parents and grown-ups, and cosy colouring books for adults. Made in Yorkshire, delivered by Amazon.'),
    'shop': ('Shop stickers, pens, journals and more | Mazo Moon',
             'Stickers, gel and brush pens, sleep masks, journals and colouring books from Mazo Moon. Buy securely on Amazon, where you can see current prices and delivery options.'),
    'reading': ('The Reading Corner | Mazo Moon',
                'Rebecca\'s bookshelf: romantasy and fantasy series she has read, with honest reviews on the way.'),
    'little-things': ('Little Things I Love | Mazo Moon',
                      'Small comforts for slower days: the little things the Mazo Moon family loves.'),
    'our-story': ('Our story and contact | Mazo Moon',
                  'Mazo Moon is a Yorkshire family business making journals, colouring books and stationery. Say hello at hello@mazomoon.com.'),
}


def meta(title, desc, url, img=IMG, kind='website', extra=''):
    t, d = html.escape(title, quote=True), html.escape(desc, quote=True)
    return f'''<!--meta-start-->
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{kind}">
<meta property="og:site_name" content="Mazo Moon">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="Mazo Moon book reviews" href="{SITE}/reading/feed.xml">{extra}
<!--meta-end-->'''


def show(src, page):
    """Make the right section visible in the HTML itself, before any script runs."""
    out = src.replace('<section class="page" data-page="home">', '<section class="page" data-page="home" hidden>', 1)
    return out.replace(f'<section class="page" data-page="{page}" hidden>', f'<section class="page" data-page="{page}">', 1)


def main():
    src = open(os.path.join(ROOT, 'src', 'site.html'), encoding='utf-8').read()
    assert '<!--meta-start-->' in src and '<!--title-end-->' in src
    b = blog.Blog(src)  # every post in content/reviews, checked (see tools/blog.py)
    src = blog.static_cards(src, b)  # review links are in the HTML for search engines
    urls = [SITE + '/']
    for path, (title, desc) in PAGES.items():
        url = f'{SITE}/{path}/'
        out = re.sub(r'<!--meta-start-->.*?<!--meta-end-->', lambda m: meta(title, desc, url), show(src, path), flags=re.S)
        out = re.sub(r'<title>.*?</title><!--title-end-->', f'<title>{html.escape(title)}</title><!--title-end-->', out, flags=re.S)
        d = os.path.join(ROOT, path)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
        urls.append(url)
    posts = blog.write(b, src, show, meta)  # {url: (lastmod, [images])} for the sitemap
    desk = write_desk(b.reviews)
    # unknown addresses show the desk, marked so search engines don't index them
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(desk.replace('<!--meta-start-->', '<meta name="robots" content="noindex">\n<!--meta-start-->', 1))
    for p in ('privacy', 'cookies', 'terms'):
        urls.append(f'{SITE}/{p}/')
    mod = {u: (lm, im) for u, (lm, im) in posts.items()}
    if b.reviews:
        mod[f'{SITE}/reading/'] = (max(p['updated'] for p in b.reviews), [])
    urls += [u for u in posts if u not in urls]
    x = lambda t: html.escape(t, quote=False)
    sm = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
          'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n')
    for u in urls:
        lm, im = mod.get(u, ('', []))
        sm += (f'  <url><loc>{u}</loc>' + (f'<lastmod>{lm}</lastmod>' if lm else '')
               + ''.join(f'<image:image><image:loc>{x(i)}</image:loc></image:image>' for i in im) + '</url>\n')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm + '</urlset>\n')
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    print('built', ', '.join(PAGES))


HOME_TITLE = 'Mazo Moon | Journals, colouring and stationery from Yorkshire'
HOME_DESC = 'Mazo Moon is a Yorkshire family business making journals, colouring books and stationery. Make a little space for you.'


def write_desk(posts):
    """index.html: the desk home page, and desk/reviews.js with the published reviews for its bookshelf."""
    body = open(os.path.join(ROOT, 'src', 'desk-body.html'), encoding='utf-8').read()
    org = {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Mazo Moon', 'legalName': 'Mazo Moon Ltd',
           'url': SITE + '/', 'logo': SITE + '/img/favicon.png', 'email': 'hello@mazomoon.com',
           'sameAs': ['https://www.instagram.com/mazomoon', 'https://uk.pinterest.com/mazomoon',
                      'https://www.amazon.co.uk/stores/MazoMoon/page/298754B3-2DA8-49CE-B163-4EA6E7FEA0E0']}
    head = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(HOME_TITLE)}</title>
{meta(HOME_TITLE, HOME_DESC, SITE + '/', extra=chr(10) + '<script type="application/ld+json">' + json.dumps(org, ensure_ascii=False) + '</script>')}
<link rel="icon" href="/img/favicon.png">
<link rel="apple-touch-icon" href="/img/favicon.png">
<script src="/consent.js" defer></script>
'''
    revs = [{'slug': p['slug'], 'book': p['book'], 'title': p['title'], 'url': f'/reading/{p["slug"]}/', 'rating': p['rating'],
             'spoilers': bool(p['spoilers']), 'date': p['nice'], 'iso': p['date'], 'excerpt': p['excerpt'], 'html': p['body']} for p in posts]
    open(os.path.join(ROOT, 'desk', 'reviews.js'), 'w', encoding='utf-8').write(
        '/* Made by tools/build_pages.py from the published reviews in Pages CMS. Don\'t edit by hand. */\n'
        'window.MM.reviews = ' + json.dumps(revs, ensure_ascii=False, indent=1).replace('</', '<\\/') + ';\n')
    # stamp each desk script with a hash of its contents, so browsers fetch the new file as soon as it changes
    for name in ('content.js', 'reviews.js', 'app.js'):
        tag = hashlib.md5(open(os.path.join(ROOT, 'desk', name), 'rb').read()).hexdigest()[:10]
        body = re.sub(r'src="/desk/' + re.escape(name) + r'(\?v=[0-9a-f]+)?"', f'src="/desk/{name}?v={tag}"', body)
    out = head + body.replace('\n<noscript>', '\n</head>\n<body>\n<noscript>', 1) + '\n</body>\n</html>\n'
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
    return out



if __name__ == '__main__':
    main()
