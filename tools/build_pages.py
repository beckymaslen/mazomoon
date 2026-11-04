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


def meta(title, desc, url, img=IMG, kind='website'):
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
    urls += build_reviews(src)
    # unknown addresses fall back to the home page
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(src)
    for p in ('privacy', 'cookies', 'terms'):
        urls.append(f'{SITE}/{p}/')
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n'
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


def build_reviews(src):
    """Make /reading/<slug>/ pages and reviews.json from content/reviews/*.md."""
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
                          excerpt=str(fm.get('excerpt') or '').strip(), body=to_html(body)))
    posts.sort(key=lambda p: p['date'], reverse=True)
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
        title = f'{p["title"]} | Mazo Moon'
        desc = p['excerpt'] or f'Rebecca\'s review of {p["book"]}' + (f' by {p["author"]}.' if p['author'] else '.')
        img = (SITE + p['cover']) if p['cover'].startswith('/') else (p['cover'] or IMG)
        e = lambda t: html.escape(t, quote=True)
        stars = (f'<span class="stars" aria-label="{p["rating"]} out of 5">{"★" * p["rating"]}{"☆" * (5 - p["rating"])}</span>'
                 if p['rating'] else '')
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
        out = re.sub(r'<!--meta-start-->.*?<!--meta-end-->', lambda m: meta(title, desc, url, img, 'article'), src, flags=re.S)
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
