#!/usr/bin/env python3
"""The Mazo Moon blog: book reviews and blog posts written in Pages CMS.

Posts are Markdown files in content/reviews/, product-reviews/, roundups/ and posts/ (fields are set up in .pages.yml). This module:
  - reads every post, fills in what can be worked out (book author, series, reading time, search text ...),
  - checks each one before it goes live (problems that would break a page keep it off the site),
  - writes the article pages, a preview page for every post at /preview/<file name>/ with the checklist,
    search and sharing previews and a promotion pack, the blog and category pages, redirects,
    the feed, posts.json/reviews.json, and the sitemap entries.

tools/build_pages.py calls it. To check the posts without building:  python3 tools/blog.py --check [file.md]
"""
import html, json, math, os, re, sys
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.mazomoon.com'
IMG = SITE + '/img/og-image.jpg'
UK = ZoneInfo('Europe/London')
# folder -> the post type its files are, unless a file says otherwise
FOLDERS = {'reviews': 'review', 'product-reviews': 'product_review', 'roundups': 'roundup', 'posts': 'blog'}
MONTHS = 'January February March April May June July August September October November December'.split()
KINDS = {'review': 'Book review', 'product_review': 'Product review', 'roundup': 'Product roundup', 'blog': 'Blog post', 'guide': 'Reading guide', 'listicle': 'List', 'editorial': 'Editorial'}
STATIC_PATHS = {'/', '/journals/', '/shop/', '/reading/', '/little-things/', '/our-story/', '/privacy/', '/cookies/', '/terms/',
                '/links/', '/blog/', '/reading/feed.xml', '/sitemap.xml'}
e = lambda t: html.escape(str(t or ''), quote=True)
# Reader comments go through Cusdis (cusdis.com): no reader accounts, and nothing shows until Rebecca approves it.
# Paste the App ID from the Cusdis dashboard here to switch comments on. Empty = no comment section.
COMMENTS_APP_ID = ''
COMMENTS_HOST = 'https://cusdis.com'


# ---------------------------------------------------------------- small helpers

def front(text):
    import yaml
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n?(.*)$', text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def to_html(body):
    body = (body or '').strip()
    if not body:
        return ''
    if re.match(r'^\s*<(p|h[1-6]|ul|ol|blockquote|div|figure|img|table)\b', body):
        return body  # the editor saved HTML already
    import markdown
    return markdown.markdown(body, extensions=['extra', 'sane_lists'])


def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', str(t).lower().replace("'", '').replace('’', '').replace('&', 'and')).strip('-')


def plain(h):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h or ''))).strip()


def short(t, n=158):
    t = (t or '').strip()
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0].rstrip(',.;: ') + '…'


def stars_html(r):
    return f'<span class="stars" aria-label="{r} out of 5 stars">{"★" * r}{"☆" * (5 - r)}</span>' if r else ''


def ref_key(v):
    """A Pages CMS reference ('rebecca.md' or 'content/authors/rebecca.md') -> 'rebecca'."""
    v = str(v or '').strip()
    return os.path.splitext(os.path.basename(v))[0] if v else ''


def as_datetime(v):
    """Front matter date (date, datetime or 'YYYY-MM-DD[THH:MM]', UK time) -> aware datetime, or None."""
    if v in (None, ''):
        return None
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=UK)
    if isinstance(v, date):
        return datetime(v.year, v.month, v.day, 9, 0, tzinfo=UK)
    s = str(v).strip().replace(' ', 'T')
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d'):
        try:
            d = datetime.strptime(s[:len(datetime.now().strftime(fmt))], fmt)
            if fmt == '%Y-%m-%d':
                d = d.replace(hour=9)
            return d.replace(tzinfo=UK)
        except ValueError:
            continue
    return None


def nice(d):
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'


def as_list(v):
    if v in (None, ''):
        return []
    return [x for x in (v if isinstance(v, list) else [v]) if x not in (None, '')]


def obj(fm, key):
    v = fm.get(key)
    return v if isinstance(v, dict) else {}


def img_url(p):
    p = str(p or '').strip()
    return '' if not p else p if p.startswith(('http://', 'https://')) else (SITE + p if p.startswith('/') else f'{SITE}/{p}')


def local_file(p):
    p = str(p or '').strip()
    if not p or p.startswith(('http://', 'https://')):
        return None
    f = os.path.join(ROOT, p.lstrip('/'))
    return f if os.path.isfile(f) else None


def image_size(p):
    f = local_file(p)
    if not f:
        return None
    try:
        from PIL import Image
        with Image.open(f) as im:
            return im.size
    except Exception:
        return None


# ---------------------------------------------------------------- the shelf, categories and writers

def shelf(src):
    """Book title -> its series details, from the READ list in src/site.html."""
    m = re.search(r'const READ=(\[.*?\]);\n', src)
    out = {}
    for name, author, books in json.loads(m.group(1)) if m else []:
        for i, b in enumerate(books):
            out[b] = dict(book=b, series=name if len(books) > 1 or name != b else '', author=author,
                          pos=i + 1, total=len(books), books=books, series_name=name)
    return out


def load_folder(name):
    d = os.path.join(ROOT, 'content', name)
    out = {}
    for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if f.endswith('.md'):
            try:
                fm, body = front(open(os.path.join(d, f), encoding='utf-8').read())
            except Exception as ex:
                print(f'  COULD NOT READ content/{name}/{f}: {ex}')
                continue
            fm['key'] = os.path.splitext(f)[0]
            fm['body'] = body
            out[fm['key']] = fm
    return out


def update_editor(books):
    """Keep the book dropdown in .pages.yml in step with the shelf."""
    p = os.path.join(ROOT, '.pages.yml')
    if not os.path.exists(p):
        return
    s = open(p, encoding='utf-8').read()

    def fill(m):
        pad = m.group(1)
        return m.group(0)[:m.end(2) - m.start(0)] + ''.join(f'{pad}- {json.dumps(b, ensure_ascii=False)}\n' for b in books) + pad + '# books-end'
    new = re.sub(r'([ \t]*)(# books-start\n).*?[ \t]*# books-end', fill, s, flags=re.S)
    if new != s:
        open(p, 'w', encoding='utf-8').write(new)


# ---------------------------------------------------------------- reading the posts

class Blog:
    def __init__(self, src, now=None):
        self.now = now or datetime.now(timezone.utc)
        self.books = shelf(src)
        update_editor(sorted(self.books))
        self.cats = load_folder('categories')
        self.authors = load_folder('authors')
        self.products = load_folder('products')
        self.partners = load_folder('partners')
        self.broken = []
        self.all = []
        files = [(d, f) for d in FOLDERS if os.path.isdir(os.path.join(ROOT, 'content', d))
                 for f in sorted(os.listdir(os.path.join(ROOT, 'content', d)))]
        for d, f in files:
            if f.endswith('.md'):
                try:
                    self.all.append(self.read(f, d))
                except Exception as ex:  # one bad file mustn't stop the rest of the site building
                    self.broken.append((f, str(ex).splitlines()[0]))
                    print(f'::error file=content/{d}/{f}::This post could not be read, so it is left off the site: {ex}' if os.environ.get('GITHUB_ACTIONS') else f'  COULD NOT READ {f}: {ex}')
        self.check_all()
        self.live = sorted([p for p in self.all if p['live']], key=lambda p: p['dt'], reverse=True)
        self.listed = [p for p in self.live if p['listed']]
        self.reviews = [p for p in self.listed if p['type'] == 'review']
        for p in self.all:
            self.relate(p)

    # -- one post
    def read(self, fname, folder='reviews'):
        fm, raw = front(open(os.path.join(ROOT, 'content', folder, fname), encoding='utf-8').read())
        fm = flatten(fm)
        stem = os.path.splitext(fname)[0]
        seo, imgs, links, promo, adv, exp, prod = (obj(fm, k) for k in ('seo', 'images', 'links', 'promo', 'advanced', 'experience', 'product'))
        status = str(fm.get('status') or ('published' if fm.get('published') else 'draft')).lower()
        typ = str(fm.get('type') or FOLDERS[folder]).lower()
        if typ not in KINDS:
            typ = FOLDERS[folder]
        book = str(fm.get('book') or '').strip()
        info = self.books.get(book, {})
        dt = as_datetime(fm.get('date'))
        slug = slugify(seo.get('slug') or fm.get('slug') or stem)
        section = 'reading' if typ == 'review' else 'blog'
        cat = ref_key(fm.get('category')) or ('book-reviews' if typ == 'review' else '')
        author_key = ref_key(fm.get('author')) or 'rebecca'
        a = self.authors.get(author_key) or {'key': author_key, 'name': 'Rebecca', 'url': '/our-story/'}
        try:
            rating = max(0, min(5, int(fm.get('rating') or 0)))
        except (TypeError, ValueError):
            rating = 0
        body = to_html(raw)
        blocks = [b for b in as_list(fm.get('blocks')) if isinstance(b, dict)]
        cover = str(imgs.get('cover') or fm.get('cover') or '').strip()
        p = dict(
            file=fname, folder=folder, stem=stem, fm=fm, type=typ, kind=KINDS[typ], title=str(fm.get('title') or '').strip(), status=status,
            dt=dt, book=book, info=info, series=info.get('series', ''), book_author=info.get('author') or str(fm.get('book_author') or ''),
            cat=cat, cat_name=(self.cats.get(cat) or {}).get('name') or cat.replace('-', ' ').capitalize(),
            tags=[str(t) for t in as_list(fm.get('tags'))], author=a, rating=rating, spoilers=bool(fm.get('spoilers')),
            excerpt_raw=str(fm.get('excerpt') or '').strip(), raw=raw, body_main=body, blocks=blocks,
            exp=exp, seo=seo, imgs=imgs, links=links, promo=promo, adv=adv, cover=cover, prod=prod,
            relationship=str(fm.get('relationship') or 'none'), brand_partner=str(fm.get('brand_partner') or '').strip(),
            items=[ref_key(x) for x in as_list(prod.get('items'))], alternatives=[ref_key(x) for x in as_list(prod.get('alternatives'))],
            used_partners={}, used_products=[], offer_problems=[],
            featured=str(imgs.get('featured') or '').strip(), slug=slug, section=section,
            path=f'/{section}/{slug}/', errors=[], warnings=[], notes=[], checks=[])
        p['url'] = SITE + p['path']
        p['preview'] = f'/preview/{slugify(stem)}/'
        p['canonical'] = str(adv.get('canonical') or '').strip() or p['url']
        upd = as_datetime(adv.get('updated') or fm.get('updated'))
        p['updated_dt'] = upd if upd and dt and upd > dt else dt
        # the legacy keys the rest of the site reads
        if dt:
            p['date'], p['nice'] = dt.date().isoformat(), nice(dt)
            p['updated'] = p['updated_dt'].date().isoformat()
        else:
            p['date'] = p['nice'] = p['updated'] = ''
        p['blocks_html'] = ''.join(self.block(b, p) for b in blocks)
        top, bottom = self.product_section(p)
        p['body'] = top + p['body_main'] + p['blocks_html'] + bottom + self.alternatives_html(p)
        p['text'] = plain(p['body'])
        p['words'] = len(p['text'].split())
        p['minutes'] = max(1, math.ceil(p['words'] / 230))
        p['excerpt'] = p['excerpt_raw'] or short(plain(p['body_main']) or p['text'], 200)
        p['affiliate_partners'] = [x for x in p['used_partners'].values() if x.get('affiliate', True)]
        p['affiliate'] = bool(links.get('affiliate')) or bool(p['affiliate_partners']) or any(b.get('_block') == 'product' and b.get('affiliate') for b in blocks) or p['relationship'] == 'affiliate'
        p['ad'] = p['relationship'] in ('gifted', 'sponsored') or (p['type'] in ('product_review', 'roundup') and p['affiliate'])
        p['image'] = p['featured'] or p['cover']
        p['old'] = [a for a in {f'/{section}/{slugify(stem)}/'} | {self.norm_path(x) for x in as_list(adv.get('old_addresses'))} if a and a != p['path']]
        return p

    @staticmethod
    def norm_path(x):
        x = str(x).strip()
        x = re.sub(r'^https?://[^/]+', '', x)
        if not x:
            return ''
        x = '/' + x.strip('/') + '/'
        return x

    # -- content blocks
    def block(self, b, p):
        kind = b.get('_block')
        if kind == 'text':
            return to_html(b.get('text'))
        if kind == 'book_card':
            h = self.book_card(str(b.get('book') or ''), b.get('note'))
            if h and b.get('url'):
                h = h.replace('<!--bookcard-link-->', '<!--bookcard-link-->' + self.offers_html(p, [{'partner': b.get('partner'), 'url': b.get('url'), 'status': 'active'}], b.get('book')))
            return h
        if kind == 'product_card':
            return self.product_card(p, ref_key(b.get('product')), b.get('badge'), to_html(str(b.get('note') or '')))
        if kind == 'spoiler':
            inner = to_html(b.get('text'))
            return f'<details class="spoiler"><summary>{e(b.get("label") or "Spoiler: tap to read")}</summary><div>{inner}</div></details>' if inner else ''
        if kind == 'quote':
            t = str(b.get('text') or '').strip()
            if not t:
                return ''
            src = f'<cite>{e(b.get("source"))}</cite>' if b.get('source') else ''
            cls = 'highlight' if b.get('style') == 'highlight' else 'pull'
            lab = '<span class="label">My highlight</span>' if cls == 'highlight' else ''
            return f'<figure class="pq {cls}">{lab}<blockquote>{e(t)}</blockquote>{src}</figure>'
        if kind == 'image':
            s = str(b.get('src') or '').strip()
            if not s:
                return ''
            cap = ' '.join(x for x in [e(b.get('caption')), f'<span class="credit">{e(b.get("credit"))}</span>' if b.get('credit') else ''] if x)
            return f'<figure class="pic"><img src="{e(s)}" alt="{e(b.get("alt"))}" loading="lazy">' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'
        if kind == 'table':
            head = [c.strip() for c in str(b.get('header') or '').split('|')]
            rows = [[c.strip() for c in str(r).split('|')] for r in as_list(b.get('rows'))]
            if not rows:
                return ''
            th = ''.join(f'<th scope="col">{e(c)}</th>' for c in head) if any(head) else ''
            tb = ''.join('<tr>' + ''.join(f'<th scope="row">{e(c)}</th>' if i == 0 and th else f'<td>{e(c)}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows)
            cap = f'<caption>{e(b.get("caption"))}</caption>' if b.get('caption') else ''
            return f'<div class="tablewrap"><table>{cap}' + (f'<thead><tr>{th}</tr></thead>' if th else '') + f'<tbody>{tb}</tbody></table></div>'
        if kind == 'faq':
            items = [i for i in as_list(b.get('items')) if isinstance(i, dict) and i.get('q')]
            if not items:
                return ''
            return '<div class="faq"><h2>Questions</h2>' + ''.join(f'<details><summary>{e(i["q"])}</summary><div>{to_html(str(i.get("a") or ""))}</div></details>' for i in items) + '</div>'
        if kind == 'related':
            return f'<div class="relcard" data-related="{e(b.get("post"))}" data-note="{e(b.get("note"))}"></div>' if b.get('post') else ''
        if kind == 'product':
            if not b.get('name'):
                return ''
            if b.get('affiliate'):
                p['used_partners'].setdefault('_oneoff', {'key': '_oneoff', 'name': 'a shop', 'affiliate': True})
            rel = 'sponsored nofollow noopener' if b.get('affiliate') else 'noopener'
            pic = f'<img src="{e(b.get("image"))}" alt="" loading="lazy">' if b.get('image') else ''
            link = f'<a class="btn btn-secondary" href="{e(b.get("url"))}" rel="{rel}" target="_blank">Have a look</a>' if b.get('url') else ''
            tag = '<span class="caption">Ad · affiliate link</span>' if b.get('affiliate') else ''
            return f'<aside class="product">{pic}<div><span class="label">My pick</span><h3>{e(b["name"])}</h3>{to_html(str(b.get("note") or ""))}{link} {tag}</div></aside>'
        return ''

    def offers_html(self, p, offers, product_name=''):
        """Shop buttons for a product: affiliate ones marked sponsored, with each programme's own statement."""
        rows, statements, any_aff = [], [], False
        for o in offers:
            if not isinstance(o, dict) or not o.get('url'):
                continue
            pk = ref_key(o.get('partner'))
            part = self.partners.get(pk)
            url = str(o['url']).strip()
            if not part:
                p['offer_problems'].append(('error', f'{product_name or "a product"}: the shop "{pk or "?"}" isn\'t in Shops'))
                continue
            if not re.match(r'^https://[^\s/]+\.[^\s]+$', url):
                p['offer_problems'].append(('error', f'{product_name}: the {part["name"]} link isn\'t a full https:// web address'))
                continue
            host = re.sub(r'^https://(www\.)?', '', url).split('/')[0].lower()
            doms = [str(d).lower().replace('www.', '') for d in as_list(part.get('domains'))]
            if doms and not any(host == d or host.endswith('.' + d) for d in doms):
                p['offer_problems'].append(('warn', f'{product_name}: the {part["name"]} link goes to {host}, not {", ".join(doms)}'))
            if part.get('status') == 'ended' or o.get('status') in ('ended', 'paused'):
                p['offer_problems'].append(('warn', f'{product_name}: the {part["name"]} link is {"ended" if part.get("status") == "ended" else o.get("status")}, so it is hidden'))
                continue
            aff = bool(part.get('affiliate', True)) and not p.get('_own')
            p['used_partners'][part['key']] = dict(part, affiliate=aff) if aff else p['used_partners'].get(part['key'], dict(part, affiliate=False))
            any_aff |= aff
            if aff and part.get('disclosure') and part['disclosure'] not in statements:
                statements.append(str(part['disclosure']).strip())
            rel = 'sponsored nofollow noopener' if aff else 'noopener'
            rows.append(f'<li><span><b>{e(part["name"])}</b><span class="caption">{"Affiliate retailer" if aff else "Retailer"}</span></span>'
                        f'<a class="btn btn-secondary" href="{e(url)}" rel="{rel}" target="_blank" data-offer="{e(part["key"])}" data-product="{e(product_name)}" data-aff="{int(aff)}">{e(part.get("button") or "View offer")}</a></li>')
        if not rows:
            return ''
        note = ('<p class="caption adnote"><b>Ad</b> · The shop links below are affiliate links. Mazo Moon may earn a commission from qualifying purchases, at no extra cost to you.'
                + ''.join(f' {e(x)}' for x in statements) + '</p>') if any_aff else ''
        return f'<div class="offers">{note}<ul>{"".join(rows)}</ul></div>'

    def product_card(self, p, key, badge='', note_html=''):
        pr = self.products.get(key)
        if not pr:
            if key:
                p['offer_problems'].append(('error', f'the product "{key}" isn\'t in the Product Library'))
            return ''
        p['used_products'].append(key)
        p['_own'] = bool(pr.get('own_product'))
        offers = self.offers_html(p, as_list(pr.get('offers')), pr.get('name'))
        p['_own'] = False
        tested = {'used': 'I use this myself', 'not_yet': "I haven't tried this one yet", 'not_used': "I haven't used this myself"}.get(str(pr.get('tested') or ''), '')
        pic = f'<img src="{e(pr["image"])}" alt="{e(pr.get("image_alt"))}" loading="lazy">' if pr.get('image') else ''
        feats = ''.join(f'<li>{e(f)}</li>' for f in as_list(pr.get('features')))
        return (f'<aside class="product pcard" id="product-{e(key)}">{pic}<div>' + (f'<span class="badge">{e(badge)}</span>' if badge else '<span class="label">Product</span>')
                + f'<h3>{e(pr["name"])}</h3>' + (f'<p class="small muted">{e(pr.get("brand"))}</p>' if pr.get('brand') else '')
                + (f'<p class="small">{e(pr.get("description"))}</p>' if pr.get('description') else '')
                + (f'<ul class="feats">{feats}</ul>' if feats else '') + (f'<p class="caption">{tested}</p>' if tested else '')
                + (note_html or '') + offers + '</div></aside>')

    def product_section(self, p):
        """The box at the top of a product review or roundup: what I tested, pros and cons, verdict, and the product cards."""
        if p['type'] not in ('product_review', 'roundup'):
            return '', ''
        pr = p['prod']
        out = ''
        how = {'used': 'I used this myself', 'not_yet': "I haven't used this yet; this is based on the details and other people's reviews",
               'not_used': "I haven't used this myself; it's a recommendation"}.get(str(pr.get('tested') or ''))
        if how or pr.get('testing'):
            out += f'<p class="tested"><b>How I tested it:</b> {e(how or "")}{". " + e(pr["testing"]) if pr.get("testing") else ""}</p>'
        if p['type'] == 'roundup' and pr.get('criteria'):
            out += f'<div class="criteria"><h2>How I chose</h2>{to_html(str(pr["criteria"]))}</div>'
        in_blocks = {ref_key(b.get('product')) for b in p['blocks'] if b.get('_block') == 'product_card'}
        out += ''.join(self.product_card(p, k) for k in p['items'] if k not in in_blocks)
        top, out = out, ''
        pros, cons = as_list(pr.get('pros')), as_list(pr.get('cons'))
        if pros or cons:
            out += ('<div class="proscons">' + (f'<div><h3>What\'s good</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in pros)}</ul></div>' if pros else '')
                    + (f'<div><h3>Not so good</h3><ul>{"".join(f"<li>{e(x)}</li>" for x in cons)}</ul></div>' if cons else '') + '</div>')
        if pr.get('who_for'):
            out += f'<p><b>Who it suits:</b> {e(pr["who_for"])}</p>'
        if pr.get('verdict'):
            out += f'<div class="verdict"><span class="label">My verdict</span>{to_html(str(pr["verdict"]))}' + (f'<p>{stars_html(p["rating"])}</p>' if p['rating'] else '') + '</div>'
        return top, out

    def alternatives_html(self, p):
        alts = [k for k in p['alternatives'] if k in self.products]
        return ('<section class="alts"><h2>Alternatives worth a look</h2>' + ''.join(self.product_card(p, k) for k in alts) + '</section>') if alts else ''

    def book_card(self, title, note=''):
        info = self.books.get(title)
        if not title:
            return ''
        rev = None  # linked after all posts are read (see link_cards)
        ser = f'Book {info["pos"]} of {info["total"]} in {e(info["series_name"])}' if info and info['total'] > 1 else ''
        return (f'<aside class="bookcard" data-book="{e(title)}"><div><span class="label">On my shelf</span><h3>{e(title)}</h3>'
                f'<p class="small muted">{e(info["author"]) if info else ""}{" · " + ser if ser else ""}</p>'
                + (f'<p class="small">{e(note)}</p>' if note else '') + '<!--bookcard-link--></div></aside>')

    # -- checks before publishing
    def check_all(self):
        by_slug = {}
        for p in self.all:
            by_slug.setdefault(p['path'], []).append(p)
        for p in self.all:
            self.check(p, by_slug)
        # second pass: duplicates and status, now every post's own problems are known
        for p in self.all:
            p['due'] = bool(p['dt'] and p['dt'] <= self.now)
            ok = not p['errors']
            p['live'] = ok and p['status'] in ('published', 'scheduled', 'archived') and (p['due'] or p['status'] == 'archived')
            p['listed'] = p['live'] and p['status'] != 'archived'
            p['indexable'] = p['listed'] and not p['adv'].get('noindex') and p['canonical'] == p['url']

    def add(self, p, group, label, state, note=''):
        p['checks'].append((group, label, state, note))
        if state == 'error':
            p['errors'].append(f'{label}: {note}' if note else label)
        elif state == 'warn':
            p['warnings'].append(f'{label}: {note}' if note else label)

    def check(self, p, by_slug):
        add = lambda *a: self.add(p, *a)
        C, S, M, P = 'Content', 'Search and Google', 'Pictures', 'Publishing'
        # Content
        if not p['title']:
            add(C, 'Headline', 'error', 'add a headline')
        elif not p['words']:
            add(C, 'Headline and writing', 'error', 'the post has no writing yet')
        else:
            add(C, 'Headline and writing', 'ok', f'{p["words"]} words, about {p["minutes"]} min read')
        if p['type'] == 'review':
            if not p['book']:
                add(C, 'Book picked', 'error', 'reviews need a book from the shelf')
            elif not p['info']:
                add(C, 'Book picked', 'error', f'"{p["book"]}" isn\'t on the shelf any more')
            else:
                add(C, 'Book picked', 'ok', f'{p["book"]} by {p["book_author"]}' + (f', book {p["info"]["pos"]} of {p["info"]["total"]} in {p["info"]["series_name"]}' if p['info']['total'] > 1 else ''))
            add(C, 'Star rating', 'ok' if p['rating'] else 'warn', f'{p["rating"]} out of 5' if p['rating'] else 'no stars yet')
        if p['type'] in ('product_review', 'roundup'):
            A = 'Products and affiliate links'
            n = len(set(p['items']) | {ref_key(b.get('product')) for b in p['blocks'] if b.get('_block') == 'product_card'} - {''})
            if p['type'] == 'product_review':
                add(A, 'Product picked', 'ok' if p['items'] else 'error', ', '.join((self.products.get(k) or {}).get('name', k) for k in p['items']) or 'pick the product you are reviewing')
            else:
                add(A, 'Products in the roundup', 'ok' if n >= 2 else 'warn', f'{n} product{"s" if n != 1 else ""}' + ('' if n >= 2 else ', a roundup usually has a few'))
                add(A, 'How I chose', 'ok' if p['prod'].get('criteria') else 'warn', '' if p['prod'].get('criteria') else 'say what you looked for; Google rewards clear selection reasons')
            t_ = str(p['prod'].get('tested') or '')
            add(A, 'Whether you used it', 'ok' if t_ else 'error', {'used': 'used it myself', 'not_yet': 'not yet', 'not_used': 'recommendation only'}.get(t_, 'say whether you used it, so nothing claims testing you did not do'))
            if t_ == 'used':
                add(A, 'How I tested it', 'ok' if p['prod'].get('testing') else 'warn', '' if p['prod'].get('testing') else 'a line on how and how long you used it')
            if p['type'] == 'product_review':
                add(A, 'Pros, cons and verdict', 'ok' if (p['prod'].get('pros') and p['prod'].get('cons') and p['prod'].get('verdict')) else 'warn',
                    ', '.join(x for x, k in (('pros', 'pros'), ('cons', 'cons'), ('verdict', 'verdict')) if not p['prod'].get(k)) and 'missing: ' + ', '.join(x for x, k in (('pros', 'pros'), ('cons', 'cons'), ('verdict', 'verdict')) if not p['prod'].get(k)))
                if p['rating'] and t_ != 'used':
                    add(A, 'Star rating', 'error', "stars are only for things you have used yourself")
        if p['offer_problems'] or p['used_products']:
            A = 'Products and affiliate links'
            for st, msg in p['offer_problems']:
                add(A, 'Shop links', st, msg)
            for k in dict.fromkeys(p['used_products']):
                pr = self.products[k]
                if not pr.get('image'):
                    add(A, 'Product photo', 'note', f'{pr["name"]} has no photo (use your own or one you have permission for)')
                elif not pr.get('image_rights'):
                    add(A, 'Product photo', 'warn', f'record where the {pr["name"]} photo comes from')
            if not p['offer_problems']:
                add(A, 'Shop links', 'ok', 'all links are full addresses on the right shop, marked sponsored where they earn commission')
        if p['relationship'] in ('gifted', 'sponsored') and not p['brand_partner']:
            add('Products and affiliate links', 'Who gifted or paid', 'error', 'name the brand, so the Ad label can say who')
        if p['affiliate'] or p['ad']:
            names = [x['name'] for x in p['affiliate_partners'] if x.get('disclosure')]
            add('Products and affiliate links', 'Advertising labels', 'ok', ('"Ad" label at the top, on cards and next to links' if p['ad'] else 'disclosure at the top and next to each affiliate link')
                + (f'; includes the statement {" and ".join(names)} {"requires" if len(names) == 1 else "require"}' if names else ''))
        if not p['cat']:
            add(C, 'Category', 'error', 'pick a category')
        elif p['cat'] not in self.cats:
            add(C, 'Category', 'warn', f'"{p["cat"]}" isn\'t in Categories')
        else:
            add(C, 'Category', 'ok', p['cat_name'])
        fm_author = ref_key(p['fm'].get('author'))
        add(C, 'Writer', 'ok' if (not fm_author or fm_author in self.authors) else 'warn', p['author'].get('name', ''))
        add(C, 'Short summary', 'ok' if p['excerpt_raw'] else 'warn', 'written' if p['excerpt_raw'] else 'none yet, so the first lines are used')
        has_spoiler_block = any(b.get('_block') == 'spoiler' for b in p['blocks'])
        if p['spoilers'] or has_spoiler_block:
            add(C, 'Spoilers marked', 'ok', ' and '.join(x for x in ['heads-up shown at the top' if p['spoilers'] else '', 'spoiler blocks hidden until tapped' if has_spoiler_block else ''] if x))
        empty = [b.get('_block', '?') for b in p['blocks'] if not self.block(b, p)]
        heads = re.findall(r'<(h[23])[^>]*>(.*?)</\1>\s*(?=<h[23]|$)', p['body_main'].strip(), re.S)
        if empty or heads:
            add(C, 'No empty blocks or headings', 'warn', ', '.join([f'empty {x.replace("_", " ")} block' for x in empty] + [f'nothing under "{plain(h)}"' for _, h in heads]))
        else:
            add(C, 'No empty blocks or headings', 'ok')
        # Search
        first = lambda o: (o['status'] not in ('published', 'archived'), o['dt'] or self.now, o['file'])
        others = [o for o in by_slug.get(p['path'], []) if o is not p and first(o) < first(p)]  # the earlier post keeps the address
        if others:
            add(S, 'Web address is unique', 'error', f'{p["path"]} is also used by {", ".join(o["file"] for o in others)}')
        elif p['path'] in STATIC_PATHS or p['slug'] in ('feed-xml', 'topics', 'index'):
            add(S, 'Web address is unique', 'error', f'{p["path"]} is already a page on the site')
        else:
            add(S, 'Web address is unique', 'ok', p['path'])
        twin = [o for o in self.all if o is not p and o['stem'] == p['stem'] and (o['folder'], o['file']) < (p['folder'], p['file'])]
        if twin:
            add(S, 'File name is unique', 'error', f'another post is also called {p["file"]} (in {twin[0]["folder"]}); rename one')
        t, d = self.seo_title(p), self.seo_desc(p)
        add(S, 'Search title', 'ok' if len(t) <= 65 else 'warn', f'{len(t)} characters' + ('' if len(t) <= 65 else ', Google may shorten it'))
        add(S, 'Search description', 'ok' if 70 <= len(d) <= 170 else 'warn', f'{len(d)} characters' + ('' if 70 <= len(d) <= 170 else ' (around 120 to 155 reads best)'))
        dup = []
        for o in self.all:
            if o is p or o['status'] == 'archived' or not o['title']:
                continue
            if self.seo_title(o).lower() == t.lower():
                dup.append(f'same search title as "{o["title"]}"')
            kw, okw = str(p['seo'].get('keyword') or '').strip().lower(), str(o['seo'].get('keyword') or '').strip().lower()
            if kw and kw == okw:
                dup.append(f'same main search phrase as "{o["title"]}"')
            if p['type'] == o['type'] == 'review' and p['book'] and p['book'] == o['book']:
                dup.append(f'"{o["title"]}" already reviews {p["book"]}')
            elif similar(p['title'], o['title']) >= .75:
                dup.append(f'very like "{o["title"]}"')
        add(S, 'Not doubling up another post', 'warn' if dup else 'ok', '; '.join(dup))
        if p['adv'].get('noindex'):
            add(S, 'Google and canonical', 'warn', 'set to stay out of Google (Advanced)')
        elif p['canonical'] != p['url']:
            add(S, 'Google and canonical', 'warn', f'canonical points to {p["canonical"]}')
        else:
            add(S, 'Google and canonical', 'ok', 'indexable, canonical is its own address')
        internal = [h for h in re.findall(r'href="([^"]+)"', p['body']) if h.startswith('/') or h.startswith(SITE)]
        add(S, 'Links to other pages on the site', 'ok' if internal or 'data-related' in p['body'] or 'class="bookcard"' in p['body'] else 'warn',
            f'{len(internal)} in the writing' if internal else 'none in the writing yet; related posts are added at the bottom for you')
        add(S, 'Structured data for Google', 'ok' if p['title'] and (p['type'] != 'review' or p['info']) else 'warn',
            ('Review of a Book' if p['type'] == 'review' else 'BlogPosting') + ', author, dates and breadcrumbs')
        # Pictures
        if p['featured']:
            add(M, 'Featured photo', 'ok')
            size = image_size(p['featured'])
            if size:
                add(M, 'Photo is big enough to share', 'ok' if size[0] >= 1200 else 'warn', f'{size[0]} x {size[1]} pixels' + ('' if size[0] >= 1200 else ', aim for 1200 wide or more'))
            add(M, 'Alt text', 'ok' if p['imgs'].get('alt') else 'warn', '' if p['imgs'].get('alt') else 'describe the featured photo')
            add(M, 'Where the photo comes from', 'ok' if p['imgs'].get('rights') else 'warn', str(p['imgs'].get('rights') or 'not recorded'))
        elif p['type'] == 'review' and (p['cover'] or p['info']):
            add(M, 'Featured photo', 'warn' if not p['cover'] else 'ok', 'using the book cover' if p['cover'] else 'none yet, sharing uses the Mazo Moon picture')
        else:
            add(M, 'Featured photo', 'warn', 'none yet, sharing uses the Mazo Moon picture')
        no_alt = len(re.findall(r'<img(?![^>]*\balt="[^"]+")[^>]*>', p['body']))
        if no_alt:
            add(M, 'Photos in the post have descriptions', 'warn', f'{no_alt} without alt text')
        add(M, 'Pinterest pin', 'ok' if p['imgs'].get('pinterest') else 'note', 'added' if p['imgs'].get('pinterest') else 'optional: a tall 2:3 pin helps on Pinterest')
        # Publishing
        bad = []
        for h in set(re.findall(r'href="([^"#?]+)', p['body'])):
            hp = re.sub(r'^' + re.escape(SITE), '', h)
            if hp.startswith('/') and not self.path_exists(hp):
                bad.append(hp)
        add(P, 'No broken links on the site', 'warn' if bad else 'ok', ', '.join(sorted(bad)))
        st = p['status']
        if not p['dt'] and st in ('published', 'scheduled'):
            add(P, 'Publish date', 'error', 'set a publish date')
        elif st == 'scheduled' and p['dt']:
            add(P, 'Publish date', 'ok', ('goes live ' if p['dt'] > self.now else 'went live ') + p['dt'].astimezone(UK).strftime('%-d %B %Y at %H:%M'))
        elif st == 'published' and p['dt'] and p['dt'] > self.now:
            add(P, 'Publish date', 'warn', 'the date is in the future, so it waits until ' + p['dt'].astimezone(UK).strftime('%-d %B %Y at %H:%M'))
        elif p['dt']:
            add(P, 'Publish date', 'ok', nice(p['dt']))
        add(P, 'Status', 'ok', {'draft': 'Draft: only on the preview link', 'scheduled': 'Scheduled', 'published': 'Published',
                                'archived': 'Archived: page kept, off the lists and out of Google'}.get(st, st))

    def path_exists(self, path):
        path = path if path.endswith('/') or '.' in os.path.basename(path) else path + '/'
        if path in STATIC_PATHS or any(o['path'] == path or path in o['old'] for o in self.all):
            return True
        if path.startswith('/blog/topics/') and path.split('/')[3] in self.cats:
            return True
        f = os.path.join(ROOT, path.lstrip('/'))
        return os.path.isfile(f) or os.path.isfile(os.path.join(f, 'index.html'))

    # -- search and sharing text
    def seo_title(self, p):
        if p['seo'].get('title'):
            return str(p['seo']['title']).strip()
        if p['type'] != 'review' or not p['book']:
            return f'{p["title"]} | Mazo Moon'
        if p['book'].lower() in p['title'].lower():
            return f'{p["title"]}: book review | Mazo Moon'
        return f'{p["title"]}: {p["book"]} review | Mazo Moon'

    def seo_desc(self, p):
        by = f' by {p["book_author"]}' if p['book_author'] else ''
        d = short(str(p['seo'].get('description') or '').strip() or p['excerpt_raw'] or (f'My honest review of {p["book"]}{by}. ' if p['type'] == 'review' and p['book'] else '') + p['text'])
        if len(d) < 70 and p['type'] == 'review' and p['book']:
            d = short(f'{d.rstrip(".")}. My honest review of {p["book"]}{by}.')
        return d

    def social(self, p):
        title = str(p['imgs'].get('social_title') or '').strip() or self.seo_title(p).replace(' | Mazo Moon', '')
        desc = str(p['imgs'].get('social_description') or '').strip() or p['excerpt_raw'] or self.seo_desc(p)
        if p['imgs'].get('social'):
            img = img_url(p['imgs']['social'])
        elif p['featured'] and os.path.isfile(os.path.join(ROOT, 'img', 'social', p['slug'] + '.jpg')):
            img = f'{SITE}/img/social/{p["slug"]}.jpg'
        else:
            img = img_url(p['featured'] or p['cover']) or IMG
        return title, desc, img

    def promo(self, p):
        pr = p['promo']
        exp = p['exp']
        bits = [x for x in [f'Spice {exp["spice"]}/5' if exp.get('spice') not in (None, '') else '', exp.get('romance') or '', exp.get('pacing') and f'{exp["pacing"]} pace'] if x]
        bits += as_list(exp.get('tropes'))[:3]
        tags = ['#' + re.sub(r'[^A-Za-z0-9]', '', t.title()) for t in (as_list(exp.get('tropes'))[:3] + p['tags'][:3])]
        tags = list(dict.fromkeys((['#romantasy', '#bookstagram', '#bookreview'] if p['type'] == 'review' else ['#mazomoon', '#cosyreading']) + tags +
                                  (['#' + re.sub(r'[^A-Za-z0-9]', '', p['book'].title())] if p['book'] else [])))
        about = f'{p["book"]} by {p["book_author"]}' if p['book'] and p['book_author'] else (p['book'] or p['title'])
        stars = f' ({p["rating"]} stars from me)' if p['rating'] else ''
        if p['type'] in ('product_review', 'roundup'):
            pin_t = p['title']
            hook = f'{p["title"]}: the honest version.'
            ig = f'New on the blog: {p["title"]}.\n\n{p["excerpt"]}'
            mail = f'I\'ve put together something new. {p["excerpt"]}'
        elif p['type'] == 'review':
            pin_t = f'{p["book"]} review: is it worth reading?' if p['book'] else p['title']
            hook = (f'This is why {p["book"]} got five stars from me.' if p['rating'] == 5 else f'I just finished {p["book"]} and I need to talk about it.') if p['book'] else p['title']
            ig = f'New on the Reading Corner: my honest thoughts on {about}{stars}.\n\n{p["excerpt"]}'
            mail = f'This week I finally wrote up {about}. {p["excerpt"]}'
        else:
            pin_t, hook = p['title'], f'{p["title"]}. Here\'s what I mean.'
            ig = f'New on the blog: {p["title"]}.\n\n{p["excerpt"]}'
            mail = f'I\'ve written something new for the blog. {p["excerpt"]}'
        if bits:
            ig += '\n\n' + ' · '.join(bits)
        ig += '\n\nThe full post is on mazomoon.com (link in bio).\n\n' + ' '.join(tags[:10])
        if p['ad'] or p['affiliate']:
            ig = ('#ad ' if p['ad'] else '#ad (affiliate links) ') + ig  # the ASA wants this up front on social posts too
            hook = '#ad ' + hook
        utm = lambda s, m: f'{p["url"]}?utm_source={s}&utm_medium={m}&utm_campaign={p["slug"]}'
        return {
            'pin_title': str(pr.get('pin_title') or '').strip() or pin_t[:100],
            'pin_description': str(pr.get('pin_description') or '').strip() or short(f'{p["excerpt"]} ' + (f'Spice, tropes and who I\'d recommend it to. ' if p['type'] == 'review' else '') + 'Read it on the Mazo Moon blog.', 480),
            'pin_url': utm('pinterest', 'social'),
            'instagram': str(pr.get('instagram') or '').strip() or ig,
            'video_hook': str(pr.get('video_hook') or '').strip() or hook,
            'email_subject': str(pr.get('email_subject') or '').strip() or p['title'],
            'email_intro': str(pr.get('email_intro') or '').strip() or mail,
            'email_url': utm('newsletter', 'email'),
            'social_url': utm('instagram', 'social'),
        }

    # -- related reading
    def relate(self, p):
        pool = [o for o in self.listed if o is not p]
        picked = []
        for k in as_list(p['links'].get('posts')):
            picked += [o for o in pool if self.is_post(o, k) and o not in picked]
        trop = set(as_list(p['exp'].get('tropes'))) | set(t.lower() for t in p['tags'])

        def score(o):
            s = 0
            if p['info'] and o['info'] and o['info']['series_name'] == p['info']['series_name']:
                s += 8
            if p['book_author'] and o['book_author'] == p['book_author']:
                s += 5
            s += 2 * len(trop & (set(as_list(o['exp'].get('tropes'))) | set(t.lower() for t in o['tags'])))
            if o['cat'] == p['cat']:
                s += 1
            if p['links'].get('collection') and o['links'].get('collection') == p['links'].get('collection'):
                s += 6
            return s
        rest = sorted([o for o in pool if o not in picked], key=lambda o: (score(o), o['date']), reverse=True)
        p['related'] = (picked + [o for o in rest if score(o) > 0] + [o for o in rest if score(o) == 0])[:3]
        books = [b for b in as_list(p['links'].get('books')) if b in self.books and b != p['book']]
        if p['info']:
            same_author = [b for b, i in self.books.items() if i['author'] == p['book_author'] and i['series_name'] != p['info']['series_name']]
            books += [b for b in same_author if b not in books][:4 - len(books)] if len(books) < 4 else []
        p['related_books'] = list(dict.fromkeys(books))[:4]

    def is_post(self, o, ref):
        """Does a reference (a web address like /reading/glow/, or a file name) point at post o?"""
        ref = str(ref or '').strip()
        return bool(ref) and (o['path'] == self.norm_path(ref) or o['stem'] == ref_key(ref) or ref in o['old'])

    def review_of(self, book):
        return next((o for o in self.reviews if o['book'] == book), None)


def flatten(fm):
    """The editor groups fields into steps (details, publish, and canonical etc. inside seo).
    Lift them back to the top level, so older files with top-level fields read the same."""
    fm = dict(fm)
    for k in ('details', 'publish'):
        if isinstance(fm.get(k), dict):
            for kk, v in fm.pop(k).items():
                if v not in (None, '', []) or kk not in fm:
                    fm[kk] = v
    adv = dict(fm.get('advanced') or {})
    seo = fm.get('seo') if isinstance(fm.get('seo'), dict) else {}
    for kk in ('canonical', 'noindex', 'old_addresses'):
        if seo.get(kk) not in (None, '', []):
            adv[kk] = seo[kk]
    if fm.get('updated') not in (None, ''):
        adv['updated'] = fm['updated']
    fm['advanced'] = adv
    return fm


def similar(a, b):
    wa, wb = set(re.findall(r'[a-z0-9]+', a.lower())) - STOP, set(re.findall(r'[a-z0-9]+', b.lower())) - STOP
    return len(wa & wb) / max(1, len(wa | wb)) if wa and wb else 0


STOP = set('a an the and or of to in on for my i is it this that with review book books best'.split())


# ---------------------------------------------------------------- writing the pages

CSS = '''<style>
.post .crumbs{font-size:13px;color:var(--text-muted);display:flex;flex-wrap:wrap;gap:6px}.post .crumbs a{color:inherit}
.post .postmeta a{color:inherit}
.post .feat{margin:8px 0 32px}.post .feat img{width:100%;aspect-ratio:3/2;object-fit:cover;border-radius:8px}
.post figcaption{font-size:13px;line-height:20px;color:var(--text-muted);margin-top:8px}.post .credit{opacity:.8;margin-left:6px}
.post .disclose{font-size:14px;line-height:22px;color:var(--text-muted);border-left:2px solid var(--accent);padding-left:12px;margin:0 0 24px}
.post .exp{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px 24px;background:var(--surface-raised);border:1px solid var(--hairline);border-radius:8px;padding:18px 20px;margin:0 0 32px;font-size:15px;line-height:22px}
.post .exp h2{grid-column:1/-1;font:500 22px/1.2 var(--display);margin:0}.post .exp dt{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--text-accent)}.post .exp dd{margin:2px 0 0}
.post details.spoiler,.post .faq details{border:1px solid var(--hairline);border-radius:8px;padding:12px 16px;margin:1.2em 0;background:var(--surface-raised)}
.post details summary{cursor:pointer;font-weight:500}.post details[open] summary{margin-bottom:10px}
.post .pq{margin:1.6em 0}.post .pq blockquote{margin:0}.post .pq cite{display:block;font-size:14px;color:var(--text-muted);margin-top:6px;font-style:normal}
.post .pq.highlight{background:var(--surface-raised);border-radius:8px;padding:18px 20px}.post .pq.highlight blockquote{border:0;padding:0}
.post .pic{margin:1.6em 0}.post .pic img{width:100%;border-radius:8px}
.post .tablewrap{overflow-x:auto;margin:1.4em 0}.post table{border-collapse:collapse;width:100%;font-size:15px;line-height:22px}
.post caption{text-align:left;font-weight:500;margin-bottom:8px}.post th,.post td{border-bottom:1px solid var(--hairline);padding:8px 10px;text-align:left;vertical-align:top}.post thead th{color:var(--text-accent);font-size:13px;letter-spacing:.06em}
.post .bookcard,.post .product,.post .relcard a{display:flex;gap:16px;align-items:flex-start;border:1px solid var(--hairline);border-radius:8px;padding:16px 18px;margin:1.4em 0;background:var(--surface-raised);color:inherit;text-decoration:none}
.post .bookcard h3,.post .product h3,.post .relcard h3{font:500 22px/1.2 var(--display);margin:4px 0}.post .bookcard p,.post .product p{margin:4px 0}
.post .product img,.post .bookcard>img{width:96px;border-radius:6px}.post .bookcard>img{aspect-ratio:2/3;object-fit:cover;flex:none}.post .product .btn{margin-top:8px}
.post .seriesnav{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;border-top:1px solid var(--hairline);padding:20px 0;font-size:15px}
.post .seriesnav a{color:var(--text-accent)}
.post .more{border-top:1px solid var(--hairline);padding:28px 0 8px}.post .more h2{font:500 28px/1.2 var(--display);margin:0 0 16px}
.post .more .review-grid{grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px}
.post .sources{font-size:15px}.post .prevnext{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:15px;padding:20px 0}
.post .prevnext a{color:var(--text-accent)}
.post .tags{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 24px;padding:0;list-style:none}.post .tags li{font-size:13px;border:1px solid var(--hairline);border-radius:99px;padding:2px 10px}
.post .catlist{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 32px;padding:0;list-style:none}.post .catlist a{display:block;border:1px solid var(--hairline);border-radius:99px;padding:4px 14px;color:inherit;text-decoration:none;font-size:14px}
.post .catlist a[aria-current]{background:var(--action);color:var(--on-action);border-color:var(--action)}
.post .adbadge{display:inline-block;background:var(--surface-inverse);color:var(--text-on-inverse);border-radius:4px;padding:0 6px;letter-spacing:.08em}
.post .pcard{flex-wrap:wrap}.post .pcard>img{width:140px;aspect-ratio:1;object-fit:cover}.post .pcard>div{flex:1 1 260px}
.post .badge{display:inline-block;font-size:12px;letter-spacing:.1em;text-transform:uppercase;background:var(--surface-feature);color:var(--text-on-feature);border-radius:99px;padding:2px 10px}
.post .feats{margin:6px 0;padding-left:18px;font-size:15px;line-height:22px}
.post .offers ul{list-style:none;margin:10px 0 0;padding:0;display:grid;gap:8px}
.post .offers li{display:flex;justify-content:space-between;align-items:center;gap:12px;border-top:1px solid var(--hairline);padding-top:8px}
.post .offers li>span{display:grid}.post .offers .btn{margin:0;white-space:nowrap}.post .adnote{margin:10px 0 0}
.post .proscons{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px 24px;margin:1.2em 0}.post .proscons h3{margin-top:0}
.post .verdict{border-left:2px solid var(--accent);padding-left:16px;margin:1.6em 0}.post .tested{font-size:16px;background:var(--surface-raised);border-radius:8px;padding:12px 16px}
</style>'''


COMMENT_CSS = '''<style>
.post .comments{border-top:1px solid var(--hairline);padding:28px 0 8px}.post .comments h2{font:500 28px/1.2 var(--display);margin:0 0 6px}
.post .comments form.contact{margin:18px 0 28px;max-width:640px}
.post .rate{border:0;margin:0;padding:0;display:grid;gap:6px}.post .rate legend{font-size:14px;font-weight:500;padding:0;margin-bottom:6px}
.post .rate .opts{display:flex;flex-direction:row-reverse;justify-content:flex-end;gap:2px}
.post .rate input{position:absolute;opacity:0;width:1px;height:1px}
.post .rate label{font-size:30px;line-height:1;cursor:pointer;color:var(--hairline);padding:2px}
.post .rate input:checked~label,.post .rate label:hover,.post .rate label:hover~label{color:var(--text-accent)}
.post .rate input:focus-visible+label{outline:2px solid var(--focus);outline-offset:2px;border-radius:4px}
.post .clist{list-style:none;margin:0;padding:0;display:grid;gap:14px}
.post .clist>li{background:var(--surface-raised);border:1px solid var(--hairline);border-radius:8px;padding:14px 18px}
.post .clist .who{display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline;font-size:14px;color:var(--text-muted)}.post .clist .who b{color:var(--text);font-weight:500;font-size:16px}
.post .clist p{margin:6px 0 0;white-space:pre-line}.post .clist .reply{margin:10px 0 0 14px;padding-left:12px;border-left:2px solid var(--accent)}
.post .cmsg{font-size:15px}.post .visually-hidden{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
</style>'''

COMMENT_JS = '''<script>(function(){var box=document.getElementById('comments');if(!box)return;
var H=box.dataset.host,A=box.dataset.app,P=box.dataset.page,list=box.querySelector('.clist'),none=box.querySelector('.cnone'),f=box.querySelector('form'),msg=box.querySelector('.cmsg');
function esc(t){var d=document.createElement('div');d.textContent=t==null?'':String(t);return d.innerHTML}
function when(t){try{return new Date(t).toLocaleDateString('en-GB',{day:'numeric',month:'long',year:'numeric'})}catch(e){return''}}
function split(c){var m=/^([\u2605\u2606]{5})[^\\n]*\\n+/.exec(c||'');return m?{stars:(m[1].match(/\u2605/g)||[]).length,text:c.slice(m[0].length)}:{stars:0,text:c||''}}
function one(c,isReply){var s=split(c.content),st=s.stars?'<span class="stars" aria-label="'+s.stars+' out of 5">'+'\u2605'.repeat(s.stars)+'\u2606'.repeat(5-s.stars)+'</span>':'';
  var r=(c.replies&&c.replies.data||[]).map(function(x){return one(x,true)}).join('');
  return(isReply?'<div class="reply">':'<li>')+'<div class="who"><b>'+esc(c.moderator||c.moderatorId?'Rebecca':c.by_nickname)+'</b>'+st+'<span>'+when(c.createdAt)+'</span></div><p>'+esc(s.text)+'</p>'+r+(isReply?'</div>':'</li>')}
fetch(H+'/api/open/comments?appId='+encodeURIComponent(A)+'&pageId='+encodeURIComponent(P)+'&page=1').then(function(r){return r.ok?r.json():null}).then(function(j){
  var items=j&&j.data&&j.data.data||[];if(!items.length)return;none.hidden=true;list.innerHTML=items.map(function(c){return one(c,false)}).join('')}).catch(function(){});
f.addEventListener('submit',function(ev){ev.preventDefault();if(f.website.value)return;
  var n=f.nickname.value.trim(),t=f.content.value.trim(),r=f.querySelector('input[name=rating]:checked'),k=r?+r.value:0;
  if(!n||!t){msg.textContent='Please add your name and a comment.';return}
  var c=(k?'\u2605'.repeat(k)+'\u2606'.repeat(5-k)+' ('+k+'/5)\\n\\n':'')+t,btn=f.querySelector('button');btn.disabled=true;msg.textContent='Sending\u2026';
  fetch(H+'/api/open/comments',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({appId:A,pageId:P,pageUrl:location.href,pageTitle:document.title,nickname:n,email:'',content:c})})
  .then(function(r){if(!r.ok)throw 0;f.reset();msg.textContent='Thank you! Your comment will appear here once I\u2019ve read it.'})
  .catch(function(){msg.textContent='Sorry, that didn\u2019t send. Please try again in a minute.'}).then(function(){btn.disabled=false})});
})();</script>'''


def comments_html(p):
    """Name, optional star rating and comment. Shows approved comments only (Rebecca approves them in Cusdis)."""
    if not COMMENTS_APP_ID:
        return ''
    stars = p['type'] in ('review', 'product_review')
    thing = 'the book' if p['type'] == 'review' else 'it'
    rate = ''
    if stars:
        opts = ''.join(f'<input type="radio" name="rating" id="cr{n}" value="{n}"><label for="cr{n}" title="{n} star{"s" if n > 1 else ""}">★<span class="visually-hidden"> {n} out of 5</span></label>' for n in range(5, 0, -1))
        rate = f'<fieldset class="rate"><legend>What did you give {thing}? (optional)</legend><div class="opts">{opts}</div></fieldset>'
    return f'''{COMMENT_CSS}
  <section class="comments" id="comments" data-host="{COMMENTS_HOST}" data-app="{e(COMMENTS_APP_ID)}" data-page="{e(p["path"])}" aria-labelledby="comments-h">
    <h2 id="comments-h">What did you think?</h2>
    <p class="small muted">No account needed. I read every comment before it goes up, so yours will appear once I've seen it.</p>
    <form class="contact" novalidate>
      <p hidden><label>Leave this empty <input name="website" tabindex="-1" autocomplete="off"></label></p>
      <div class="field"><label for="cNick">Your name</label><input id="cNick" name="nickname" autocomplete="given-name" maxlength="60" required></div>
      {rate}
      <div class="field"><label for="cText">Your comment</label><textarea id="cText" name="content" maxlength="3000" required></textarea></div>
      <div><button class="btn btn-primary" type="submit">Post comment</button></div>
      <p class="cmsg" role="status" aria-live="polite"></p>
    </form>
    <ul class="clist"></ul>
    <p class="cnone small muted">No comments yet. Be the first!</p>
  </section>
  {COMMENT_JS}'''


TRACK = '''<script>document.addEventListener('click',function(ev){var a=ev.target.closest&&ev.target.closest('a[data-offer]');if(!a||!window.mmTrack)return;mmTrack('affiliate_click',{retailer:a.dataset.offer,product_name:(a.dataset.product||'').slice(0,100),affiliate:a.dataset.aff==='1',page_path:location.pathname,outbound:true,transport_type:'beacon'})});</script>'''


def card(p):
    img = (p['cover'] or p['featured']) if p['type'] == 'review' else (p['featured'] or p['cover'])  # reviews show the book cover
    return (f'<a class="review-card" href="{p["path"]}">' + (f'<img src="{e(img)}" alt="" loading="lazy">' if img else '')
            + f'<span class="label">{"Ad · " if p["ad"] else ""}{e(p["book"] if p["type"] == "review" else p["cat_name"])}</span><h3 class="strong-s">{e(p["title"])}</h3>'
            + f'<p class="small muted">{p["nice"]} {stars_html(p["rating"])}</p>' + (f'<p class="small">{e(short(p["excerpt"], 160))}</p>' if p['excerpt'] else '') + '</a>')


def link_cards(b, h):
    """Fill in book-card links and related-post cards now every post is known."""
    def bc(m):
        book = html.unescape(m.group(1))
        r = b.review_of(book)
        cover = next((o['cover'] for o in sorted(b.all, key=lambda o: not o['listed']) if o['book'] == book and o['cover']), '')
        out = m.group(0).replace('<aside class="bookcard" data-book="' + m.group(1) + '">',
                                 '<aside class="bookcard" data-book="' + m.group(1) + '">' + (f'<img src="{e(cover)}" alt="Cover of {e(book)}" loading="lazy">' if cover else ''), 1)
        return out.replace('<!--bookcard-link-->', f'<p><a href="{r["path"]}">Read my review</a> {stars_html(r["rating"])}</p>' if r else '<p><a href="/reading/">See it on my bookshelf</a></p>')
    h = re.sub(r'<aside class="bookcard" data-book="([^"]*)">.*?</aside>', bc, h, flags=re.S)

    def rc(m):
        o = next((x for x in b.listed if b.is_post(x, html.unescape(m.group(1)))), None)
        if not o:
            return ''
        note = html.unescape(m.group(2))
        return (f'<div class="relcard"><a href="{o["path"]}"><div><span class="label">You might also like</span><h3>{e(o["title"])}</h3>'
                + f'<p class="small muted">{e(note or short(o["excerpt"], 140))}</p></div></a></div>')
    return re.sub(r'<div class="relcard" data-related="([^"]*)" data-note="([^"]*)"></div>', rc, h)


def experience_html(p):
    x = p['exp']
    rows = [('Romance', x.get('romance')), ('Spice', f'{x["spice"]} out of 5' if x.get('spice') not in (None, '') else ''),
            ('Tone', ', '.join(as_list(x.get('tone')))), ('Pacing', x.get('pacing')),
            ('Tropes', ', '.join(as_list(x.get('tropes')) + as_list(x.get('more_tropes')))), ('Series', x.get('series_status'))]
    rows = [(k, v) for k, v in rows if v]
    if not rows:
        return ''
    return '<dl class="exp"><h2>The reading experience</h2>' + ''.join(f'<div><dt>{k}</dt><dd>{e(v)}</dd></div>' for k, v in rows) + '</dl>'


def article(b, p, prev_next=True):
    a = p['author']
    is_rev = p['type'] == 'review'
    sec_name, sec_path = ('The Reading Corner', '/reading/') if is_rev else ('Blog', '/blog/')
    crumbs = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="{sec_path}">{sec_name}</a>'
              + ('' if is_rev else f' › <a href="/blog/topics/{p["cat"]}/">{e(p["cat_name"])}</a>') + '</nav>')
    bits = [f'<span>By <a href="{e(a.get("url") or "/our-story/")}" rel="author">{e(a.get("name") or "Rebecca")}</a></span>']
    if p['dt']:
        bits.append(f'<time datetime="{p["dt"].isoformat()}">{p["nice"]}</time>')
    if p['updated_dt'] and p['dt'] and p['updated_dt'].date() > p['dt'].date():
        bits.append(f'<span>Updated <time datetime="{p["updated_dt"].isoformat()}">{nice(p["updated_dt"])}</time></span>')
    bits.append(f'<span>{p["minutes"]} min read</span>')
    if p['rating']:
        bits.append(stars_html(p['rating']))
    label = e(p['series'] or ('Book review' if is_rev else p['kind'] if p['type'] in ('product_review', 'roundup') else p['cat_name']))
    about = ''
    if is_rev and p['book']:
        about = f'My review of {e(p["book"])}' + (f' by {e(p["book_author"])}' if p['book_author'] else '')
        if p['info'] and p['info']['total'] > 1:
            about += f', book {p["info"]["pos"]} of {p["info"]["total"]} in {e(p["info"]["series_name"])}'
        about = f'<p class="small muted" style="margin:0">{about}</p>'
    cover = f'<img src="{e(p["cover"])}" alt="Cover of {e(p["book"])}">' if p['cover'] else ''
    feat = ''
    if p['featured']:
        pos = {'top': 'center top', 'bottom': 'center bottom', 'left': 'left center', 'right': 'right center'}.get(p['imgs'].get('focus'), 'center')
        cap = ' '.join(x for x in [e(p['imgs'].get('caption')), f'<span class="credit">{e(p["imgs"].get("credit"))}</span>' if p['imgs'].get('credit') else ''] if x)
        feat = (f'<figure class="feat"><img src="{e(p["featured"])}" alt="{e(p["imgs"].get("alt"))}" style="object-position:{pos}" fetchpriority="high">'
                + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>')
    statements = ' '.join(e(x['disclosure']) for x in p['affiliate_partners'] if x.get('disclosure'))
    if p['relationship'] == 'gifted':
        disclose = f'<p class="disclose"><b>Ad</b> · {e(p["brand_partner"] or "The brand")} gifted me this product. I wasn\'t paid, and what I say is my own honest opinion.'
    elif p['relationship'] == 'sponsored':
        disclose = f'<p class="disclose"><b>Ad</b> · This is a paid partnership with {e(p["brand_partner"] or "the brand")}.'
    elif p['ad']:
        disclose = '<p class="disclose"><b>Ad</b> · This post contains affiliate links. If you buy through them, Mazo Moon may earn a commission at no extra cost to you. My opinions are my own.'
    elif p['affiliate']:
        disclose = '<p class="disclose">Some links in this post are affiliate links, marked "Ad" beside them. If you buy through them, Mazo Moon may earn a commission at no extra cost to you.'
    else:
        disclose = ''
    if disclose:
        disclose += (f' {statements}' if statements else '') + '</p>'
    if p['ad']:
        label = '<span class="adbadge">Ad</span> ' + label
    spoil = '<p class="spoiler-note">Heads up: this review has spoilers.</p>' if p['spoilers'] else ''
    tags = ''.join(f'<li>{e(t)}</li>' for t in p['tags'])
    sources = [s for s in as_list(p['links'].get('sources')) if isinstance(s, dict) and s.get('url')]
    src_html = ('<div class="sources"><h2>Sources</h2><ul>' + ''.join(f'<li><a href="{e(s["url"])}" rel="noopener" target="_blank">{e(s.get("title") or s["url"])}</a></li>' for s in sources) + '</ul></div>') if sources else ''
    snav = ''
    if is_rev and p['info'] and p['info']['total'] > 1:
        bs, i = p['info']['books'], p['info']['pos'] - 1

        def side(t, word):
            r = b.review_of(t)
            return f'{word}: <a href="{r["path"]}">{e(t)}</a>' if r else f'{word}: {e(t)} <span class="muted">(review to come)</span>'
        left = side(bs[i - 1], 'Previous in the series') if i > 0 else ''
        right = side(bs[i + 1], 'Next in the series') if i + 1 < len(bs) else ''
        snav = f'<nav class="seriesnav" aria-label="Series"><span>{left}</span><span>{right}</span></nav>' if left or right else ''
    more = ''
    if p['related']:
        more += f'<section class="more"><h2>You might also like</h2><div class="review-grid">{"".join(card(o) for o in p["related"])}</div></section>'
    if p['related_books']:
        more += '<section class="more"><h2>More books like this on my shelf</h2>' + ''.join(b.book_card(t) for t in p['related_books']) + '</section>'
    pn = ''
    if prev_next and p in b.listed:
        i = b.listed.index(p)
        newer, older = (b.listed[i - 1] if i > 0 else None), (b.listed[i + 1] if i + 1 < len(b.listed) else None)
        pn = ('<nav class="prevnext" aria-label="More posts"><span>' + (f'Older: <a href="{older["path"]}">{e(older["title"])}</a>' if older else '') + '</span><span>'
              + (f'Newer: <a href="{newer["path"]}">{e(newer["title"])}</a>' if newer else '') + '</span></nav>')
    body = link_cards(b, f'''{CSS}
<article class="wrap review post" data-review="1">
  <div class="page-hero rise">
    {crumbs}
    <div class="review-top">
      <div style="display:grid;gap:12px">
        <span class="label">{label}</span>
        <h1 class="d-xl">{e(p["title"])}</h1>
        <p class="postmeta">{" · ".join(bits)}</p>
        {about}
      </div>
      {cover}
    </div>
  </div>
  <div class="review-body">
    {feat}{disclose}{spoil}{experience_html(p) if is_rev else ''}
    {p["body"]}
    {src_html}
    {f'<ul class="tags" aria-label="Topics">{tags}</ul>' if tags else ''}
  </div>
  {comments_html(p)}
  {snav}{more}{pn}
  {TRACK}
  <div class="review-foot sec-tight" style="padding-top:24px">
    <a class="btn btn-secondary" href="{sec_path}">{"See the whole bookshelf" if is_rev else "More from the blog"}</a>
    <a class="btn btn-text" href="/our-story/#contact">Tell me what you thought</a>
  </div>
</article>''')
    return body


def schema(b, p):
    title, desc, img = b.social(p)
    a = p['author']
    person = {'@type': 'Person', 'name': a.get('name') or 'Rebecca', 'url': img_url(a.get('url') or '/our-story/')}
    if as_list(a.get('profiles')):
        person['sameAs'] = as_list(a.get('profiles'))
    pub = {'@type': 'Organization', 'name': 'Mazo Moon', 'url': SITE + '/', 'logo': {'@type': 'ImageObject', 'url': SITE + '/img/favicon.png'}}
    base = {'@context': 'https://schema.org', 'headline': p['title'][:110], 'name': p['title'], 'url': p['url'],
            'mainEntityOfPage': p['url'], 'datePublished': p['dt'].isoformat() if p['dt'] else None,
            'dateModified': (p['updated_dt'] or p['dt']).isoformat() if p['dt'] else None, 'description': b.seo_desc(p),
            'author': person, 'publisher': pub, 'inLanguage': 'en-GB', 'wordCount': p['words']}
    if img != IMG:
        base['image'] = [img]
    if p['tags'] or p['seo'].get('keyword'):
        base['keywords'] = ', '.join([str(p['seo'].get('keyword') or '')] + p['tags']).strip(', ')
    if p['type'] == 'review' and p['book']:
        book = {'@type': 'Book', 'name': p['book']}
        if p['book_author']:
            book['author'] = [{'@type': 'Person', 'name': x.strip()} for x in re.split(r'\s*&\s*|\s+and\s+', p['book_author'])]
        if p['info'] and p['info']['total'] > 1:
            book['isPartOf'] = {'@type': 'BookSeries', 'name': p['info']['series_name']}
            book['position'] = p['info']['pos']
        if p['cover']:
            book['image'] = img_url(p['cover'])
        ld = dict(base, **{'@type': 'Review', 'itemReviewed': book})
        if p['rating']:
            ld['reviewRating'] = {'@type': 'Rating', 'ratingValue': p['rating'], 'bestRating': 5, 'worstRating': 1}
    elif p['type'] == 'product_review' and p['items'] and p['items'][0] in b.products:
        pr = b.products[p['items'][0]]
        item = {'@type': 'Product', 'name': pr['name']}
        if pr.get('brand'):
            item['brand'] = {'@type': 'Brand', 'name': pr['brand']}
        if pr.get('image'):
            item['image'] = img_url(pr['image'])
        if pr.get('description'):
            item['description'] = pr['description']
        ld = dict(base, **{'@type': 'Review', 'itemReviewed': item})
        if p['rating'] and str(p['prod'].get('tested')) == 'used':
            ld['reviewRating'] = {'@type': 'Rating', 'ratingValue': p['rating'], 'bestRating': 5, 'worstRating': 1}
        pros, cons = as_list(p['prod'].get('pros')), as_list(p['prod'].get('cons'))
        if pros:
            ld['positiveNotes'] = {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': x} for i, x in enumerate(pros)]}
        if cons:
            ld['negativeNotes'] = {'@type': 'ItemList', 'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': x} for i, x in enumerate(cons)]}
    else:
        ld = dict(base, **{'@type': 'BlogPosting', 'articleSection': p['cat_name']})
        mentioned = [b.products[k] for k in dict.fromkeys(p['used_products']) if k in b.products]
        if mentioned:
            ld['mentions'] = [{'@type': 'Product', 'name': x['name'], **({'brand': {'@type': 'Brand', 'name': x['brand']}} if x.get('brand') else {})} for x in mentioned]
    ld = {k: v for k, v in ld.items() if v is not None}
    sec = [('The Reading Corner', f'{SITE}/reading/')] if p['type'] == 'review' else [('Blog', f'{SITE}/blog/'), (p['cat_name'], f'{SITE}/blog/topics/{p["cat"]}/')]
    trail = [('Home', SITE + '/')] + sec + [(p['title'], p['url'])]
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(trail)]}
    return [ld, crumbs]


def head_meta(meta, b, p, robots):
    title, desc, img = b.social(p)
    extra = (f'\n<meta name="robots" content="{robots}">'
             + (f'\n<meta property="article:published_time" content="{p["dt"].isoformat()}">' if p['dt'] else '')
             + (f'\n<meta property="article:modified_time" content="{(p["updated_dt"] or p["dt"]).isoformat()}">' if p['dt'] else '')
             + f'\n<meta property="article:author" content="{e(p["author"].get("name") or "Rebecca")}">'
             + f'\n<meta property="article:section" content="{e(p["cat_name"])}">'
             + ''.join(f'\n<meta property="article:tag" content="{e(t)}">' for t in p['tags'][:6])
             + (f'\n<meta name="twitter:image:alt" content="{e(p["imgs"].get("alt"))}">' if p['imgs'].get('alt') else '')
             + f'\n<script type="application/ld+json">{json.dumps(schema(b, p), ensure_ascii=False).replace("</", "<\\/")}</script>')
    out = meta(title, b.seo_desc(p), p['canonical'], img, 'article', extra)
    if title != b.seo_title(p):
        out = out.replace(f'<meta property="og:title" content="{html.escape(b.seo_title(p), quote=True)}">', f'<meta property="og:title" content="{e(title)}">')
    if desc != b.seo_desc(p):
        out = out.replace(f'<meta property="og:description" content="{html.escape(b.seo_desc(p), quote=True)}">', f'<meta property="og:description" content="{e(desc)}">')
    return out


def page(src, show, meta, title, meta_html, inner):
    out = re.sub(r'<!--meta-start-->.*?<!--meta-end-->', lambda m: meta_html, show(src, 'review'), flags=re.S)
    out = re.sub(r'<title>.*?</title><!--title-end-->', lambda m: f'<title>{html.escape(title)}</title><!--title-end-->', out, flags=re.S)
    return out.replace('<!--review-start--><!--review-end-->', f'<!--review-start-->{inner}<!--review-end-->')


def save(path, text):
    f = os.path.join(ROOT, path.strip('/'), 'index.html')
    os.makedirs(os.path.dirname(f), exist_ok=True)
    open(f, 'w', encoding='utf-8').write(text)


def clear_generated():
    """Remove pages this module made last time (marked data-review="1" or data-generated="blog")."""
    for top in ('reading', 'blog', 'preview'):
        d = os.path.join(ROOT, top)
        if not os.path.isdir(d):
            continue
        for dirpath, dirs, files in os.walk(d, topdown=False):
            if dirpath == d and top == 'reading':
                continue  # /reading/index.html is the Reading Corner itself
            if 'index.html' in files:
                fp = os.path.join(dirpath, 'index.html')
                t = open(fp, encoding='utf-8').read()
                if 'data-review="1"' in t or 'data-generated="blog"' in t:
                    os.remove(fp)
            if dirpath != d and not os.listdir(dirpath):
                os.rmdir(dirpath)
        if top != 'reading' and not os.listdir(d):
            os.rmdir(d)


def social_images(b):
    """Cut a 1200 x 630 sharing image from each featured photo (needs Pillow; skipped quietly without it)."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return
    out = os.path.join(ROOT, 'img', 'social')
    for p in b.all:
        f = local_file(p['featured'])
        if not f or p['imgs'].get('social'):
            continue
        os.makedirs(out, exist_ok=True)
        dest = os.path.join(out, p['slug'] + '.jpg')
        if os.path.exists(dest) and os.path.getmtime(dest) >= os.path.getmtime(f):
            continue
        cx, cy = {'top': (.5, 0), 'bottom': (.5, 1), 'left': (0, .5), 'right': (1, .5)}.get(p['imgs'].get('focus'), (.5, .5))
        try:
            with Image.open(f) as im:
                im = ImageOps.exif_transpose(im).convert('RGB')
                ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(cx, cy)).save(dest, 'JPEG', quality=85, optimize=True)
        except Exception as ex:
            print(f'  could not make a sharing image for {p["file"]}: {ex}')


def checklist_html(p):
    icon = {'ok': '✓', 'warn': '!', 'error': '✕', 'note': '·'}
    groups = {}
    for g, label, state, note in p['checks']:
        groups.setdefault(g, []).append((label, state, note))
    out = ''
    for g, items in groups.items():
        out += f'<div class="mmc-g"><h3>{e(g)}</h3><ul>' + ''.join(
            f'<li class="mmc-{s}"><span class="mmc-i" aria-hidden="true">{icon[s]}</span><span><b>{e(label)}</b>{" · " + e(note) if note else ""}</span></li>' for label, s, note in items) + '</ul></div>'
    return out


PANEL_CSS = '''<style>
.mmp{max-width:980px;margin:24px auto 8px;padding:0 20px;font:15px/22px var(--sans);color:var(--text)}
.mmp-box{border:1px solid var(--hairline);border-radius:12px;background:var(--surface-raised);overflow:hidden}
.mmp-top{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center;justify-content:space-between;padding:14px 18px;background:var(--surface-sunken)}
.mmp-top b{font-size:16px}.mmp-badge{display:inline-block;border-radius:99px;padding:2px 10px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;background:var(--surface-inverse);color:var(--text-on-inverse)}
.mmp-tabs{display:flex;flex-wrap:wrap;gap:4px;padding:10px 12px 0;border-bottom:1px solid var(--hairline)}
.mmp-tabs button{font:inherit;font-size:14px;border:0;background:none;padding:8px 12px;border-bottom:2px solid transparent;cursor:pointer;color:var(--text-muted)}
.mmp-tabs button[aria-selected="true"]{color:var(--text);border-bottom-color:var(--accent)}
.mmp-pane{padding:18px}.mmp-pane[hidden]{display:none}
.mmc-g h3{font:500 20px/1.2 var(--display);margin:6px 0 8px}.mmc-g ul{list-style:none;margin:0 0 14px;padding:0;display:grid;gap:6px}
.mmc-g li{display:flex;gap:10px}.mmc-i{flex:none;width:20px;height:20px;border-radius:50%;display:grid;place-items:center;font-size:12px;font-weight:600}
.mmc-ok .mmc-i{background:#dfe7d8;color:#3d5a2e}.mmc-warn .mmc-i{background:#f1e2c4;color:#7a5300}.mmc-error .mmc-i{background:#f2d3d0;color:#8a1f17}.mmc-note .mmc-i{background:var(--surface-sunken)}
.mmc-error{color:#8a1f17}
.mmp-g{font-family:Arial,sans-serif;max-width:600px;margin:0 0 20px}.mmp-g .u{font-size:12px;color:#4d5156}.mmp-g .t{font-size:20px;line-height:26px;color:#1a0dab;margin:4px 0 2px}.mmp-g .d{font-size:14px;line-height:22px;color:#4d5156}
.mmp-g.m{max-width:360px;border:1px solid #dadce0;border-radius:12px;padding:12px 14px;background:#fff}.mmp-g.m .t{font-size:18px;line-height:24px}
.mmp-pv{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}
.mmp-card{border:1px solid #dadce0;border-radius:10px;overflow:hidden;background:#fff;color:#222;max-width:520px;font-family:Arial,sans-serif}
.mmp-card img{width:100%;aspect-ratio:1200/630;object-fit:cover;display:block}.mmp-card div{padding:10px 12px}.mmp-card small{color:#606770;text-transform:uppercase;font-size:12px}
.mmp-card b{display:block;font-size:16px;margin:2px 0}.mmp-card p{margin:0;font-size:14px;color:#606770}
.mmp-pin{width:220px}.mmp-pin img{width:100%;aspect-ratio:2/3;object-fit:cover;border-radius:16px;display:block;background:var(--surface-sunken)}.mmp-pin b{display:block;font-size:14px;margin-top:6px}
.mmp-copy{display:grid;gap:14px}.mmp-copy label{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--text-accent)}
.mmp-copy textarea{width:100%;box-sizing:border-box;font:14px/21px var(--sans);border:1px solid var(--hairline);border-radius:8px;padding:10px;background:var(--surface);color:var(--text);resize:vertical}
.mmp-copy .row{display:flex;justify-content:space-between;align-items:end;gap:8px}.mmp-copy button{font:inherit;font-size:13px;border:1px solid var(--hairline);border-radius:99px;background:var(--surface);padding:3px 12px;cursor:pointer;color:var(--text)}
.mmp-dev{display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start}.mmp-dev iframe{border:1px solid var(--hairline);border-radius:14px;background:#fff}
.mmp-note{font-size:13px;color:var(--text-muted);margin:0 0 12px}
</style>'''


def panel(b, p):
    title, desc, img = b.social(p)
    t, d = b.seo_title(p), b.seo_desc(p)
    pr = b.promo(p)
    n_err, n_warn = len(p['errors']), len(p['warnings'])
    if n_err:
        state = f'{n_err} thing{"s" if n_err > 1 else ""} to fix before this can go live'
    elif p['live']:
        state = 'Live on the site' if p['status'] != 'archived' else 'Archived: the page works but is hidden from lists and Google'
    elif p['status'] in ('published', 'scheduled') and p['dt']:
        state = 'Scheduled for ' + p['dt'].astimezone(UK).strftime('%-d %B %Y at %H:%M')
    else:
        state = 'Draft: ready to publish' + (f' ({n_warn} suggestion{"s" if n_warn > 1 else ""})' if n_warn else '')
    crumb = 'www.mazomoon.com › ' + ' › '.join(x for x in p['path'].strip('/').split('/'))
    tt = lambda s, n: s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + ' ...'
    google = (f'<p class="mmp-note">How it could look in Google. Google sometimes rewrites titles and descriptions, so this is a guide.</p>'
              f'<div class="mmp-pv"><div class="mmp-g"><div class="u">Mazo Moon<br>{e(crumb)}</div><div class="t">{e(tt(t, 60))}</div><div class="d">{e(p["nice"] + " — " if p["nice"] else "")}{e(tt(d, 158))}</div></div>'
              f'<div class="mmp-g m"><div class="u">Mazo Moon · {e(crumb)}</div><div class="t">{e(tt(t, 70))}</div><div class="d">{e(tt(d, 120))}</div></div></div>')
    pin_img = p['imgs'].get('pinterest') or p['featured'] or p['cover']
    share = (f'<div class="mmp-pv"><div><p class="mmp-note">Facebook, WhatsApp, iMessage and X</p><div class="mmp-card"><img src="{e(img)}" alt=""><div><small>mazomoon.com</small><b>{e(title)}</b><p>{e(short(desc, 120))}</p></div></div></div>'
             f'<div><p class="mmp-note">Pinterest</p><div class="mmp-pin">' + (f'<img src="{e(pin_img)}" alt="">' if pin_img else '<img alt="">') + f'<b>{e(pr["pin_title"])}</b></div>'
             + ('' if p['imgs'].get('pinterest') else '<p class="mmp-note">No tall pin yet, so this uses your photo or the cover.</p>') + '</div></div>')

    def box(label, key, rows=3):
        return (f'<div><div class="row"><label for="mm-{key}">{label}</label><button type="button" data-copy="mm-{key}">Copy</button></div>'
                f'<textarea id="mm-{key}" rows="{rows}" readonly>{e(pr[key])}</textarea></div>')
    promo = ('<p class="mmp-note">Written for you from the post. Links carry tracking tags, so you can see in Google Analytics where readers came from.</p><div class="mmp-copy">'
             + box('Pinterest title', 'pin_title', 2) + box('Pinterest description', 'pin_description', 4) + box('Pinterest link', 'pin_url', 2)
             + box('Instagram or Facebook caption', 'instagram', 9) + box('TikTok or Reel opening line', 'video_hook', 2) + box('Link for social posts', 'social_url', 2)
             + box('Newsletter subject line', 'email_subject', 2) + box('Newsletter introduction', 'email_intro', 4) + box('Newsletter link', 'email_url', 2)
             + '</div><p class="mmp-note" style="margin-top:14px">Promotion checklist: pin it to a Pinterest board, share it on Instagram stories and in the next newsletter, and check Google Search Console in a couple of weeks to see how people find it.</p>')
    devices = (f'<p class="mmp-note">The post as it looks on a phone. Scroll inside the frame.</p><div class="mmp-dev">'
               '<iframe src="about:blank" title="Phone preview" width="390" height="760" id="mmPhone"></iframe></div>')
    tabs = [('check', 'Checklist', checklist_html(p)), ('google', 'Google preview', google), ('share', 'Sharing preview', share),
            ('promo', 'Promotion', promo), ('phone', 'Phone view', devices)]
    btns = ''.join(f'<button type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}" data-tab="{k}">{lab}</button>' for i, (k, lab, _) in enumerate(tabs))
    panes = ''.join(f'<div class="mmp-pane" data-pane="{k}"{"" if i == 0 else " hidden"}>{h}</div>' for i, (k, _, h) in enumerate(tabs))
    live_link = f' · <a href="{p["path"]}">Open the live page</a>' if p['live'] else ''
    return (PANEL_CSS + f'<div class="mmp" data-generated="blog"><div class="mmp-box"><div class="mmp-top"><span><span class="mmp-badge">Preview</span> <b>{e(state)}</b></span>'
            f'<span class="small">Only people with this link can see it. Google is told not to show it.{live_link}</span></div>'
            f'<div class="mmp-tabs" role="tablist">{btns}</div>{panes}</div></div>'
            '''<script>
(function(){var r=document.querySelector('.mmp');if(!r)return;
r.querySelectorAll('[data-tab]').forEach(function(b){b.addEventListener('click',function(){r.querySelectorAll('[data-tab]').forEach(function(x){x.setAttribute('aria-selected',x===b)});r.querySelectorAll('[data-pane]').forEach(function(p){p.hidden=p.dataset.pane!==b.dataset.tab});var f=document.getElementById('mmPhone');if(b.dataset.tab==='phone'&&f&&f.src.indexOf('about:')===0){f.src=location.pathname+'?frame=1'}})});
r.querySelectorAll('[data-copy]').forEach(function(b){b.addEventListener('click',function(){var t=document.getElementById(b.dataset.copy);t.select();try{navigator.clipboard.writeText(t.value)}catch(e){document.execCommand('copy')}b.textContent='Copied';setTimeout(function(){b.textContent='Copy'},1500)})});
if(new URLSearchParams(location.search).get('frame')){r.remove()}
})();
</script>''')


def redirect_page(to, title):
    t = html.escape(title)
    return (f'<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>{t}</title><meta name="robots" content="noindex">'
            f'<link rel="canonical" href="{SITE}{to}"><meta http-equiv="refresh" content="0; url={to}"></head>'
            f'<body data-generated="blog"><p>This page has moved to <a href="{to}">{t}</a>.</p><script>location.replace("{to}"+location.search+location.hash)</script></body></html>')


def listing(b, src, show, meta, path, title, h1, lead, posts, current=''):
    cats = sorted([c for c in b.cats.values() if any(p['cat'] == c['key'] for p in b.listed)], key=lambda c: (c.get('order') or 99, c['name']))
    chips = ('<ul class="catlist">' + f'<li><a href="/blog/"{" aria-current=\"page\"" if not current else ""}>Everything</a></li>'
             + ''.join(f'<li><a href="/blog/topics/{c["key"]}/"{" aria-current=\"page\"" if c["key"] == current else ""}>{e(c["name"])}</a></li>' for c in cats) + '</ul>')
    cards = ''.join(card(p) for p in posts) or '<p class="muted">Nothing here yet. New posts are on their way.</p>'
    inner = (f'''{CSS}<div class="wrap review post" data-review="1" data-generated="blog" style="max-width:1120px"><div class="page-hero rise">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/blog/">Blog</a></nav>
<span class="label">The Mazo Moon blog</span><h1 class="d-xl">{e(h1)}</h1><p class="lead">{e(lead)}</p></div>
{chips}<div class="review-grid">{cards}</div>
<p class="small muted" style="margin-top:32px"><a href="/reading/feed.xml">Follow new posts by RSS</a></p></div>''')
    url = SITE + path
    items = [{'@type': 'ListItem', 'position': i + 1, 'url': p['url'], 'name': p['title']} for i, p in enumerate(posts)]
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'url': url, 'description': lead,
          'mainEntity': {'@type': 'ItemList', 'itemListElement': items}}
    extra = f'\n<meta name="robots" content="{"index, follow, max-image-preview:large" if posts else "noindex, follow"}">\n<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script>'
    save(path, page(src, show, meta, title, meta(title, lead, url, IMG, 'website', extra), inner))


def write(b, src, show, meta):
    """Write every blog page. Returns sitemap entries: {url: (lastmod, [image urls])}."""
    clear_generated()
    social_images(b)
    entries = {}
    for p in b.all:
        robots = 'index, follow, max-image-preview:large' if p['indexable'] else 'noindex, follow'
        inner = article(b, p)
        if p['live']:
            save(p['path'], page(src, show, meta, b.seo_title(p), head_meta(meta, b, p, robots), inner))
            for old in p['old']:
                if not any(o['path'] == old for o in b.all if o['live']):
                    f = os.path.join(ROOT, old.strip('/'), 'index.html')
                    os.makedirs(os.path.dirname(f), exist_ok=True)
                    open(f, 'w', encoding='utf-8').write(redirect_page(p['path'], p['title']))
            if p['indexable']:
                entries[p['url']] = (p['updated'], [img_url(x) for x in [p['featured'], p['cover']] if x])
        # a preview of every post, live or not, with the checklist and promotion pack
        if p['title']:
            pv = page(src, show, meta, 'Preview: ' + p['title'], head_meta(meta, b, p, 'noindex, nofollow'), panel(b, p) + inner)
            pv = pv.replace('<!--review-start-->', '<!--review-start--><span data-generated="blog" hidden></span>', 1)
            save(p['preview'], pv)
    # the blog home and category pages
    listing(b, src, show, meta, '/blog/', 'Blog | Mazo Moon', 'Notes from my desk.',
            'Book reviews, reading guides and slow, cosy living from Rebecca at Mazo Moon.', b.listed)
    if b.listed:
        entries[SITE + '/blog/'] = (max(p['updated'] for p in b.listed), [])
    for k, c in b.cats.items():
        ps = [p for p in b.listed if p['cat'] == k]
        if not ps:
            continue
        listing(b, src, show, meta, f'/blog/topics/{k}/', f'{c["name"]} | Mazo Moon blog', c['name'],
                str(c.get('description') or f'Posts about {c["name"].lower()} from Mazo Moon.'), ps, k)
        entries[f'{SITE}/blog/topics/{k}/'] = (max(p['updated'] for p in ps), [])
    write_feed(b)
    data = [{k: p[k] for k in ('slug', 'title', 'book', 'series', 'date', 'nice', 'rating', 'cover', 'excerpt')} | {'author': p['book_author']} for p in b.reviews]
    open(os.path.join(ROOT, 'reviews.json'), 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))
    posts = [{'slug': p['slug'], 'file': p['file'], 'type': p['type'], 'title': p['title'], 'url': p['path'], 'date': p['dt'].isoformat() if p['dt'] else '',
              'updated': p['updated'], 'category': p['cat'], 'book': p['book'], 'rating': p['rating'], 'excerpt': p['excerpt'],
              'image': p['featured'] or p['cover'], 'minutes': p['minutes'], 'tags': p['tags'],
              'experience': {k: v for k, v in p['exp'].items() if v not in (None, '', [])}} for p in b.listed]
    open(os.path.join(ROOT, 'posts.json'), 'w', encoding='utf-8').write(json.dumps(posts, ensure_ascii=False, indent=1))
    for p in b.all:
        if p['errors'] and p['status'] in ('published', 'scheduled'):
            msg = '; '.join(p['errors'])
            print(f'::warning file=content/{p["folder"]}/{p["file"]}::Not published yet: {msg}' if os.environ.get('GITHUB_ACTIONS') else f'  NOT PUBLISHED {p["file"]}: {msg}')
    if b.live:
        print('posts:', ', '.join(p['path'] for p in b.live))
    return entries


def write_feed(b):
    x = lambda t: html.escape(str(t or ''), quote=False)
    items = ''.join(
        f'<item><title>{x(p["title"])}</title><link>{p["url"]}</link><guid isPermaLink="true">{p["url"]}</guid>'
        f'<pubDate>{p["dt"].astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate><category>{x(p["cat_name"])}</category>'
        f'<dc:creator>{x(p["author"].get("name") or "Rebecca")}</dc:creator><description>{x(p["excerpt"] or short(p["text"], 300))}</description></item>\n'
        for p in b.listed[:30])
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:atom="http://www.w3.org/2005/Atom"><channel>\n'
           '<title>Mazo Moon: reviews and blog</title>'
           f'<link>{SITE}/blog/</link><atom:link href="{SITE}/reading/feed.xml" rel="self" type="application/rss+xml"/>'
           '<description>Honest book reviews and notes from Rebecca at Mazo Moon.</description><language>en-gb</language>\n'
           f'{items}</channel></rss>\n')
    os.makedirs(os.path.join(ROOT, 'reading'), exist_ok=True)
    open(os.path.join(ROOT, 'reading', 'feed.xml'), 'w', encoding='utf-8').write(rss)


def static_cards(src, b):
    """Write the review cards into the Reading Corner HTML, so they don't depend on scripts."""
    if not b.reviews:
        return src
    src = src.replace('<div class="wrap sec-tight" id="reviewsWrap" hidden>', '<div class="wrap sec-tight" id="reviewsWrap">', 1)
    return src.replace('<div class="review-grid" id="reviewGrid"></div>', f'<div class="review-grid" id="reviewGrid">{"".join(card(p) for p in b.reviews)}</div>', 1)


# ---------------------------------------------------------------- the checker (used by the "Check this post" button)

def report(b, only=None, live_now=None):
    """Markdown report for the GitHub job summary. Returns (text, number of posts with blocking problems)."""
    posts = [p for p in b.all if not only or p['file'] in only]
    lines, bad = ['# Post check', ''], 0
    for f, msg in b.broken:
        if not only or f in only:
            bad += 1
            lines += [f'## {f}', '', f'**✕ This file could not be read**, so it stays off the site: {msg}', '']
    for p in posts:
        bad += bool(p['errors'])
        head = '✕ Needs fixing' if p['errors'] else ('✓ Ready' if not p['warnings'] else f'✓ Ready, {len(p["warnings"])} suggestion{"s" if len(p["warnings"]) > 1 else ""}')
        lines += [f'## {p["title"] or p["file"]}', '', f'**{head}** · status: {p["status"]} · preview: {SITE}{p["preview"]} · page: {p["url"]}', '']
        if live_now is not None and p['status'] in ('published', 'scheduled') and p['path'] not in live_now and p['dt'] and (b.now - p['dt']).days > 3:
            lines += [f'- ! The publish date is {nice(p["dt"])} but this post isn\'t live yet. If this is its first time going live, set the date to today.', '']
        for g, label, s, note in p['checks']:
            lines.append(f'- {dict(ok="✓", warn="!", error="✕", note="·")[s]} {g}: **{label}**' + (f' · {note}' if note else ''))
        lines.append('')
    return '\n'.join(lines), bad


def check_outside_links(b, only):
    """Try each outside link (shop links included) once. Only clear failures count: shops often refuse robots."""
    import urllib.request, urllib.error
    seen = {}

    def status(u):
        if u not in seen:
            try:
                req = urllib.request.Request(u, method='GET', headers={'User-Agent': 'Mozilla/5.0 (Mazo Moon link check)'})
                with urllib.request.urlopen(req, timeout=10) as r:
                    seen[u] = r.status
            except urllib.error.HTTPError as ex:
                seen[u] = ex.code
            except Exception:
                seen[u] = 0
        return seen[u]
    for p in b.all:
        if only and p['file'] not in only:
            continue
        urls = sorted({h for h in re.findall(r'href="(https?://[^"]+)"', p['body']) if not h.startswith(SITE)})
        bad = [u for u in urls if status(u) in (0, 404, 410)]
        b.add(p, 'Publishing', 'Outside and shop links work', 'warn' if bad else 'ok',
              ('these did not open: ' + ', '.join(bad)) if bad else f'{len(urls)} checked')


def main(argv):
    src = open(os.path.join(ROOT, 'src', 'site.html'), encoding='utf-8').read()
    b = Blog(src)
    only = None
    if '--payload' in argv:
        try:
            payload = json.loads(argv[argv.index('--payload') + 1] or '{}')
            ctx = payload.get('context') or {}
            if ctx.get('type') == 'entry' and ctx.get('path'):
                only = [os.path.basename(ctx['path'])]
        except (ValueError, IndexError):
            pass
    only = only or [a for a in argv[1:] if a.endswith('.md')] or None
    live_now = None
    try:
        import urllib.request
        with urllib.request.urlopen(SITE + '/posts.json', timeout=10) as r:
            live_now = {x['url'] for x in json.load(r)}
    except Exception:
        pass
    if '--links' in argv:
        check_outside_links(b, only)
    text, bad = report(b, only, live_now)
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8').write(text + '\n')
    if '--due' in argv:
        # used by the hourly run: is a scheduled post due that the live site doesn't have yet?
        due = [p for p in b.listed if live_now is not None and p['path'] not in live_now]
        print('due:', ', '.join(p['path'] for p in due) or 'none')
        if os.environ.get('GITHUB_OUTPUT'):
            open(os.environ['GITHUB_OUTPUT'], 'a').write(f'due={"yes" if due or live_now is None else "no"}\n')
        return 0
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
