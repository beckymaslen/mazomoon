#!/usr/bin/env python3
"""Writes the Privacy, Cookies and Terms pages. Edit the text here, then run:
python3 tools/legal.py"""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPDATED = '4 November 2026'

SHELL = '''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | Mazo Moon</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="https://mazomoon.com/{slug}/">
<link rel="icon" href="/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Jost:wght@400;500&display=swap">
<style>
:root{{--surface:#f7f4ef;--text:#303133;--muted:#62605e;--accent:#80615f;--hairline:#e4ded6;color-scheme:light}}
@media (prefers-color-scheme: dark){{:root{{--surface:#303133;--text:#f7f4ef;--muted:#b9b0aa;--accent:#c4a9b4;--hairline:#4d4e4f;color-scheme:dark}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--surface);color:var(--text);font:400 17px/1.65 Jost,system-ui,sans-serif}}
.wrap{{max-width:720px;margin:0 auto;padding:32px 16px 80px}}
header{{display:flex;justify-content:space-between;align-items:center;gap:16px;border-bottom:1px solid var(--hairline);padding-bottom:20px;margin-bottom:40px}}
.wm{{display:block;width:168px;aspect-ratio:900/124;background:var(--text);-webkit-mask:url(/img/wordmark-mask.png) center/contain no-repeat;mask:url(/img/wordmark-mask.png) center/contain no-repeat}}
.wm span{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}
a{{color:var(--accent);text-underline-offset:3px}}
h1{{font:500 clamp(36px,6vw,52px)/1.1 "Cormorant Garamond",Georgia,serif;margin:0 0 8px}}
h2{{font:600 24px/1.25 "Cormorant Garamond",Georgia,serif;margin:36px 0 8px}}
.updated{{color:var(--muted);font-size:14px;margin:0 0 28px}}
ul{{padding-left:20px}}
footer{{border-top:1px solid var(--hairline);margin-top:56px;padding-top:20px;font-size:14px;color:var(--muted);display:flex;flex-wrap:wrap;gap:8px 20px}}
</style>
</head>
<body>
<div class="wrap">
<header><a class="wm" href="/"><span>Mazo Moon home</span></a><a href="/">Back to the site</a></header>
<main>
<h1>{title}</h1>
<p class="updated">Last updated {updated}</p>
{body}
</main>
<footer><span>© 2026 Mazo Moon Ltd · Company no. 16988519</span><a href="/privacy/">Privacy</a><a href="/cookies/">Cookies</a><a href="/terms/">Terms</a><a href="mailto:hello@mazomoon.com">hello@mazomoon.com</a></footer>
</div>
</body>
</html>
'''

PAGES = {
'privacy': ('Privacy policy', 'How Mazo Moon looks after the personal details you share with us.', '''
<p>This website is run by Mazo Moon Ltd, a private limited company registered in England and Wales (company number 16988519), whose registered office is 13-15 Boothtown Road, Halifax, HX3 6EU. Mazo Moon Ltd is responsible for your personal details as the data controller. This page explains what we collect when you use mazomoon.com, why, and what you can ask us to do with it. If you have a question, email <a href="mailto:hello@mazomoon.com">hello@mazomoon.com</a>.</p>
<h2>What we collect</h2>
<ul>
<li><strong>When you send us a message:</strong> your name, email address, the topic you choose and your message.</li>
<li><strong>When you sign up for the monthly letter:</strong> your email address.</li>
</ul>
<p>We don't ask for anything else, and we never collect payment details. All orders are placed and paid for on Amazon, so Amazon handles your order, delivery and payment details under <a href="https://www.amazon.co.uk/gp/help/customer/display.html?nodeId=201909010" rel="noopener">Amazon's privacy notice</a>.</p>
<h2>Why we use it</h2>
<ul>
<li>To reply to your message. Our lawful basis is our legitimate interest in answering you.</li>
<li>To send the monthly letter you asked for. Our lawful basis is your consent, and every letter has a way to unsubscribe.</li>
</ul>
<p>We never sell your details or share them for anyone else's marketing.</p>
<h2>Who helps us</h2>
<ul>
<li><strong>FormSubmit</strong> (formsubmit.co) passes the contact and sign-up forms to our inbox.</li>
<li><strong>IONOS</strong> hosts our email.</li>
<li><strong>GitHub Pages</strong> hosts the website and keeps standard server logs, such as IP addresses, for security.</li>
<li><strong>Google Fonts</strong> serves our fonts, and <strong>Amazon</strong> serves some product photos, so your browser connects to their servers when you visit.</li>
</ul>
<p>Some of these companies may handle data outside the UK. When they do, they use recognised safeguards such as standard contractual clauses.</p>
<h2>How long we keep it</h2>
<p>We keep messages for as long as we need them to help you, and for no more than two years. We keep your email address on the letter list until you unsubscribe.</p>
<h2>Your rights</h2>
<p>You can ask to see the details we hold about you, correct them, delete them, or stop receiving the letter. Just email <a href="mailto:hello@mazomoon.com">hello@mazomoon.com</a>. If you're unhappy with how we've handled your details, you can complain to the Information Commissioner's Office at <a href="https://ico.org.uk" rel="noopener">ico.org.uk</a>.</p>
'''),
'cookies': ('Cookies', 'Mazo Moon does not use tracking or advertising cookies.', '''
<p>mazomoon.com doesn't use advertising or tracking cookies, and we don't run analytics that follow you around the web.</p>
<h2>What the site does store</h2>
<ul>
<li><strong>Session storage:</strong> the site remembers, for the current visit only, that you've already seen the opening animation, so it doesn't play again on every page. This is cleared when you close the tab.</li>
</ul>
<h2>Other websites</h2>
<p>Our fonts come from Google Fonts, and some product photos load from Amazon. When you tap "Buy on Amazon", you move to Amazon's website, which uses its own cookies under <a href="https://www.amazon.co.uk/cookies" rel="noopener">Amazon's cookie notice</a>.</p>
<p>If we ever add analytics or anything else that uses cookies, we'll update this page and ask for your consent first where the law requires it.</p>
'''),
'terms': ('Terms of use', 'The terms for using the Mazo Moon website.', '''
<p>These terms cover your use of mazomoon.com, which is run by Mazo Moon Ltd, a private limited company registered in England and Wales (company number 16988519). Our registered office is 13-15 Boothtown Road, Halifax, HX3 6EU. Contact us at <a href="mailto:hello@mazomoon.com">hello@mazomoon.com</a>.</p>
<h2>Buying our products</h2>
<p>We sell through Amazon. When you buy, your contract is made through Amazon, under <a href="https://www.amazon.co.uk/gp/help/customer/display.html?nodeId=201909000" rel="noopener">Amazon's conditions of use and sale</a>, including its delivery and returns policies. Prices and stock are shown on Amazon and can change there at any time.</p>
<h2>Our content</h2>
<p>The words, photos, illustrations, sticker designs and journal pages on this site belong to Mazo Moon Ltd. You're welcome to share links to our pages. Please don't copy or reuse our designs or content for commercial purposes without asking us first.</p>
<h2>Reviews and recommendations</h2>
<p>The Reading Corner and Little Things I Love are our honest opinions. When we recommend another company's product, we'll say so clearly.</p>
<h2>Links to other sites</h2>
<p>We link to Amazon and other websites. We're not responsible for their content or how they work.</p>
<h2>Changes</h2>
<p>We may update these terms from time to time. The date at the top shows when they last changed. These terms are governed by the law of England and Wales.</p>
'''),
}

for slug, (title, desc, body) in PAGES.items():
    d = os.path.join(ROOT, slug); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(
        SHELL.format(title=title, desc=desc, slug=slug, body=body.strip(), updated=UPDATED))
print('wrote', ', '.join(PAGES))
