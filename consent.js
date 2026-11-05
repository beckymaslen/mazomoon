/* Mazo Moon cookie choice and Google Analytics.
   Analytics only loads after a visitor taps "Accept". Nothing is tracked before that, or after "Decline".
   The choice is kept in this browser (localStorage "mm-consent") and can be changed on /cookies/ or from the footer link. */
(function () {
  var GA = 'G-5131GXSM7M', KEY = 'mm-consent', loaded = false;
  function get() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function set(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { dataLayer.push(arguments); };
  gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });

  function startAnalytics() {
    if (loaded) return; loaded = true;
    gtag('consent', 'update', { analytics_storage: 'granted' });
    gtag('js', new Date());
    gtag('config', GA, { anonymize_ip: true });
    var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA;
    document.head.appendChild(s);
  }
  function stopAnalytics() {
    gtag('consent', 'update', { analytics_storage: 'denied' });
    // remove any Google Analytics cookies already set on this site
    document.cookie.split(';').forEach(function (c) {
      var n = c.split('=')[0].trim();
      if (/^_ga/.test(n)) ['', '.mazomoon.com', '.www.mazomoon.com', location.hostname].forEach(function (d) {
        document.cookie = n + '=; Max-Age=0; path=/' + (d ? '; domain=' + d : '');
      });
    });
  }

  var css = '#mmc{position:fixed;z-index:9999;left:16px;right:16px;bottom:16px;margin:0 auto;max-width:560px;'
    + 'background:var(--surface-raised,#fbf9f6);color:var(--text,#434342);border:1px solid var(--hairline,#d9d2cb);border-radius:4px;'
    + 'box-shadow:0 18px 40px -18px rgba(48,49,51,.45);padding:18px 20px;font:400 15px/1.55 var(--sans,"Jost",system-ui,sans-serif);'
    + 'display:grid;gap:12px;padding-bottom:calc(18px + env(safe-area-inset-bottom,0px))}'
    + '#mmc h2{margin:0;font:500 22px/1.2 var(--display,"Cormorant Garamond",Georgia,serif);color:inherit}'
    + '#mmc p{margin:0;color:var(--text-muted,#675f5b)}#mmc a{color:var(--text-accent,#705b65);text-underline-offset:3px}'
    + '#mmc .b{display:flex;flex-wrap:wrap;gap:10px}'
    + '#mmc button{font:500 15px/1 var(--sans,"Jost",system-ui,sans-serif);min-height:44px;padding:0 22px;border-radius:var(--r-sm,2px);cursor:pointer;'
    + 'border:1px solid var(--action,#434342);background:transparent;color:var(--text,#434342)}'
    + '#mmc button.y{background:var(--action,#434342);color:var(--on-action,#f7f4ef)}'
    + '#mmc button:focus-visible{outline:2px solid var(--focus,#80615f);outline-offset:2px}'
    + '@media (prefers-color-scheme:dark){#mmc{background:var(--surface-raised,#3a3b3c);color:var(--text,#f7f4ef);border-color:var(--hairline,#4d4e4f)}'
    + '#mmc p{color:var(--text-muted,#b9b0aa)}#mmc a{color:var(--text-accent,#c4a9b4)}#mmc button{border-color:var(--action,#f7f4ef);color:var(--text,#f7f4ef)}'
    + '#mmc button.y{background:var(--action,#f7f4ef);color:var(--on-action,#303133)}}'
    + '@media print{#mmc{display:none}}';

  function banner() {
    if (document.getElementById('mmc')) return;
    if (!document.getElementById('mmcs')) { var st = document.createElement('style'); st.id = 'mmcs'; st.textContent = css; document.head.appendChild(st); }
    var d = document.createElement('section'); d.id = 'mmc'; d.setAttribute('role', 'region'); d.setAttribute('aria-labelledby', 'mmcT');
    d.innerHTML = '<h2 id="mmcT">A little cookie question</h2>'
      + '<p>May I use Google Analytics cookies to see which pages people visit, so I can make the site better? No adverts, and I never sell your data. '
      + '<a href="/cookies/">More about cookies</a></p>'
      + '<div class="b"><button type="button" class="y" data-v="granted">Accept</button><button type="button" data-v="denied">Decline</button></div>';
    d.addEventListener('click', function (e) {
      var b = e.target.closest && e.target.closest('button[data-v]'); if (!b) return;
      choose(b.getAttribute('data-v')); d.remove();
      var c = document.getElementById('mmcChoice'); if (c) c.textContent = label();
    });
    document.body.appendChild(d);
  }
  function label() { var v = get(); return v === 'granted' ? 'You’ve accepted analytics cookies.' : v === 'denied' ? 'You’ve declined analytics cookies.' : 'You haven’t chosen yet.'; }
  function choose(v) { set(v); if (v === 'granted') startAnalytics(); else stopAnalytics(); }

  /* Which product someone taps before going to Amazon. Only sent when analytics was accepted (gtag sends nothing otherwise). */
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="amazon."]'); if (!a || !loaded) return;
    var card = a.closest('article, li, .card, .product, section'), h = card && card.querySelector('h1, h2, h3, h4, .name, .title');
    var m = /\/dp\/([A-Z0-9]{10})/i.exec(a.href), name = (h && h.textContent || a.getAttribute('title') || a.textContent || '').replace(/\s+/g, ' ').trim();
    gtag('event', 'amazon_click', { product_name: name.slice(0, 100), asin: m ? m[1] : '', link_text: (a.getAttribute('aria-label') || a.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 100), page_path: location.pathname, transport_type: 'beacon' });
  }, true);

  window.mmCookies = { open: banner, choose: choose, label: label };
  if (get() === 'granted') startAnalytics();
  function ready() {
    if (!get()) banner();
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('[data-cookie-settings]'); if (!a) return;
      e.preventDefault(); banner(); var y = document.querySelector('#mmc button.y'); if (y) y.focus();
    });
    var c = document.getElementById('mmcChoice'); if (c) c.textContent = label();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready); else ready();
})();
