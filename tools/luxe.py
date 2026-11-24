"""Luxe product pages: the /comic/ design, for any product whose json has a "luxe" block.

tools/sales.py calls page() for those products instead of its own nine-step layout, so the address
(/products/<slug>/), the shop links and the sitemap stay the same. Styles are in products/luxe.css.

The "luxe" block (everything else comes from the normal fields of the json):
  "word":     the giant word across the colour block, e.g. "TRAVEL" (short is best, it shrinks to fit)
  "specs":    two small labels either side above the word, e.g. ["6 × 9 in · Paperback", "106 pp · Cream paper"]
  "strip":    three short facts for the dark strip at the very top
  "benefits": four [icon, "two words"] pairs; icons are the keys of ICONS below
  "gift":     one line under the price (optional)
  "kit":      the heading of the "Complete the set" box (optional); the set is this product plus the first two "related"
  "block", "ink": colours for the colour block and the giant word (optional, default navy and gold)
A second Amazon ASIN in "hardcover" adds a Paperback / Hardcover choice.
Real customer reviews only, in "quotes": [{"title": "...", "text": "...", "stars": 5}].
"""
import html
import json

e = lambda s: html.escape(str(s), quote=True)

_P = '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">{}</svg>'
ICONS = {
    'book': '<path d="M4 5a2 2 0 0 1 2-2h12v16H6a2 2 0 0 0-2 2z"/><path d="M4 19V5"/><path d="M8 7h6"/>',
    'grid': '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 11h18"/><path d="M12 3v8"/><path d="M9 11v10"/>',
    'burst': '<path d="M12 2l2 5 5-2-2 5 5 2-5 2 2 5-5-2-2 5-2-5-5 2 2-5-5-2 5-2-2-5 5 2z"/>',
    'award': '<circle cx="12" cy="9" r="6"/><path d="M9 14.5L7.5 22 12 19.5 16.5 22 15 14.5"/>',
    'passport': '<rect x="5" y="2.5" width="14" height="19" rx="1.5"/><circle cx="12" cy="10" r="3.5"/><path d="M8.5 10h7"/><path d="M12 6.5c1.2 1 1.2 6 0 7"/><path d="M12 6.5c-1.2 1-1.2 6 0 7"/><path d="M9 17h6"/>',
    'dice': '<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><circle cx="8.5" cy="8.5" r=".6"/><circle cx="15.5" cy="15.5" r=".6"/><circle cx="12" cy="12" r=".6"/><circle cx="15.5" cy="8.5" r=".6"/><circle cx="8.5" cy="15.5" r=".6"/>',
    'calendar': '<rect x="3.5" y="5" width="17" height="15.5" rx="1.5"/><path d="M3.5 10h17"/><path d="M8 3v4"/><path d="M16 3v4"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/>',
    'people': '<circle cx="9" cy="8" r="3"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><circle cx="17" cy="9.5" r="2.4"/><path d="M15.5 14.6A4.5 4.5 0 0 1 21 19"/>',
    'swap': '<path d="M4 8h14l-3.5-3.5"/><path d="M20 16H6l3.5 3.5"/>',
    'tree': '<circle cx="12" cy="4.5" r="2"/><circle cx="6" cy="19.5" r="2"/><circle cx="18" cy="19.5" r="2"/><path d="M12 6.5V12M6 17.5V12h12v5.5"/>',
    'chat': '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
    'map': '<path d="M3 6l6-2.5 6 2.5 6-2.5v14.5l-6 2.5-6-2.5-6 2.5z"/><path d="M9 3.5v14.5M15 6v14.5"/>',
    'leaf': '<path d="M5 19c0-8 5-14 15-14 0 10-6 15-14 15"/><path d="M5 19c3-5 6-8 10-10"/>',
    'lock': '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    'person': '<circle cx="12" cy="7.5" r="3.5"/><path d="M5 21a7 7 0 0 1 14 0"/>',
    'spark': '<path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="M12 8l1.4 2.6L16 12l-2.6 1.4L12 16l-1.4-2.6L8 12l2.6-1.4z"/>',
    'pencil': '<path d="M4 20l1-4L16 5l3 3L8 19z"/><path d="M14 7l3 3"/>',
    'moon': '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
    'wave': '<path d="M2 12c2.5-4 4.5-4 7 0s4.5 4 7 0 4.5-4 6 0"/>',
    'drop': '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    'heart': '<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10z"/>',
}
ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14"/><path d="M13 6l6 6-6 6"/></svg>'
GIFT = ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13"/>'
        '<path d="M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C10 3 12 8 12 8s2-5 4.5-5a2.5 2.5 0 0 1 0 5"/></svg>')
TRUST = ('<div class="trust">'
         '<div>' + _P.format('<path d="M3 7h11v9H3z"/><path d="M14 10h4l3 3v3h-7"/><circle cx="7" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/>') + 'Delivered by Amazon</div>'
         '<div>' + _P.format('<path d="M4 12a8 8 0 1 0 2.3-5.7"/><path d="M4 4v4h4"/>') + 'Returns through Amazon</div>'
         '<div>' + _P.format(ICONS['lock']) + 'Secure Amazon checkout</div></div>')

SCRIPT = '''<script>
(function(){
  /* look inside: swap the hero picture */
  var book=document.getElementById('book'),img=document.getElementById('bookImg'),th=document.querySelector('.thumbs');
  if(th)th.addEventListener('click',function(ev){
    var b=ev.target.closest('button');if(!b)return;
    var cover=b===th.querySelector('button')||(+b.dataset.w<+b.dataset.h);  /* portrait pictures (covers) keep the cover shape */
    th.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b);});
    img.src=b.dataset.src;img.alt=b.dataset.alt;img.width=b.dataset.w;img.height=b.dataset.h;
    book.classList.toggle('spread',!cover);
    book.style.animation='none';void book.offsetWidth;book.style.animation='';
  });
  /* flip through: counter and arrows */
  var t=document.getElementById('track'),c=document.getElementById('count');
  if(t){var f=t.children,two=function(n){return(n<10?'0':'')+n;};
    var at=function(){var w=f[0].getBoundingClientRect().width+12;return Math.max(0,Math.min(f.length-1,Math.round(t.scrollLeft/w)));};
    t.addEventListener('scroll',function(){c.textContent=two(at()+1)+' / '+two(f.length);},{passive:true});
    var go=function(d){var i=(at()+d+f.length)%f.length;t.scrollTo({left:f[i].offsetLeft-f[0].offsetLeft,behavior:'smooth'});};
    document.getElementById('prev').onclick=function(){go(-1);};
    document.getElementById('next').onclick=function(){go(1);};}
  /* colours: swap the picture and point every Buy button at that colour */
  var cs=document.querySelector('.colours');
  if(cs)cs.addEventListener('click',function(ev){
    var b=ev.target.closest('button');if(!b)return;
    cs.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b);});
    document.querySelectorAll('[data-buy]').forEach(function(a){a.href=b.dataset.href;});
    document.getElementById('barFmt').textContent=b.dataset.fmt;
    var f=document.querySelector('.buy .fmt');if(f)f.textContent=b.dataset.name+' · '+cs.children.length+' colours';
    img.src=b.dataset.src;img.alt=b.dataset.name+' earplugs';
  });
  /* paperback or hardcover: point every Buy button at the chosen one */
  var fm=document.querySelector('.formats');
  if(fm)fm.addEventListener('click',function(ev){
    var b=ev.target.closest('button');if(!b)return;
    fm.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b);});
    document.querySelectorAll('[data-buy]').forEach(function(a){a.href=b.dataset.href;});
    document.getElementById('barFmt').textContent=b.dataset.fmt;
  });
  /* share */
  document.getElementById('share').addEventListener('click',function(ev){
    ev.preventDefault();
    if(navigator.share)navigator.share({title:document.title,url:location.href}).catch(function(){});
    else if(navigator.clipboard)navigator.clipboard.writeText(location.href);
  });
})();
</script>'''


def _size(src):
    """Width and height of a picture in the repo, for layout without jumps."""
    try:
        from PIL import Image
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with Image.open(root + src) as im:
            return im.size
    except Exception:
        return (1200, 861)


def _ld(x):
    return '<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def page(p, by_slug, url, ld, amz, price, maas_store, css_v):
    L = p['luxe']
    name, where = p['name'], p['slug']
    soon = bool(p.get('soon'))  # not on Amazon yet: every Buy button goes to the 'tell me when it's out' form
    buy = '#notify' if soon else e(amz(p['asin']))
    cover = (p.get('hero') or p['gallery'][0])[0]
    cw, ch = _size(cover)
    spreads = [g for g in p['gallery'] if len(g) > 2 and g[2] == 'spread']
    word = L['word']
    style = ''
    if L.get('block') or L.get('ink'):
        style = f' style="--block:{e(L.get("block", "#1e1c3b"))};--ink:{e(L.get("ink", "#d9b88a"))}' + (f';--block-deep:{e(L["deep"])}' if L.get('deep') else '') + '"'

    def thumb(src, alt, pressed):
        w, h = _size(src)
        return (f'<button type="button" aria-pressed="{pressed}" aria-label="Show: {e(alt)}" data-src="{e(src)}" data-alt="{e(alt)}" '
                f'data-w="{w}" data-h="{h}"><img src="{e(src)}" alt="" loading="lazy"></button>')
    import sales  # noqa: E402  (sales imports this module)
    is_book = p.get('kind') == 'book'
    thumbs = thumb(cover, f'{name} cover', 'true') + ''.join(thumb(g[0], g[1], 'false') for g in spreads[:3])
    if is_book and not spreads:  # no look-inside pages yet: show the back cover as a thumbnail, no flip-through
        thumbs += ''.join(thumb(g[0], g[1], 'false') for g in p['gallery'] if g[0] != cover)
    if not is_book:
        thumbs = ''  # products show a colour choice instead of a look inside

    benefits = ''.join(f'<div>{_P.format(ICONS[i])}{e(t)}</div>' for i, t in L['benefits'])

    figs = ''
    for g in p['gallery']:
        w, h = _size(g[0])
        figs += f'<figure><img src="{e(g[0])}" alt="{e(g[1])}" loading="lazy" width="{w}" height="{h}"><figcaption>{e(g[1])}</figcaption></figure>'
    n = len(p['gallery'])

    made = ''.join(f'<li><b>0{i + 1}</b><span>{e(x[4:] if x.startswith("For ") else x)}</span></li>' for i, x in enumerate(p['for']))
    note = p['proof']['note']
    quote = note[0]
    more = ''.join(f'<p class="note-more">{x}</p>' for x in note[1:])

    reviews = ''
    if p.get('quotes'):  # real customer words only
        cards = ''
        for q in p['quotes']:
            st = int(q.get('stars', 5))
            cards += (f'<figure><p class="stars" role="img" aria-label="{st} out of 5 stars">{"★" * st}</p>'
                      + (f'<h3>{e(q["title"])}</h3>' if q.get('title') else '')
                      + f'<blockquote>“{e(q["text"])}”</blockquote></figure>')
        reviews = f'''
  <section class="wrap reviews" aria-labelledby="revH">
    <h2 class="serif" id="revH">{e(L.get("reviews_h", "What parents say"))}</h2>
    <div class="rev-grid">{cards}</div>
  </section>'''

    kit = ''
    mates = [by_slug[s] for s in p.get('related', []) if s in by_slug and by_slug[s].get('asin') and by_slug[s].get('price') and not by_slug[s].get('soon') and not by_slug[s].get('hub')][:2]
    if len(mates) == 2 and not soon:
        items = [p] + mates
        cart = e(maas_store)  # Amazon's multi-item basket link breaks in the app, so the button opens the storefront
        total = price(sum(x['price'] for x in items))
        tiles = []
        for x in items:
            href = buy if x is p else e(x.get('moved_to') or f'/products/{x["slug"]}/')
            ext = ' target="_blank" rel="noopener" data-where="' + e(where) + ': kit"' if x is p else ''
            img = (x.get('hero') or x['gallery'][0])[0]
            short = x['name'].split(',')[0]
            tiles.append(f'<a href="{href}"{ext}><img src="{e(img)}" alt="" loading="lazy">{e(short)}<small>{price(x["price"])}</small></a>')
        kit = f'''
    <div class="kit">
      <div><p class="label">Complete the set</p><h2 class="serif" id="kitH">{e(L.get("kit", "Make it a set"))}</h2></div>
      <div class="kit-items">{'<span class="plus" aria-hidden="true">+</span>'.join(tiles)}</div>
      <a class="cta" href="{cart}" target="_blank" rel="noopener" data-where="{e(where)}: kit store">Find all three in my Amazon shop<span>{total}</span></a>
    </div>'''

    inside = ''.join(f'<li>{e(x)}</li>' for x in p['inside']['items'])
    specs = ''.join(f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>' for k, v in p['specs'])
    faq = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(p['faq']))
    pr = price(p['price'])
    fmt_label = 'Paperback' if p.get('kind') == 'book' else L.get('fmt', p.get('label', ''))
    formats = ''
    if p.get('hardcover'):  # paperback or hardcover: a two-way choice that changes every Buy link
        fmt_label = 'Paperback or hardcover'
        hc = e(amz(p['hardcover']))
        formats = (f'<div class="formats" role="group" aria-label="Format">'
                   f'<button type="button" aria-pressed="true" data-href="{buy}" data-fmt="Paperback · {pr}">Paperback<small>{pr}</small></button>'
                   f'<button type="button" aria-pressed="false" data-href="{hc}" data-fmt="Hardcover">Hardcover<small>price on Amazon</small></button></div>')
        pr_hero = 'From ' + pr
    else:
        pr_hero = pr
    if p.get('variants') and L.get('colours'):  # one Amazon page per colour: swatches change the picture and every Buy link
        vs = p['variants']
        fmt_label = f'{len(vs)} colours'
        first = next((v for v in vs if v['asin'] == p['asin']), vs[0])
        fmt_label = first['name'] + ' · ' + fmt_label
        btns = ''
        for v in vs:
            img = L['colours'][v['name']]
            w, h = _size(img)
            btns += (f'<button type="button" class="sw" aria-pressed="{"true" if v is first else "false"}" aria-label="{e(v["name"])}" '
                     f'data-href="{e(amz(v["asin"]))}" data-fmt="{e(v["name"])} · {pr}" data-name="{e(v["name"])}" data-src="{e(img)}" data-w="{w}" data-h="{h}" '
                     f'style="--sw:{e(v["colour"])}"></button>')
        formats = f'<div class="colours" role="group" aria-label="{e(p.get("variant_label", "Colour"))}">{btns}</div>'
    bar_fmt = (fmt_label.split(' · ')[0] + ' · ' + pr) if not is_book else 'Paperback · ' + pr
    back, back_label = sales.book_home(p) if is_book else ('/shop/', 'Back to the shop')
    gift = f'<p class="gift">{GIFT}{e(L["gift"])}</p>' if L.get('gift') else ''
    lds = ''.join(_ld(x) for x in ld)
    flip = '' if is_book and not spreads else f'''  <section class="flip" aria-labelledby="flipH">
    <div class="wrap flip-head">
      <h2 class="serif" id="flipH">{'Flip through it' if is_book else 'Take a closer look'}</h2>
      <span class="count" id="count" aria-live="polite">01 / {n:02d}</span>
    </div>
    <div class="track" id="track" tabindex="0" aria-label="Pages from the book, swipe to see more">{figs}</div>
    <div class="wrap flip-nav">
      <button type="button" id="prev" aria-label="Previous pages"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
      <button type="button" id="next" aria-label="Next pages"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
    </div>
  </section>'''

    out = f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(p['title'])}</title>
<meta name="description" content="{e(p['description'])}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="product">
<meta property="og:site_name" content="Mazo Moon">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{e(p['title'])}">
<meta property="og:description" content="{e(p['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://www.mazomoon.com{e(cover)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="pinterest-rich-pin" content="true">
<meta name="theme-color" content="{e(L.get('block', '#1e1c3b'))}">
<link rel="icon" href="/img/favicon.png">
<link rel="apple-touch-icon" href="/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;1,500&family=Jost:wght@400;500;800&display=swap">
<link rel="stylesheet" href="/products/luxe.css?v={css_v}">
<script src="/consent.js" defer></script>
{lds}
</head>
<body{style}>
<a class="skip" href="#main">Skip to content</a>

<div class="strip label" role="note">{''.join(f'<span>{e(x)}</span>' for x in L['strip'])}</div>

<main id="main">
  <div class="hero">
    <div class="stage">
      <div class="bar">
        <a href="{back}" aria-label="{back_label}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></a>
        <a href="/" aria-label="Mazo Moon home" style="width:auto"><span class="wordmark"></span></a>
        <a href="#" id="share" aria-label="Share this page"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15V3"/><path d="M7 8l5-5 5 5"/><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg></a>
      </div>
      <div class="speclabels label"><span>{e(L['specs'][0])}</span><span>{e(L['specs'][1])}</span></div>
      <p class="big" aria-hidden="true" style="--n:{max(len(word), 5)}">{e(word)}</p>
      <div class="show">
        <div class="book{'' if is_book else ' obj'}" id="book"><img id="bookImg" src="{e(cover)}" alt="{e(name)}{' cover' if is_book else ''}" width="{cw}" height="{ch}" fetchpriority="high"></div>
      </div>
    </div>

    <div class="buy">
      <div>
        <h1>{e(name)}</h1>
        <p class="by">{e(L.get("by", "Designed by Rebecca in Yorkshire"))}</p>
      </div>
      <div class="row">
        <div><div class="price">{pr_hero}</div><div class="fmt">{fmt_label}</div></div>
        {f'<div class="thumbs" role="group" aria-label="Look inside">{thumbs}</div>' if thumbs else ''}
      </div>
      {formats}
      {gift}
      <a class="cta" id="heroBuy" data-buy href="{buy}" target="_blank" rel="noopener" data-product="{e(name)}" data-where="{e(where)}: hero">Buy on Amazon{ARROW}</a>
    </div>
  </div>

  <div class="wrap">
    <div class="benefits">{benefits}</div>
  </div>

{flip}

  <section class="wrap made" aria-label="Who it’s for">
    <p class="label">Made for</p>
    <ol>{made}</ol>
  </section>

  <section class="wrap" aria-label="A note from Rebecca">
    <blockquote>“{e(quote)}”</blockquote>
    {more}
    <div class="who"><img src="/img/rebecca-portrait.jpg" alt="Rebecca, founder of Mazo Moon" loading="lazy"><div><b>Rebecca</b><span>Founder of Mazo Moon, Yorkshire</span></div></div>
  </section>
{reviews}
  <section class="wrap inside" aria-labelledby="inH">
    <p class="label" id="inH">{'Everything in the book' if is_book else 'In the box'}</p>
    <ul>{inside}</ul>
    <dl class="specs">{specs}</dl>
  </section>

  <section class="wrap" aria-label="Buying">{kit}
    {TRUST}
  </section>

  <section class="wrap faq" aria-labelledby="faqH">
    <h2 class="serif" id="faqH">Questions</h2>
    {faq}
  </section>

  <section class="close" aria-labelledby="closeH">
    <div class="wrap">
      <h2 id="closeH">{e(p['close']['h'])}.</h2>
      <p>{e(p['close']['p'])}</p>
      <a class="cta light" data-buy href="{buy}" target="_blank" rel="noopener" data-product="{e(name)}" data-where="{e(where)}: close">Buy on Amazon{ARROW}</a>
    </div>
  </section>
</main>

<footer>
  <span class="wordmark" role="img" aria-label="Mazo Moon"></span>
  <nav aria-label="Site"><a href="/">Home</a><a href="/journals/">Journals</a><a href="/colouring/">Colouring books</a><a href="/create/">Create your own</a><a href="/shop/">Shop</a><a href="/products/">All products</a><a href="/our-story/">Our Story &amp; Contact</a><a href="{e(maas_store)}" target="_blank" rel="noopener" data-where="footer">Amazon store</a></nav>
  <nav aria-label="Legal"><a href="/privacy/">Privacy</a><a href="/cookies/">Cookies</a><a href="/cookies/" data-cookie-settings>Cookie settings</a><a href="/terms/">Terms</a></nav>
  <p>© 2026 Mazo Moon Ltd. Registered in England, company no. 16988519. Made in Yorkshire.</p>
</footer>

<div class="buybar" id="buybar">
  <img src="{e(cover)}" alt="">
  <div><b>{e(name)}</b><span id="barFmt">{e(bar_fmt)}</span></div>
  <a data-buy href="{buy}" target="_blank" rel="noopener" data-product="{e(name)}" data-where="{e(where)}: bar">Buy</a>
</div>
{SCRIPT}
</body>
</html>
'''
    if soon:
        import sales
        out = out.replace(f'href="{buy}" target="_blank" rel="noopener"', f'href="{buy}"')
        out = out.replace(f'>Buy on Amazon{ARROW}</a>', f'>Tell me when it’s out{ARROW}</a>')
        out = out.replace('data-where="' + e(where) + ': bar">Buy</a>', 'data-where="' + e(where) + ': bar">Notify me</a>')
        out = out.replace('<section class="close" aria-labelledby="closeH">', '<section class="wrap soon-form">' + sales.NOTIFY + '</section>\n  <section class="close" aria-labelledby="closeH">', 1)
    return out
