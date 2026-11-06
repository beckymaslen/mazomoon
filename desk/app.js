/* Mazo Moon desk (www.mazomoon.com home page). Content comes from content.js and reviews.js (window.MM). */
(function(){
'use strict';
const MM = window.MM;
const $ = (s, r=document) => r.querySelector(s);
const esc = t => String(t ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const amz = a => MM.amazon + a + (MM.maas ? '?' + MM.maas : '');   // Amazon Attribution: sales from this site show in Seller Central
const gbp = p => '£' + Number(p).toFixed(2);
const store = { get(k){ try{ return localStorage.getItem(k); }catch(_){ return null; } }, set(k,v){ try{ localStorage.setItem(k,v); }catch(_){} } };
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- the scene: images and where each object sits (x, y, w, h in % of the image) ---------- */
const SCENE = {
  desk: { day:'/desk/img/scene/day-desk.webp', night:'/desk/img/scene/night-desk.webp', steam:[70.8,41,7], size:[1536,864], nb:.34,
    cover:[[400,489],[583,489],[558,615],[327,616]], shade:[314,484,277,195],
    spines:[[[630,323],[852,329],[852,346],[630,339]],[[616,349],[852,362],[852,389],[616,376]],[[612,374],[848,388],[848,417],[612,403]],[[606,407],[846,421],[846,452],[606,433]]],
    puzzle:[[398,676],[556,668],[574,752],[382,762]], piece:[[592,706],[624,701],[630,729],[596,735]],
    book:{ body:[[398,487],[586,486],[589,512],[580,641],[562,652],[331,653],[319,641],[316,616],[388,488]],
      pages:[[323,617],[556,615],[556,642],[325,644]], side:[[556,615],[561,606],[563,639],[556,642]], ribbon:[[337,630],[352,631],[339,677],[325,676]] },
    hot: {
      laptop:[78,51,22,19,'in'], journal:[20,56,18,20], books:[39,34,19.5,20], lamp:[81,9,18,42,'in'], mug:[64,41,12.5,18],
      notebook:[38.5,56,32,20,'in'], stickers:[3,65,17,14], puzzle:[24,76,17,13], pens:[15,42,7.5,21], envelope:[57,77,20,15], scrapbook:[75,70,24,21] } },
  phone: { day:'/desk/img/scene/day-phone.webp', night:'/desk/img/scene/night-phone.webp', steam:[73.8,40.5,13], size:[788,1400], nb:.6,
    cover:[[23,606],[207,580],[287,727],[66,766]], shade:[13,576,280,257],
    spines:[[[142,410],[350,433],[350,461],[142,437]],[[136,442],[348,467],[348,495],[136,470]],[[136,474],[346,500],[346,524],[136,498]]],
    puzzle:[[205,1138],[392,1122],[416,1240],[214,1258]], piece:[[432,1262],[466,1255],[474,1284],[438,1292]],
    book:{ body:[[15,607],[26,598],[207,578],[214,581],[289,728],[291,744],[281,752],[70,793],[60,787],[17,624]],
      pages:[[66,766],[276,735],[279,753],[69,782]], side:[[276,735],[287,728],[289,743],[279,753]], ribbon:[[84,769],[96,768],[110,828],[99,831]] },
    hot: {
      lamp:[1,6,36,20], books:[16,26.5,37,12], journal:[2,41,35,16], mug:[63,38,21,12], pens:[85,33,14,16,'r'],
      notebook:[38,50.5,53,16.5], stickers:[0,62,30,15,'l'], envelope:[31,68,29,10.5], puzzle:[31,79,26,9], scrapbook:[61,69,38,24] } }
};
const OBJ = {
  journal:  ['Journals & colouring', 'Journals'],
  books:    ['The Reading Corner', 'Reading Corner'],
  laptop:   ['Shop Mazo Moon', 'Shop'],
  mug:      ['What’s on Becky’s desk', 'Mug'],
  lamp:     ['Day or moonlight', 'Lamp'],
  envelope: ['Letters & contact', 'Letters'],
  stickers: ['Sticker playground', 'Stickers'],
  notebook: ['Try a little doodle', 'Doodle'],
  pens:     ['Pens & stationery', 'Pens'],
  scrapbook:['My story', 'Story'],
  puzzle:   ['Moon & stars game', 'Puzzle']
};

const root = document.documentElement, room = $('#room'), stage = $('#stage'), layer = $('#layer');
const mq = matchMedia('(max-width: 700px), (max-width: 900px) and (orientation: portrait)');
let layout = null;

/* the daytime photo changes with the season: same desk, a different view through the window */
function curSeason(){ return window.__mmSeason || (/[?&]season=(spring|summer|autumn|winter)/.exec(location.search) || [])[1]
  || ['winter','winter','spring','spring','spring','summer','summer','summer','autumn','autumn','autumn','winter'][new Date().getMonth()]; }
function seasonal(src){ return src.replace(/\.webp$/, '-' + curSeason() + '.webp'); }
let ensureNight = () => {};
function build(){
  const mob = mq.matches; const next = mob ? 'phone' : 'desk';
  document.body.classList.toggle('mobile', mob);
  if (layout === next) return; layout = next;
  const S = SCENE[layout];
  const day = seasonal(S.day); $('#imgD').src = day;
  // the moonlight photo only loads when it's needed, or once the daytime one has finished
  const loadNight = ensureNight = () => { if ($('#imgN').getAttribute('src') !== S.night) { $('#imgN').src = S.night; document.querySelector('.blur.n').style.backgroundImage = `url(${S.night})`; } };
  if (root.classList.contains('night')) loadNight(); else $('#imgD').addEventListener('load', () => setTimeout(loadNight, 1500), { once: true });
  document.querySelector('.blur.d').style.backgroundImage = `url(${day})`;
  const st = $('#steam'); st.style.cssText = `--x:${S.steam[0]}%;--y:${S.steam[1]}%;--w:${S.steam[2]}%`;
  $('#hots').innerHTML = Object.entries(S.hot).map(([k,[x,y,w,h,lp]]) =>
    `<button class="hot${lp?' lab-'+lp:''}" type="button" data-k="${k}" style="--x:${x}%;--y:${y}%;--w:${w}%;--h:${h}%" aria-label="${esc(OBJ[k][1])}: ${esc(OBJ[k][0])}"><span class="lab">${esc(layout === 'phone' && k === 'pens' ? 'Pens' : OBJ[k][0])}</span></button>`).join('');
  $('#hots').querySelectorAll('.hot').forEach(b => b.addEventListener('click', () => openObj(b.dataset.k, b)));
}
/* perspective transform for the gold spine lettering on the desk's book stack.
   The Mazo Moon book and the moon puzzle are part of the photographs themselves (/desk/img/scene). */
function homog(w, h, q){
  const [[x0,y0],[x1,y1],[x2,y2],[x3,y3]] = q;
  const dx1 = x1-x2, dx2 = x3-x2, dy1 = y1-y2, dy2 = y3-y2, sx = x0-x1+x2-x3, sy = y0-y1+y2-y3;
  const den = dx1*dy2 - dx2*dy1, g = (sx*dy2 - dx2*sy)/den, hh = (dx1*sy - sx*dy1)/den;
  const A = x1-x0+g*x1, B = x3-x0+hh*x3, D = y1-y0+g*y1, E = y3-y0+hh*y3;
  const m = [A/w, D/w, 0, g/w,  B/h, E/h, 0, hh/h,  0, 0, 1, 0,  x0, y0, 0, 1];
  return `matrix3d(${m.map(v => +v.toFixed(8)).join(',')})`;
}
function placeCover(){
  const S = SCENE[layout]; if (!S.spines) return;
  layer.style.setProperty('--nb', S.nb);
  const kx = stage.offsetWidth / S.size[0], ky = stage.offsetHeight / S.size[1], ST = [].concat(MM.spineText || []);
  $('#spines').innerHTML = S.spines.map((q, i) => ST[i] ? `<div class="spt" style="transform:${homog(400, 40, q.map(([x,y]) => [x*kx, y*ky]))}"><i></i><span>${esc(ST[i])}</span><i></i></div>` : '').join('');
}
if (!$('#spines')) { const sps = document.createElement('div'); sps.id = 'spines'; sps.setAttribute('aria-hidden','true'); $('#steam').before(sps); }
document.documentElement.lang = 'en-GB';
build(); placeCover();
if (window.ResizeObserver) new ResizeObserver(placeCover).observe(stage); else addEventListener('resize', placeCover);
mq.addEventListener ? mq.addEventListener('change', () => { build(); placeCover(); }) : mq.addListener(() => { build(); placeCover(); });
build();

/* ---------- day and moonlight ---------- */
function yorkshireHour(){ try{ return +new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/London',hour:'numeric',hour12:false}).format(new Date()); }catch(_){ return new Date().getHours(); } }
function setMode(m, save){ if (arguments[0] === "night") ensureNight(); root.classList.toggle('night', m === 'night'); if (save) store.set('mm-mode', m);
  $('#hintText').textContent = m === 'night' ? 'Choose an object to explore.' : 'Choose an object to explore.'; }
setMode(store.get('mm-mode') || ((yorkshireHour() >= 19 || yorkshireHour() < 6) ? 'night' : 'day'));
const toggleLamp = () => setMode(root.classList.contains('night') ? 'day' : 'night', true);

/* ---------- gentle depth on desktop ---------- */
if (!reduce) addEventListener('pointermove', e => {
  if (layout !== 'desk' || e.pointerType !== 'mouse') return;
  const x = (e.clientX / innerWidth - .5) * -10, y = (e.clientY / innerHeight - .5) * -6;
  layer.style.setProperty('--px', x.toFixed(1) + 'px'); layer.style.setProperty('--py', y.toFixed(1) + 'px');
});

/* ---------- labels: optional, one control, remembered ---------- */
function around(on, save = true){ const v = on ?? !stage.classList.contains('around'); stage.classList.toggle('around', v);
  ['#aroundBtn', '#mExplore'].forEach(s => { const b = $(s); if (b) { b.textContent = v ? 'Hide labels' : 'Show labels'; b.setAttribute('aria-pressed', v); } });
  if (save) store.set('mm-labels', v ? '1' : '0'); }
$('#aroundBtn').addEventListener('click', () => around());
$('#mExplore').addEventListener('click', () => around());
around(store.get('mm-labels') === '1', false);

/* ---------- camera: push towards an object, then open its sheet ---------- */
function push(el){
  if (!el || reduce || layout !== 'desk') return;
  const r = el.getBoundingClientRect(), s = stage.getBoundingClientRect();
  const ox = ((r.left + r.width/2 - s.left) / s.width * 100).toFixed(1), oy = ((r.top + r.height/2 - s.top) / s.height * 100).toFixed(1);
  stage.style.transformOrigin = `${ox}% ${oy}%`;
  stage.style.transform = 'translate(-50%,-50%) scale(1.12)';
}
function release(){ stage.style.transform = ''; room.classList.remove('soft'); }

let lastOpener = null;
function openObj(k, el){
  if (k === 'lamp') { toggleLamp(); return; }
  lastOpener = el || null; push(el); room.classList.add('soft');
  const run = () => ({ journal:openJournals, books:openLibrary, laptop:openShop, mug:openMug, envelope:openLetter,
    stickers:openStickers, notebook:openDoodle, pens:f=>{ shopCat='pens'; openShop(f); }, scrapbook:openStory, puzzle:openPuzzle }[k] || openShop)(el);
  reduce || layout !== 'desk' ? run() : setTimeout(run, 380);
}

/* ---------- sheet helpers ---------- */
const sheet = $('#sheet'), slip = $('#slip'), menu = $('#menu');
function showSheet(eyebrow, html, cls, from){
  sheet.className = 'sheet' + (cls ? ' ' + cls : '');
  $('#sheetEyebrow').textContent = eyebrow; $('#sheetBody').innerHTML = html; $('#sheetBody').scrollTop = 0;
  if (from && !reduce && layout === 'desk') { const r = from.getBoundingClientRect();
    sheet.style.setProperty('--sx', (r.left + r.width/2 - innerWidth/2) + 'px'); sheet.style.setProperty('--sy', (r.top + r.height/2 - innerHeight/2) + 'px'); sheet.style.setProperty('--ss', '.25'); }
  else { sheet.style.removeProperty('--sx'); sheet.style.removeProperty('--sy'); sheet.style.removeProperty('--ss'); }
  if (!sheet.open) sheet.showModal();
  const h = $('#sheetBody h2'); if (h) { h.id = 'sheetTitle'; }
}
function closeAll(){ [sheet, slip, menu].forEach(d => d.open && d.close()); }
[sheet, slip].forEach(d => { d.addEventListener('close', () => { if (!sheet.open && !slip.open) { release(); if (lastOpener) lastOpener.focus(); } });
  d.addEventListener('click', e => { if (e.target === d || e.target.closest('[data-close]')) d.close(); }); });

/* ---------- journals ---------- */
let jIdx = 0, jPage = 0;
function openJournals(from){
  const J = MM.journals;
  showSheet('Journals & colouring', `
    <h2 class="t">Big adventures. Little things worth remembering.</h2>
    <p class="lead" style="margin-top:10px">Pick a journal, open the cover and turn through real pages from inside.</p>
    <div class="carhost" id="carhost"></div>
    <div class="jwrap" id="jwrap"></div>`, '', from);
  journalCarousel($('#carhost'), i => { jIdx = i; jPage = 0; drawJournal(); });
  drawJournal();
}
/* ---------- journal carousel: 3D books on a gentle arc, flick or drag, tap one to bring it to the front ---------- */
let carAbort = null;
function journalCarousel(host, onPick){
  if (carAbort) carAbort.abort(); const ac = carAbort = new AbortController(); const sig = { signal: ac.signal };
  const J = MM.journals, n = J.length, phone = layout === 'phone';
  const W = phone ? 104 : 132, step = phone ? 27 : 17;        // book width, degrees between books on the arc
  host.innerHTML = `<div class="car" tabindex="0" role="listbox" aria-label="Choose a journal. Drag, or use the arrow keys" aria-activedescendant="car${jIdx}">
      <div class="carrig">${J.map((j, i) => `<div class="cit" id="car${i}" role="option" aria-selected="${i === jIdx}" aria-label="${esc(j.name)}" data-i="${i}" style="--w:${W}px"><span class="cfloor" aria-hidden="true"></span>
        <span class="b3 car3" style="--w:${W}px;--h:${Math.round(W * 1.5)}px;--d:${phone ? 10 : 13}px"><span class="b3f b3back"></span><span class="b3f b3spine"><span>${esc(j.name)}</span></span>
          <span class="b3f b3edge r"></span><span class="b3f b3edge t"></span><span class="b3f b3edge b"></span>
          <span class="b3f b3front"><img src="${j.cover}" alt="" loading="lazy" draggable="false"><i class="glint"></i></span></span></div>`).join('')}</div>
      <p class="carname" aria-hidden="true"></p></div>`;
  const car = host.querySelector('.car'), rig = car.querySelector('.carrig'), items = [...rig.children], name = car.querySelector('.carname');
  items.forEach((it, i) => spineColour(J[i].cover, s => { const b = it.querySelector('.b3'); b.style.setProperty('--sc', s.c); b.style.setProperty('--h', Math.round(W / s.ar) + 'px'); }));
  let R = 0; const size = () => { R = Math.max(phone ? 300 : 560, car.clientWidth * (phone ? .95 : .78)); };
  new ResizeObserver(() => { size(); draw(); }).observe(car); size();

  let pos = jIdx, vel = 0, target = jIdx, drag = null, raf = 0, last = performance.now(), t0 = last, shown = -1;
  const wrap = o => ((o % n) + n * 1.5) % n - n / 2;          // shortest way round the loop
  function draw(now = performance.now()){
    const sway = reduce ? 0 : Math.sin((now - t0) / 2600) * 1.6;     // idle drift: the whole rig breathes very slightly
    items.forEach((it, i) => { const o = wrap(i - pos), a = o * step * Math.PI / 180, vis = Math.abs(o) < (phone ? 2.4 : 3.8);
      it.style.visibility = vis ? 'visible' : 'hidden'; if (!vis) return;
      const x = Math.sin(a) * R, z = (1 - Math.cos(a)) * R * .55 - Math.max(0, 1 - Math.abs(o)) * 30, ry = -o * step * .9 + sway + 24;     // a constant quarter turn so each book shows its spine and page edges
      it.style.transform = `translateX(${x.toFixed(1)}px) translateZ(${z.toFixed(1)}px) rotateY(${ry.toFixed(2)}deg)`;
      it.style.zIndex = 100 - Math.round(Math.abs(o) * 10);
      it.style.setProperty('--lit', (.5 + Math.max(-.5, Math.min(.5, -(ry - 24) / 60))).toFixed(3));   // key light from the left
      it.style.opacity = Math.max(0, Math.min(1, (phone ? 2.4 : 3.8) - Math.abs(o))).toFixed(2);
      const f = Math.max(0, 1 - Math.abs(o)); it.style.setProperty('--up', (f * f * (3 - 2 * f)).toFixed(3)); });   // the front book rises a little and grows 5%
    const c = ((Math.round(pos) % n) + n) % n;
    if (c !== shown) { shown = c; name.textContent = J[c].name; }
  }
  function tick(now){
    raf = 0; if (!document.contains(car)) { ac.abort(); return; } const dt = Math.min(48, now - last) / 16.67; last = now;
    if (!drag) {
      if (Math.abs(vel) > .002) { pos += vel * dt; vel *= Math.pow(.92, dt); if (Math.abs(vel) < .02) target = Math.round(pos); }
      else { const f = (target - pos) * .12 - vel * .3; vel = 0; pos += reduce ? target - pos : f * dt; }   // spring to the nearest book
      if (Math.abs(vel) < .002 && Math.abs(target - pos) < .0015) { pos = target; settle(); }
    }
    draw(now);
    if (!reduce) raf = requestAnimationFrame(tick);    // keeps the idle drift alive
  }
  const go = () => { if (!raf) { last = performance.now(); raf = requestAnimationFrame(tick); } };
  function settle(){ const c = ((Math.round(pos) % n) + n) % n; if (c === jIdx) return;
    items.forEach((it, i) => it.setAttribute('aria-selected', i === c)); car.setAttribute('aria-activedescendant', 'car' + c); onPick(c); }
  const to = i => { const o = wrap(i - pos); target = pos + o; target = Math.round(target); vel = 0; go(); if (reduce) { pos = target; draw(); settle(); } };

  car.addEventListener('pointerdown', e => { if (e.button) return; drag = { x:e.clientX, p:pos, t:performance.now(), moved:0, hist:[[e.clientX, performance.now()]], id:e.pointerId }; vel = 0; car.classList.add('grab'); });
  window.addEventListener('pointermove', e => { if (!drag || e.pointerId !== drag.id) return; const dx = e.clientX - drag.x; drag.moved = Math.max(drag.moved, Math.abs(dx));
    if (drag.moved > 6 && !drag.cap) { drag.cap = true; try { car.setPointerCapture(e.pointerId); } catch(_) {} }
    pos = drag.p - dx / (R * step * Math.PI / 180); drag.hist.push([e.clientX, performance.now()]); if (drag.hist.length > 6) drag.hist.shift(); go(); }, sig);
  const end = e => { if (!drag || e.pointerId !== drag.id) return; car.classList.remove('grab'); const d = drag; drag = null;
    if (d.moved <= 6) { const it = document.elementFromPoint(e.clientX, e.clientY)?.closest('.cit'); if (it) to(+it.dataset.i); return; }
    const [x0, t1] = d.hist[0], [x1, t2] = d.hist[d.hist.length - 1];
    vel = reduce ? 0 : -((x1 - x0) / Math.max(16, t2 - t1)) * 16.67 / (R * step * Math.PI / 180);   // momentum flick
    if (Math.abs(vel) < .02) { vel = 0; target = Math.round(pos); } go(); };
  window.addEventListener('pointerup', end, sig); window.addEventListener('pointercancel', end, sig);
  car.addEventListener('wheel', e => { if (Math.abs(e.deltaX) < Math.abs(e.deltaY)) return; e.preventDefault(); vel = 0; pos += e.deltaX / 400; target = Math.round(pos); go(); }, { passive:false });
  car.addEventListener('keydown', e => { const k = { ArrowRight:1, ArrowLeft:-1 }[e.key]; if (!k) return; e.preventDefault(); to(Math.round(target) + k); });
  sheet.addEventListener('close', () => { cancelAnimationFrame(raf); raf = 0; ac.abort(); }, sig);
  draw(); go();
  return { to };
}

/* ---------- 3D journals: mini books on the shelf, one big book you can turn and open ---------- */
const SPC = {};
function spineColour(src, cb){
  if (SPC[src]) return cb(SPC[src]);
  const im = new Image(); im.onload = () => { try {
      const c = document.createElement('canvas'), w = 8, h = 40; c.width = w; c.height = h; const g = c.getContext('2d');
      g.drawImage(im, 0, 0, im.naturalWidth * 0.05, im.naturalHeight, 0, 0, w, h);
      const d = g.getImageData(0, 0, w, h).data; let r = 0, gg = 0, b = 0; for (let i = 0; i < d.length; i += 4) { r += d[i]; gg += d[i+1]; b += d[i+2]; }
      const n = d.length / 4; SPC[src] = { c:`rgb(${r/n*.78|0},${gg/n*.78|0},${b/n*.78|0})`, ar: im.naturalWidth / im.naturalHeight }; } catch(_) { SPC[src] = { c:'#2b2752', ar:2/3 }; }
    cb(SPC[src]); };
  im.onerror = () => cb(SPC[src] = { c:'#2b2752', ar:2/3 }); im.src = src;
}
const miniBook = j => `<span class="b3 mini" style="--w:64px;--h:96px;--d:11px"><span class="b3f b3back"></span><span class="b3f b3spine"></span>
  <span class="b3f b3edge r"></span><span class="b3f b3edge t"></span><span class="b3f b3edge b"></span><span class="b3f b3front"><img src="${j.cover}" alt="" loading="lazy"></span></span>`;
function paintMini(btn, src){ spineColour(src, s => { const b = btn.querySelector('.b3'); b.style.setProperty('--sc', s.c); b.style.setProperty('--h', Math.round(64 / s.ar) + 'px'); }); }
let b3 = { ry:28, rx:10, open:false, leaf:0 };
function drawJournal(){
  const j = MM.journals[jIdx], pages = (j.pages || []).slice(), n = pages.length;
  const buy = j.soon || !j.asin ? `<span class="btn line" aria-disabled="true">Coming soon to Amazon</span>`
    : `<a class="btn ext" href="${amz(j.asin)}" target="_blank" rel="noopener" aria-label="${esc(j.name)}${j.hardcover?' paperback':''} on Amazon, opens in a new tab">${j.hardcover?'Paperback on Amazon':'Buy on Amazon'}</a>` +
      (j.hardcover ? `<a class="btn line ext" href="${amz(j.hardcover)}" target="_blank" rel="noopener" aria-label="${esc(j.name)} hardcover on Amazon, opens in a new tab">Hardcover</a>` : '');
  // a real book: each leaf has a page on the front (right) and the next page on its back (left), then a closing note
  const seq = pages.concat(['MORE']), leaves = []; for (let k = 0; k < seq.length; k += 2) leaves.push([seq[k], seq[k + 1]]);
  const face = (p, cls) => p === 'MORE' ? `<div class="lf ${cls}"><span class="more">${/^\d+ pages/.test(j.spec) ? `There are ${esc(j.spec.split('·')[0].trim())} in the real book.<br>${n > 1 ? 'These are a few of them.' : 'This is a sample.'}` : 'There’s lots more to fill in the real book.'}</span></div>`
    : `<div class="lf ${cls}"${p ? ` style="background-image:url('${p}')"` : ''}></div>`;
  $('#jwrap').innerHTML = `
    <div class="b3col">
      <div class="b3stage" id="b3stage" role="img">
        <div class="b3 big" id="b3" aria-hidden="true">
          <div class="b3f b3back"></div><div class="b3f b3spine"><span>${esc(j.name)}</span></div>
          <div class="b3f b3edge r"></div><div class="b3f b3edge t"></div><div class="b3f b3edge b"></div><div class="b3f b3inback"></div>
          ${leaves.map(([f, bk], i) => `<div class="b3leaf" data-l="${i}">${face(f, 'fr')}${face(bk, 'bk')}</div>`).reverse().join('')}
          <div class="b3leaf cover" data-l="c"><div class="lf fr"><img src="${j.cover}" alt="Cover of ${esc(j.name)}"></div><div class="lf bk endp"></div></div>
        </div>
      </div>
      <div class="pager">
        <button class="btn line" type="button" id="pPrev">Previous</button>
        <span class="ctr" id="pCtr" aria-live="polite"></span>
        <button class="btn" type="button" id="pNext">Open the book</button>
      </div>
      <p class="small muted b3hint">Drag the book to turn it round. Tap the right page to turn forward.</p>
      <button class="quiet" type="button" id="pZoom">Enlarge the cover</button>
    </div>
    <div class="info">
      <span class="eyebrow">${j.colouring?'Colouring book':'Keepsake journal'}</span>
      <h3 style="font-size:34px">${esc(j.name)}</h3>
      <p class="for">${esc(j.line)}</p>
      <p class="muted">${esc(j.about)}</p>
      <p class="small muted">${esc(j.spec)}</p>
      ${j.price && !j.soon ? `<span class="price">${j.hardcover?'From ':''}${gbp(j.price)}</span>` : ''}
      <div class="row">${buy}</div>
      <p class="small muted">Buttons open Amazon in a new tab. Prices are my usual Amazon prices.</p>
    </div>`;
  // odd number of pages: the closing note sits on the back of the last leaf, so that leaf can turn too, showing the inside back cover
  b3 = { ry:28, rx:10, open:false, leaf:0, n: leaves.length + (seq.length % 2 === 0 ? 1 : 0) };
  const book = $('#b3'), st = $('#b3stage');
  spineColour(j.cover, s => {
    const avail = Math.min(st.clientWidth || 300, 560), w = Math.round(Math.min(250, avail / 2 - 12)), h = Math.round(w / s.ar);
    book.style.cssText = `--w:${w}px;--h:${h}px;--d:${Math.round(w * .09)}px;--sc:${s.c}`; st.style.height = (h + 70) + 'px'; b3pose(); });
  // drag to turn the closed book round
  let drag = null;
  st.addEventListener('pointerdown', e => { if (b3.open) return; drag = { x:e.clientX, y:e.clientY, ry:b3.ry, rx:b3.rx, moved:false }; st.setPointerCapture(e.pointerId); book.classList.add('grab'); });
  st.addEventListener('pointermove', e => { if (!drag) return; const dx = e.clientX - drag.x, dy = e.clientY - drag.y; if (Math.abs(dx) + Math.abs(dy) > 4) drag.moved = true;
    b3.ry = Math.max(-170, Math.min(60, drag.ry + dx * .5)); b3.rx = Math.max(-25, Math.min(35, drag.rx - dy * .3)); b3pose(); });
  let dragged = false; const end = () => { if (!drag) return; dragged = drag.moved; drag = null; book.classList.remove('grab'); };
  st.addEventListener('pointerup', end); st.addEventListener('pointercancel', () => { drag = null; book.classList.remove('grab'); });
  st.addEventListener('click', e => { if (dragged) { dragged = false; return; } if (!b3.open) return b3go(1); const r = st.getBoundingClientRect(); b3go(e.clientX > r.left + r.width / 2 ? 1 : -1); });
  if (!reduce && matchMedia('(hover:hover)').matches) st.addEventListener('pointermove', e => { if (drag || b3.open) return;
    const r = st.getBoundingClientRect(); book.style.setProperty('--hx', ((e.clientX - r.left) / r.width - .5) * 14 + 'deg'); book.style.setProperty('--hy', ((e.clientY - r.top) / r.height - .5) * -8 + 'deg'); });
  st.addEventListener('pointerleave', () => { book.style.setProperty('--hx', '0deg'); book.style.setProperty('--hy', '0deg'); });
  $('#pNext').addEventListener('click', () => b3go(1));
  $('#pPrev').addEventListener('click', () => b3go(-1));
  $('#pZoom').addEventListener('click', () => { const v = b3view(pages), k = v.right ?? v.left; k != null ? zoom(pages[k], `${j.name}, sample page ${k + 1}`) : zoom(j.cover, `Cover of ${j.name}`); });
}
// which sample pages are showing: left = back of the last turned leaf, right = front of the next one (indexes into pages)
function b3view(pages){ const n = pages.length, L = b3.open ? b3.leaf : 0, at = i => i >= 0 && i < n ? i : null;
  if (L < 1) return { left:null, right:null };
  const li = L >= 2 ? 2 * (L - 2) + 1 : -1, ri = 2 * (L - 1);
  return { left: at(li), right: at(ri) }; }
function b3go(d){
  const max = b3.n; let to = b3.open ? b3.leaf + d : (d > 0 ? 1 : 0);
  if (!b3.open && d > 0) { b3.open = true; b3.leaf = 1; }
  else if (to <= 0) { b3.open = false; b3.leaf = 0; }
  else b3.leaf = Math.min(max, to);
  b3pose(true);
}
function b3pose(turning){
  const book = $('#b3'); if (!book) return; const j = MM.journals[jIdx];
  if (b3.open) { book.style.setProperty('--ry', '0deg'); book.style.setProperty('--rx', '24deg'); book.style.setProperty('--tx', 'calc(var(--w) / 2)'); }
  else { book.style.setProperty('--ry', b3.ry + 'deg'); book.style.setProperty('--rx', b3.rx + 'deg'); book.style.setProperty('--tx', '0px'); }
  book.classList.toggle('open', b3.open);
  // cover is leaf 0, then the pages. Turned leaves stack on the left.
  const all = [book.querySelector('.b3leaf.cover'), ...[...book.querySelectorAll('.b3leaf:not(.cover)')].sort((a,b) => a.dataset.l - b.dataset.l)];
  all.forEach((el, i) => { const turned = i < b3.leaf;
    el.style.setProperty('--a', turned ? '-180deg' : '0deg');
    el.style.setProperty('--z', turned ? `calc(var(--d) / 2 + ${1.5 + i * 1.5}px)` : `calc(var(--d) / 2 - ${i === 0 ? 0 : 1 + i * .6}px)`);
    el.style.zIndex = turned ? 10 + i : 100 - i;
    if (turning && !reduce && i === b3.leaf - 1) { el.classList.remove('turning'); void el.offsetWidth; el.classList.add('turning'); } });
  // only the two facing leaves stay drawn once a turn settles, so leaves underneath can't show through (Chrome and Safari 3D sorting)
  const keep = (lo, hi) => all.forEach((el, i) => { el.style.visibility = i >= lo && i <= hi ? '' : 'hidden'; });
  clearTimeout(b3.t); keep(b3.leaf - 2, b3.leaf + 1);
  b3.t = setTimeout(() => keep(b3.leaf - 1, b3.leaf), turning && !reduce ? 1050 : 0);
  const n = (j.pages || []).length;
  const v = b3view(j.pages || []), shown = [v.left, v.right].filter(x => x != null).map(x => x + 1);
  const what = !b3.open ? 'Cover' : !shown.length ? 'End of the sample' : shown.length === 2 ? `Sample pages ${shown[0]} and ${shown[1]} of ${n}` : `Sample page ${shown[0]} of ${n}`;
  $('#pCtr').textContent = what;
  $('#b3stage').setAttribute('aria-label', !b3.open ? `Cover of ${j.name}` : `${j.name}: ${what.toLowerCase()}`);
  $('#pNext').textContent = !b3.open ? 'Open the book' : 'Next page'; $('#pNext').disabled = b3.open && b3.leaf >= b3.n;
  $('#pPrev').textContent = b3.open && b3.leaf === 1 ? 'Close the book' : 'Previous'; $('#pPrev').disabled = !b3.open;
  $('#pZoom').textContent = shown.length ? 'Enlarge this page' : 'Enlarge the cover';
}
function zoom(src, alt){
  const z = document.createElement('div'); z.className = 'zoom'; z.setAttribute('role','dialog'); z.setAttribute('aria-label', alt);
  z.innerHTML = `<img src="${src}" alt="${esc(alt)}"><button class="back" type="button">Close</button>`;
  const prev = document.activeElement; const done = () => { z.remove(); prev && prev.focus(); };
  z.addEventListener('click', e => { if (e.target === z || e.target.closest('.back')) done(); });
  z.addEventListener('keydown', e => { if (e.key === 'Escape') { e.stopPropagation(); e.preventDefault(); done(); } });
  (sheet.open ? sheet : document.body).appendChild(z); z.querySelector('.back').focus();
}

/* ---------- the reading corner: a shelf of generated spines that fan open as you pass ---------- */
const MON = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const mon = w => w ? MON[+w.slice(5)-1] + ' ' + w.slice(0,4) : '';
let libSel = -1;
const FX0 = Object.assign({ curve:130, gap:14, tilt:7, lift:18, swing:'left', panelSide:'left', widths:'auto' }, MM.shelfFx || {});
let FX = Object.assign({}, FX0); try { Object.assign(FX, JSON.parse(store.get('mm-shelf') || '{}')); } catch(_) {}

/* Each spine is drawn once from its title, so every book gets its own cloth, leather or paper, foil and ornament. */
const hash = s => { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619); } return h >>> 0; };
const rng = seed => () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
const pick = (r, a) => a[Math.floor(r() * a.length)];
const BASES = [ // colour, kind of finish that suits it
  ['#1d2547','cloth'],['#14182e','leather'],['#5a1a22','leather'],['#2c4a3a','cloth'],['#3a2440','cloth'],['#1f3b4d','cloth'],
  ['#111214','paper'],['#7e2a2a','paper'],['#efe6d4','aged'],['#e8dcc6','aged'],['#2f2a26','leather'],['#5b3a29','leather'],
  ['#80615f','cloth'],['#20334a','paper'],['#6b5a2a','cloth'],['#c9a19a','paper'],['#41506b','paper'],['#3b2a1f','leather']];
const FOILS = { gold:['#7a5a22','#e9cf8a','#a9843c','#fff1c4','#8a6628'], silver:['#6d7279','#e7eaee','#9aa1a8','#ffffff','#7c838a'],
  copper:['#6e3a22','#e6a47a','#9c5634','#ffd7bb','#7a4026'] };
const MOTIFS = ['bands','moon','deco','vine','orbit','stars','block','frame'];
const FONTS = [['600','Cormorant Garamond',false],['700','Cinzel',true],['500','Jost',true],['600','Playfair Display',false],['italic 500','Cormorant Garamond',false]];

function spineSize(s){
  const pin = (MM.spinePins || {})[s.series]; const ph = layout === 'phone' ? .78 : 1;
  const r = rng(hash(s.series + 'size'));
  if (pin && (pin.w || pin.h)) return { w:(pin.w || 46) * ph, h:(pin.h || 270) * ph };
  if (FX.widths === 'pinned') return { w:46 * ph, h:270 * ph };
  const n = s.books.length;                                    // auto: thickness follows how many books the series holds
  return { w:Math.round(Math.min(78, 30 + n * 6.5 + r() * 8) * ph), h:Math.round((236 + r() * 52) * ph) };
}

function drawSpine(cv, s, w, h){
  const D = 2, r = rng(hash(s.series)), W = w * D, H = h * D; cv.width = W; cv.height = H;
  const x = cv.getContext('2d'); x.scale(D, D);
  const [base, kind] = BASES[hash(s.series) % BASES.length];
  const light = kind === 'aged' || base === '#c9a19a';
  const foilName = light ? pick(r, ['gold','copper']) : kind === 'leather' ? pick(r, ['gold','gold','silver']) : pick(r, ['gold','gold','gold','silver','copper']);
  const F = FOILS[foilName];
  const motif = kind === 'leather' && r() < .6 ? 'bands' : pick(r, MOTIFS);
  const [fw, fam, caps] = pick(r, FONTS);
  const ink = light ? '#2c2522' : null;                       // pale paper jackets are printed, not foiled
  x.fillStyle = base; x.fillRect(0, 0, w, h);

  // surface: cloth weave, leather grain or paper, then age
  const img = x.getImageData(0, 0, W, H), d = img.data;
  const lo = document.createElement('canvas'); lo.width = Math.max(2, W/5|0); lo.height = Math.max(2, H/5|0);
  const lx = lo.getContext('2d'), ld = lx.createImageData(lo.width, lo.height);
  for (let i = 0; i < ld.data.length; i += 4) { const v = r() * 255; ld.data[i]=ld.data[i+1]=ld.data[i+2]=v; ld.data[i+3]=255; }
  lx.putImageData(ld, 0, 0); const big = document.createElement('canvas'); big.width = W; big.height = H;
  const bx = big.getContext('2d'); bx.imageSmoothingEnabled = true; bx.drawImage(lo, 0, 0, W, H); const low = bx.getImageData(0, 0, W, H).data;
  for (let y = 0; y < H; y++) for (let X = 0; X < W; X++) {
    const i = (y * W + X) * 4; let v = (r() - .5) * 14;
    if (kind === 'cloth') v += (((X >> 1) + (y >> 1)) & 1 ? 7 : -7) + (r() - .5) * 8;
    else if (kind === 'leather') v += (low[i] - 128) * .1 + (r() < .03 ? -18 : 0) + (r() - .5) * 10;
    else if (kind === 'aged') { v += (low[i] - 128) * .06; const e = Math.min(X, W - X, y, H - y) / (W * .5); v -= Math.max(0, 1 - e) * 26; }
    else v *= .5;
    d[i] += v; d[i+1] += v; d[i+2] += v * (kind === 'aged' ? .7 : 1);
  }
  x.putImageData(img, 0, 0); x.setTransform(D, 0, 0, D, 0, 0);
  if (kind === 'aged') for (let k = 0; k < 10; k++) { x.fillStyle = `rgba(140,100,50,${.05 + r() * .08})`; x.beginPath(); x.arc(r() * w, r() * h, .6 + r() * 2.2, 0, 7); x.fill(); }

  // foil: a metallic gradient, debossed into the surface and a little worn
  const foil = document.createElement('canvas'); foil.width = W; foil.height = H; const f = foil.getContext('2d'); f.scale(D, D);
  const paint = () => { if (ink) return ink; const g = f.createLinearGradient(0, 0, w, h * .35); F.forEach((c, i) => g.addColorStop(i / (F.length - 1), c)); return g; };
  f.fillStyle = f.strokeStyle = paint(); f.lineWidth = 1;
  const cx = w / 2;
  const star = (X, Y, R) => { f.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, q = i % 2 ? R * .32 : R; f.lineTo(X + Math.cos(a) * q, Y + Math.sin(a) * q); } f.closePath(); f.fill(); };
  if (motif === 'bands') { for (const t of [.08, .2, .8, .92]) { f.fillRect(4, h * t - 1.5, w - 8, 1); f.fillRect(4, h * t + 2, w - 8, .6);
      x.fillStyle = 'rgba(0,0,0,.28)'; x.fillRect(0, h * t + 3.4, w, 1.6); x.fillStyle = 'rgba(255,255,255,.10)'; x.fillRect(0, h * t - 2.6, w, 1.2); } }
  if (motif === 'moon') { const Y = h * .74, R = Math.min(w * .26, 11); f.beginPath(); f.arc(cx, Y, R, 0, 7); f.fill(); f.globalCompositeOperation = 'destination-out'; f.beginPath(); f.arc(cx + R * .45, Y - R * .2, R * .86, 0, 7); f.fill(); f.globalCompositeOperation = 'source-over';
    for (let k = 0; k < 5; k++) star(6 + r() * (w - 12), h * (.08 + r() * .12), 1.2 + r() * 1.6); }
  if (motif === 'stars') for (let k = 0; k < 12; k++) star(5 + r() * (w - 10), h * (.06 + r() * .9) * (k % 2 ? .25 : 1) + (k % 2 ? h * .7 : 0), .8 + r() * 1.5);
  if (motif === 'deco') { f.strokeRect(4.5, 4.5, w - 9, h - 9); f.strokeRect(7, 7, w - 14, h - 14); for (const t of [.12, .86]) { f.beginPath(); f.moveTo(7, h * t); f.lineTo(cx, h * t - 6); f.lineTo(w - 7, h * t); f.stroke(); } }
  if (motif === 'frame') { f.lineWidth = 1.4; f.strokeRect(3.5, 3.5, w - 7, h - 7); f.lineWidth = .7; f.strokeRect(6, 6, w - 12, h - 12); star(cx, h * .9, 3); }
  if (motif === 'vine') { f.lineWidth = .9; f.beginPath(); for (let y = 6; y < h - 6; y += 2) f.lineTo(cx + Math.sin(y / 14) * (w * .3), y); f.stroke();
    for (let y = 16; y < h - 10; y += 22) { const X = cx + Math.sin(y / 14) * (w * .3), s2 = y % 44 ? 1 : -1; f.beginPath(); f.ellipse(X + s2 * 4, y, 4, 1.8, s2 * .6, 0, 7); f.fill(); }
    x.fillStyle = light ? 'rgba(239,230,212,.85)' : base; }
  if (motif === 'orbit') { const Y = h * .8; f.lineWidth = .7; for (const q of [.3, .42]) { f.beginPath(); f.ellipse(cx, Y, w * q, w * q * .38, -.3, 0, 7); f.stroke(); } f.beginPath(); f.arc(cx, Y, w * .12, 0, 7); f.fill(); star(cx + w * .28, Y - 8, 2); }
  if (motif === 'block') { const g = x.createLinearGradient(0, h * .7, 0, h); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, pick(r, ['rgba(176,144,79,.55)','rgba(128,97,95,.6)','rgba(28,33,64,.7)'])); x.fillStyle = g; x.fillRect(0, h * .62, w, h * .38); }

  // title and author
  const T = caps ? s.series.toUpperCase() : s.series, words = T.split(/\s+/), auth = s.author || '';
  const font = (px) => `${fw} ${px}px "${fam}", Georgia, serif`;
  const titleZone = motif === 'bands' ? [h * .22, h * .78] : motif === 'moon' || motif === 'orbit' ? [h * .1, h * .64] : [h * .08, h * .8];
  const zoneH = titleZone[1] - titleZone[0];
  const stackFit = () => { if (w < 54 || words.length > 5) return 0; f.font = font(10); const long = Math.max(...words.map(t => f.measureText(t).width));
    const px = Math.min(15, 10 * (w - 14) / long); return px >= 9.5 && words.length * px * 1.08 < zoneH ? px : 0; };
  let px = stackFit();
  if (motif === 'bands' && !ink) { x.fillStyle = 'rgba(0,0,0,.25)'; x.fillRect(5, titleZone[0], w - 10, zoneH); }
  if (px) { f.font = font(px); f.textAlign = 'center'; f.textBaseline = 'middle'; const y0 = titleZone[0] + zoneH / 2 - (words.length - 1) * px * .54;
    words.forEach((t, i) => f.fillText(t, cx, y0 + i * px * 1.08)); }
  else { f.save(); f.translate(cx, titleZone[0]); f.rotate(Math.PI / 2); f.textBaseline = 'middle'; f.textAlign = 'left';
    let p2 = Math.min(w * .44, 22); f.font = font(p2); const tw = f.measureText(T).width; if (tw > zoneH * .94) { p2 *= zoneH * .94 / tw; f.font = font(p2); }
    f.fillText(T, (zoneH - f.measureText(T).width) / 2, 0); f.restore(); }
  if (auth) { const last = auth.split(' ').pop().toUpperCase(); f.font = `500 ${Math.min(8.5, w * .17)}px Jost, sans-serif`; f.textAlign = 'center'; f.textBaseline = 'middle';
    if (f.measureText(last).width < w - 8) { f.letterSpacing = '1px'; f.fillText(last, cx, h * (motif === 'bands' ? .86 : .955)); } }

  // wear the foil a little, press it in, then light the rounded spine
  if (!ink) { f.globalCompositeOperation = 'destination-out'; for (let k = 0; k < w * h * .05; k++) { f.fillStyle = `rgba(0,0,0,${r() * .7})`; f.fillRect(r() * w, r() * h, .6, .6); } f.globalCompositeOperation = 'source-over'; }
  x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = .5; x.filter = 'blur(.6px)'; x.globalCompositeOperation = 'multiply'; x.drawImage(foil, 0, 1.2); x.filter = 'none';
  x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.drawImage(foil, 0, 0); x.setTransform(D, 0, 0, D, 0, 0);
  const g = x.createLinearGradient(0, 0, w, 0);
  [[0,'rgba(0,0,0,.55)'],[.07,'rgba(0,0,0,.12)'],[.28,'rgba(255,255,255,.16)'],[.42,'rgba(255,255,255,.04)'],[.75,'rgba(0,0,0,.10)'],[1,'rgba(0,0,0,.6)']].forEach(([o, c]) => g.addColorStop(o, c));
  x.fillStyle = g; x.fillRect(0, 0, w, h);
  const v = x.createLinearGradient(0, 0, 0, h); v.addColorStop(0, 'rgba(0,0,0,.22)'); v.addColorStop(.04, 'rgba(0,0,0,0)'); v.addColorStop(.97, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.3)');
  x.fillStyle = v; x.fillRect(0, 0, w, h);
}

const reviewed = s => MM.reviews.some(r => s.books.some(b => b.title === r.book));
function shelfHTML(){
  return MM.shelf.map((s, i) => { const { w, h } = spineSize(s), n = s.books.length;
    const rv = reviewed(s);
    return `<button type="button" class="spn${rv ? ' rev' : ''}" data-i="${i}" aria-pressed="${i === libSel}" style="--w:${w}px;--h:${h}px" tabindex="${i === Math.max(0, libSel) ? 0 : -1}"
      aria-label="${esc(s.series)} by ${esc(s.author)}, ${n} book${n > 1 ? 's' : ''}${rv ? ', reviewed' : ''}"><canvas width="${w}" height="${h}" aria-hidden="true"></canvas></button>`; }).join('');
}
function paintShelf(row){
  const items = [...row.querySelectorAll('.spn')]; let k = 0;
  const fonts = ['600 12px "Cormorant Garamond"','italic 500 12px "Cormorant Garamond"','700 12px Cinzel','500 12px Jost','600 12px "Playfair Display"'];
  const step = () => { const t = performance.now(); while (k < items.length && performance.now() - t < 12) { const b = items[k], s = MM.shelf[+b.dataset.i], { w, h } = spineSize(s);
      drawSpine(b.querySelector('canvas'), s, w, h); k++; } if (k < items.length) requestAnimationFrame(step); };
  Promise.race([Promise.all(fonts.map(f => document.fonts.load(f))), new Promise(r => setTimeout(r, 1500))]).catch(() => {}).then(step);
}

/* Reading now / Recently finished / Next on my pile. Only shows once Becky fills MM.readingPile in content.js. */
function pileHTML(){
  const P = MM.readingPile || {}, rows = [['now','Reading now'],['finished','Recently finished'],['next','Next on my pile']].filter(([k]) => (P[k] || []).length);
  if (!rows.length) return '';
  return `<div class="pile">${rows.map(([k, t]) => `<div><span class="eyebrow">${t}</span><ul>${P[k].map(b => `<li><strong>${esc(b.title)}</strong>${b.author ? ` <span>by ${esc(b.author)}</span>` : ''}</li>`).join('')}</ul></div>`).join('')}</div>`;
}
function openLibrary(from){
  const total = MM.shelf.reduce((n, s) => n + s.books.length, 0);
  showSheet('The Reading Corner', `
    <h2 class="t">One more chapter. Always.</h2>
    <p class="lead" style="margin-top:10px">My reading log so far: ${total} books from ${MM.shelf.length} series and standalones, newest first. Choose a spine to explore a book. A gold ribbon means I’ve written a review.</p>
    ${pileHTML()}
    <div class="shtools"><label class="sr" for="shq">Search my shelf</label><input type="search" id="shq" placeholder="Search by book, series or author" autocomplete="off" aria-describedby="shqHelp">
      <button type="button" class="btn line" id="shList" aria-pressed="false" aria-controls="slist">List view</button></div>
    <p class="small muted" id="shqHelp">Searching lists the matching books below and highlights their spines on the shelf.</p>
    <div class="slist" id="slist" hidden></div>
    <div class="shelf2"><div class="srow" role="group" aria-label="My bookshelf, scroll sideways for more">${shelfHTML()}</div><div class="sledge" aria-hidden="true"></div></div>
    <div class="rbook" id="rbook" aria-live="polite" hidden></div>
    ${postsHTML()}`, 'lib', from);
  const row = $('#sheetBody .srow'); paintShelf(row); shelfFan(row);
  const q = $('#shq'), lb = $('#shList'), sl = $('#slist'); let listOn = false;
  const pick = i => { libSel = i; const sp = row.querySelectorAll('.spn'); sp.forEach((x, k) => { x.setAttribute('aria-pressed', k === i); x.tabIndex = k === i ? 0 : -1; });
    sp[i]?.scrollIntoView({ block:'nearest', inline:'center', behavior: reduce ? 'auto' : 'smooth' }); row._kick?.(); drawBook(true);
    $('#rbook').scrollIntoView({ block:'start', behavior: reduce ? 'auto' : 'smooth' }); };
  const drawList = () => { const t = q.value.trim().toLowerCase(), show = listOn || !!t; sl.hidden = !show;
    const all = MM.shelf.map((s, i) => ({ s, i, m: !t || [s.series, s.author, ...s.books.map(b => b.title)].some(x => x.toLowerCase().includes(t)) })), hits = all.filter(x => x.m);
    const sp = row.querySelectorAll('.spn'); all.forEach(({ i, m }) => { sp[i]?.classList.toggle('hit', !!t && m); sp[i]?.classList.toggle('miss', !!t && !m); });
    if (t && hits.length) sp[hits[0].i]?.scrollIntoView({ block:'nearest', inline:'center', behavior: reduce ? 'auto' : 'smooth' });
    if (!show) return;
    sl.innerHTML = hits.length ? `<p class="small muted" role="status">${hits.length} of ${MM.shelf.length} on my shelf</p><ul>${hits.map(({ s, i }) => {
        const books = t ? s.books.filter(b => b.title.toLowerCase().includes(t)) : [];
        return `<li><button type="button" data-i="${i}"><span class="sn">${esc(s.series)}</span><span class="sa">${esc(s.author)} · ${s.books.length} book${s.books.length > 1 ? 's' : ''}${reviewed(s) ? ' · <b>Reviewed</b>' : ''}</span>${books.length && !(books.length === 1 && books[0].title === s.series) ? `<span class="sb">${books.map(b => esc(b.title)).join(', ')}</span>` : ''}</button></li>`; }).join('')}</ul>`
      : `<p class="small muted" role="status">Nothing on my shelf matches “${esc(q.value.trim())}”.</p>`; };
  q.addEventListener('input', drawList);
  lb.addEventListener('click', () => { listOn = !listOn; lb.setAttribute('aria-pressed', listOn); lb.textContent = listOn ? 'Hide the list' : 'List view'; drawList(); });
  sl.addEventListener('click', e => { const b = e.target.closest('button[data-i]'); if (b) pick(+b.dataset.i); });
  if (libSel >= 0) drawBook(false);
  $('#sheetBody .posts')?.addEventListener('click', e => { const b = e.target.closest('[data-shelf]'); if (!b) return;
    libSel = +b.dataset.shelf; row.querySelectorAll('.spn').forEach((x, i) => { x.setAttribute('aria-pressed', i === libSel); x.tabIndex = i === libSel ? 0 : -1; });
    row.querySelectorAll('.spn')[libSel]?.scrollIntoView({ block:'nearest', inline:'center', behavior: reduce ? 'auto' : 'smooth' }); row._kick?.();
    drawBook(true); $('#rbook').scrollIntoView({ block:'start', behavior: reduce ? 'auto' : 'smooth' }); });
}

/* newest blog posts under the shelf, straight from the reviews in Pages CMS */
function postsHTML(){
  const list = MM.reviews.slice().sort((a, b) => (b.iso || '').localeCompare(a.iso || ''));
  if (!list.length) return '';
  const stars = n => n ? `<span class="stars" aria-label="${n} out of 5">${'★'.repeat(n)}${'☆'.repeat(5 - n)}</span>` : '';
  return `<section class="posts" aria-labelledby="postsH"><h3 id="postsH">Latest from my reading blog</h3><p class="muted">Newest first.</p><ol>${list.map(r => {
    const si = MM.shelf.findIndex(s => s.books.some(b => b.title === r.book)), au = si >= 0 ? MM.shelf[si].author : '';
    return `<li class="post"><p class="pmeta"><time datetime="${esc(r.iso)}">${esc(r.date)}</time>${stars(r.rating)}${r.spoilers ? '<span class="pill">Contains spoilers</span>' : ''}</p>
      <h4>${esc(r.title)}</h4><p class="rbk"><strong>${esc(r.book)}</strong>${au ? ` by ${esc(au)}` : ''}</p>${r.excerpt ? `<p class="pex">${esc(r.excerpt)}</p>` : ''}
      <p class="row">${si >= 0 ? `<button class="btn line" type="button" data-shelf="${si}">Read it here</button>` : ''}<a class="btn ext quiet" href="${r.url}" target="_blank" rel="noopener" aria-label="${esc(r.title)} on mazomoon.com, opens in a new tab">Open on mazomoon.com</a></p></li>`; }).join('')}</ol></section>`;
}

/* the fan: spines near the pointer lift and lean apart, like fingers walking along the shelf */
function shelfFan(row){
  const items = [...row.querySelectorAll('.spn')]; let px = null, raf = 0, idle = 0;
  const cur = items.map(() => ({ x:0, y:0, r:0 }));
  const frame = () => { raf = 0; let moving = false; const rr = row.getBoundingClientRect();
    items.forEach((b, i) => { const c = cur[i], mid = b.offsetLeft - row.scrollLeft + b.offsetWidth / 2 + rr.left, sel = i === libSel;
      let tx = 0, ty = sel ? -30 : 0, tr = 0;
      if (px !== null) { const dx = mid - px, u = dx / FX.curve, fall = Math.exp(-u * u);
        tx = FX.gap * Math.tanh(dx / (FX.curve * .55)); ty = Math.min(ty, -FX.lift * fall); tr = FX.tilt * 2.33 * u * fall; }
      const k = reduce ? 1 : .2; c.x += (tx - c.x) * k; c.y += (ty - c.y) * k; c.r += (tr - c.r) * k;
      if (Math.abs(tx - c.x) + Math.abs(ty - c.y) + Math.abs(tr - c.r) > .05) moving = true;
      b.style.transform = `translate(${c.x.toFixed(2)}px,${c.y.toFixed(2)}px) rotate(${c.r.toFixed(2)}deg)`; });
    if (moving) raf = requestAnimationFrame(frame); };
  const kick = () => { if (!raf) raf = requestAnimationFrame(frame); };
  row._kick = kick;
  if (reduce) { kick(); return; }
  row.addEventListener('pointermove', e => { if (e.pointerType === 'mouse' || e.pointerType === 'pen') { px = e.clientX; kick(); } });
  row.addEventListener('pointerleave', e => { if (e.pointerType !== 'touch') { px = null; kick(); } });
  row.addEventListener('scroll', () => { if (matchMedia('(hover: none)').matches) { const rr = row.getBoundingClientRect(); px = rr.left + rr.width / 2;
      clearTimeout(idle); idle = setTimeout(() => { px = null; kick(); }, 500); } kick(); }, { passive:true });
  row.addEventListener('focusin', e => { const b = e.target.closest('.spn'); if (!b) return; const rr = b.getBoundingClientRect(); px = rr.left + rr.width / 2; kick(); });
  row.addEventListener('focusout', () => { px = null; kick(); });
  row.addEventListener('wheel', e => { if (Math.abs(e.deltaX) > Math.abs(e.deltaY)) return; const max = row.scrollWidth - row.clientWidth;
    if ((e.deltaY > 0 && row.scrollLeft < max - 1) || (e.deltaY < 0 && row.scrollLeft > 0)) { e.preventDefault(); row.scrollLeft += e.deltaY; } }, { passive:false });
  row.addEventListener('keydown', e => { const b = e.target.closest('.spn'); if (!b) return; const i = items.indexOf(b);
    const j = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1 : -1;
    if (j < 0 || j >= items.length || j === i) return; e.preventDefault(); b.tabIndex = -1; items[j].tabIndex = 0; items[j].focus(); items[j].scrollIntoView({ block:'nearest', inline:'nearest' }); });
  row.addEventListener('click', e => { const b = e.target.closest('.spn'); if (!b) return; libSel = +b.dataset.i;
    items.forEach(x => { x.setAttribute('aria-pressed', x === b); x.tabIndex = x === b ? 0 : -1; }); kick(); drawBook(true); });
}

/* the open book: the series on one page, my reviews on the other */
function drawBook(animate){
  const s = MM.shelf[libSel], el = $('#rbook'); if (!s || !el) return;
  const revs = MM.reviews.filter(r => s.books.some(b => b.title === r.book));
  const dated = s.books.filter(b => b.when).map(b => b.when).sort();
  const rel = ['Dark Romance Reader Stickers','Bookish Witch Stickers','Clip-On Reading Light'].map(n => MM.products.find(p => p.name === n)).filter(Boolean);
  const stars = n => n ? `<span class="stars" aria-label="${n} out of 5">${'★'.repeat(n)}${'☆'.repeat(5 - n)}</span>` : '';
  const toc = `<div class="rpage toc">
      <span class="eyebrow">Pulled off the shelf</span>
      <h3>${esc(s.series)}</h3>
      <p class="muted">${esc(s.author)} · ${s.books.length} book${s.books.length > 1 ? 's' : ''}${dated.length ? ` · ${mon(dated[0])}${dated.length > 1 && dated[dated.length-1] !== dated[0] ? ' to ' + mon(dated[dated.length-1]) : ''}` : ''}</p>
      <ol>${s.books.map(b => { const r = revs.find(v => v.book === b.title);
        return `<li><span>${esc(b.title)}${b.when ? ` <span class="when">${mon(b.when)}</span>` : ''}</span>${r ? `<a href="#rv-${r.slug}" class="rlink">My review</a>` : `<span class="soon">Read</span>`}</li>`; }).join('')}</ol>
      <p class="small muted">Dates are roughly when I started each one, from my Audible history.</p>
    </div>`;
  const nook = `<div class="nook"><span class="eyebrow">For your reading nook</span>
      <div class="rel">${rel.map(p => `<a href="${amz(p.asin)}" target="_blank" rel="noopener" aria-label="${esc(p.name)} on Amazon, opens in a new tab"><img src="${p.img}" alt="" loading="lazy"><span>${esc(p.name)} · ${gbp(p.price)}</span></a>`).join('')}</div></div>`;
  const art = `<div class="rpage art">${revs.length ? revs.map(r => `<article class="prose" id="rv-${r.slug}">
        <span class="eyebrow">My review</span>
        <p class="rbk"><strong>${esc(r.book)}</strong> by ${esc(s.author)}</p>
        <h2>${esc(r.title)}</h2>
        <p class="meta">${stars(r.rating)}<span>${esc(r.date)}</span></p>
        ${r.spoilers ? `<p class="spoil">Contains spoilers.</p>` : ''}
        ${r.html}
        <p><a class="btn ext" href="${r.url}" target="_blank" rel="noopener">Open on mazomoon.com</a></p></article>`).join('<hr>')
      : `<div class="empty"><span class="eyebrow">From my reading log</span><p class="t">Read, not reviewed yet.</p><p class="small">When I write about this one, it will appear here.</p></div>`}</div>`;
  el.hidden = false; el.dataset.side = FX.panelSide; el.dataset.swing = FX.swing;
  el.innerHTML = `<div class="spread">${FX.panelSide === 'right' ? art + toc : toc + art}</div><div class="torch" aria-hidden="true"></div>${nook}
    <button type="button" class="lampbtn" aria-pressed="false">Lights on</button>`;
  if (animate && !reduce) { el.classList.remove('swing'); void el.offsetWidth; el.classList.add('swing'); }
  torch(el);
  if (animate) el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block:'nearest' });
}

/* at night the page is lit only by a torch that follows you */
function torch(el){
  const t = el.querySelector('.torch'), btn = el.querySelector('.lampbtn'); let on = false, tx = .5, ty = .25, x = tx, y = ty, raf = 0;
  const night = () => root.classList.contains('night') && !on;
  const sync = () => { el.classList.toggle('dark', night()); btn.hidden = !root.classList.contains('night'); btn.textContent = on ? 'Reading by torchlight' : 'Lights on'; btn.setAttribute('aria-pressed', on); };
  const paint = () => { raf = 0; x += (tx - x) * (reduce ? 1 : .16); y += (ty - y) * (reduce ? 1 : .16);
    t.style.setProperty('--tx', (x * 100).toFixed(2) + '%'); t.style.setProperty('--ty', (y * 100).toFixed(2) + '%');
    if (Math.abs(tx - x) + Math.abs(ty - y) > .001) raf = requestAnimationFrame(paint); };
  const at = (cx, cy) => { const r = el.getBoundingClientRect(); tx = (cx - r.left) / r.width; ty = (cy - r.top) / r.height; if (!raf) raf = requestAnimationFrame(paint); };
  el.addEventListener('pointermove', e => at(e.clientX, e.clientY));
  el.addEventListener('pointerdown', e => at(e.clientX, e.clientY));
  el.addEventListener('focusin', e => { const r = e.target.getBoundingClientRect(); at(r.left + r.width / 2, r.top + r.height / 2); });
  btn.addEventListener('click', () => { on = !on; sync(); });
  new MutationObserver(sync).observe(root, { attributes:true, attributeFilter:['class'] });
  sync(); paint();
}

/* draft-only controls, so you can try the feel before we fix it */
function drawTune(row){
  const box = $('#tunes'); if (!box) return;
  const rng2 = (k, label, min, max, unit) => `<label>${label}<input type="range" data-k="${k}" min="${min}" max="${max}" value="${FX[k]}"><output>${FX[k]}${unit}</output></label>`;
  const sel = (k, label, opts) => `<label>${label}<select data-k="${k}">${opts.map(([v, t]) => `<option value="${v}"${FX[k] === v ? ' selected' : ''}>${t}</option>`).join('')}</select></label>`;
  box.innerHTML = rng2('curve','Curve',40,280,'px') + rng2('gap','Gap',0,40,'px') + rng2('tilt','Tilt',0,20,'°') + rng2('lift','Hover lift',0,44,'px')
    + sel('swing','Swing direction',[['left','From the left'],['right','From the right']]) + sel('panelSide','Book list',[['left','Left page'],['right','Right page']])
    + sel('widths','Spine sizes',[['auto','Auto, from book count'],['pinned','Pinned']]) + `<button type="button" class="btn ghost" data-reset>Reset</button>`;
  const save = () => store.set('mm-shelf', JSON.stringify(FX));
  box.oninput = box.onchange = e => { const k = e.target.dataset.k; if (!k) return; const v = e.target.type === 'range' ? +e.target.value : e.target.value;
    if (FX[k] === v) return; FX[k] = v; save();
    if (e.target.type === 'range') { e.target.nextElementSibling.textContent = v + ({ tilt:'°' }[k] || 'px'); row._kick(); }
    else if (k === 'widths') openLibrary();
    else if (libSel >= 0) drawBook(true); };
  box.onclick = e => { if (!e.target.closest('[data-reset]')) return; FX = Object.assign({}, FX0); save(); openLibrary(); };
}

/* ---------- the shop ---------- */
let shopCat = 'all';
function shopItems(){
  const J = MM.journals.map(j => ({ name:j.name, line:j.line, price:j.soon?null:j.price, from:!!j.hardcover, asin:j.asin, soon:j.soon, img:j.cover, page:(j.pages || [])[0], cover:true, ji:MM.journals.indexOf(j), cat:j.colouring?'colouring':'journals' }));
  return J.concat(MM.products.map(p => ({ ...p })));
}
// a category whose every item is still on its way says so in its name
function catName(c){ const it = c.id === 'all' ? [] : shopItems().filter(x => x.cat === c.id); return c.name + (it.length && it.every(x => x.soon) ? ' (coming soon)' : ''); }
function openShop(from){
  showSheet('Shop Mazo Moon', `
    <h2 class="t">Discover the Mazo Moon collection.</h2>
    <p class="lead" style="margin-top:10px">Shop securely on Amazon, where you’ll find the latest prices, delivery options and returns information.</p>
    <div class="chips" role="group" aria-label="Filter the shop">${MM.categories.map(c => `<button type="button" data-c="${c.id}" aria-pressed="${c.id===shopCat}">${esc(catName(c))}</button>`).join('')}</div>
    <div id="shopTip"></div>
    <div class="grid" id="shopGrid"></div>
    <p class="note">Buttons open Amazon in a new tab. Prices are my usual Amazon prices, and Amazon always shows the latest price and delivery. <a href="${MM.store}" target="_blank" rel="noopener" class="ext">See my Amazon storefront</a></p>`, '', from);
  $('#sheetBody .chips').addEventListener('click', e => { const b = e.target.closest('button[data-c]'); if (!b) return; shopCat = b.dataset.c;
    $('#sheetBody .chips').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b)); drawShop(); });
  drawShop();
}
function drawShop(){
  const items = shopItems().filter(x => shopCat === 'all' || x.cat === shopCat || (shopCat === 'books' && (x.cat === 'journals' || x.cat === 'colouring')));
  $('#shopTip').innerHTML = shopCat === 'pens' ? `<p class="note tip">Want to see the colours first? <button class="quiet" type="button" id="toDoodle">Try them in the doodle pad</button></p>` : '';
  $('#toDoodle')?.addEventListener('click', () => openDoodle());
  $('#shopGrid').innerHTML = items.map(x => `
    <article class="card">
      ${x.cover ? `<div class="im cv sb3w" tabindex="-1"><span class="sb3"><span class="sb3pg"${x.page ? ` style="background-image:url('${x.page}')"` : ''}></span><span class="sb3cv"><img src="${x.img}" alt="${esc(x.name)}" loading="lazy"><i class="sb3in" aria-hidden="true"></i></span></span></div>`
        : `<div class="im"><img src="${x.img}" alt="${esc(x.name)}" loading="lazy"></div>`}
      <h3>${esc(x.name)}</h3><p>${esc(x.line)}</p>
      ${x.colours ? `<div class="sws" role="group" aria-label="Colours">${x.colours.map(c => `<a href="${amz(c.asin)}" target="_blank" rel="noopener" style="--c:${c.swatch}" title="${esc(c.name)}" aria-label="${esc(x.name)}, ${esc(c.name)}, on Amazon"></a>`).join('')}</div>` : ''}
      <div class="meta">${x.price ? `<b>${x.from?'From ':''}${gbp(x.price)}</b>` : '<span></span>'}<small>${x.soon ? 'Coming soon' : 'Sold on Amazon'}</small></div>
      ${x.soon || !x.asin ? `<span class="btn line" aria-disabled="true">Coming soon to Amazon</span>` : `<a class="btn ext" href="${amz(x.asin)}" target="_blank" rel="noopener" aria-label="Buy ${esc(x.name)} on Amazon, opens in a new tab">Buy on Amazon</a>`}
      ${x.cover ? `<button class="btn line look" type="button" data-ji="${x.ji}" aria-label="Look inside ${esc(x.name)}">Look inside</button>` : ''}
    </article>`).join('');
  $('#shopGrid').querySelectorAll('.look').forEach(b => b.addEventListener('click', () => { jIdx = +b.dataset.ji; jPage = 0; openJournals(); }));
  // touch screens have no hover, so a tap on the cover opens and closes the book
  $('#shopGrid').onclick = e => { const w = e.target.closest('.sb3w'); if (!w || matchMedia('(hover:hover)').matches) return;
    $('#shopGrid').querySelectorAll('.sb3w.on').forEach(x => x !== w && x.classList.remove('on')); w.classList.toggle('on'); };
}

/* ---------- mug: what's on my desk ---------- */
function openMug(){
  const d = new Date(); const date = d.toLocaleDateString('en-GB', { day:'numeric', month:'long', year:'numeric' });
  $('#slipBody').innerHTML = `<div class="receipt">
    <button class="back x" type="button" data-close aria-label="Back to the desk">Close</button>
    <div class="top"><b id="slipTitle">MAZO MOON</b><span>what’s on Becky’s desk</span><span>Yorkshire · ${date}</span></div>
    <dl>${MM.deskNote.map(n => `<div><dt>${esc(n.label)}</dt><dd class="${/^\[.*\]$/.test(n.text)?'ph':''}">${esc(n.text)}</dd></div>`).join('')}</dl>
    <div class="top" style="border:0;border-top:1px dashed #cfc6bb;padding:14px 0 0">thank you for stopping by<span class="sig">Becky x</span></div>
  </div>`;
  slip.showModal();
}

/* ---------- envelope: letters and contact ---------- */
/* Mailchimp sign-up. The thank-you only shows once Mailchimp itself says the sign-up worked. If the page can't talk to
   Mailchimp directly (for example inside this private preview), the sign-up opens on Mailchimp's own page in a new tab instead. */
function subscribe(email, fname, done){
  const C = MM.mailchimp; if (!C || !C.post) return done({ ok:false, msg:'Sign-up isn’t set up yet. Please email me instead.' });
  const clean = h => String(h || '').replace(/<[^>]*>/g, '').replace(/^\d+\s*-\s*/, '').replace(/\s+/g, ' ').trim();
  const cb = 'mmc' + Date.now().toString(36), sc = document.createElement('script'); let over = false;
  const finish = r => { if (over) return; over = true; clearTimeout(tm); sc.remove(); try { delete window[cb]; } catch(_) { window[cb] = undefined; } done(r); };
  const handoff = () => { const f = document.createElement('form'); f.method = 'post'; f.action = C.post; f.target = '_blank'; f.hidden = true;
    [['EMAIL', email], ['FNAME', fname], [C.bot, '']].forEach(([n, v]) => { const i = document.createElement('input'); i.name = n; i.value = v; f.appendChild(i); });
    document.body.appendChild(f); f.submit(); f.remove();
    finish({ ok:false, handoff:true, msg:'Mailchimp has opened in a new tab to finish your sign-up. Please check that tab to see whether it worked.' }); };
  window[cb] = d => { const msg = clean(d && d.msg);
    if (d && d.result === 'success') { window.mmTrack && mmTrack('sign_up', { method: 'newsletter', form_location: 'desk_letter' }); finish({ ok:true, msg: msg || 'Thank you, you’re signed up.' }); }
    else finish({ ok:false, msg: /already subscribed/i.test(msg) ? 'That email is already on my list, so you’re all set.' : (msg || 'Something went wrong. Please try again, or email me.') }); };
  const q = new URLSearchParams({ EMAIL:email, FNAME:fname, [C.bot]:'', c:cb });
  sc.src = C.post.replace('/subscribe/post?', '/subscribe/post-json?') + '&' + q.toString();
  sc.onerror = handoff;
  const tm = setTimeout(() => finish({ ok:false, msg:'I couldn’t reach Mailchimp just now. Please try again in a moment, or email me.' }), 12000);
  document.head.appendChild(sc);
}
function openLetter(){
  $('#slipBody').innerHTML = `<div class="letter">
    <div class="row" style="justify-content:space-between"><span class="eyebrow">Letters & contact</span><button class="back" type="button" data-close>Back to the desk</button></div>
    <h2 id="slipTitle">Dear you,</h2>
    <p class="muted">Once a month I send a short letter with new designs, what I’m reading and the odd offer. Or just say hello.</p>
    <div class="tabs2" role="group" aria-label="Choose"><button type="button" aria-pressed="true" data-t="news">Monthly letter</button><button type="button" aria-pressed="false" data-t="hello">Say hello</button></div>
    <form id="lf" novalidate>
      <div id="lfFields"></div>
      <button class="btn" type="submit" id="lfGo">Send</button>
      <p class="lfmsg" id="lfMsg" role="status" aria-live="polite"></p>
      <p class="small muted" id="lfNote"></p>
    </form>
    <p class="small muted">Or email me at <a href="mailto:${esc(MM.email)}">${esc(MM.email)}</a></p>
  </div>`;
  let tab = 'news', busy = false;
  const draw = t => { tab = t; $('#lfMsg').textContent = ''; $('#lfMsg').className = 'lfmsg'; $('#lfFields').innerHTML = t === 'news'
      ? `<label for="lfF">First name <span class="muted">(optional)</span></label><input id="lfF" autocomplete="given-name"><label for="lfE">Your email</label><input id="lfE" type="email" autocomplete="email" required>`
      : `<label for="lfN">Your name</label><input id="lfN" autocomplete="name" required><label for="lfE">Your email</label><input id="lfE" type="email" autocomplete="email" required><label for="lfM">Your message</label><textarea id="lfM" required></textarea>`;
    $('#lfGo').textContent = t === 'news' ? 'Sign me up' : 'Send my note'; $('#lfGo').disabled = false;
    $('#lfNote').innerHTML = t === 'news'
      ? `I’ll only use your email to send my monthly letter, through Mailchimp. Every letter has an unsubscribe link. <a href="${MM.site}/privacy/" target="_blank" rel="noopener">Privacy notice</a>`
      : `Your note comes straight to my inbox, and I’ll only use your details to reply. <a href="${MM.site}/privacy/" target="_blank" rel="noopener">Privacy notice</a>`; };
  draw('news');
  $('#slipBody .tabs2').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; $('#slipBody .tabs2').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b)); draw(b.dataset.t); });
  const say = (t, kind) => { const m = $('#lfMsg'); m.textContent = t; m.className = 'lfmsg' + (kind ? ' ' + kind : ''); };
  $('#lf').addEventListener('submit', e => { e.preventDefault(); if (busy) return;
    if (tab !== 'news') { const nm = $('#lfN'), em2 = $('#lfE'), msg = $('#lfM');
      for (const [el, ok, t] of [[nm, nm.value.trim(), 'Please add your name.'], [em2, /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(em2.value.trim()), 'Please check your email address.'], [msg, msg.value.trim().length >= 10, 'Please write a little more in your message.']]) {
        if (!ok) { say(t, 'err'); el.setAttribute('aria-invalid', 'true'); el.focus(); return; } el.removeAttribute('aria-invalid'); }
      busy = true; $('#lfGo').disabled = true; say('Sending your note…');
      const fd = new FormData(); fd.append('name', nm.value.trim()); fd.append('email', em2.value.trim()); fd.append('message', msg.value.trim());
      fd.append('_subject', 'New message from the Mazo Moon desk'); fd.append('_template', 'table'); fd.append('_captcha', 'false');
      const fail = () => { busy = false; $('#lfGo').disabled = false; say(`Sorry, that didn’t send. Please email me at ${MM.email} instead.`, 'err'); };
      const ctl = 'AbortController' in window ? new AbortController() : null, tm = setTimeout(() => ctl && ctl.abort(), 15000);
      fetch('https://formsubmit.co/ajax/' + MM.email, { method: 'POST', headers: { Accept: 'application/json' }, body: fd, signal: ctl && ctl.signal })
        .then(r => r.json()).then(j => { clearTimeout(tm); if (String(j.success) !== 'true') throw 0; busy = false;
          say('Thank you, your note is on its way. I’ll get back to you as soon as I can.', 'ok'); $('#lfGo').textContent = 'Sent'; nm.value = msg.value = ''; })
        .catch(() => { clearTimeout(tm); fail(); });
      return; }
    const em = $('#lfE'), fn = $('#lfF'), email = em.value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { say('Please check your email address.', 'err'); em.setAttribute('aria-invalid', 'true'); em.focus(); return; }
    em.removeAttribute('aria-invalid'); busy = true; $('#lfGo').disabled = true; say('Signing you up…');
    subscribe(email, fn.value.trim(), r => { busy = false; $('#lfGo').disabled = false;
      if (r.ok) { say(r.msg, 'ok'); $('#lfGo').textContent = /confirm/i.test(r.msg) ? 'Check your inbox' : 'Signed up'; $('#lfGo').disabled = true; }
      else if (r.handoff) say(r.msg);
      else { say(r.msg, 'err'); em.focus(); } }); });
  slip.showModal();
}

/* ---------- peelable stickers: a corner lifts and folds back, showing the paper backing ---------- */
const peelHTML = src => `<span class="peel" data-src="${src}"><img src="${src}" alt="" draggable="false"><span class="flap"><span class="fc"><i class="fb" style="-webkit-mask-image:url('${src}');mask-image:url('${src}')"></i></span></span></span>`;
function setPeel(pe, p, corner){
  const img = pe.firstElementChild, W = img.offsetWidth, H = img.offsetHeight; if (!W || !H) return;
  corner = corner || pe.dataset.corner || 'br'; pe.dataset.corner = corner; pe.dataset.p = p;
  const fc = pe.querySelector('.fc'), fb = pe.querySelector('.fb'), flap = pe.querySelector('.flap');
  if (p <= 0.001) { img.style.clipPath = ''; flap.style.display = 'none'; return; }
  flap.style.display = '';
  const cx = corner[1] === 'r' ? W : 0, cy = corner[0] === 'b' ? H : 0, nx = cx ? 1 : -1, ny = cy ? 1 : -1;
  const s = p * Math.min(W, H) * 0.9, k = nx * cx + ny * cy - s;
  const A = [cx - nx * s, cy], B = [cx, cy - ny * s], C = [cx - nx * s, cy - ny * s];
  const rect = [[0,0],[W,0],[W,H],[0,H]], ci = rect.findIndex(q => q[0] === cx && q[1] === cy);
  const pts = []; rect.forEach((q, i) => { if (i === ci) { const prev = rect[(i + 3) % 4]; const first = prev[0] === cx ? B : A; pts.push(first, first === A ? B : A); } else pts.push(q); });
  img.style.clipPath = `polygon(${pts.map(q => q[0].toFixed(1) + 'px ' + q[1].toFixed(1) + 'px').join(',')})`;
  fc.style.clipPath = `polygon(${[A,B,C].map(q => q[0].toFixed(1) + 'px ' + q[1].toFixed(1) + 'px').join(',')})`;
  fb.style.width = W + 'px'; fb.style.height = H + 'px';
  fb.style.transform = `matrix(0,${-nx*ny},${-nx*ny},0,${(k*nx).toFixed(2)},${(k*ny).toFixed(2)})`;
  fb.style.setProperty('--fa', `${Math.atan2(-ny, -nx) * 180 / Math.PI + 90}deg`);
  flap.style.filter = `drop-shadow(${-nx*2}px ${-ny*2}px ${2 + p*5}px rgba(0,0,0,${.22 + p*.18}))`;
}
function animPeel(pe, to, ms, corner){
  if (reduce) return setPeel(pe, to, corner);
  const from = +pe.dataset.p || 0, t0 = performance.now(); cancelAnimationFrame(pe._raf);
  const step = t => { const k = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - k, 3); setPeel(pe, from + (to - from) * e, corner); if (k < 1) pe._raf = requestAnimationFrame(step); };
  pe._raf = requestAnimationFrame(step);
}
function nearCorner(el, e){
  const r = el.getBoundingClientRect(), x = e.clientX - (r.left + r.width / 2), y = e.clientY - (r.top + r.height / 2);
  const t = (parseFloat(getComputedStyle(el).getPropertyValue('--r')) || 0) * -Math.PI / 180, lx = x * Math.cos(t) - y * Math.sin(t), ly = x * Math.sin(t) + y * Math.cos(t);
  return (ly > 0 ? 'b' : 't') + (lx > 0 ? 'r' : 'l');
}
function peelable(el, pe, hoverP){
  el.addEventListener('pointerenter', e => { if (e.pointerType === 'mouse') animPeel(pe, hoverP, 220, nearCorner(el, e)); });
  el.addEventListener('pointermove', e => { if (e.pointerType !== 'mouse' || el.classList.contains('lift')) return; const c = nearCorner(el, e); if (c !== pe.dataset.corner) { setPeel(pe, 0); animPeel(pe, hoverP, 160, c); } });
  el.addEventListener('pointerleave', () => { if (!el.classList.contains('lift')) animPeel(pe, 0, 200); });
}

/* ---------- sticker playground ---------- */
const SURF = { journal:'Journal cover', laptop:'Laptop lid', bottle:'Water bottle' };
let stPack = 0, stSurf = 'journal', stSel = -1;
let placed = (() => { try { const v = JSON.parse(store.get('mm-stickers') || '{}'); return v && typeof v === 'object' ? v : {}; } catch(_) { return {}; } })();
const saveSt = () => store.set('mm-stickers', JSON.stringify(placed));
const cut = id => `/desk/img/cut/${id}.webp`;
const curSt = () => (placed[stSurf] = placed[stSurf] || []);
function openStickers(from){
  showSheet('Sticker playground', `
    <h2 class="t">Decorate something.</h2>
    <p class="lead" style="margin-top:10px">Peel a sticker off the sheet and stick it down. Pick one up again to move it, turn it, resize it or peel it off.</p>
    <div class="play">
      <div class="playL">
        <div class="chips" id="surfs" role="group" aria-label="What to decorate">${Object.entries(SURF).map(([k,v]) => `<button type="button" data-s="${k}" aria-pressed="${k===stSurf}">${v}</button>`).join('')}</div>
        <div class="bwrap"><div class="board" id="board" role="group" aria-label="${SURF[stSurf]} with your stickers"></div></div>
        <div class="tools" id="stTools" role="group" aria-label="Selected sticker">
          <button class="btn line sm" type="button" data-t="l" aria-label="Turn left">↺ Turn</button>
          <button class="btn line sm" type="button" data-t="r" aria-label="Turn right">Turn ↻</button>
          <button class="btn line sm" type="button" data-t="+">Bigger</button>
          <button class="btn line sm" type="button" data-t="-">Smaller</button>
          <button class="btn line sm" type="button" data-t="x">Peel off</button>
        </div>
        <p class="small muted" id="stHelp">With a keyboard: Tab to a sticker, move it with the arrow keys, R to turn, + and − to resize, Delete to peel it off.</p>
      </div>
      <div class="playR">
        <div class="chips" id="packs" role="group" aria-label="Sticker pack">${MM.stickerPacks.map((p,i) => `<button type="button" data-p="${i}" aria-pressed="${i===stPack}">${esc(p.name.replace(' Stickers',''))}</button>`).join('')}</div>
        <div class="tray" id="tray" role="group" aria-label="Stickers to add"></div>
        <div class="row" id="packBuy"></div>
        <div class="row" style="margin-top:8px"><button class="btn line" type="button" id="stReset">Start again</button><button class="btn" type="button" id="stSave">Save as a picture</button></div>
        <p class="small muted" id="stMsg" aria-live="polite">Your design is kept in this browser only.</p>
      </div>
    </div>`, 'wide', from);
  $('#surfs').addEventListener('click', e => { const b = e.target.closest('button[data-s]'); if (!b) return; stSurf = b.dataset.s; stSel = -1;
    $('#surfs').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b)); drawBoard(); });
  $('#packs').addEventListener('click', e => { const b = e.target.closest('button[data-p]'); if (!b) return; stPack = +b.dataset.p;
    $('#packs').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b)); drawTray(); });
  $('#tray').addEventListener('click', e => { const b = e.target.closest('button[data-id]'); if (!b || b._dragged) return;
    const L = curSt(); L.push({ id:b.dataset.id, x:30 + Math.random()*40, y:30 + Math.random()*40, r:Math.round(Math.random()*24 - 12), s:stSurf === 'bottle' ? 46 : 26 });
    stSel = L.length - 1; saveSt(); drawBoard(true); $('#stMsg').textContent = 'Stuck on. Drag it to move it.'; });
  $('#stTools').addEventListener('click', e => { const b = e.target.closest('button[data-t]'); if (b) tool(b.dataset.t); });
  $('#stReset').addEventListener('click', () => { placed[stSurf] = []; stSel = -1; saveSt(); drawBoard(); $('#stMsg').textContent = 'All peeled off.'; });
  $('#stSave').addEventListener('click', saveStickers);
  drawTray(); drawBoard();
}
function drawTray(){
  const P = MM.stickerPacks[stPack];
  $('#tray').innerHTML = P.stickers.map(id => `<button type="button" data-id="${id}" aria-label="Add the ${esc((MM.stickerNames || {})[id] || 'sticker')} sticker, from ${esc(P.name)}">${peelHTML(cut(id))}</button>`).join('');
  $('#tray').querySelectorAll('button').forEach(b => { const pe = b.querySelector('.peel'); peelable(b, pe, .22); trayDrag(b); });
  $('#packBuy').innerHTML = `<a class="btn ext" href="${amz(P.asin)}" target="_blank" rel="noopener" aria-label="Buy ${esc(P.name)} on Amazon, opens in a new tab">Buy this pack on Amazon</a>`;
}
function trayDrag(b){
  b.addEventListener('pointerdown', e => {
    if (e.button) return; const sx = e.clientX, sy = e.clientY; let ghost = null;
    const mv = ev => {
      if (!ghost) { if (Math.hypot(ev.clientX - sx, ev.clientY - sy) < 8) return;
        ghost = document.createElement('div'); ghost.className = 'ghost'; ghost.innerHTML = peelHTML(cut(b.dataset.id)); sheet.appendChild(ghost);
        ghost.style.width = b.offsetWidth + 'px'; requestAnimationFrame(() => setPeel(ghost.firstElementChild, .42, 'tl')); b.classList.add('taken'); }
      const sr = sheet.getBoundingClientRect(); ghost.style.transform = `translate(${ev.clientX - sr.left - b.offsetWidth * .3}px,${ev.clientY - sr.top - b.offsetWidth * .3}px) rotate(-6deg)`; };
    const up = ev => { removeEventListener('pointermove', mv); removeEventListener('pointerup', up); removeEventListener('pointercancel', up);
      if (!ghost) return; ghost.remove(); b.classList.remove('taken'); b._dragged = true; setTimeout(() => b._dragged = false, 50);
      const r = $('#board').getBoundingClientRect();
      if (ev.type === 'pointerup' && ev.clientX > r.left && ev.clientX < r.right && ev.clientY > r.top && ev.clientY < r.bottom) {
        const L = curSt(); L.push({ id:b.dataset.id, x:(ev.clientX - r.left) / r.width * 100, y:(ev.clientY - r.top) / r.height * 100, r:Math.round(Math.random()*16 - 8), s:stSurf === 'bottle' ? 46 : 26 });
        stSel = L.length - 1; saveSt(); drawBoard(true); $('#stMsg').textContent = 'Stuck on. Drag it to move it.'; } };
    addEventListener('pointermove', mv); addEventListener('pointerup', up); addEventListener('pointercancel', up);
  });
}
const stName = id => { const n = (MM.stickerNames || {})[id]; return n ? `${n} sticker` : 'Sticker'; };
function drawBoard(focusSel){
  const bd = $('#board'); bd.className = 'board s-' + stSurf; bd.setAttribute('aria-label', `${SURF[stSurf]} with your stickers`);
  const L = curSt();
  bd.innerHTML = (L.length ? '' : `<span class="empty">Tap a sticker, or drag one here.</span>`) + L.map((t,i) => `<button type="button" class="stk${i===stSel?' sel':''}" data-i="${i}" style="left:${t.x}%;top:${t.y}%;width:${t.s}%;--r:${t.r}deg" aria-label="${esc(stName(t.id))}, ${i+1} of ${L.length}${i===stSel?', selected':''}" aria-pressed="${i===stSel}">${peelHTML(cut(t.id))}</button>`).join('');
  $('#stTools').classList.toggle('off', stSel < 0);
  $('#stTools').querySelectorAll('button').forEach(b => b.disabled = stSel < 0);
  bd.querySelectorAll('.stk').forEach(el => {
    const pe = el.querySelector('.peel'); peelable(el, pe, .16);
    el.addEventListener('pointerdown', e => { animPeel(pe, .5, 260, nearCorner(el, e));
      const i = +el.dataset.i; if (stSel !== i) { stSel = i; markSel(); }
      const r = bd.getBoundingClientRect(), t = curSt()[i], ox = e.clientX, oy = e.clientY, sx = t.x, sy = t.y; let moved = false;
      el.setPointerCapture(e.pointerId); el.classList.add('lift');
      const mv = ev => { const dx = (ev.clientX - ox) / r.width * 100, dy = (ev.clientY - oy) / r.height * 100; if (Math.abs(dx) + Math.abs(dy) > .5) moved = true;
        t.x = Math.max(0, Math.min(100, sx + dx)); t.y = Math.max(0, Math.min(100, sy + dy)); el.style.left = t.x + '%'; el.style.top = t.y + '%'; };
      const up = () => { el.removeEventListener('pointermove', mv); el.removeEventListener('pointerup', up); el.removeEventListener('pointercancel', up); el.classList.remove('lift'); animPeel(pe, 0, 320);
        if (!reduce) { el.classList.remove('press'); void el.offsetWidth; el.classList.add('press'); } if (moved) saveSt(); };
      el.addEventListener('pointermove', mv); el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
    });
    el.addEventListener('focus', () => { const i = +el.dataset.i; if (stSel !== i) { stSel = i; markSel(); } });
    el.addEventListener('keydown', e => {
      const t = curSt()[+el.dataset.i], st = e.shiftKey ? 6 : 2; let hit = true;
      if (e.key === 'ArrowLeft') t.x = Math.max(0, t.x - st); else if (e.key === 'ArrowRight') t.x = Math.min(100, t.x + st);
      else if (e.key === 'ArrowUp') t.y = Math.max(0, t.y - st); else if (e.key === 'ArrowDown') t.y = Math.min(100, t.y + st);
      else if (e.key === 'r' || e.key === 'R') { tool(e.shiftKey ? 'l' : 'r'); return e.preventDefault(); }
      else if (e.key === '+' || e.key === '=') { tool('+'); return e.preventDefault(); }
      else if (e.key === '-' || e.key === '_') { tool('-'); return e.preventDefault(); }
      else if (e.key === 'Delete' || e.key === 'Backspace') { tool('x'); return e.preventDefault(); }
      else hit = false;
      if (hit) { e.preventDefault(); el.style.left = t.x + '%'; el.style.top = t.y + '%'; saveSt(); }
    });
  });
  if (focusSel && stSel >= 0) bd.querySelector(`.stk[data-i="${stSel}"]`)?.focus({ preventScroll:true });
}
function markSel(){ const L = curSt();
  $('#board').querySelectorAll('.stk').forEach(x => { const on = +x.dataset.i === stSel; x.classList.toggle('sel', on); x.setAttribute('aria-pressed', on);
    x.setAttribute('aria-label', `${stName(L[+x.dataset.i].id)}, ${+x.dataset.i + 1} of ${L.length}${on ? ', selected' : ''}`); });
  $('#stTools').classList.toggle('off', stSel < 0); $('#stTools').querySelectorAll('button').forEach(b => b.disabled = stSel < 0); }
function tool(t){
  const L = curSt(), s = L[stSel]; if (!s) return;
  if (t === 'l') s.r -= 15; else if (t === 'r') s.r += 15;
  else if (t === '+') s.s = Math.min(80, s.s + 4); else if (t === '-') s.s = Math.max(10, s.s - 4);
  else if (t === 'x') { L.splice(stSel, 1); stSel = -1; saveSt(); drawBoard(); $('#stMsg').textContent = 'Peeled off.'; $('#tray button')?.focus(); return; }
  saveSt(); drawBoard(true);
}
function saveStickers(){
  const bd = $('#board'), r = bd.getBoundingClientRect(), k = 2, c = document.createElement('canvas');
  c.width = Math.round(r.width * k); c.height = Math.round(r.height * k); const g = c.getContext('2d');
  const cs = getComputedStyle(bd); g.fillStyle = cs.backgroundColor || '#2b2f45';
  const rad = parseFloat(cs.borderTopRightRadius) * k || 0; g.beginPath(); g.roundRect ? g.roundRect(0, 0, c.width, c.height, rad) : g.rect(0, 0, c.width, c.height); g.fill(); g.save(); g.clip();
  bd.querySelectorAll('.stk').forEach(el => { const t = curSt()[+el.dataset.i], im = el.querySelector('img'); if (!im.complete || !im.naturalWidth) return;
    const w = t.s / 100 * c.width, h = w * im.naturalHeight / im.naturalWidth;
    g.save(); g.translate(t.x / 100 * c.width, t.y / 100 * c.height); g.rotate(t.r * Math.PI / 180); g.shadowColor = 'rgba(0,0,0,.25)'; g.shadowBlur = 8 * k; g.shadowOffsetY = 3 * k;
    g.drawImage(im, -w/2, -h/2, w, h); g.restore(); });
  g.restore(); g.fillStyle = 'rgba(255,255,255,.7)'; g.font = `${12*k}px Jost, sans-serif`; g.textAlign = 'right'; g.fillText('mazomoon.com', c.width - 12*k, c.height - 12*k);
  c.toBlob(b => { if (!b) { $('#stMsg').textContent = 'Sorry, this browser could not make the picture.'; return; }
    const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = `mazo-moon-${stSurf}-stickers.png`; document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000); $('#stMsg').textContent = 'Picture made. Check your downloads.'; }, 'image/png');
}

/* ---------- doodle pad ---------- */
const PATTERNS = [['Stars','#c9a24a'],['Hearts','#c98f7e'],['Dots','#6b7a5e']];
let dPen = 'gel', dCol = 0, strokes = [];
function penColours(){
  if (dPen === 'gel') return MM.products.find(p => p.name.startsWith('Gel Pen Set')).colours.map(c => [c.name, c.swatch, c.asin]);
  if (dPen === 'pattern') return PATTERNS.map(p => [p[0], p[1]]);
  return MM.doodlePens.find(p => p.id === 'brush').colours;
}
function openDoodle(from){
  showSheet('Try a little doodle', `
    <h2 class="t">A page to doodle on.</h2>
    <p class="lead" style="margin-top:10px">Pick a pen and a colour and have a go. Nothing is saved or sent anywhere unless you save the picture yourself.</p>
    <div class="dwrap">
      <div class="dctl">
        <span class="eyebrow">Pen</span>
        <div class="chips" id="dPens" role="group" aria-label="Pen">${MM.doodlePens.map(p => `<button type="button" data-p="${p.id}" aria-pressed="${p.id===dPen}">${esc(p.name.split(',')[0])}</button>`).join('')}</div>
        <span class="eyebrow" id="dColLab">Colour</span>
        <div class="sws big" id="dCols" role="radiogroup" aria-labelledby="dColLab"></div>
        <p class="small" id="dBuy"></p>
        <div class="row"><button class="btn line" type="button" id="dUndo">Undo</button><button class="btn line" type="button" id="dClear">Clear the page</button><button class="btn" type="button" id="dSave">Save as a picture</button></div>
        <p class="small muted">Drawing needs a mouse, finger or stylus. The colours are the real ones from each set, as close as a screen can show them.</p>
      </div>
      <div class="pad"><canvas id="padC" role="img" aria-label="Doodle pad"></canvas></div>
    </div>`, 'wide', from);
  $('#dPens').addEventListener('click', e => { const b = e.target.closest('button[data-p]'); if (!b) return; dPen = b.dataset.p; dCol = 0;
    $('#dPens').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b)); drawCols(); });
  $('#dCols').addEventListener('click', e => { const b = e.target.closest('button[data-c]'); if (!b) return; dCol = +b.dataset.c; drawCols(); $(`#dCols button[data-c="${dCol}"]`)?.focus(); });
  $('#dUndo').addEventListener('click', () => { strokes.pop(); redraw(); });
  $('#dClear').addEventListener('click', () => { strokes = []; redraw(); });
  $('#dSave').addEventListener('click', () => { const cv = $('#padC'), o = document.createElement('canvas'); o.width = cv.width; o.height = cv.height; const g = o.getContext('2d');
    g.fillStyle = '#fffdf7'; g.fillRect(0, 0, o.width, o.height); g.drawImage(cv, 0, 0);
    o.toBlob(b => { if (!b) return; const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'mazo-moon-doodle.png'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); }, 'image/png'); });
  drawCols(); setupPad();
}
function drawCols(){
  const C = penColours(), pen = MM.doodlePens.find(p => p.id === dPen);
  $('#dCols').innerHTML = C.map((c,i) => `<button type="button" role="radio" data-c="${i}" aria-checked="${i===dCol}" tabindex="${i===dCol?0:-1}" style="--c:${c[1]}" title="${esc(c[0])}" aria-label="${esc(c[0])}">${dPen==='pattern'?`<b>${c[0]==='Stars'?'✦':c[0]==='Hearts'?'♥':'•'}</b>`:''}</button>`).join('');
  $('#dCols').onkeydown = e => { if (!/Arrow(Left|Right|Up|Down)/.test(e.key)) return; e.preventDefault(); const d = /Right|Down/.test(e.key) ? 1 : -1; dCol = (dCol + d + C.length) % C.length; drawCols(); $(`#dCols button[data-c="${dCol}"]`).focus(); };
  const c = C[dCol], asin = c[2] || pen.asin;
  $('#dBuy').innerHTML = `${esc(c[0])}, from the ${esc(pen.name)}. ${asin ? `<a class="ext" href="${amz(asin)}" target="_blank" rel="noopener">See it on Amazon</a>` : ''}`;
}
function setupPad(){
  const cv = $('#padC'), dpr = Math.min(2, devicePixelRatio || 1);
  const size = () => { const w = cv.offsetWidth, h = cv.offsetHeight; if (!w || (cv.width === Math.round(w * dpr) && cv.height === Math.round(h * dpr))) return;
    cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); cv.getContext('2d').setTransform(dpr, 0, 0, dpr, 0, 0); redraw(); };
  size(); if (window.ResizeObserver) new ResizeObserver(size).observe(cv);
  let cur = null;
  const pt = e => { const r = cv.getBoundingClientRect(), k = cv.offsetWidth / r.width; return [(e.clientX - r.left) * k, (e.clientY - r.top) * k, e.timeStamp]; };
  cv.onpointerdown = e => { cv.setPointerCapture(e.pointerId); const C = penColours()[dCol]; cur = { pen:dPen, col:C[1], kind:C[0], pts:[pt(e)] }; strokes.push(cur); redraw(); };
  cv.onpointermove = e => { if (!cur) return; (e.getCoalescedEvents ? e.getCoalescedEvents() : [e]).forEach(ev => cur.pts.push(pt(ev))); redraw(); };
  cv.onpointerup = cv.onpointercancel = () => { cur = null; };
}
function shape(g, kind, x, y, s){
  g.beginPath();
  if (kind === 'Stars') { for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4, rr = i % 2 ? s * .35 : s; g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); }
  else if (kind === 'Hearts') { g.moveTo(x, y + s * .8); g.bezierCurveTo(x - s * 1.4, y - s * .2, x - s * .5, y - s * 1.2, x, y - s * .35); g.bezierCurveTo(x + s * .5, y - s * 1.2, x + s * 1.4, y - s * .2, x, y + s * .8); }
  else g.arc(x, y, s * .55, 0, Math.PI * 2);
  g.fill();
}
function redraw(){
  const cv = $('#padC'); if (!cv) return; const g = cv.getContext('2d'); g.clearRect(0, 0, cv.width, cv.height); g.lineCap = g.lineJoin = 'round';
  strokes.forEach(s => {
    const P = s.pts; if (!P.length) return;
    if (s.pen === 'pattern') { g.strokeStyle = s.col; g.lineWidth = 2; g.globalAlpha = .55; g.beginPath(); P.forEach((p,i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); g.stroke(); g.globalAlpha = 1;
      g.fillStyle = s.col; let acc = 14, prev = P[0];
      for (let i = 1; i < P.length; i++) { const p = P[i], d = Math.hypot(p[0]-prev[0], p[1]-prev[1]); acc += d; if (acc >= 16) { shape(g, s.kind, p[0], p[1], 6); acc = 0; } prev = p; }
      if (P.length === 1) shape(g, s.kind, P[0][0], P[0][1], 6); return; }
    if (s.pen === 'brush') { for (let i = 1; i < P.length; i++) { const a = P[i-1], b = P[i], v = Math.hypot(b[0]-a[0], b[1]-a[1]) / Math.max(1, b[2]-a[2]);
        g.strokeStyle = s.col; g.lineWidth = Math.max(3, 11 - v * 4); g.beginPath(); g.moveTo(a[0], a[1]); g.lineTo(b[0], b[1]); g.stroke(); }
      g.strokeStyle = 'rgba(255,255,255,.45)'; g.lineWidth = 1.5; g.beginPath(); P.forEach((p,i) => i ? g.lineTo(p[0]-1, p[1]-1.5) : g.moveTo(p[0]-1, p[1]-1.5)); g.stroke();
      if (P.length === 1) { g.fillStyle = s.col; g.beginPath(); g.arc(P[0][0], P[0][1], 5, 0, Math.PI*2); g.fill(); } return; }
    g.strokeStyle = s.col; g.lineWidth = 2.6; g.beginPath(); P.forEach((p,i) => i ? g.lineTo(p[0], p[1]) : g.moveTo(p[0], p[1])); if (P.length === 1) g.lineTo(P[0][0] + .1, P[0][1]); g.stroke();
  });
}

/* ---------- scrapbook: my story ---------- */
let sbAt = 0;
function storyPages(){
  const S = MM.scrapbook, tilt = [-3, 2, -1.5, 3, -2, 1.5];
  const doodle = `<svg class="sbdoodle" viewBox="0 0 160 120" aria-hidden="true"><path d="M20 96c18-6 30-24 46-26s22 16 38 10 18-30 36-34" fill="none" stroke="#b0904f" stroke-width="2" stroke-linecap="round" stroke-dasharray="1 7"/>
    <path d="M118 22c-4 10-2 20 8 24-12 2-18-8-16-18 1-4 4-6 8-6z" fill="#e9c46a"/><path d="M40 30l3 7 7 1-5 5 1 7-6-3-6 3 1-7-5-5 7-1z" fill="#dcbcb3"/><path d="M100 72l2 4 4 .5-3 3 .8 4-3.8-2-3.8 2 .8-4-3-3 4-.5z" fill="#b0904f"/>
    <path d="M24 70l46-34 6 6-46 34-9 3z" fill="#80615f"/><path d="M70 36l6 6 4-4-6-6z" fill="#303133"/></svg>`;
  return S.pages.map((p, i) => `<div class="sbp">
      ${p.photos.length ? `<div class="snaps n${p.photos.length}">${p.photos.map((f, k) => `<figure class="snap" style="--r:${tilt[(i + k * 3) % 6]}deg"><img src="${f.src}" alt="${esc(f.alt)}" loading="lazy"><i class="tape"></i></figure>`).join('')}</div>` : doodle}
      <span class="eyebrow">Page ${i + 1}</span><h3>${esc(p.title)}</h3><p class="sbtext">${esc(p.text)}</p></div>`)
  .concat([`<div class="sbp last"><span class="eyebrow">Thank you for reading</span><h3>Come and say hello.</h3>
      <dl class="facts">${S.facts.map(f => `<div><dt>${esc(f[0])}</dt><dd>${esc(f[1])}</dd></div>`).join('')}</dl>
      <div class="row"><button class="btn" type="button" id="sbMail">Write to me</button><a class="btn line ext" href="https://www.instagram.com/mazomoon" target="_blank" rel="noopener">Instagram</a></div></div>`]);
}
function openStory(from){
  sbAt = 0;
  showSheet('My story', `<h2 class="t">A little album.</h2><p class="lead" style="margin-top:10px">A few pages about me and the world behind Mazo Moon. Turn the pages.</p>
    <div class="album" id="album"></div>
    <div class="pager"><button class="btn line" type="button" id="sbPrev">Previous page</button><span class="ctr" id="sbCtr" aria-live="polite"></span><button class="btn" type="button" id="sbNext">Next page</button></div>`, 'wide', from);
  $('#sbPrev').addEventListener('click', () => sbTurn(-1)); $('#sbNext').addEventListener('click', () => sbTurn(1));
  drawStory();
}
function drawStory(dir){
  const P = storyPages(), step = layout === 'phone' ? 1 : 2, a = $('#album');
  a.innerHTML = `<div class="spread${dir ? (dir > 0 ? ' fwd' : ' back') : ''}">${P.slice(sbAt, sbAt + step).join('')}${step === 2 && sbAt + 1 >= P.length ? '<div class="sbp blank"></div>' : ''}</div>`;
  $('#sbCtr').textContent = step === 2 ? `Pages ${sbAt+1}${sbAt+2<=P.length?'–'+(sbAt+2):''} of ${P.length}` : `Page ${sbAt+1} of ${P.length}`;
  $('#sbPrev').disabled = sbAt === 0; $('#sbNext').disabled = sbAt + step >= P.length;
  const m = $('#sbMail'); if (m) m.addEventListener('click', () => { sheet.close(); openObj('envelope', $('.hot[data-k="envelope"]')); });
}
function sbTurn(d){ const step = layout === 'phone' ? 1 : 2, n = storyPages().length, to = sbAt + d * step; if (to < 0 || to >= n) return; sbAt = to; drawStory(d);
  ($(d > 0 ? '#sbNext' : '#sbPrev').disabled ? $(d > 0 ? '#sbPrev' : '#sbNext') : $(d > 0 ? '#sbNext' : '#sbPrev')).focus(); }

/* ---------- moon and stars puzzle: a matching game ---------- */
const ICONS = {
  crescent:'<path d="M30 6a20 20 0 1 0 14 34A17 17 0 1 1 30 6z" fill="#e9c46a"/>',
  full:'<circle cx="24" cy="24" r="17" fill="#efe3c2"/><circle cx="18" cy="19" r="3.2" fill="#d8c79f"/><circle cx="29" cy="28" r="4.2" fill="#d8c79f"/><circle cx="27" cy="15" r="2" fill="#d8c79f"/>',
  star:'<path d="M24 5l5.6 12.2 13.4 1.4-10 9 2.9 13.2L24 34l-11.9 6.8L15 27.6l-10-9 13.4-1.4z" fill="#e9c46a"/>',
  sparkle:'<path d="M24 4c1.6 10 4 12.4 14 14-10 1.6-12.4 4-14 14-1.6-10-4-12.4-14-14 10-1.6 12.4-4 14-14z" fill="#f3e6c0"/><path d="M37 30c.8 4.4 1.8 5.4 6 6-4.2.6-5.2 1.6-6 6-.8-4.4-1.8-5.4-6-6 4.2-.6 5.2-1.6 6-6z" fill="#e9c46a"/>',
  planet:'<circle cx="24" cy="24" r="11" fill="#dcbcb3"/><ellipse cx="24" cy="25" rx="20" ry="6" fill="none" stroke="#e9c46a" stroke-width="2.6" transform="rotate(-18 24 25)"/>',
  shooting:'<path d="M8 38L30 18" stroke="#f3e6c0" stroke-width="3" stroke-linecap="round" opacity=".7"/><path d="M14 40L32 24" stroke="#f3e6c0" stroke-width="1.6" stroke-linecap="round" opacity=".5"/><path d="M35 8l2.7 6 6.5.7-4.9 4.4 1.4 6.4L35 22.2l-5.7 3.3 1.4-6.4-4.9-4.4 6.5-.7z" fill="#e9c46a"/>',
  cloud:'<path d="M31 9a12 12 0 1 0 9 19A10 10 0 1 1 31 9z" fill="#e9c46a"/><path d="M12 40h22a7 7 0 0 0 0-14 9 9 0 0 0-17-2 7.5 7.5 0 0 0-5 16z" fill="#f3ece2"/>',
  constellation:'<path d="M8 34L19 14L31 22L41 9" stroke="#e9c46a" stroke-width="1.4" fill="none" opacity=".75"/><circle cx="8" cy="34" r="3" fill="#f3e6c0"/><circle cx="19" cy="14" r="3.6" fill="#f3e6c0"/><circle cx="31" cy="22" r="2.6" fill="#f3e6c0"/><circle cx="41" cy="9" r="3.2" fill="#f3e6c0"/>'
};
const ICON_NAME = { crescent:'Crescent moon', full:'Full moon', star:'Star', sparkle:'Sparkles', planet:'Ringed planet', shooting:'Shooting star', cloud:'Moon and cloud', constellation:'Constellation' };
const icon = k => `<svg viewBox="0 0 48 48" aria-hidden="true">${ICONS[k]}</svg>`;
let mg = null;
function shuffle(a){ for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function openPuzzle(from){
  showSheet('Moon & stars', `
    <h2 class="t">A little game of moons and stars.</h2>
    <p class="lead" style="margin-top:10px">Turn over two cards at a time and find the matching pairs.</p>
    <div class="mgwrap">
      <div class="mg" id="mg" role="grid" aria-label="Matching cards"></div>
      <div class="mgside">
        <p class="mgstat" id="mgStat" aria-live="polite"></p>
        <div class="row"><button class="btn line" type="button" id="mgNew">Shuffle and start again</button></div>
        <p class="small muted">Works with a mouse, a finger or the keyboard. Nothing is saved.</p>
        <div id="mgDone"></div>
      </div>
    </div>`, 'wide night-sheet', from);
  $('#mgNew').addEventListener('click', newGame);
  $('#mg').addEventListener('click', e => { const b = e.target.closest('button[data-i]'); if (b) flip(+b.dataset.i); });
  newGame();
}
function newGame(){
  mg = { cards: shuffle(Object.keys(ICONS).flatMap(k => [k, k])), up: [], done: new Set(), moves: 0, lock: false };
  $('#mgDone').innerHTML = '';
  $('#mg').innerHTML = mg.cards.map((k,i) => `<button type="button" class="mc" data-i="${i}" aria-label="Card ${i+1}, face down"><span class="in"><span class="cb">${icon('crescent')}</span><span class="cf">${icon(k)}</span></span></button>`).join('');
  mgStat();
}
function mgStat(){ $('#mgStat').textContent = `Pairs found: ${mg.done.size} of 8 · Turns: ${mg.moves}`; }
function setCard(i){ const b = $(`#mg .mc[data-i="${i}"]`), k = mg.cards[i], up = mg.up.includes(i) || mg.done.has(k);
  b.classList.toggle('up', up); b.classList.toggle('got', mg.done.has(k));
  b.setAttribute('aria-label', `Card ${i+1}, ${up ? ICON_NAME[k] + (mg.done.has(k) ? ', matched' : '') : 'face down'}`);
  b.setAttribute('aria-disabled', up ? 'true' : 'false'); }
function flip(i){
  if (mg.lock || mg.up.includes(i) || mg.done.has(mg.cards[i])) return;
  mg.up.push(i); setCard(i);
  if (mg.up.length < 2) return;
  mg.moves++; const [a, b] = mg.up;
  if (mg.cards[a] === mg.cards[b]) { mg.done.add(mg.cards[a]); mg.up = []; setCard(a); setCard(b); mgStat();
    if (mg.done.size === 8) $('#mgDone').innerHTML = `<div class="mgwin"><b>All eight pairs, in ${mg.moves} turns.</b><p class="muted">If you love a moon and stars, my journals have them on the cover.</p><button class="btn" type="button" id="mgShop">See the journals</button></div>`,
      $('#mgShop').addEventListener('click', () => { shopCat = 'journals'; openShop(); }), $('#mgShop').focus();
    return; }
  mgStat(); mg.lock = true;
  setTimeout(() => { mg.up = []; mg.lock = false; setCard(a); setCard(b); }, reduce ? 700 : 950);
}

/* ---------- seasons: the same desk, with the light shifting through the year ---------- */
const SEASON_NAME = { spring:'Spring', summer:'Summer', autumn:'Autumn', winter:'Winter' };
let season = curSeason();
const setSeason = s => { season = window.__mmSeason = s; ['spring','summer','autumn','winter'].forEach(x => stage.classList.toggle('season-' + x, x === s));
  if (layout) { const day = seasonal(SCENE[layout].day); $('#imgD').src = day; document.querySelector('.blur.d').style.backgroundImage = `url(${day})`; } };
setSeason(season);

/* ---------- menu ---------- */
function openMenu(){
  const G = [
    ['Read & Discover', [['books','The Reading Corner'], ['mug','What’s on Becky’s Desk']]],
    ['Take a Little Break', [['notebook','Doodle'], ['stickers','Stickers'], ['puzzle','Moon & Stars']]],
    ['About & Contact', [['scrapbook','My Story'], ['envelope','Letters & Contact']]]
  ];
  $('#menuBody').innerHTML = `
    <div class="row" style="justify-content:space-between"><span class="eyebrow">Menu</span><button class="back" type="button" data-close>Close</button></div>
    ${G.map(([g, list]) => `<section class="mgrp" aria-label="${esc(g)}"><h3 class="eyebrow">${esc(g)}</h3><ul>${list.map(([k, t]) => `<li><button type="button" data-k="${k}">${esc(t)}</button></li>`).join('')}</ul></section>`).join('')}
    <div class="msec">
      <button type="button" class="quiet" data-a="lamp">${root.classList.contains('night') ? 'Switch to daytime' : 'Switch to moonlight'}</button>
      <button type="button" class="quiet" data-a="intro">Replay the introduction</button>
    </div>
    <nav class="mgrp mpages" aria-label="All pages"><h3 class="eyebrow">All pages</h3><ul>
      <li><a href="/shop/">Shop Mazo Moon</a></li><li><a href="/journals/">Journals &amp; Colouring</a></li><li><a href="/reading/">The Reading Corner</a></li>
      <li><a href="/little-things/">Little Things I Love</a></li><li><a href="/our-story/">Our Story &amp; Contact</a></li></ul></nav>
    <p class="small muted mlegal"><a href="/privacy/">Privacy</a> · <a href="/cookies/">Cookies</a> · <a href="/cookies/" data-cookie-settings>Cookie settings</a> · <a href="/terms/">Terms</a></p>
    <p class="small muted">© Mazo Moon Ltd, company no. 16988519</p>`;
  menu.showModal();
}
menu.addEventListener('click', e => {
  if (e.target === menu || e.target.closest('[data-close]')) { menu.close(); return; }
  if (e.target.closest('[data-cookie-settings]')) { menu.close(); return; }
  const b = e.target.closest('button[data-k],button[data-a]'); if (!b) return; menu.close();
  if (b.dataset.a === 'lamp') toggleLamp(); else if (b.dataset.a === 'intro') playIntro(); else if (b.dataset.a === 'season') { const o = ['spring','summer','autumn','winter']; setSeason(o[(o.indexOf(season) + 1) % 4]); } else if (b.dataset.k.startsWith('shop:')) shopTo(b.dataset.k.slice(5)); else openObj(b.dataset.k, $(`.hot[data-k="${b.dataset.k}"]`) || null);
});
$('#navMenu').addEventListener('click', openMenu);
const shopTo = cat => { closeShopMenu(); closeAll(); shopCat = cat || 'all'; openObj('laptop', layout === 'desk' ? $('.hot[data-k="laptop"]') : null); };
const goShop = () => shopTo('all');
/* the Shop button opens a short menu of product categories */
const sm = $('#shopMenu'); let smFrom = null;
sm.innerHTML = MM.categories.map(c => `<button type="button" role="menuitem" data-c="${c.id}">${esc(catName(c))}</button>`).join('') +
  `<a role="menuitem" href="${MM.store}" target="_blank" rel="noopener">My Amazon storefront<small>opens Amazon in a new tab</small></a>`;
function openShopMenu(btn){
  smFrom = btn; sm.hidden = false; btn.setAttribute('aria-expanded','true');
  const r = btn.getBoundingClientRect(), up = r.top > innerHeight / 2;
  sm.style.right = Math.max(12, innerWidth - r.right) + 'px';
  sm.style.top = up ? 'auto' : (r.bottom + 8) + 'px'; sm.style.bottom = up ? (innerHeight - r.top + 8) + 'px' : 'auto';
  sm.querySelector('[role=menuitem]').focus();
}
function closeShopMenu(back){ if (sm.hidden) return; sm.hidden = true; if (smFrom) { smFrom.setAttribute('aria-expanded','false'); if (back) smFrom.focus(); } }
['#navShop','#mShop'].forEach(id => { const b = $(id); b.setAttribute('aria-haspopup','menu'); b.setAttribute('aria-expanded','false'); b.setAttribute('aria-controls','shopMenu');
  b.addEventListener('click', e => { e.stopPropagation(); sm.hidden ? openShopMenu(b) : closeShopMenu(true); }); });
sm.addEventListener('click', e => { const b = e.target.closest('button[data-c]'); if (b) shopTo(b.dataset.c); else if (e.target.closest('a')) closeShopMenu(); });
sm.addEventListener('keydown', e => { const it = [...sm.querySelectorAll('[role=menuitem]')], i = it.indexOf(document.activeElement);
  if (e.key === 'Escape') { e.preventDefault(); closeShopMenu(true); }
  else if (e.key === 'ArrowDown') { e.preventDefault(); it[(i + 1) % it.length].focus(); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); it[(i - 1 + it.length) % it.length].focus(); }
  else if (e.key === 'Tab') closeShopMenu(); });
document.addEventListener('click', e => { if (!sm.hidden && !sm.contains(e.target)) closeShopMenu(); });
if (MM.tagline) $('#tagline').textContent = MM.tagline;

/* ---------- welcome: "welcome" writes itself as you scroll (or on its own), then becomes Mazo Moon ---------- */
function runWelcome(done){
  const w = $('#welcome'); if (!w) return done();
  const ps = [...w.querySelectorAll('.wsvg path')], lens = ps.map(p => p.getTotalLength()), tot = lens.reduce((x,y) => x + y, 0);
  ps.forEach((p,i) => { p.style.strokeDasharray = lens[i]; p.style.strokeDashoffset = lens[i]; });
  w.hidden = false; let prog = 0, last = performance.now(), idle = 0, raf, fin = false;
  const END = 2;
  const paint = () => {
    let acc = 0; const drawn = Math.min(1, prog) * tot;
    ps.forEach((p,i) => { p.style.strokeDashoffset = Math.max(0, lens[i] - Math.max(0, drawn - acc)); acc += lens[i]; });
    const k = Math.max(0, Math.min(1, (prog - 1.02) / .3));   // "welcome to" rises a little, then Mazo Moon fades in below
    w.style.setProperty('--k', k.toFixed(3));
    w.style.setProperty('--m', Math.max(0, Math.min(1, (prog - 1.15) / .4)).toFixed(3));   // then it holds for a moment
    w.style.setProperty('--out', Math.max(0, Math.min(1, (prog - 1.82) / .18)).toFixed(3));
  };
  const finish = () => { if (fin) return; fin = true; cancelAnimationFrame(raf); removeEventListener('wheel', onWheel); removeEventListener('touchmove', onTouch); removeEventListener('keydown', onKey);
    w.classList.add('gone'); setTimeout(() => { w.hidden = true; }, 600); done(); };
  const tick = t => { const dt = Math.min(64, t - last); last = t; idle += dt;
    if (idle > 900) prog += dt / 2600;     // nobody scrolling: it writes itself
    paint(); if (prog >= END) return finish(); raf = requestAnimationFrame(tick); };
  const push = v => { prog = Math.max(0, Math.min(END, prog + v)); idle = 0; };
  const onWheel = e => { e.preventDefault(); push(Math.max(-.08, Math.min(.08, e.deltaY / 900))); };
  let ty = null; const onTouch = e => { const y = e.touches[0].clientY; if (ty != null) push((ty - y) / 500); ty = y; e.preventDefault(); };
  const onKey = e => { if (['ArrowDown','PageDown',' ','Enter'].includes(e.key)) { e.preventDefault(); push(.2); } if (e.key === 'Escape') { prog = END; } };
  addEventListener('wheel', onWheel, { passive:false }); addEventListener('touchmove', onTouch, { passive:false }); addEventListener('touchend', () => ty = null); addEventListener('keydown', onKey);
  $('#wSkip').onclick = () => { prog = END; paint(); finish(); };
  if (reduce) { prog = 1.6; paint(); setTimeout(() => { prog = END; paint(); finish(); }, 1400); return; }
  raf = requestAnimationFrame(tick); $('#wSkip').focus({ preventScroll:true });
}

/* ---------- intro ---------- */
const intro = $('#intro');
function enterDesk(thenShop){
  store.set('mm-seen', '1'); intro.classList.add('gone'); intro.setAttribute('aria-hidden', 'true');
  if (thenShop) setTimeout(() => shopTo('all'), reduce ? 0 : 500); else setTimeout(() => $('#hots .hot')?.focus({ preventScroll:true }), 700);
  // first time in: show every label for a few seconds, then tuck them away unless the visitor chose to keep them
  if (!thenShop && store.get('mm-labels') == null) { around(true, false); setTimeout(() => { if (store.get('mm-labels') == null) around(false, false); }, 6500); }
}
const riseIntro = () => intro.querySelectorAll('.comp > *, .arr').forEach(f => { f.style.animation = 'none'; void f.offsetWidth; f.style.animation = ''; });
function playIntro(){ intro.classList.remove('gone'); intro.removeAttribute('aria-hidden');
  runWelcome(() => { riseIntro(); $('#enter').focus({ preventScroll:true }); }); }
$('#enter').addEventListener('click', () => enterDesk(false));
$('#introShop').addEventListener('click', () => enterDesk(true));
if (store.get('mm-seen')) { intro.classList.add('gone'); intro.setAttribute('aria-hidden', 'true'); } else runWelcome(() => { riseIntro(); $('#enter').focus({ preventScroll:true }); });
})();
