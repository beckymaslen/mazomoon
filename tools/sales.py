#!/usr/bin/env python3
"""Product sales pages: mazomoon.com/products/<slug>/ and the list at /products/.

Each product is one file in content/sales/<slug>.json (words, pictures, Amazon links, questions).
The page follows the same nine steps for every product, in this order:

  01 opening      hero: who it's for, one Buy button        "This is for someone like me."
  02 problem      what's hard right now                      "Finally. That explains it."
  03 approach     a gentler way (the rosewood band)          "Maybe there's a better way."
  04 offer        what it is and three key features          "I see how this gets me there."
  05 proof        real pages / photos, a note from Rebecca   "This works for people like me."
  06 inside       everything you get, and the details        "There's real substance here."
  07 decision     price, formats, how buying works           "I know exactly what I'm agreeing to."
  08 faq          honest answers                             "They've thought through my concerns."
  09 close        one line, one button                       "This feels like my next move."

Run by tools/build_pages.py on every build. To add a product, copy a json file, change it and push.
"""
import html
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.mazomoon.com'
MAAS = 'maas=maas_adg_5620BE20E00531051704C67F4D1D438F_afap_abs&ref_=aa_maas&tag=maas'
STORE = 'https://www.amazon.co.uk/stores/MazoMoon/page/298754B3-2DA8-49CE-B163-4EA6E7FEA0E0?' + MAAS
GROUPS = [('journals', 'Journals'), ('colouring', 'Colouring books'), ('stickers', 'Stickers'),
          ('pens', 'Pens'), ('rest', 'Rest and relaxation')]

e = lambda s: html.escape(str(s), quote=True)


def amz(asin, reviews=False):
    return f'https://www.amazon.co.uk/dp/{asin}?{MAAS}' + ('#customerReviews' if reviews else '')


def absu(src):
    return src if src.startswith('http') else SITE + src


def load():
    d = os.path.join(ROOT, 'content', 'sales')
    items = []
    for f in sorted(os.listdir(d)):
        if f.endswith('.json'):
            p = json.load(open(os.path.join(d, f), encoding='utf-8'))
            p.setdefault('slug', f[:-5])
            if p.get('status', 'published') == 'published':
                items.append(p)
    items.sort(key=lambda p: ([g for g, _ in GROUPS].index(p['group']), p.get('order', 50), p['name']))
    return items


def price(p):
    return f'£{p:.2f}'


def buy_button(p, where, label=None, cls='btn btn-primary', asin=None):
    if p.get('soon'):  # not on Amazon yet: the button goes to the "tell me when it's out" sign-up
        return f'<a class="{cls}" href="#notify">Tell me when it’s out</a>'
    label = label or 'Buy on Amazon'
    pr = f' <small>{price(p["price"])}</small>' if p.get('price') else ''
    return (f'<a class="{cls}" href="{e(amz(asin or p["asin"]))}" target="_blank" rel="noopener" '
            f'data-product="{e(p["name"])}" data-where="{e(where)}">{e(label)}{pr}</a>')


# ---------------------------------------------------------------- page chrome

HEADER = '''<a class="skip" href="#main">Skip to the page</a>
<header class="site">
  <div class="wrap bar">
    <a href="/" class="wordmark" aria-label="Mazo Moon home, the desk"><span>Mazo Moon</span></a>
    <button class="menu-btn" id="menuBtn" aria-expanded="false" aria-controls="mainNav">Menu</button>
    <nav class="main" id="mainNav" aria-label="Main">
      <ul>
        <li><a href="/">The desk</a></li>
        <li><a href="/journals/"{j}>Journals &amp; Colouring</a></li>
        <li><a href="/shop/"{s}>Shop Mazo Moon</a></li>
        <li><a href="/reading/">The Reading Corner</a></li>
        <li><a href="/little-things/">Little Things I Love</a></li>
        <li><a href="/our-story/">Our Story &amp; Contact</a></li>
      </ul>
    </nav>
  </div>
</header>'''

FOOTER = f'''<footer class="site">
  <div class="wrap foot">
    <div class="foot-about">
      <span class="wordmark" role="img" aria-label="Mazo Moon"></span>
      <p>Make a little space for you. Journals, colouring and stationery, made by Rebecca in Yorkshire.</p>
      <form class="news" method="POST" action="https://mazomoon.us2.list-manage.com/subscribe/post?u=84d0e303fbeb76a0c2b77b779&amp;id=0c0ea5d4d1&amp;f_id=00b2a0e0f0" target="_blank">
        <p hidden><label>Leave this empty <input name="b_84d0e303fbeb76a0c2b77b779_0c0ea5d4d1" tabindex="-1" value=""></label></p>
        <label for="newsEmail" class="vh">Email address</label>
        <input id="newsEmail" name="EMAIL" type="email" required placeholder="Your email address" autocomplete="email">
        <button class="btn" type="submit">Get the monthly letter</button>
      </form>
      <p class="small dim">I send it through Mailchimp, and every letter has an unsubscribe link. <a href="/privacy/">Privacy notice</a></p>
    </div>
    <div>
      <h4>Explore</h4>
      <ul>
        <li><a href="/products/">All products</a></li>
        <li><a href="/journals/">Journals &amp; Colouring</a></li>
        <li><a href="/shop/">Shop Mazo Moon</a></li>
        <li><a href="/reading/">The Reading Corner</a></li>
        <li><a href="/our-story/">Our Story &amp; Contact</a></li>
      </ul>
    </div>
    <div>
      <h4>Find us</h4>
      <ul>
        <li><a href="{e(STORE)}" target="_blank" rel="noopener" data-where="footer">Mazo Moon on Amazon</a></li>
        <li><a href="https://www.instagram.com/mazomoon/" target="_blank" rel="noopener">Instagram</a></li>
        <li><a href="https://uk.pinterest.com/mazomoon/" target="_blank" rel="noopener">Pinterest</a></li>
        <li><a href="mailto:hello@mazomoon.com">hello@mazomoon.com</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap legal"><span>© 2026 Mazo Moon Ltd. Registered in England, company no. 16988519. Made in Yorkshire.</span><span><a href="/privacy/">Privacy</a> · <a href="/cookies/">Cookies</a> · <a href="/cookies/" data-cookie-settings>Cookie settings</a> · <a href="/terms/">Terms</a></span></div>
</footer>'''

SCRIPT = '''<script>
(function(){
  var b=document.getElementById('menuBtn'),n=document.getElementById('mainNav');
  if(b)b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o);});
  /* gallery: tap a thumbnail to show it big */
  document.querySelectorAll('[data-thumbs]').forEach(function(g){
    var big=document.getElementById(g.getAttribute('data-thumbs'));
    g.addEventListener('click',function(ev){var t=ev.target.closest('button[data-src]');if(!t)return;
      big.src=t.getAttribute('data-src');big.alt=t.getAttribute('data-alt');
      g.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===t);});});
  });
  /* phone buy bar: shows once the main Buy button has scrolled away */
  var bar=document.querySelector('.buybar'),hero=document.querySelector('.hero .btn-primary'),end=document.getElementById('decision');
  if(bar&&hero&&'IntersectionObserver' in window){var seen={h:true,d:false};
    var io=new IntersectionObserver(function(es){es.forEach(function(x){seen[x.target===hero?'h':'d']=x.isIntersecting;});bar.classList.toggle('show',!seen.h&&!seen.d);});
    io.observe(hero);if(end)io.observe(end);}
})();
</script>'''


def head(title, desc, url, img, ld, kind='product'):
    t, d = e(title), e(desc)
    lds = ''.join('\n<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>' for x in ld)
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="{'product' if kind == 'product' else 'website'}">
<meta property="og:site_name" content="Mazo Moon">
<meta property="og:locale" content="en_GB">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{e(img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="pinterest-rich-pin" content="true">
<link rel="icon" href="/img/favicon.png">
<link rel="apple-touch-icon" href="/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Jost:wght@400;500&display=swap">
<link rel="stylesheet" href="/products/sales.css?v={CSS_V}">
<script src="/consent.js" defer></script>{lds}
</head>'''


CSS_V = '1'

NOTIFY = '''<form class="notify" id="notify" method="POST" action="https://mazomoon.us2.list-manage.com/subscribe/post?u=84d0e303fbeb76a0c2b77b779&amp;id=0c0ea5d4d1&amp;f_id=00b2a0e0f0" target="_blank">
          <p class="strong-s">Coming soon to Amazon. I’ll email you the day it’s out.</p>
          <p hidden><label>Leave this empty <input name="b_84d0e303fbeb76a0c2b77b779_0c0ea5d4d1" tabindex="-1" value=""></label></p>
          <label for="notifyEmail" class="vh">Email address</label>
          <input id="notifyEmail" name="EMAIL" type="email" required placeholder="Your email address" autocomplete="email">
          <button class="btn btn-primary" type="submit">Tell me when it’s out</button>
          <p class="caption">This signs you up to my monthly letter through Mailchimp. Every letter has an unsubscribe link. <a href="/privacy/">Privacy notice</a></p>
        </form>'''


# ---------------------------------------------------------------- one product page

def paras(xs):
    return ''.join(f'<p>{x}</p>' for x in xs)  # copy may hold simple <em>/<strong>, written by us


def page(p, by_slug):
    url = f'{SITE}/products/{p["slug"]}/'
    gal = p['gallery']
    hero_img = p.get('hero') or gal[0]
    is_book = p['kind'] == 'book'
    where = p['slug']

    # structured data for Google
    images = [absu(hero_img[0])] + [absu(g[0]) for g in gal if g[0] != hero_img[0]][:5]
    thing = {'@context': 'https://schema.org', '@type': 'Book' if is_book else 'Product', 'name': p['name'],
             'description': p['description'], 'image': images, 'url': url,
             'brand': {'@type': 'Brand', 'name': 'Mazo Moon'}}
    if p.get('asin'):
        thing['sameAs'] = f'https://www.amazon.co.uk/dp/{p["asin"]}'
    if is_book:
        thing.update({'author': {'@type': 'Person', 'name': 'Rebecca Maslen'},
                      'publisher': {'@type': 'Organization', 'name': 'Mazo Moon', 'url': SITE + '/'},
                      'inLanguage': 'en-GB', 'bookFormat': 'https://schema.org/Paperback',
                      'genre': 'Colouring book' if p['group'] == 'colouring' else 'Journal'})
        thing.pop('brand')
        if p.get('pages_count'):
            thing['numberOfPages'] = p['pages_count']
    elif p.get('asin'):
        thing['sku'] = p['asin']
    # no price or star ratings here on purpose: Amazon sets the live price, and Google only allows
    # review stars for reviews collected on this site.
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Mazo Moon', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Products', 'item': SITE + '/products/'},
        {'@type': 'ListItem', 'position': 3, 'name': p['name'], 'item': url}]}
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faq']]}

    # 01 opening
    thumbs = ''
    tgal = [g for g in gal if not (len(g) > 2 and g[2] == 'aplus')]  # A+ panels are too wide for the hero stage
    if len(tgal) > 1:
        thumbs = '<div class="thumbs" data-thumbs="heroImg" role="group" aria-label="More pictures">' + ''.join(
            f'<button type="button" data-src="{e(s)}" data-alt="{e(a)}" aria-pressed="{str(i == 0).lower()}" aria-label="Show: {e(a)}"><img src="{e(s)}" alt="" loading="lazy" width="80" height="80"></button>'
            for i, (s, a) in enumerate((g[0], g[1]) for g in [hero_img] + [g for g in tgal if g[0] != hero_img[0]][:5])) + '</div>'
    stage_cls = 'stage cover' if p.get('hero_cover') else 'stage'
    variants = ''
    if p.get('variants'):
        variants = (f'<div class="variants"><p class="strong-s">{e(p.get("variant_label", "Choose"))}</p><div class="var-row">' +
                    ''.join(f'<a class="var" href="{e(amz(v["asin"]))}" target="_blank" rel="noopener" data-product="{e(p["name"] + " " + v["name"])}" data-where="{where}: hero choice">'
                            + (f'<span class="dot" style="--sw:{e(v["colour"])}"></span>' if v.get('colour') else '') + f'{e(v["name"])}</a>' for v in p['variants'])
                    + '</div></div>')
    hc = ''
    if p.get('hardcover'):
        hc = f'<a class="btn btn-secondary" href="{e(amz(p["hardcover"]))}" target="_blank" rel="noopener" data-product="{e(p["name"])} hardcover" data-where="{where}: hero">Hardcover on Amazon</a>'
    for_list = ''.join(f'<li>{x}</li>' for x in p['for'])
    hero = f'''<section class="wrap hero" data-where="{where}: hero">
  <div class="hero-copy">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span aria-hidden="true">/</span> <a href="/products/">Products</a> <span aria-hidden="true">/</span> <span aria-current="page">{e(p['name'])}</span></nav>
    <p class="label">{e(p['label'])}</p>
    <h1 class="d-xl">{p['h1']}</h1>
    <p class="lead">{p['lead']}</p>
    <ul class="for">{for_list}</ul>
    {variants}
    <div class="btn-row">{buy_button(p, where + ': hero', p.get('buy_label'))}{hc}<a class="btn btn-text" href="#proof">{e(p.get('peek', 'Take a look inside'))}</a></div>
    <p class="caption">{'Coming soon to Amazon. Leave your email and I’ll tell you the day it’s out.' if p.get('soon') else 'Sold and delivered by Amazon, so checkout, delivery and returns are the ones you already know.'}</p>
  </div>
  <div class="hero-art">
    <figure class="{stage_cls}"><img id="heroImg" src="{e(hero_img[0])}" alt="{e(hero_img[1])}" width="1200" height="1200" fetchpriority="high"></figure>
    {thumbs}
  </div>
</section>
<div class="proofbar"><div class="wrap"><span>{'Written and designed by Rebecca' if is_book else 'Chosen by Rebecca'}, in Yorkshire</span><span>{e(p['proofbar'])}</span>{'<span>Coming soon to Amazon</span>' if p.get('soon') else f'<a href="{e(amz(p["asin"], True))}" target="_blank" rel="noopener" data-product="{e(p["name"])}" data-where="{where}: reviews">Read the reviews on Amazon</a>'}</div></div>'''

    # 02 problem, 03 approach
    prob = p['problem']
    appr = p['approach']
    problem = f'''<section class="wrap sec narrow" data-where="{where}: problem">
  <p class="label">{e(prob.get('label', 'Sound familiar?'))}</p>
  <h2 class="d-l">{prob['h']}</h2>
  <div class="prose">{paras(prob['p'])}</div>
</section>
<section class="feature" data-where="{where}: approach">
  <div class="wrap sec narrow">
    <p class="label">{e(appr.get('label', 'A gentler way'))}</p>
    <h2 class="d-l">{appr['h']}</h2>
    <div class="prose">{paras(appr['p'])}</div>
  </div>
</section>'''

    # 04 offer
    off = p['offer']
    feats = ''.join(f'<li><span class="num">{i:02d}</span><h3 class="t">{e(t)}</h3><p class="muted">{d}</p></li>' for i, (t, d) in enumerate(off['features'], 1))
    offer = f'''<section class="wrap sec" data-where="{where}: offer">
  <div class="sec-head"><p class="label">{e(off.get('label', 'What it is'))}</p><h2 class="d-l">{off['h']}</h2><p class="lead">{off['p']}</p></div>
  <ol class="feats">{feats}</ol>
</section>'''

    # the ages / versions in a collection, each with its own page
    fam = [by_slug[x] for x in p.get('family', []) if x in by_slug]
    if fam:
        offer += (f'<section class="wrap sec-tight" data-where="{where}: family"><div class="sec-head"><p class="label">{e(p.get("family_label", "Choose one"))}</p><h2 class="h">{e(p.get("family_h", "Find the right one"))}</h2></div><div class="rel">' + ''.join(
            f'<a class="relcard" href="/products/{r["slug"]}/"><span class="art{" cover" if r.get("hero_cover") else ""}"><img src="{e((r.get("hero") or r["gallery"][0])[0])}" alt="" loading="lazy"></span><span class="t">{e(r["name"])}</span><span class="small muted">{e(r["card"])}</span></a>'
            for r in fam) + '</div></section>')

    # 05 proof
    pr = p['proof']
    kind = lambda g: g[2] if len(g) > 2 else ''
    figs = ''.join(f'<figure class="shot {kind(g)}"><img src="{e(g[0])}" alt="{e(g[1])}" loading="lazy"><figcaption>{e(g[1])}</figcaption></figure>' for g in gal)
    gcls = 'gallery spreads' if all(kind(g) in ('spread', 'aplus') for g in gal) else 'gallery'
    quotes = ''
    if p.get('quotes'):  # real customer words only, with where they came from
        quotes = '<div class="quotes">' + ''.join(f'<blockquote><p>“{e(q["text"])}”</p><cite>{e(q["who"])}</cite></blockquote>' for q in p['quotes']) + '</div>'
    proof = f'''<section class="sunken" id="proof" data-where="{where}: proof">
  <div class="wrap sec">
    <div class="sec-head"><p class="label">{e(pr.get('label', 'Take a look inside'))}</p><h2 class="d-l">{pr['h']}</h2><p class="lead">{pr['p']}</p></div>
    <div class="{gcls}">{figs}</div>
    {quotes}
    <div class="note">
      <figure class="portrait"><img src="/img/rebecca-portrait.jpg" alt="Rebecca, founder of Mazo Moon" loading="lazy"></figure>
      <div class="prose"><p class="label">A note from Rebecca</p>{paras(pr['note'])}<p class="sign">Rebecca x</p></div>
    </div>
  </div>
</section>'''

    # 06 inside
    ins = p['inside']
    items = ''.join(f'<li><span class="star" aria-hidden="true">✦</span><span>{x}</span></li>' for x in ins['items'])
    specs = ''.join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v in p['specs'])
    inside = f'''<section class="wrap sec" data-where="{where}: inside">
  <div class="split">
    <div><p class="label">{e(ins.get('label', "What's inside"))}</p><h2 class="d-l">{ins['h']}</h2><ul class="ticks">{items}</ul></div>
    <aside class="box"><h3 class="t">The details</h3><dl class="facts">{specs}</dl></aside>
  </div>
</section>'''

    # 07 decision
    opts = ''
    if p.get('variants'):
        opts = f'<p class="strong-s">{e(p.get("variant_label", "Choose"))}</p><div class="var-row">' + ''.join(
            f'<a class="var" href="{e(amz(v["asin"]))}" target="_blank" rel="noopener" data-product="{e(p["name"] + " " + v["name"])}" data-where="{where}: decision">'
            + (f'<span class="dot" style="--sw:{e(v["colour"])}"></span>' if v.get('colour') else '') + f'{e(v["name"])}</a>' for v in p['variants']) + '</div>'
    if p.get('hardcovers'):
        opts += '<p class="strong-s">Or in hardcover</p><div class="var-row">' + ''.join(
            f'<a class="var" href="{e(amz(v["asin"]))}" target="_blank" rel="noopener" data-product="{e(p["name"] + " " + v["name"])} hardcover" data-where="{where}: decision">{e(v["name"])}</a>'
            for v in p['hardcovers']) + '</div>'
    hc2 =(f'<a class="btn btn-secondary" href="{e(amz(p["hardcover"]))}" target="_blank" rel="noopener" data-product="{e(p["name"])} hardcover" data-where="{where}: decision">Hardcover on Amazon</a>'
           if p.get('hardcover') else '')
    terms = ''.join(f'<li>{x}</li>' for x in p['decision']['points'])
    decision = f'''<section class="sunken" id="decision" data-where="{where}: decision">
  <div class="wrap sec">
    <div class="deal">
      <div><p class="label">The simple bit</p><h2 class="d-l">{p['decision']['h']}</h2><ul class="plain">{terms}</ul></div>
      <div class="price-card">
        <p class="t">{e(p['name'])}</p>
        <p class="bigprice">{price(p['price']) if p.get('price') else ''}<small>{e(p['decision'].get('price_note', 'planned price' if p.get('soon') else 'at the time of writing'))}</small></p>
        {opts}
        {NOTIFY if p.get('soon') else f'<div class="btn-col">{buy_button(p, where + ": decision", p.get("buy_label"))}{hc2}</div><p class="caption">Amazon shows today’s price and delivery date before you pay. Prices can change, and Amazon’s page is always the right one.</p>'}
      </div>
    </div>
  </div>
</section>'''

    # 08 faq
    qa = ''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in p['faq'])
    faqs = f'''<section class="wrap sec narrow" data-where="{where}: faq">
  <p class="label">Questions</p>
  <h2 class="d-l">{e(p.get('faq_h', 'Things people ask me'))}</h2>
  <div class="faq">{qa}</div>
  <p class="small muted">Something I haven't answered? Email me at <a href="mailto:hello@mazomoon.com">hello@mazomoon.com</a> and I'll get back to you.</p>
</section>'''

    # 09 close
    cl = p['close']
    rel = [by_slug[s] for s in p.get('related', []) if s in by_slug][:3]
    rel_html = ''
    if rel:
        rel_html = '<section class="wrap sec" data-where="' + where + ': related"><div class="sec-head"><p class="label">You might also like</p><h2 class="h">More from the desk</h2></div><div class="rel">' + ''.join(
            f'<a class="relcard" href="/products/{r["slug"]}/"><span class="art{" cover" if r.get("hero_cover") else ""}"><img src="{e((r.get("hero") or r["gallery"][0])[0])}" alt="" loading="lazy"></span><span class="t">{e(r["name"])}</span><span class="small muted">{e(r["card"])}</span></a>'
            for r in rel) + '</div></section>'
    close = f'''<section class="close" data-where="{where}: close">
  <div class="wrap sec narrow center">
    <h2 class="d-l">{cl['h']}</h2>
    <p class="lead">{cl['p']}</p>
    <div class="btn-row center">{buy_button(p, where + ': close', p.get('buy_label'))}</div>
  </div>
</section>
{rel_html}
<div class="buybar" aria-hidden="false"><span class="bb-name">{e(p['name'])}</span>{buy_button(p, where + ': phone bar', 'Buy on Amazon')}</div>'''

    title = p['title']
    body = '\n'.join([hero, problem, offer, proof, inside, decision, faqs, close])
    nav = HEADER.format(j=' aria-current="page"' if is_book else '', s='' if is_book else ' aria-current="page"')
    return (head(title, p['description'], url, absu(p.get('og') or hero_img[0]), [thing, crumbs, faq]) +
            f'\n<body>\n{nav}\n<main id="main">\n{body}\n</main>\n{FOOTER}\n{SCRIPT}\n</body>\n</html>\n')


def index_page(items):
    url = f'{SITE}/products/'
    title = 'All Mazo Moon products: journals, colouring books, stickers and pens'
    desc = 'Every Mazo Moon journal, colouring book, sticker pack, pen set and sleep comfort, each with its own page: what it is, who it suits and a look inside.'
    blocks = ''
    for g, name in GROUPS:
        xs = [p for p in items if p['group'] == g]
        if not xs:
            continue
        blocks += f'<section class="wrap sec-tight"><h2 class="h">{e(name)}</h2><div class="rel">' + ''.join(
            f'<a class="relcard" href="/products/{p["slug"]}/"><span class="art{" cover" if p.get("hero_cover") else ""}"><img src="{e((p.get("hero") or p["gallery"][0])[0])}" alt="" loading="lazy"></span><span class="t">{e(p["name"])}</span><span class="small muted">{e(p["card"])}</span></a>'
            for p in xs) + '</div></section>'
    ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': 'Mazo Moon products', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'url': f'{SITE}/products/{p["slug"]}/', 'name': p['name']} for i, p in enumerate(items, 1)]}
    body = f'''<section class="wrap page-hero"><p class="label">Everything I make and sell</p><h1 class="d-xl">Find the right one for you</h1><p class="lead">Each product has its own page, with who it's for, a proper look inside and honest answers. When you're ready, the button takes you to Amazon.</p></section>
{blocks}
<div style="height:48px"></div>'''
    return (head(title, desc, url, SITE + '/img/og-image.jpg', [ld], kind='website') +
            f'\n<body>\n{HEADER.format(j="", s="")}\n<main id="main">\n{body}\n</main>\n{FOOTER}\n{SCRIPT}\n</body>\n</html>\n')


REQUIRED = ['name', 'kind', 'group', 'label', 'title', 'description', 'h1', 'lead', 'for', 'proofbar', 'card',
            'gallery', 'problem', 'approach', 'offer', 'proof', 'inside', 'specs', 'decision', 'faq', 'close']


def write():
    """Write every product page and the list. Returns the page addresses with their pictures, for the sitemap."""
    global CSS_V
    import hashlib
    CSS_V = hashlib.md5(open(os.path.join(ROOT, 'products', 'sales.css'), 'rb').read()).hexdigest()[:10]
    items = load()
    by = {p['slug']: p for p in items}
    out = {}
    for p in items:
        miss = [k for k in REQUIRED if k not in p]
        assert not miss, f'content/sales/{p["slug"]}.json is missing {miss}'
        for g in p['gallery']:
            assert os.path.exists(ROOT + g[0]), f'{p["slug"]}: picture {g[0]} not found'
        d = os.path.join(ROOT, 'products', p['slug'])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(page(p, by))
        out[f'{SITE}/products/{p["slug"]}/'] = [absu(g[0]) for g in p['gallery'][:6]]
    open(os.path.join(ROOT, 'products', 'index.html'), 'w', encoding='utf-8').write(index_page(items))
    out = {f'{SITE}/products/': [], **out}
    return out


def asin_pages():
    """{ASIN: '/products/<slug>/'} so the shop and journals cards can link to their sales page."""
    m = {}
    items = load()
    for p in items:  # a collection page only fills gaps: each age's own page wins
        for v in p.get('variants', []) + p.get('hardcovers', []):
            m.setdefault(v['asin'], f'/products/{p["slug"]}/')
    for p in items:
        url = f'/products/{p["slug"]}/'
        m[p['name']] = url  # books not on Amazon yet are matched by name
        if p.get('hub'):
            continue
        if p.get('asin'):
            m[p['asin']] = url
        if p.get('hardcover'):
            m[p['hardcover']] = url
    return m


if __name__ == '__main__':
    print('\n'.join(write()))
