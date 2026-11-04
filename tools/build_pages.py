#!/usr/bin/env python3
"""Make a copy of index.html for each section so it has its own address,
title and sharing details (mazomoon.com/shop/, /journals/ ...).

It also turns each book review in content/reviews/*.md (written in Pages CMS,
see .pages.yml) into its own page at /reading/<slug>/, writes reviews.json for
the bookshelf, and refreshes the book list in the editor.

Run this after every change to index.html:  python3 tools/build_pages.py
(GitHub runs it too on every push, see .github/workflows/pages.yml.)
"""
import html, json, os, re
from datetime import date, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.mazomoon.com'
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
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    assert '<!--meta-start-->' in src and '<!--title-end-->' in src
    posts = load_posts(src)
    src = static_reviews(src, posts)  # review links are in the HTML for search engines
    urls = [SITE + '/']
    for path, (title, desc) in PAGES.items():
        url = f'{SITE}/{path}/'
        out = re.sub(r'<!--meta-start-->.*?<!--meta-end-->', lambda m: meta(title, desc, url), show(src, path), flags=re.S)
        out = re.sub(r'<title>.*?</title><!--title-end-->', f'<title>{html.escape(title)}</title><!--title-end-->', out, flags=re.S)
        d = os.path.join(ROOT, path)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
        urls.append(url)
    urls += write_reviews(src, posts)
    write_feed(posts)
    # unknown addresses fall back to the home page
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read())
    for p in ('privacy', 'cookies', 'terms'):
        urls.append(f'{SITE}/{p}/')
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    mod = {f'{SITE}/reading/{p["slug"]}/': p['updated'] for p in posts}
    if posts:
        mod[f'{SITE}/reading/'] = max(p['updated'] for p in posts)
    sm += ''.join(f'  <url><loc>{u}</loc>' + (f'<lastmod>{mod[u]}</lastmod>' if u in mod else '') + '</url>\n' for u in urls) + '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
    print('built', ', '.join(PAGES))


MONTHS = 'January February March April May June July August September October November December'.split()


def front(text):
    """Split a markdown file into (front matter dict, body)."""
    import yaml
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def to_html(body):
    body = body.strip()
    if re.match(r'^\s*<(p|h[1-6]|ul|ol|blockquote|div|figure|img)\b', body):
        return body  # the editor saved HTML already
    import markdown
    return markdown.markdown(body, extensions=['extra', 'sane_lists'])


def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower().replace("'", '').replace('&', 'and')).strip('-')


def as_date(v):
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return datetime.strptime(str(v)[:10], '%Y-%m-%d').date()
    except ValueError:
        return date.today()


def shelf(src):
    m = re.search(r'const READ=(\[.*?\]);\n', src)
    return json.loads(m.group(1))


def load_posts(src):
    """Read the published reviews in content/reviews/*.md, newest first."""
    folder = os.path.join(ROOT, 'content', 'reviews')
    read = shelf(src)
    series = {b: (n, a) for n, a, books in read for b in books}
    update_editor(sorted(series))
    posts = []
    for f in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if not f.endswith('.md'):
            continue
        fm, body = front(open(os.path.join(folder, f), encoding='utf-8').read())
        if not fm.get('published') or not fm.get('title'):
            continue  # drafts stay off the site
        book = str(fm.get('book') or '').strip()
        n, a = series.get(book, ('', fm.get('author') or ''))
        d = as_date(fm.get('date') or date.today())
        try:
            rating = max(0, min(5, int(fm.get('rating') or 0)))
        except (TypeError, ValueError):
            rating = 0
        slug = slugify(str(fm.get('slug') or os.path.splitext(f)[0]))
        cover = str(fm.get('cover') or '')
        posts.append(dict(slug=slug, title=str(fm['title']), book=book or str(fm['title']), series=n, author=a,
                          date=d.isoformat(), nice=f'{d.day} {MONTHS[d.month - 1]} {d.year}', rating=rating,
                          spoilers=bool(fm.get('spoilers')), cover=cover,
                          excerpt=str(fm.get('excerpt') or '').strip(), body=to_html(body),
                          seo_title=str(fm.get('seo_title') or '').strip(),
                          seo_description=str(fm.get('seo_description') or '').strip(),
                          updated=as_date(fm.get('updated') or d).isoformat(), text=plain(to_html(body))))
    posts.sort(key=lambda p: p['date'], reverse=True)
    return posts


def plain(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h))).strip()


def short(t, n=158):
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0].rstrip(',.;: ') + '…'


def stars_html(r):
    return f'<span class="stars" aria-label="{r} out of 5">{"★" * r}{"☆" * (5 - r)}</span>' if r else ''


def static_reviews(src, posts):
    """Write the review cards into the Reading Corner HTML, so they don't depend on scripts."""
    if not posts:
        return src
    e = lambda t: html.escape(t, quote=True)
    cards = ''.join(
        f'<a class="review-card" href="/reading/{p["slug"]}/">' + (f'<img src="{e(p["cover"])}" alt="" loading="lazy">' if p['cover'] else '')
        + f'<span class="label">{e(p["book"])}</span><h3 class="strong-s">{e(p["title"])}</h3>'
        + f'<p class="small muted">{p["nice"]} {stars_html(p["rating"])}</p>' + (f'<p class="small">{e(p["excerpt"])}</p>' if p['excerpt'] else '') + '</a>'
        for p in posts)
    src = src.replace('<div class="wrap sec-tight" id="reviewsWrap" hidden>', '<div class="wrap sec-tight" id="reviewsWrap">', 1)
    return src.replace('<div class="review-grid" id="reviewGrid"></div>', f'<div class="review-grid" id="reviewGrid">{cards}</div>', 1)


def write_feed(posts):
    e = lambda t: html.escape(t, quote=False)
    items = ''.join(
        f'<item><title>{e(p["title"])}</title><link>{SITE}/reading/{p["slug"]}/</link><guid>{SITE}/reading/{p["slug"]}/</guid>'
        f'<pubDate>{datetime.strptime(p["date"], "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0000")}</pubDate>'
        f'<description>{e(p["excerpt"] or short(p["text"], 300))}</description></item>\n' for p in posts)
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n<title>Mazo Moon: The Reading Corner</title>'
           f'<link>{SITE}/reading/</link><description>Honest book reviews from Rebecca at Mazo Moon.</description><language>en-gb</language>\n{items}</channel></rss>\n')
    open(os.path.join(ROOT, 'reading', 'feed.xml'), 'w', encoding='utf-8').write(rss)


def write_reviews(src, posts):
    """Make a /reading/<slug>/ page for each review, plus reviews.json for the bookshelf."""
    # clear out pages for reviews that were deleted or unpublished
    rd = os.path.join(ROOT, 'reading')
    keep = {p['slug'] for p in posts}
    for d in os.listdir(rd):
        fp = os.path.join(rd, d, 'index.html')
        if os.path.isfile(fp) and d not in keep and 'data-review="1"' in open(fp, encoding='utf-8').read():
            os.remove(fp); os.rmdir(os.path.join(rd, d))
    urls = []
    for p in posts:
        url = f'{SITE}/reading/{p["slug"]}/'
        by = f' by {p["author"]}' if p['author'] else ''
        if p['seo_title']:
            title = p['seo_title']
        elif p['book'].lower() in p['title'].lower():
            title = f'{p["title"]}: book review | Mazo Moon'
        else:
            title = f'{p["title"]}: {p["book"]} review | Mazo Moon'
        desc = short(p['seo_description'] or p['excerpt'] or f'My honest review of {p["book"]}{by}. {p["text"]}')
        if len(desc) < 70:
            desc = short(f'{desc.rstrip(".")}. My honest review of {p["book"]}{by}.')
        img = (SITE + p['cover']) if p['cover'].startswith('/') else (p['cover'] or IMG)
        e = lambda t: html.escape(t, quote=True)
        stars = stars_html(p['rating'])
        bits = [f'<span>By Rebecca</span>', f'<time datetime="{p["date"]}">{p["nice"]}</time>']
        if stars: bits.append(stars)
        label = e(p['series'] or 'Book review')
        about = e(p['book']) + (f' by {e(p["author"])}' if p['author'] else '')
        page = f'''<article class="wrap review" data-review="1">
  <div class="page-hero rise">
    <a class="btn btn-text" href="#reading" style="justify-self:start">Back to the Reading Corner</a>
    <div class="review-top">
      <div style="display:grid;gap:12px">
        <span class="label">{label}</span>
        <h1 class="d-xl">{e(p["title"])}</h1>
        <p class="postmeta">{" · ".join(bits)}</p>
        <p class="small muted" style="margin:0">My review of {about}</p>
      </div>
      {f'<img src="{e(p["cover"])}" alt="Cover of {e(p["book"])}">' if p["cover"] else ''}
    </div>
  </div>
  <div class="review-body">
    {'<p class="spoiler-note">Heads up: this review has spoilers.</p>' if p["spoilers"] else ''}
    {p["body"]}
  </div>
  <div class="review-foot sec-tight" style="padding-top:24px">
    <a class="btn btn-secondary" href="#reading">See the whole bookshelf</a>
    <a class="btn btn-text" href="#contact">Tell me what you thought</a>
  </div>
</article>'''
        ld = {'@context': 'https://schema.org', '@type': 'Review', 'name': p['title'], 'url': url,
              'datePublished': p['date'], 'dateModified': p['updated'], 'description': desc,
              'author': {'@type': 'Person', 'name': 'Rebecca', 'url': f'{SITE}/our-story/'},
              'publisher': {'@type': 'Organization', 'name': 'Mazo Moon', 'url': SITE + '/'},
              'itemReviewed': {'@type': 'Book', 'name': p['book']}}
        if p['author']:
            ld['itemReviewed']['author'] = [{'@type': 'Person', 'name': x.strip()} for x in re.split(r'\s*&\s*|\s+and\s+', p['author'])]
        if p['series']:
            ld['itemReviewed']['isPartOf'] = {'@type': 'BookSeries', 'name': p['series']}
        if p['rating']:
            ld['reviewRating'] = {'@type': 'Rating', 'ratingValue': p['rating'], 'bestRating': 5, 'worstRating': 1}
        if p['cover']:
            ld['image'] = img
        crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'The Reading Corner', 'item': f'{SITE}/reading/'},
            {'@type': 'ListItem', 'position': 3, 'name': p['title'], 'item': url}]}
        extra = (f'\n<meta property="article:published_time" content="{p["date"]}">'
                 f'\n<meta property="article:modified_time" content="{p["updated"]}">'
                 f'\n<script type="application/ld+json">{json.dumps([ld, crumbs], ensure_ascii=False).replace("</", "<\\/")}</script>')
        out = re.sub(r'<!--meta-start-->.*?<!--meta-end-->', lambda m: meta(title, desc, url, img, 'article', extra), show(src, 'review'), flags=re.S)
        out = re.sub(r'<title>.*?</title><!--title-end-->', lambda m: f'<title>{html.escape(title)}</title><!--title-end-->', out, flags=re.S)
        out = out.replace('<!--review-start--><!--review-end-->', f'<!--review-start-->{page}<!--review-end-->')
        d = os.path.join(rd, p['slug']); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)
        urls.append(url)
    pub = [{k: p[k] for k in ('slug', 'title', 'book', 'series', 'author', 'date', 'nice', 'rating', 'cover', 'excerpt')} for p in posts]
    open(os.path.join(ROOT, 'reviews.json'), 'w', encoding='utf-8').write(json.dumps(pub, ensure_ascii=False, indent=1))
    if posts:
        print('reviews:', ', '.join(p['slug'] for p in posts))
    return urls


def update_editor(books):
    """Keep the book dropdown in .pages.yml in step with the shelf."""
    p = os.path.join(ROOT, '.pages.yml')
    if not os.path.exists(p):
        return
    s = open(p, encoding='utf-8').read()
    vals = ''.join(f'            - {json.dumps(b, ensure_ascii=False)}\n' for b in books)
    new = re.sub(r'(# books-start\n).*?(\s*# books-end)', lambda m: m.group(1) + vals.rstrip('\n') + m.group(2), s, flags=re.S)
    if new != s:
        open(p, 'w', encoding='utf-8').write(new)


if __name__ == '__main__':
    main()
