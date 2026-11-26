/* Sinag · Codal Studio — Philippine law, one provision at a time.
   Static app: no build step, no framework. Data lives in data/*.json; progress lives in this browser. */
(() => {
'use strict';
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const main = $('#main');
const DAY = 86400000;
const today = () => new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 10);

/* ------------------------------------------------------------------ storage */
const KEY = 'sinag.codal.v1';
const DEFAULTS = { cards: {}, notes: {}, marks: {}, flags: {}, days: {}, last: null, tutor: {}, hooks: {}, lessons: {}, lastBy: {}, b2: {}, cal: [],
  settings: { newPerDay: 10, focus: null, figure: '', hl: { op: false, cond: true, exc: true, num: true, pen: true, def: true }, hlv: 2, passcode: '' } };
let S;
try { S = Object.assign(structuredClone(DEFAULTS), JSON.parse(localStorage.getItem(KEY) || '{}')); }
catch (e) { S = structuredClone(DEFAULTS); }
S.settings = Object.assign(structuredClone(DEFAULTS.settings), S.settings || {});
/* fewer default cues: "shall" and "may" occur in nearly every sentence, so marking them by default only adds noise */
if (S.settings.hlv !== 2) { const h = S.settings.hl || {}; if (Object.values(h).every(Boolean)) h.op = false; S.settings.hlv = 2; }
let saveT;
function save() { clearTimeout(saveT); saveT = setTimeout(() => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { toast('Could not save progress in this browser.'); } }, 150); }
function toast(msg) { const t = $('#toast'); t.textContent = msg; t.classList.add('on'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('on'), 2600); }
function bumpDay(k) { const d = today(); S.days[d] = S.days[d] || { r: 0, n: 0 }; S.days[d][k]++; }

/* ------------------------------------------------------------------ data */
let CAT = null;
const CODES = {}, CASES = {}, NOTES = {};
async function getJSON(url) { const r = await fetch(url); if (!r.ok) throw new Error(r.status + ' ' + url); return r.json(); }
const meta = id => CAT.codes.find(c => c.id === id);
async function loadCode(id) {
  if (CODES[id]) return CODES[id];
  const m = meta(id); if (!m) throw new Error('Unknown code ' + id);
  const d = await getJSON(`data/codes/${id}.json?v=${m.hash}`);
  d.byId = {}; d.order = [];
  d.provisions.forEach((p, i) => { p.ix = i; d.byId[p.i] = p; d.order.push(p.i); });
  d.kids = d.divisions.map(() => []); d.roots = []; d.divProv = d.divisions.map(() => []); d.loose = [];
  d.divisions.forEach((v, i) => (v.p == null ? d.roots : d.kids[v.p]).push(i));
  d.provisions.forEach(p => (p.d == null ? d.loose : d.divProv[p.d]).push(p));
  d.byNum = {};
  d.provisions.forEach(p => { if (p.n != null && !(p.n in d.byNum)) d.byNum[p.n] = p; });
  /* a provision whose id changed when its heading was corrected keeps its old links and your progress */
  if (d.alias) {
    let moved = 0;
    for (const [o, n] of Object.entries(d.alias)) {
      if (d.byId[n]) d.byId[o] = d.byId[n];
      for (const f of ['cards', 'notes', 'marks', 'hooks', 'tutor']) { const ok = ck(id, o), nk = ck(id, n); if (S[f] && S[f][ok] !== undefined) { if (S[f][nk] === undefined) S[f][nk] = S[f][ok]; delete S[f][ok]; moved++; } }
      if (S.last && S.last.c === id && S.last.p === o) S.last.p = n;
    }
    if (moved) save();
  }
  CODES[id] = d;
  return d;
}
let SYL = null, SYX = null, REC = null;
async function loadSyllabus() { if (!SYL) SYL = await getJSON('data/syllabus.json?v=' + (CAT.shash || CAT.built)).catch(() => ({ courses: [] })); return SYL; }
async function loadSylIndex() { if (!SYX) SYX = await getJSON('data/syllabus_index.json?v=' + (CAT.shash || CAT.built)).catch(() => ({})); return SYX; }
async function loadRecent() { if (!REC) REC = await getJSON('data/recent.json?v=' + (CAT.rhash || CAT.built)).catch(() => ({ by: {}, general: [] })); return REC; }
let B2 = null;
async function loadB2() { if (!B2) B2 = await getJSON('data/book2.json?v=' + (CAT.bhash || CAT.built)); return B2; }
let CUR = null;
async function loadCur() {
  if (!CUR) { CUR = await getJSON('data/curriculum.json?v=' + (CAT.chash || CAT.built)); CUR.byId = Object.fromEntries(CUR.fields.map(f => [f.id, f])); }
  return CUR;
}
const fieldOf = cid => CUR.byId[CUR.homes[cid]];
const focusIds = () => (S.settings.focus && S.settings.focus.length ? S.settings.focus : CUR.focus);
const figName = () => 'the House of Law';
const fieldCodes = f => f.tracks.flatMap(t => t.items.filter(i => i.t === 'code' && !i.x).map(i => i.id));
function fieldCount(f) { let total = 0, touched = 0, m = 0; for (const id of fieldCodes(f)) { const k = counts(id); total += k.total; touched += k.touched; m += k.m; } return { total, touched, m, pct: total ? touched / total * 100 : 0 }; }
const rich = t => esc(t).replace(/⟦([^|⟧]+)\|([^|⟧]+)\|([^⟧]+)⟧/g, (m, c, i, l) => `<a class="pref" href="#/p/${c}/${i}">${l}</a>`);
/* The memory figure: one standing figure, read head to toe. Each field of law has a fixed place on it. */
/* The House of Law: the memory palace. Eight places, read from the roof down to the steps. */
const FIGKEY = 'sinag.figure.img';
const figImg = () => { try { return localStorage.getItem(FIGKEY) || ''; } catch (e) { return ''; } };
const figPos = id => (figImg() && S.settings.housePos && S.settings.housePos[id]) || null;
let figSeq = 0;
// The House of Law, after the Supreme Court building on Padre Faura, Manila (UP Main Library, 1928-30, neoclassical):
// a central portico of four columns before three doors, seven marble steps flanked by two statues, two-storey wings.
// Places: pediment, inscription ("BATAS AT BAYAN", the Court's motto), four columns, three doors, seven steps. viewBox 0 0 600 520.
const HOUSE_COLS = [196, 262, 338, 404];
const HOUSE_PIN = { pol: [366, 160], craft: [104, 212], lab: [196, 340], civ: [262, 340], com: [338, 340], crim: [404, 340], intl: [300, 384], eth: [300, 457] };
function houseSVG(u, opt = {}) {
  const act = opt.active || null;
  const M = '#efe9dd', M2 = '#ddd4c3', M3 = '#c6bba7', MS = '#a99c85';
  const tint = (id, el) => act === id ? `<g class="lit f-${id}">${el}</g>` : '';
  const win = (x, y, w, h, lit, arch) => `<g><rect x="${x - 3}" y="${y - 3}" width="${w + 6}" height="${h + 6}" fill="${M2}"/>${arch ? `<path d="M${x - 3},${y + 6} A${w / 2 + 3},${w / 2 + 3} 0 0 1 ${x + w + 3},${y + 6}" fill="${M2}"/>` : ''}
      <path d="M${x},${y + (arch ? 6 : 0)} ${arch ? `A${w / 2},${w / 2} 0 0 1 ${x + w},${y + 6}` : `H${x + w}`} V${y + h} H${x} Z" fill="${lit ? 'url(#' + u + 'lit)' : '#22314d'}"/>
      <path d="M${x + w / 2},${y + (arch ? 2 : 0)} V${y + h} M${x},${y + h * .45} H${x + w}" stroke="${M3}" stroke-width="1.4"/>
      <rect x="${x - 5}" y="${y + h}" width="${w + 10}" height="4" fill="${M}"/></g>`;
  const wing = x0 => { const xs = [x0 + 22, x0 + 80]; return `
      <rect x="${x0}" y="200" width="134" height="232" fill="url(#${u}wing)"/>
      ${xs.map((x, i) => win(x, 240, 32, 56, (x0 + i) % 3 === 0) + win(x, 324, 32, 80, i === 1, true)).join('')}
      <rect x="${x0 + 64}" y="232" width="6" height="200" fill="#fff" opacity=".18"/>
      <rect x="${x0}" y="300" width="134" height="6" fill="${M2}"/>`; };
  const col = x => `
      <rect x="${x - 15}" y="252" width="30" height="168" fill="url(#${u}col)"/>
      <g stroke="${M3}" stroke-width="1" opacity=".85"><path d="M${x - 8},258 V416"/><path d="M${x - 3},258 V416"/><path d="M${x + 2},258 V416"/><path d="M${x + 7},258 V416"/></g>
      <rect x="${x - 21}" y="238" width="42" height="6" fill="${M}"/><path d="M${x - 18},244 H${x + 18} L${x + 15},253 H${x - 15} Z" fill="${M2}"/>
      <circle cx="${x - 17}" cy="248" r="4" fill="none" stroke="${M3}" stroke-width="1.6"/><circle cx="${x + 17}" cy="248" r="4" fill="none" stroke="${M3}" stroke-width="1.6"/>
      <path d="M${x - 18},420 H${x + 18} L${x + 21},430 H${x - 21} Z" fill="${M2}"/>`;
  const door = (x, w, top) => `<g><rect x="${x - 4}" y="${top - 26}" width="${w + 8}" height="${432 - top + 26}" fill="#e6ddcb"/>
      <rect x="${x}" y="${top - 22}" width="${w}" height="16" fill="url(#${u}lit)"/><path d="M${x + w / 2},${top - 22} V${top - 6}" stroke="#e6ddcb" stroke-width="1.5"/>
      <rect x="${x}" y="${top}" width="${w / 2 - .8}" height="${432 - top}" fill="url(#${u}door)"/><rect x="${x + w / 2 + .8}" y="${top}" width="${w / 2 - .8}" height="${432 - top}" fill="url(#${u}door)"/>
      <g fill="none" stroke="#c9a24f" stroke-width="1" opacity=".85"><rect x="${x + 4}" y="${top + 6}" width="${w / 2 - 9}" height="${(432 - top) * .38}"/><rect x="${x + 4}" y="${top + 12 + (432 - top) * .38}" width="${w / 2 - 9}" height="${(432 - top) * .48}"/><rect x="${x + w / 2 + 4}" y="${top + 6}" width="${w / 2 - 9}" height="${(432 - top) * .38}"/><rect x="${x + w / 2 + 4}" y="${top + 12 + (432 - top) * .38}" width="${w / 2 - 9}" height="${(432 - top) * .48}"/></g>
      <rect x="${x + w / 2 - 4}" y="${top + (432 - top) * .45}" width="3" height="10" rx="1" fill="url(#${u}gold)"/><rect x="${x + w / 2 + 1}" y="${top + (432 - top) * .45}" width="3" height="10" rx="1" fill="url(#${u}gold)"/></g>`;
  const statue = x => `<g><rect x="${x - 15}" y="422" width="30" height="52" fill="url(#${u}step)"/><rect x="${x - 18}" y="416" width="36" height="7" fill="${M}"/><rect x="${x - 18}" y="468" width="36" height="6" fill="${M2}"/>
      <path d="M${x - 9},394 Q${x},389 ${x + 9},394 L${x + 12},416 H${x - 12} Z" fill="url(#${u}bronze)"/>
      <path d="M${x - 9},395 L${x - 12},410 M${x + 9},395 L${x + 7},406" stroke="#3c2e1e" stroke-width="2.4" stroke-linecap="round"/>
      <rect x="${x - 2.5}" y="386" width="5" height="6" fill="#5a4530"/><circle cx="${x}" cy="381" r="6" fill="url(#${u}bronze)"/></g>`;
  const steps = []; for (let i = 0; i < 7; i++) { const w = 268 + i * 14, y = 432 + i * 6; steps.push(`<rect x="${300 - w / 2}" y="${y}" width="${w}" height="6" fill="url(#${u}step)"/><rect x="${300 - w / 2}" y="${y + 5}" width="${w}" height="1" fill="#000" opacity=".16"/>`); }
  const stepPoly = (() => { let l = [], r = []; for (let i = 0; i < 7; i++) { const w = 268 + i * 14, y = 432 + i * 6; l.push(`${300 - w / 2},${y} ${300 - w / 2},${y + 6}`); r.unshift(`${300 + w / 2},${y + 6} ${300 + w / 2},${y}`); } return `<polygon points="${l.join(' ')} ${r.join(' ')}"/>`; })();
  return `<defs>
    <linearGradient id="${u}sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a1322"/><stop offset=".6" stop-color="#15264a"/><stop offset=".84" stop-color="#2a3b5e"/><stop offset="1" stop-color="#1b2742"/></linearGradient>
    <radialGradient id="${u}glow" cx=".5" cy=".6" r=".6"><stop offset="0" stop-color="#f4d58d" stop-opacity=".26"/><stop offset=".55" stop-color="#f4d58d" stop-opacity=".06"/><stop offset="1" stop-color="#f4d58d" stop-opacity="0"/></radialGradient>
    <linearGradient id="${u}col" x1="0" x2="1"><stop offset="0" stop-color="${M3}"/><stop offset=".35" stop-color="${M}"/><stop offset=".6" stop-color="#f8f4ec"/><stop offset="1" stop-color="${MS}"/></linearGradient>
    <linearGradient id="${u}ped" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f6f1e7"/><stop offset="1" stop-color="${M2}"/></linearGradient>
    <linearGradient id="${u}wing" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e7e0d1"/><stop offset="1" stop-color="#cfc5b1"/></linearGradient>
    <linearGradient id="${u}wall" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8c826e"/><stop offset="1" stop-color="#b1a58e"/></linearGradient>
    <linearGradient id="${u}door" x1="0" x2="1"><stop offset="0" stop-color="#3b2a1a"/><stop offset=".5" stop-color="#5c4128"/><stop offset="1" stop-color="#3b2a1a"/></linearGradient>
    <linearGradient id="${u}lit" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffe3a0"/><stop offset="1" stop-color="#e9a94a"/></linearGradient>
    <linearGradient id="${u}gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f0d791"/><stop offset="1" stop-color="#b8913f"/></linearGradient>
    <linearGradient id="${u}bronze" x1="0" x2="1"><stop offset="0" stop-color="#4b3a26"/><stop offset=".5" stop-color="#8a6a3f"/><stop offset="1" stop-color="#3c2e1e"/></linearGradient>
    <linearGradient id="${u}step" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#f3eee4"/><stop offset="1" stop-color="${M3}"/></linearGradient>
  </defs>
  ${opt.bg === false ? '' : `<rect width="600" height="520" rx="22" fill="url(#${u}sky)"/><rect width="600" height="520" rx="22" fill="url(#${u}glow)"/>
  <g fill="#fff">${[[52, 48, .5], [126, 92, .35], [482, 54, .45], [548, 110, .3], [520, 30, .25], [78, 140, .25], [418, 34, .3], [196, 40, .3]].map(([x, y, o]) => `<circle cx="${x}" cy="${y}" r="1.2" opacity="${o}"/>`).join('')}</g>`}
  <rect x="0" y="474" width="600" height="46" fill="#000" opacity=".22"/>
  <ellipse cx="300" cy="476" rx="290" ry="12" fill="#000" opacity=".3"/>
  <!-- flag -->
  <path d="M300,58 V114" stroke="#e6c77a" stroke-width="2.6"/><circle cx="300" cy="57" r="2.6" fill="url(#${u}gold)"/>
  <g transform="translate(301,62)"><rect width="34" height="10" fill="#0038a8"/><rect y="10" width="34" height="10" fill="#ce1126"/><path d="M0,0 L17.3,10 L0,20 Z" fill="#fff"/><circle cx="6" cy="10" r="2.6" fill="#fcd116"/><g fill="#fcd116"><circle cx="2" cy="2.6" r=".9"/><circle cx="2" cy="17.4" r=".9"/><circle cx="14.4" cy="10" r=".9"/></g></g>
  <!-- wings -->
  ${wing(32)}${wing(434)}
  <!-- portico: back wall and three doors -->
  <rect x="166" y="226" width="268" height="206" fill="url(#${u}wall)"/>
  <rect x="166" y="226" width="268" height="12" fill="#000" opacity=".18"/>
  ${door(215, 30, 350)}${door(280, 40, 330)}${door(355, 30, 350)}
  ${tint('intl', `<rect x="215" y="350" width="30" height="82"/><rect x="280" y="330" width="40" height="102"/><rect x="355" y="350" width="30" height="82"/>`)}
  <!-- four columns -->
  ${HOUSE_COLS.map(col).join('')}
  ${['lab', 'civ', 'com', 'crim'].includes(act) ? (() => { const x = HOUSE_COLS[['lab', 'civ', 'com', 'crim'].indexOf(act)]; return `<g class="lit f-${act}"><rect x="${x - 15}" y="252" width="30" height="168"/><rect x="${x - 21}" y="238" width="42" height="15"/></g>`; })() : ''}
  <!-- entablature across the whole front, with the motto -->
  <rect x="26" y="190" width="548" height="10" fill="${M}"/>
  <rect x="30" y="200" width="540" height="26" fill="url(#${u}ped)"/>
  <rect x="160" y="196" width="280" height="34" fill="url(#${u}ped)"/><rect x="160" y="230" width="280" height="8" fill="${M2}"/>
  ${tint('craft', `<rect x="30" y="200" width="540" height="26"/><rect x="160" y="196" width="280" height="34"/>`)}
  <text x="300" y="219" text-anchor="middle" font-family="Literata, Georgia, serif" font-size="15" font-weight="600" letter-spacing="5" fill="#6f5a35">BATAS AT BAYAN</text>
  <!-- pediment over the portico -->
  <path d="M146,192 L300,112 L454,192 Z" fill="${M}"/>
  <path d="M172,186 L300,122 L428,186 Z" fill="url(#${u}ped)"/>
  <path d="M172,186 L300,122 L428,186" fill="none" stroke="${M3}" stroke-width="1.5"/>
  ${tint('pol', `<path d="M172,186 L300,122 L428,186 Z"/>`)}
  <circle cx="300" cy="162" r="17" fill="none" stroke="url(#${u}gold)" stroke-width="3"/>
  <g fill="none" stroke="#b8913f" stroke-width="1.5" stroke-linecap="round"><path d="M300,151 V173 M291,156 H309 M287,156 L283,165 M313,156 L317,165 M279,165 Q283,170 287,165 M313,165 Q317,170 321,165 M295,173 H305"/></g>
  <!-- seven steps and two statues -->
  ${steps.join('')}
  ${tint('eth', stepPoly)}
  ${statue(98)}${statue(502)}`;
}
function figure(active, plain) {
  const u = 'fg' + (++figSeq); const img = figImg();
  const order = ['pol', 'craft', 'lab', 'civ', 'com', 'crim', 'intl', 'eth'];
  const zone = id => { const f = CUR.byId[id]; const on = active === id; const [px, py] = figPos(id) || HOUSE_PIN[id];
    if (plain && !on) return '';
    return `<a class="zone f-${id}${on ? ' on' : ''}" data-id="${id}" href="#/field/${id}" aria-label="${f.n}. ${esc(f.name)}: ${esc(f.pname)}">${on ? `<circle class="halo" cx="${px}" cy="${py}" r="30"/>` : ''}<circle class="pinsh" cx="${px}" cy="${py + 2.5}" r="17"/><circle class="pin" cx="${px}" cy="${py}" r="17"/><text class="nt" x="${px}" y="${py + 0.5}">${f.n}</text></a>`; };
  return `<svg class="fig${plain ? ' plain' : ''}${active && !plain ? ' dim' : ''}" viewBox="0 0 600 520" role="img" aria-label="The House of Law: eight fields of law placed in eight parts of one building">
    ${img ? `<defs><clipPath id="${u}r"><rect width="600" height="520" rx="22"/></clipPath></defs><rect width="600" height="520" rx="22" fill="#0b1424"/><image href="${img}" width="600" height="520" preserveAspectRatio="xMidYMid slice" clip-path="url(#${u}r)"/>` : houseSVG(u, { active: plain ? active : null })}
    ${order.map(zone).join('')}</svg>`;
}
async function figurePicture(done) {
  const m = modal(`<h3>Use a place you know</h3><p class="small muted">The method works best with a place you know well: your law school, a courthouse you pass, your own home. Choose a photo of it, then place the eight numbers on it in the order you would walk through. The photo stays on this device only.</p>
    <div class="row"><label class="btn primary">Choose a picture<input type="file" id="fgf" accept="image/*" hidden></label><button class="btn" id="fga">Move the markers</button><button class="btn ghost" id="fgr">Use the House of Law</button></div>
    <div id="fgbox" style="margin-top:10px;max-width:420px"></div><div class="row" style="justify-content:flex-end;margin-top:10px"><button class="btn" id="mok">Done</button></div>`);
  const box = $('#fgbox', m.el); let sel = null;
  const draw = () => {
    $('#fga', m.el).hidden = $('#fgr', m.el).hidden = !figImg();
    if (!figImg()) { box.innerHTML = ''; return; }
    box.innerHTML = `<p class="small"><b>${sel ? `Now tap the place on your photo for ${CUR.byId[sel].n}, ${esc(CUR.byId[sel].name)}.` : 'To move a number, tap it, then tap its place on the photo.'}</b></p>` + figure(sel || undefined);
    const svg = $('svg', box);
    svg.addEventListener('click', e => {
      e.preventDefault(); const z = e.target.closest('.zone');
      if (z && !sel) { sel = z.dataset.id; return draw(); }
      if (!sel) return;
      const pt = svg.createSVGPoint(); pt.x = e.clientX; pt.y = e.clientY; const q = pt.matrixTransform(svg.getScreenCTM().inverse());
      S.settings.housePos = S.settings.housePos || {}; S.settings.housePos[sel] = [Math.round(q.x), Math.round(q.y)]; save(); sel = null; draw();
    });
  };
  $('#fga', m.el).onclick = draw;
  $('#fgr', m.el).onclick = () => { try { localStorage.removeItem(FIGKEY); } catch (e) {} S.settings.housePos = {}; save(); sel = null; draw(); toast('Back to the House of Law.'); };
  $('#fgf', m.el).onchange = e => {
    const f = e.target.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = () => { const im = new Image(); im.onload = () => {
      const sc = Math.min(1, 1100 / im.height, 800 / im.width); const c = document.createElement('canvas'); c.width = Math.round(im.width * sc); c.height = Math.round(im.height * sc);
      const g = c.getContext('2d'); g.fillStyle = '#fcfdff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(im, 0, 0, c.width, c.height);
      try { localStorage.setItem(FIGKEY, c.toDataURL('image/jpeg', 0.85)); S.settings.housePos = {}; save(); toast('Picture saved on this device.'); sel = null; draw(); } catch (err) { toast('That picture is too large to keep. Try a smaller one.'); }
    }; im.onerror = () => toast('That file could not be read as a picture.'); im.src = r.result; };
    r.readAsDataURL(f);
  };
  $('#mok', m.el).onclick = () => { m.close(); done && done(); };
  draw();
}
function partsList() {
  const foc = focusIds();
  return `<ol class="parts">${CUR.fields.map(f => `<li class="f-${f.id}${foc.includes(f.id) ? '' : ' off'}"><a href="#/field/${f.id}"><span class="n">${f.n}</span><span class="tx"><span class="t">${esc(f.name)}</span><span class="p">${esc(f.pname)}</span><span class="hk">${esc(f.hook)}</span></span></a></li>`).join('')}</ol>`;
}
async function chooseFocus() {
  const foc = focusIds();
  return new Promise(res => {
    const m = modal(`<h3>This semester</h3><p class="small muted">Tick the fields you are taking now. The others stay available but step back.</p><div class="stack" style="gap:6px">${CUR.fields.map(f => `<label class="f-${f.id}"><input type="checkbox" value="${f.id}" ${foc.includes(f.id) ? 'checked' : ''}> <b>${esc(f.name)}</b> <span class="tiny muted">${esc(f.pname)}</span></label>`).join('')}</div><div class="row" style="margin-top:12px;justify-content:flex-end"><button class="btn" id="mno">Cancel</button><button class="btn primary" id="mok">Save</button></div>`);
    $('#mno', m.el).onclick = () => { m.close(); res(false); };
    $('#mok', m.el).onclick = () => { S.settings.focus = $$('input:checked', m.el).map(i => i.value); save(); m.close(); res(true); };
  });
}
const COURSE = { cl2: 'Con Law 2', crim1: 'Crim 1', crim2: 'Crim 2', ethics: 'Ethics', pil: 'PIL' };

/* ------------------------------------------------------------------ in-page dialogs (no alert/confirm/prompt: they are blocked in some hosts) */
function modal(html) {
  const wrap = document.createElement('div'); wrap.className = 'modal'; wrap.innerHTML = `<div class="mbox" role="dialog" aria-modal="true">${html}</div>`;
  document.body.appendChild(wrap);
  const close = () => wrap.remove();
  wrap.addEventListener('click', e => { if (e.target === wrap) close(); });
  return { el: wrap, close };
}
function askText(title, value = '', placeholder = '') {
  return new Promise(res => {
    const m = modal(`<h3>${esc(title)}</h3><textarea id="mtxt" rows="5" placeholder="${esc(placeholder)}">${esc(value)}</textarea><div class="row" style="margin-top:10px;justify-content:flex-end"><button class="btn" id="mno">Cancel</button><button class="btn primary" id="mok">Save</button></div>`);
    const t = $('#mtxt', m.el); t.focus();
    $('#mno', m.el).onclick = () => { m.close(); res(null); };
    $('#mok', m.el).onclick = () => { const v = t.value; m.close(); res(v); };
  });
}
function askYes(msg, yes = 'Yes') {
  return new Promise(res => {
    const m = modal(`<p>${esc(msg)}</p><div class="row" style="margin-top:10px;justify-content:flex-end"><button class="btn" id="mno">Cancel</button><button class="btn primary" id="mok">${esc(yes)}</button></div>`);
    $('#mno', m.el).onclick = () => { m.close(); res(false); };
    $('#mok', m.el).onclick = () => { m.close(); res(true); };
  });
}
async function loadExtras(id) {
  const m = meta(id);
  if (m.cases && !CASES[id]) CASES[id] = await getJSON(`data/cases/${id}.json?v=${m.hash}`).catch(() => ({}));
  if (m.notes && !NOTES[id]) NOTES[id] = await getJSON(`data/notes/${id}.json?v=${m.nhash || m.hash}`).catch(() => ({}));
}

/* ------------------------------------------------------------------ memory model (FSRS-5)
   Each provision you rate carries a stability S (the days until your chance of recalling it falls to 90%) and a
   difficulty D (1–10). Recall decays on a power curve, R(t) = (1 + 19/81 · t/S)^−0.5. A review is scheduled for the
   day R would fall to your target (90% by default), so each review comes just before you would forget. A successful
   recall at low R raises S the most: effortful retrieval is what makes memory last. Weights: FSRS-5 defaults
   (open-spaced-repetition), fitted on hundreds of millions of reviews. */
const ck = (cid, pid) => cid + '|' + pid;
const FW = [0.40255, 1.18385, 3.173, 15.69105, 7.1949, 0.5345, 1.4604, 0.0046, 1.54575, 0.1192, 1.01925, 1.9395, 0.11, 0.29605, 2.2698, 0.2315, 2.9898, 0.51655, 0.6621];
const DECAY = -0.5, FACTOR = 19 / 81;
const clampD = d => Math.min(10, Math.max(1, d));
const goal = () => S.settings.retention || 0.9;
const retr = (t, s) => Math.pow(1 + FACTOR * t / s, DECAY);
const ivlFor = s => Math.max(1, Math.min(36500, Math.round(s / FACTOR * (Math.pow(goal(), 1 / DECAY) - 1))));
const d0 = g => clampD(FW[4] - Math.exp(FW[5] * (g - 1)) + 1);
/* cards rated under the earlier SM-2 scheduler keep their history: interval ≈ stability, ease → difficulty */
function upgrade(c) { if (c && c.s == null && c.last && c.ivl != null) { c.s = Math.max(0.5, c.ivl || 0.5); c.d = clampD(10 - ((c.ease || 2.5) - 1.3) * 3.5); } return c; }
function recallNow(c, now = Date.now()) { if (!c || c.s == null || !c.last) return null; return retr(Math.max(0, (now - c.last) / DAY), c.s); }
function nextState(c0, g, now) {
  const c = upgrade(Object.assign({}, c0 || {}));
  const el = c.last ? Math.max(0, (now - c.last) / DAY) : 0;
  let s, d;
  if (c.s == null) { s = FW[g - 1]; d = d0(g); }
  else {
    const R = retr(el, c.s);
    d = clampD(FW[7] * d0(4) + (1 - FW[7]) * (c.d + (-FW[6] * (g - 3)) * (10 - c.d) / 9));
    if (el < 1) s = c.s * Math.exp(FW[17] * (g - 3 + FW[18]));
    else if (g === 1) s = Math.min(c.s, FW[11] * Math.pow(c.d, -FW[12]) * (Math.pow(c.s + 1, FW[13]) - 1) * Math.exp(FW[14] * (1 - R)));
    else s = c.s * (1 + Math.exp(FW[8]) * (11 - c.d) * Math.pow(c.s, -FW[9]) * (Math.exp(FW[10] * (1 - R)) - 1) * (g === 2 ? FW[15] : 1) * (g === 4 ? FW[16] : 1));
  }
  s = Math.max(0.1, s);
  return { s, d, ivl: g === 1 ? 0 : ivlFor(s) };
}
function status(key) {
  const c = S.cards[key];
  if (!c) return '';
  if (!c.reps) return 's';
  if (c.ivl >= 21) return 'm';
  return 'l';
}
const LEECH = 4;
function rate(key, g) {
  const now = Date.now();
  const c = upgrade(S.cards[key] || { reps: 0, lapses: 0, seen: now });
  const first = !c.reps && !c.last;
  const ns = nextState(c, g, now);
  if (g === 1 && !first && (c.ivl || 0) >= 1) c.lapses = (c.lapses || 0) + 1;
  c.s = ns.s; c.d = ns.d; c.ivl = ns.ivl; c.reps = (c.reps || 0) + 1;
  c.due = g === 1 ? now + 10 * 60000 : now + c.ivl * DAY - 3600000;
  c.last = now; c.hist = (c.hist || []).slice(-19).concat([[now, g]]);
  delete c.ease;
  S.cards[key] = c;
  bumpDay(first ? 'n' : 'r');
  if (g === 1 && c.lapses >= LEECH && c.lapses % 2 === 0) setTimeout(() => toast(`Forgotten ${c.lapses} times. Give it a picture hook: it is the fastest fix for a stubborn provision.`), 300);
  save();
  return c;
}
function dueKeys() { const now = Date.now(); return Object.entries(S.cards).filter(([, c]) => (c.reps || c.last) && c.due && c.due <= now).sort((a, b) => a[1].due - b[1].due).map(([k]) => k); }
function newToday() { return (S.days[today()] || {}).n || 0; }
function streak() { let n = 0, d = new Date(); for (;;) { const k = new Date(d - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); const v = S.days[k]; if (v && (v.r + v.n) > 0) { n++; d = new Date(d - DAY); } else break; } return n; }
function fmtIvl(d) { if (d < 1) return '10m'; if (d < 30) return Math.round(d) + 'd'; if (d < 365) return Math.round(d / 30) + 'mo'; return (d / 365).toFixed(1) + 'y'; }
function preview(key) { const now = Date.now(); return [1, 2, 3, 4].map(g => g === 1 ? '10m' : fmtIvl(nextState(S.cards[key], g, now).ivl)); }
/* the whole memory at a glance: average recall now, what is slipping, what falls due, what keeps being forgotten */
function memoryStats() {
  const now = Date.now(); let n = 0, sum = 0, risk = 0; const fc = Array(14).fill(0); const leeches = [];
  for (const [k, c0] of Object.entries(S.cards)) {
    const c = upgrade(c0); if (c.s == null || !c.last) continue;
    const r = recallNow(c, now); n++; sum += r; if (r < goal()) risk++;
    const dd = Math.floor((c.due - now) / DAY); if (dd < 14) fc[Math.max(0, dd)]++;
    if ((c.lapses || 0) >= LEECH) leeches.push(k);
  }
  return { n, avg: n ? sum / n : 0, risk, fc, leeches };
}

/* ------------------------------------------------------------------ text helpers */
const FN = /⟨(\d+)⟩/g;
const plain = s => typeof s === 'string' ? s.replace(FN, '') : '';
/* The text in force. When a later law restated the whole provision, its text is what the learner reads and recalls;
   the text as enacted stays available as history. A partial restatement ("x x x") without a consolidated text falls
   back to the enacted text, flagged as partly amended. */
const letters = s => (s || '').toLowerCase().replace(/[^a-z]/g, '');
function stripHead(ps, cap) {
  const out = ps.slice(); const fi = out.findIndex(x => typeof x === 'string'); if (fi < 0) return { ps: out, cap: '' };   // tables are kept in place
  let s = out[fi]; let newCap = '';
  const art = /^\s*(?:Art(?:icle)?\.?|ART(?:ICLE)?\.?|Sec(?:tion)?\.?|SEC(?:TION)?\.?)\s*\d+(?:-[A-Za-z])?\.?\s*/.exec(s);
  if (art) s = s.slice(art[0].length);
  // where the provision's own caption ends, if the amended text starts with it
  const want = letters(cap); let capEnd = -1;
  if (want && letters(s).startsWith(want)) { let k = 0, i = 0; while (i < s.length && k < want.length) { if (/[a-z]/i.test(s[i])) k++; i++; } capEnd = i; }
  if (art || capEnd >= 0) {
    // the heading ends at the first ". -", " - ", "—" or "–" after the caption (a caption may be longer in the new law)
    const sep = [...s.slice(0, 320).matchAll(/\.\s*[–—-]+\s*|\s[–—-]{1,2}\s*|[—–]\s*/g)].find(m => m.index >= Math.max(0, capEnd - 1));
    if (sep) { newCap = s.slice(0, sep.index); s = s.slice(sep.index + sep[0].length); }
    else if (capEnd >= 0) { newCap = s.slice(0, capEnd); s = s.slice(capEnd).replace(/^[\s.;:,–—-]+/, ''); }
  } else {
    // a caption without an article number: "Qualified theft. – The crime…", "Graduated scales.—In…"
    const m = /^([A-Z][^.—–]{3,230}?)(?:\.\s*[—–-]+|\s+[—–]|[—–])\s*(?=["“(]?[A-Z])/.exec(s);
    if (m) {
      newCap = m[1]; s = s.slice(m[0].length);
      const m2 = /^([A-Z][^.—–]{3,60}?)\.\s*[—–-]+\s*(?=["“(]?[A-Z])/.exec(s);   // a two-part caption: "… — Who shall be deemed as such. –"
      if (m2) { newCap += ' — ' + m2[1]; s = s.slice(m2[0].length); }
    }
  }
  if (s.trim()) out[fi] = s; else out.splice(fi, 1);
  return { ps: out, cap: newCap.replace(/[\s.;:—–-]+$/, '').trim() };
}
const isPart = a => !a.cons && /\bx\s*x\s*x\b/i.test(a.p.filter(x => typeof x === 'string').join(' '));
function inForce(p) {
  const as = p.a || []; const a = as.at(-1);
  if (!a) return { ps: p.p, a: null, partial: false, cap: p.c || '' };
  if (!isPart(a)) { const h = stripHead(a.cons || a.p, p.c); return { ps: h.ps, a, partial: false, cap: h.cap || p.c || '' }; }
  // the latest law rewrote only parts ("x x x"): the base is the last whole text before it, and the parts follow
  let k = as.length - 1; while (k >= 0 && isPart(as[k])) k--;
  const parts = as.slice(k + 1);
  if (k >= 0) { const h = stripHead(as[k].cons || as[k].p, p.c); return { ps: h.ps, a, partial: true, base: as[k], parts, cap: h.cap || p.c || '' }; }
  return { ps: p.p, a, partial: true, base: null, parts, cap: p.c || '' };
}
const provText = p => inForce(p).ps.filter(x => typeof x === 'string').map(plain).join('\n');
const words = s => s.split(/\s+/).filter(Boolean);
const NUMW = 'one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|half|one-half|one-third|one-fourth|two-thirds|three-fourths|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth';
const DEFSRC = String.raw`\b(?:shall mean|refers? to|shall refer to|is understood|are understood|shall be understood|is defined as|are those|shall include)\b|(?<!\b(?:by|of|any|other|similar|employing|employ|the|a|an|such|all|these|those|no|its|his|her|their|legal|lawful|available|reasonable|adequate|financial|appropriate|effective|some|every|same|necessary|proper|whatever|peaceful|electronic|fraudulent|illegal)\s)\bmeans\b(?=[\s,](?!\s*(?:of|to|whereby|employed|used|be|by|for|through)\b))`;
const RX = {
  pen: /\b(reclusi[oó]n perpetua|reclusi[oó]n temporal|prisi[oó]n mayor|prisi[oó]n correccional|arresto mayor|arresto menor|destierro|public censure|perpetual (?:absolute|special) disqualification|temporary (?:absolute|special) disqualification|life imprisonment|imprisonment|fine of [^,;.]{1,60}|a fine|fines?|penalty of [a-z ]{3,40}|death penalty)\b/gi,
  num: new RegExp(String.raw`(?:₱|P(?=\s?\d))\s?\d[\d,]*(?:\.\d+)?|\b\d+(?:\.\d+)?\s?%|\b(?:\d[\d,]*(?:\.\d+)?|(?:${NUMW})(?:[ -](?:${NUMW}|and))*)(?:\s*\(\d[\d,.]*\))?\s+(?:calendar |working |consecutive |full )?(?:days?|months?|years?|hours?|weeks?|minutes?|per\s?cent(?:um)?|percent|pesos|centavos|hectares?|meters?|kilometers?|degrees?|times|members|votes|witnesses)\b|\b(?:${NUMW})(?:[ -](?:${NUMW}))*\s*\(\d[\d,.]*\)|\b(?:one-half|one-third|two-thirds|three-fourths|one-fourth|majority)\b`, 'gi'),
  exc: /\b(unless|except(?:ing)?|notwithstanding|however|nevertheless|without prejudice to|other than|save (?:as|those|when|in)|provided,? however)\b/gi,
  cond: /\b(if|when|whenever|in case|in the event|provided(?:,)? that|provided(?=,?\s+(?:that|further|finally|also|moreover)\b)|as long as|so long as|only if|on condition|subject to)\b/gi,
  op: /\b(shall not|shall|may not|may|must not|must|cannot|can not|is prohibited|are prohibited|is hereby|are hereby|it shall be unlawful|null and void|void|voidable|unenforceable|rescissible|inexistent|liable|entitled)\b/gi,
  def: new RegExp(DEFSRC, 'gi'),
};
const HLORDER = ['pen', 'num', 'exc', 'cond', 'op', 'def'];
const HLCLASS = { op: 'hl-op', cond: 'hl-cond', exc: 'hl-exc', num: 'hl-num', pen: 'hl-pen', def: 'hl-def' };
const HLNAME = { op: 'Duties & powers', cond: 'Conditions', exc: 'Exceptions', num: 'Numbers & periods', pen: 'Penalties', def: 'Definitions' };
function spans(text, on) {
  const out = [];
  for (const k of HLORDER) {
    if (!on[k]) continue;
    RX[k].lastIndex = 0; let m;
    while ((m = RX[k].exec(text))) {
      if (!m[0].trim()) { RX[k].lastIndex++; continue; }
      const a = m.index, b = a + m[0].length;
      if (k === 'num' && /^(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)$/i.test(m[0])) continue;
      if (!out.some(s => a < s[1] && b > s[0])) out.push([a, b, k]);
    }
  }
  return out.sort((x, y) => x[0] - y[0]);
}
const OTHER_LAW = /^\s*(?:,?\s*(?:paragraph|par\.|No\.|number)[^,]{0,20})?\s*of\s+(?:the\s+)?(?:Act|Republic|Presidential|Commonwealth|Batas|Executive|Revised Penal|Civil Code|Labor Code|Family Code|Code of Commerce|Constitution|Rules|Local Government|Tax Code|National Internal|Corporation|Insurance|Administrative|Omnibus|this Act|the Act)/i;
function linkRefs(html, d, cid) {
  if (!d) return html;
  return html.replace(/\b(Art(?:icle|\.)s?|ART\.|Sec(?:tion|\.)s?|SEC\.)\s+(\d+(?:-[A-Z])?)(?![\w-])/g, (all, kw, n, off, str) => {
    const after = str.slice(off + all.length, off + all.length + 70).replace(/<[^>]+>/g, '');
    if (OTHER_LAW.test(after) && !/^\s*of\s+this\s+Code/i.test(after)) return all;
    const p = d.byNum[n];
    const kind = /^S/i.test(kw) ? 'section' : 'article';
    if (!p || !p.l.toLowerCase().includes(kind)) return all;
    return `<a href="#/p/${cid}/${p.i}" title="${esc(p.l + (p.c ? ' — ' + p.c : ''))}">${all}</a>`;
  });
}
function hlText(text, on) {
  const ss = spans(text, on); let h = '', i = 0;
  for (const [a, b, k] of ss) { h += esc(text.slice(i, a)) + `<span class="${HLCLASS[k]}">${esc(text.slice(a, b))}</span>`; i = b; }
  return h + esc(text.slice(i));
}
/* --------- reading layout: the verbatim words, arranged so the structure shows.
   Enumerations hang from a marker gutter and nest by level; a lead-in that ends with a colon
   says how many items follow; each proviso starts on its own line. Not one word is changed. */
const MK = /^(\(?)([0-9]{1,2}|[a-z]{1,2}|[ivx]{1,5})([.)])\s+/;
const ORDW = ['First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh', 'Eighth', 'Ninth', 'Tenth', 'Eleventh', 'Twelfth'];
const ORD = new RegExp(`^(${ORDW.join('|')})[.,—:-]`);
const ROMAN = /^(i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|xiii|xiv|xv)$/;
const PROVISO = /(?<=[:;.,]\s)(?=Provided(?:,)?(?:\s+(?:however|further(?:more)?|finally|also|moreover|lastly))?,?\s+[Tt]hat\b)/;
function markerOf(x, last) {
  if (typeof x !== 'string') return null;
  const o = ORD.exec(x); if (o) return { key: 'ord', tok: o[1], mk: String(ORDW.indexOf(o[1]) + 1), body: x, first: o[1] === 'First' };
  const m = MK.exec(x); if (!m) return null;
  const [all, open, tok, close] = m; const shape = open ? '()' : close;
  let type = /^\d+$/.test(tok) ? 'n' : 'a';
  if (type === 'a' && ROMAN.test(tok)) {
    const la = last['a' + shape];
    const afterLetter = tok.length === 1 && la && la.length === 1 && la.charCodeAt(0) + 1 === tok.charCodeAt(0);
    if (!afterLetter && (tok.length > 1 || tok === 'i' || last['r' + shape])) type = 'r';
  }
  const first = tok === '1' || (type === 'a' && tok === 'a') || (type === 'r' && tok === 'i');
  return { key: type + shape, tok, mk: all.trim(), body: x.slice(all.length), first };
}
const SRCN = /([.;:"”])\s(\((?:\d+[a-z]?|n)(?:,\s*(?:\d+[a-z]?|n))*\))\s*$/;
function splitSrc(t) { const m = SRCN.exec(t); return m ? [t.slice(0, m.index + 1), m[2]] : [t, '']; }
function inlineLaw(t, on, d, cid) {
  let h = on ? hlText(t, on) : esc(t);
  h = h.replace(/⟨(\d+)⟩/g, '<sup class="fn" data-fn="$1">$1</sup>');
  return linkRefs(h, d, cid);
}
function lawInline(t, on, d, cid) {
  const segs = t.split(PROVISO);
  return segs.map((x, i) => i ? `<span class="so">${inlineLaw(x, on, d, cid)}</span>` : inlineLaw(x, on, d, cid)).join('');
}
function tableHTML(x) { return `<div class="tbl"><table>${x.rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div>`; }
function lawLayout(paras) {
  const last = {}; const ms = paras.map(x => { const m = markerOf(x, last); if (m) last[m.key] = m.tok; return m; });
  const stack = []; const info = [];
  paras.forEach((x, i) => {
    const m = ms[i];
    if (m) {
      let k = stack.indexOf(m.key);
      if (k >= 0) stack.length = k + 1; else { stack.push(m.key); k = stack.length - 1; }
      info.push({ kind: 'item', lv: Math.min(k + 1, 3) }); return;
    }
    if (typeof x !== 'string') { info.push({ kind: 'table', lv: stack.length ? Math.min(stack.length, 3) : 0 }); return; }
    if (/^\s*x\s*x\s*x\.?\s*$/i.test(x)) { info.push({ kind: 'elide', lv: Math.min(stack.length, 3) }); return; }
    let j = i + 1; while (j < paras.length && !ms[j]) j++;
    const nx = ms[j];
    if (stack.length && nx && stack.includes(nx.key) && !nx.first) { info.push({ kind: 'cont', lv: Math.min(stack.length, 3) }); return; }
    stack.length = 0; info.push({ kind: 'para', lv: 0 });
  });
  return { ms, info };
}
/* wrap one paragraph's inner html in the same hanging layout the law text uses */
function layoutWrap(m, f, inner, extra = '') {
  if (m) return `<div class="en l${f.lv}${extra}"><span class="mk">${esc(m.mk)}</span><p>${inner}</p></div>`;
  return `<p class="${f.kind === 'cont' ? `cont l${f.lv}` : ''}${extra}">${inner}</p>`;
}
function lawBody(paras, on, d, cid) {
  const { ms, info } = lawLayout(paras);
  return paras.map((x, i) => {
    const m = ms[i], f = info[i];
    if (f.kind === 'table') return tableHTML(x);
    if (f.kind === 'elide') return `<p class="elide l${f.lv}">${esc(x)}</p>`;
    const text = m ? m.body : x;
    let tag = '';
    if (/:\s*$/.test(text) && ms[i + 1]) {
      let n = 0;
      for (let j = i + 1; j < paras.length; j++) {
        const g = info[j];
        if (g.kind === 'para') break;
        if (g.kind === 'item') { if (g.lv <= f.lv) break; if (g.lv === f.lv + 1) n++; }
      }
      if (n >= 2) tag = `<span class="nitems" title="${n} items follow">${n} items</span>`;
    }
    const [main, src] = splitSrc(text);
    const body = lawInline(main, on, d, cid) + (src ? ` <span class="srcn" title="Source note, not part of the rule: the earlier article this one is based on (a = amended, n = new)">${esc(src)}</span>` : '') + tag;
    if (m) return `<div class="en l${f.lv}${tag ? ' stem' : ''}"><span class="mk" aria-hidden="${m.key === 'ord'}">${esc(m.mk)}</span><p>${body}</p></div>`;
    return `<p class="${f.kind === 'cont' ? `cont l${f.lv}` : ''}${tag ? ' stem' : ''}${/^Provided\b/.test(text) ? ' so' : ''}">${body}</p>`;
  }).join('');
}
function renderPara(x, on, d, cid) { return lawBody([x], on, d, cid); }

/* --------- legal anatomy: an automatic reading guide built from the verbatim text */
function sentences(t) { return t.replace(/\s+/g, ' ').split(/(?<=[.;:])\s+(?=[A-Z(“"])/).map(s => s.trim()).filter(s => s.length > 2); }
function kindOf(s, item) {
  const l = s.toLowerCase();
  if (new RegExp(DEFSRC, 'i').test(s) || /\b(is one who|are those who|is deemed|are deemed|shall be deemed|there is \w+ when)\b/i.test(s)) return 'Definition';
  if (/\b(reclusi[oó]n|prisi[oó]n|arresto|destierro|imprisonment|fine of|shall be punished|penalty of|shall suffer)\b/.test(l)) return 'Penalty';
  if (item) return 'Element / item';
  if (/\b(shall not|may not|must not|cannot|can not|is prohibited|are prohibited|unlawful|no person shall|no .{1,40} shall)\b/.test(l)) return 'Prohibition';
  if (/\b(unless|except|notwithstanding|however|nevertheless|provided,? however)\b/.test(l)) return 'Exception';
  if (/^(if|when|whenever|in case|should|where)\b/.test(l)) return 'Condition';
  if (/\b(shall|must|is required|are required|is obliged|are obliged|is bound)\b/.test(l)) return 'Duty / rule';
  if (/\b(may|is entitled|are entitled|has the right|have the right)\b/.test(l)) return 'Power / right';
  return 'Statement';
}
/* one row per enumerated item (marker kept), one row per sentence elsewhere; provisos get their own row */
function anatomy(p) {
  const out = []; const last = {}; const stems = [];
  for (const x of inForce(p).ps) {
    if (typeof x !== 'string') continue;
    const m = markerOf(x, last); if (m) last[m.key] = m.tok;
    const t = splitSrc(plain(m && m.key !== 'ord' ? m.body : x))[0];
    if (/^\s*x\s*x\s*x\.?\s*$/i.test(t)) continue;
    if (m) { out.push([kindOf(t, true), t, m.key === 'ord' ? '' : m.mk]); continue; }
    if (/:\s*$/.test(t)) stems.push(t);
    for (const seg of t.split(PROVISO)) for (const s of sentences(seg)) {
      let k = /^Provided\b/.test(s) ? 'Proviso' : kindOf(s, false);
      if (/:\s*$/.test(s) && (k === 'Exception' || k === 'Condition' || k === 'Statement')) k = 'Duty / rule';
      out.push([k, s, '']);
    }
  }
  const t = provText(p);
  const periods = (t.match(RX.num) || []).filter(x => /day|month|year|hour|week|per\s?cent|percent|pesos|₱|\d{2,}/i.test(x));
  const lay = lawLayout(inForce(p).ps); const nested = lay.info.some(f => f.kind === 'item' && f.lv > 1);
  const st = stems.join(' ');
  const mode = nested || stems.length !== 1 ? '' : /\bany (?:one )?of the following\b|\beither\b/i.test(st) ? 'any' : /\bconcur|\brequisites?\b|\ball of the following\b|\belements?\b/i.test(st) ? 'all' : '';
  return { items: out, periods: [...new Set(periods)].slice(0, 12), mode };
}

/* --------- recall builders */
const LEX = /^(void|voidable|unenforceable|rescissible|inexistent|solidary|solidarily|joint|jointly|divisible|indivisible|fortuitous|negligence|fraud|delay|mora|dolo|culpa|reclusion|prision|arresto|destierro|perpetua|temporal|mayor|correccional|menor|accessory|principal|accomplice|accomplices|accessories|aggravating|mitigating|justifying|exempting|alternative|consummated|frustrated|attempted|conspiracy|proposal|usufruct|easement|servitude|possession|ownership|prescription|laches|estoppel|novation|compensation|confusion|condonation|subrogation|consignation|tender|redemption|pre-emption|mortgage|pledge|antichresis|guaranty|surety|agency|partnership|lease|sale|donation|legitime|collation|reserva|testamentary|intestate|holographic|notarial|codicil|annulment|nullity|legal|separation|conjugal|community|filiation|legitimate|illegitimate|legitimated|adoption|support|parental|authority|emancipation|majority|jurisdiction|appellate|original|exclusive|concurrent|certiorari|mandamus|prohibition|quo|warranto|habeas|amparo|due|process|equal|protection|search|seizure|warrant|probable|cause|privacy|expression|assembly|religion|establishment|abode|travel|information|association|eminent|domain|compensation|contracts|impairment|custodial|investigation|counsel|bail|self-incrimination|double|jeopardy|ex|post|facto|attainder|tenure|regular|probationary|casual|seasonal|project|retirement|separation|backwages|reinstatement|strike|lockout|bargaining|unfair|union|wages|overtime|holiday|premium|night|differential|service|incentive|leave|maternity|paternity|quorum|majority|two-thirds|three-fourths|ultra|vires|derivative|appraisal|dividends|by-laws|incorporators|directors|trustees|stockholders|members|good|faith|bad|faith|public|policy|morals|customs|order|damages|moral|exemplary|nominal|temperate|liquidated|actual|compensatory|interest|penal|clause)$/i;
function hashStr(s) { let h = 2166136261; for (const c of s) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; }
function clozeModel(p, level, seed) {
  const t = provText(p);
  const toks = t.split(/(\s+)/);
  const cand = [];
  let wi = 0;
  toks.forEach((tok, i) => {
    if (/^\s+$/.test(tok) || !tok) return;
    wi++;
    const core = tok.replace(/^[“"(‘'[]+|[”"),.;:!?’'\]]+$/g, '');
    if (!core || core.length < 2) return;
    let score = 0;
    if (/^\d[\d,.]*%?$/.test(core) || new RegExp(`^(${NUMW})$`, 'i').test(core) || /^\(\d+\)$/.test(core)) score = 9;
    else if (/^(shall|may|must|cannot|not|void|voidable|unenforceable|liable)$/i.test(core)) score = 6;
    else if (LEX.test(core)) score = 7;
    else if (/^(days?|months?|years?|hours?|weeks?)$/i.test(core)) score = 8;
    else if (core.length >= 9) score = 3;
    else if (core.length >= 6 && !/^(the|and|which|shall|their|there|these|those|other|under|without|within|before|after|such|said|whose|whom|that|this|with|from|upon|into|have|been|being|where|when|while)$/i.test(core)) score = 1;
    if (score) cand.push({ i, core, score: score + ((hashStr(seed + ':' + i) % 100) / 100) });
  });
  const nWords = wi;
  const target = Math.max(1, Math.min(level === 1 ? 4 : level === 2 ? 8 : 14, Math.round(nWords / (level === 1 ? 16 : level === 2 ? 9 : 5))));
  const picked = new Set(cand.sort((a, b) => b.score - a.score).slice(0, target).map(c => c.i));
  return { toks, picked };
}
function normWord(w) { return w.toLowerCase().replace(/[“”"’‘'().,;:!?[\]—–-]/g, '').replace(/ó/g, 'o'); }
function lcsDiff(a, b) {
  // a = verbatim words, b = attempt words; returns ops on a: [{w, ok}], extras from b
  const n = a.length, m = b.length;
  const A = a.map(normWord), B = b.map(normWord);
  const dp = Array.from({ length: n + 1 }, () => new Uint16Array(m + 1));
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--) dp[i][j] = A[i] === B[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const out = []; let i = 0, j = 0;
  while (i < n && j < m) { if (A[i] === B[j]) { out.push({ w: a[i], t: 'ok' }); i++; j++; } else if (dp[i + 1][j] >= dp[i][j + 1]) { out.push({ w: a[i], t: 'miss' }); i++; } else { out.push({ w: b[j], t: 'extra' }); j++; } }
  while (i < n) out.push({ w: a[i++], t: 'miss' });
  while (j < m) out.push({ w: b[j++], t: 'extra' });
  return { out, score: n ? dp[0][0] / n : 0, precision: m ? dp[0][0] / m : 0 };
}

/* ------------------------------------------------------------------ views */
function setNav(k) { $$('[data-nav]').forEach(a => a.classList.toggle('on', a.dataset.nav === k)); }
function crumbs(d, p, cid) {
  const chain = []; let v = p ? p.d : null;
  while (v != null) { chain.unshift(v); v = d.divisions[v].p; }
  const f = fieldOf(cid);
  return `<div class="crumbs"><a href="#/learn">Learn</a>${f ? `<span class="sep">›</span><a href="#/field/${f.id}">${esc(f.name)}</a>` : ''}<span class="sep">›</span><a href="#/code/${cid}">${esc(d.short)}</a>${chain.slice(-2).map(i => `<span class="sep">›</span><a href="#/code/${cid}?div=${i}">${esc(shortDiv(d.divisions[i].t))}</a>`).join('')}</div>`;
}
function shortDiv(t) { return t.length > 60 ? t.slice(0, 57) + '…' : t; }
function counts(cid) {
  const m = meta(cid); let s = 0, l = 0, mm = 0;
  const pre = cid + '|';
  for (const k in S.cards) if (k.startsWith(pre)) { const st = status(k); if (st === 'm') mm++; else if (st === 'l') l++; else if (st === 's') s++; }
  return { total: m.count, s, l, m: mm, touched: s + l + mm };
}
function bar(c) { const t = c.total || 1; return `<div class="bar" title="${c.m} mastered · ${c.l} learning · ${c.s} read"><i class="m" style="width:${c.m / t * 100}%"></i><i class="l" style="width:${c.l / t * 100}%"></i><i class="s" style="width:${c.s / t * 100}%"></i></div>`; }
function codeCard(c) {
  const k = counts(c.id);
  return `<a class="card codecard" href="#/code/${c.id}"><div class="row"><span class="t">${esc(c.short)}</span><span class="spacer"></span>${c.core ? '<span class="chip gold">Core</span>' : ''}</div><div class="c">${esc(c.citation)}</div>${bar(k)}<div class="row tiny muted"><span>${c.count.toLocaleString()} provisions</span><span class="spacer"></span><span>${k.touched ? Math.round(k.touched / k.total * 100) + '% studied' : 'Not started'}</span>${c.cases ? '<span class="chip violet">Cases</span>' : ''}${c.notes ? '<span class="chip ok">Guides</span>' : ''}</div></a>`;
}

async function home() {
  setNav('home');
  const due = dueKeys().length, nt = newToday(), st = streak();
  const last = S.last;
  let head, sub, btn, second = '';
  const ms = memoryStats(); const mins = S.settings.sprint || 5;
  if (due) { head = `${due} provision${due === 1 ? ' is' : 's are'} slipping`; sub = `A ${mins}-minute sprint brings back the ones you are closest to forgetting, one at a time.`; btn = `<a class="btn primary" href="#/sprint">Start a ${mins}-minute sprint</a>`; second = `<a class="btn" href="#/review">Review all ${due}</a>`; }
  else if (last) { head = `Continue where you stopped`; sub = esc(last.l); btn = `<a class="btn primary" href="#/p/${last.c}/${last.p}">Continue</a>`; second = `<a class="btn" href="#/sprint">${mins}-minute sprint</a>`; }
  else { head = 'Start with ten minutes'; sub = 'One short lesson on how to read any provision. It makes everything after it easier.'; btn = `<a class="btn primary" href="#/lesson/read-provision">Read the first lesson</a>`; second = `<a class="btn" href="#/learn">Choose a field</a>`; }
  main.innerHTML = `
  <section class="next"><span class="eyebrow">Your next step</span><h1>${head}</h1><p class="muted" style="margin:0">${sub}</p>
    <div class="row">${btn}${second}</div>
    <div class="meters">${ms.n ? `<span title="Average chance you would recall a provision you are keeping, if asked right now"><b>${Math.round(ms.avg * 100)}%</b> recall</span>` : ''}<span><b>${due}</b> due</span><span><b>${nt}</b> of ${S.settings.newPerDay} new today</span><span><b>${st}</b> day streak</span><a href="#/progress">Memory</a></div></section>
  <div class="sect"><h2>The House of Law</h2><span class="spacer"></span><button class="btn sm ghost" id="foc">This semester</button><button class="btn sm ghost" id="pic">Use a place you know</button></div>
  <p class="small muted" style="margin:-4px 0 12px;max-width:65ch">Eight fields, eight places in one building drawn after the Supreme Court on Padre Faura, read from the roof down to the seven steps. A fixed place is a fixed cue: when you forget, walk through the building again.</p>
  <div class="plate bodymap"><div class="pfig">${figure()}</div>${partsList()}<p class="cap">Read from the roof down to the steps. Faded fields are outside this semester.</p></div>
  <div class="more"><a href="#/map">The whole map</a><a href="#/sprint">Sprint</a><a href="#/syllabus">Syllabus cases</a><a href="#/syllabus/recent">Recent rulings</a><a href="#/drill">Drill</a><a href="#/search">Find a case</a><a href="#/about">How this works</a></div>`;
  $('#foc').onclick = async () => { if (await chooseFocus()) home(); };
  $('#pic').onclick = () => figurePicture(home);
}

function learn() {
  setNav('library');
  const foc = focusIds();
  const tile = f => { const k = fieldCount(f); const lb = S.lastBy[f.id]; const first = f.tracks[0].items[0];
    const start = first.t === 'code' ? meta(first.id).short : first.t === 'lesson' ? CUR.lessons[first.id].title : first.title || '';
    return `<a class="tile f-${f.id}" href="#/field/${f.id}"><span class="p">${f.n} · ${esc(f.pname)}</span><span class="t">${esc(f.name)}</span><span class="q">${esc(f.q)}</span><div class="thin"><i style="width:${Math.min(100, k.pct).toFixed(1)}%"></i></div><span class="go">${lb ? `Continue: <b>${esc(lb.l)}</b>` : `Start here: <b>${esc(start)}</b>`}</span></a>`; };
  const mine = CUR.fields.filter(f => foc.includes(f.id)), rest = CUR.fields.filter(f => !foc.includes(f.id));
  main.innerHTML = `<div class="crumbs"><a href="#/map">The whole map</a><span class="sep">›</span><span>Fields and study paths</span></div><h1>Learn</h1><p class="lead">Pick one field. Inside it you will find a short path: start here, then the core, then deeper only when you need it.</p>
  <div class="sect"><h2>This semester</h2><span class="spacer"></span><button class="btn sm ghost" id="foc">Change</button></div>
  <div class="tiles">${mine.map(tile).join('') || '<p class="muted">No fields chosen yet.</p>'}</div>
  ${rest.length ? `<div class="sect"><h2>Other fields</h2></div><div class="tiles">${rest.map(tile).join('')}</div>` : ''}
  <div class="more"><a href="#/library">All ${CAT.codes.length} codes in one list</a><a href="#/search">Search</a></div>`;
  $('#foc').onclick = async () => { if (await chooseFocus()) learn(); };
}

function itemRow(it, f) {
  if (it.t === 'code') { const m = meta(it.id), k = counts(it.id); return `<li><a href="#/code/${it.id}"><span class="kind">Code</span><span><span class="it">${esc(m.short)}</span><br><span class="im">${esc(m.citation)}${it.x ? ' · also in ' + esc(fieldOf(it.id).name) : ''}</span></span><span class="st">${k.touched}/${k.total.toLocaleString()}</span></a></li>`; }
  if (it.t === 'lesson') { const l = CUR.lessons[it.id]; return `<li><a href="#/lesson/${it.id}"><span class="kind k-lesson">Lesson</span><span><span class="it">${esc(l.title)}</span><br><span class="im">${l.mins} minute read</span></span><span class="st">${S.lessons[it.id] ? '<span class="done">Read</span>' : ''}</span></a></li>`; }
  if (it.t === 'set') { const st = CUR.sets[it.id]; const n = st.items.filter(x => S.cards[ck(x.c, x.i)]).length; return `<li><a href="#/set/${it.id}"><span class="kind k-set">Walk</span><span><span class="it">${esc(st.title)}</span><br><span class="im">${st.items.length} provisions, placed head to toe</span></span><span class="st">${n}/${st.items.length}</span></a></li>`; }
  if (it.t === 'b2') return `<li><a href="#/b2"><span class="kind k-set">Studio</span><span><span class="it">${esc(it.title)}</span><br><span class="im">Crimes in families: elements, comparison tables, drills</span></span><span class="st"></span></a></li>`;
  if (it.t === 'syl') return `<li><a href="#/syllabus/${it.id}"><span class="kind k-syl">Cases</span><span><span class="it">${esc(it.title)}</span><br><span class="im">Every assigned case, filed under its provision</span></span><span class="st"></span></a></li>`;
  return `<li><div class="miss"><span class="kind k-miss">Not yet</span><span><span class="it">${esc(it.title)}</span><br><span class="im">${esc(it.citation)}. ${esc(it.why)}${it.url ? ` <a href="${esc(it.url)}" target="_blank" rel="noopener">Official text</a>` : ''}</span></span></div></li>`;
}
function fieldView(id) {
  setNav('library');
  const f = CUR.byId[id];
  if (!f) return learn();
  const k = fieldCount(f); const lb = S.lastBy[f.id];
  const tierName = { start: 'Start here', core: 'Core', deep: 'Go deeper when you need it' };
  let prevTier = '';
  const tracks = f.tracks.map(t => {
    const head = t.tier !== prevTier ? `<div class="tier">${tierName[t.tier]}</div>` : ''; prevTier = t.tier;
    const n = t.items.filter(i => i.t !== 'missing').length;
    return `${head}<details class="track" ${t.tier === 'start' ? 'open' : ''}><summary><span class="tn">${esc(t.name)}</span><span class="cnt">${n} item${n === 1 ? '' : 's'}</span><span class="pic">Picture: ${esc(t.pic)}</span>${t.why ? `<span class="why">${esc(t.why)}</span>` : ''}</summary><ul class="items">${t.items.map(i => itemRow(i, f)).join('')}</ul></details>`;
  }).join('');
  main.innerHTML = `<div class="f-${f.id}"><div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><span>${esc(f.name)}</span></div>
  <div class="fhead"><div><span class="eyebrow" style="color:var(--f)">${f.n} · ${esc(f.pname)}</span><h1>${esc(f.name)}</h1><p class="hook" style="margin:0 0 6px">${esc(f.hook)}</p><p class="small" style="margin:0 0 10px">${esc(f.q)}</p>
    <div class="thin" style="max-width:320px"><i style="width:${Math.min(100, k.pct).toFixed(1)}%"></i></div><p class="tiny muted" style="margin:6px 0 10px">${k.touched.toLocaleString()} of ${k.total.toLocaleString()} provisions studied</p>
    ${lb ? `<a class="btn primary" href="#/p/${lb.c}/${lb.p}">Continue ${esc(lb.l)}</a>` : ''}</div>${figure(f.id, true)}</div>
  <div class="path">${tracks}</div></div>`;
}
function findItem(type, id) { for (const f of CUR.fields) for (const t of f.tracks) { const ix = t.items.findIndex(i => i.t === type && i.id === id); if (ix >= 0) return { f, t, ix }; } return null; }
function lessonView(id) {
  setNav('library');
  const l = CUR.lessons[id]; if (!l) return learn();
  const at = findItem('lesson', id); const f = at.f; const nx = at.t.items[at.ix + 1];
  const nxLink = nx && nx.t !== 'missing' ? (nx.t === 'code' ? [`#/code/${nx.id}`, meta(nx.id).short] : nx.t === 'lesson' ? [`#/lesson/${nx.id}`, CUR.lessons[nx.id].title] : nx.t === 'set' ? [`#/set/${nx.id}`, CUR.sets[nx.id].title] : nx.t === 'b2' ? ['#/b2', nx.title] : [`#/syllabus/${nx.id}`, nx.title]) : null;
  main.innerHTML = `<article class="lesson f-${f.id}"><div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><a href="#/field/${f.id}">${esc(f.name)}</a><span class="sep">›</span><span>${esc(at.t.name)}</span></div>
  <span class="eyebrow" style="color:var(--f)">Lesson · ${l.mins} minutes</span><h1>${esc(l.title)}</h1><p class="lead">${rich(l.lead)}</p>
  ${l.sections.map(x => `<h2 class="sec">${esc(x.h.replace(/^\d+\.\s*/, ''))}</h2><div class="explain">${x.p.map(p => `<p>${rich(p)}</p>`).join('')}${x.l.length ? `<ul>${x.l.map(p => `<li>${rich(p)}</li>`).join('')}</ul>` : ''}</div>`).join('')}
  ${l.try.length ? `<h2>Try it now</h2><div class="tryit explain">${l.try.map(p => `<p>${rich(p)}</p>`).join('')}</div>` : ''}
  <p class="tiny muted" style="margin-top:14px">Lessons are study aids in our own words. The verbatim provisions they link to are what you cite.</p>
  <div class="pn"><button class="btn${S.lessons[id] ? '' : ' primary'}" id="ldone">${S.lessons[id] ? 'Read ✓' : 'Mark as read'}</button>${nxLink ? `<a class="btn" href="${nxLink[0]}">Next: ${esc(nxLink[1])} →</a>` : `<a class="btn" href="#/field/${f.id}">Back to ${esc(f.name)}</a>`}</div></article>`;
  $('#ldone').onclick = () => { if (S.lessons[id]) delete S.lessons[id]; else S.lessons[id] = Date.now(); save(); lessonView(id); };
}
function setView(id) {
  setNav('library');
  const st = CUR.sets[id]; if (!st) return learn();
  const at = findItem('set', id); const f = at.f;
  const first = st.items.find(x => !S.cards[ck(x.c, x.i)]) || st.items[0];
  main.innerHTML = `<div class="f-${f.id}" style="max-width:760px"><div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><a href="#/field/${f.id}">${esc(f.name)}</a><span class="sep">›</span><span>${esc(at.t.name)}</span></div>
  <span class="eyebrow" style="color:var(--ok)">A walk · ${st.items.length} provisions</span><h1>${esc(st.title)}</h1><p class="lead">${esc(st.blurb)}</p>
  <div class="tryit small" style="margin:12px 0"><b>How to use the walk.</b> Start at the flag on the roof of the House of Law and move down to the seven steps. At each place, see the provision’s key idea happening there, the stranger the better. To recall the list later, walk through the building again and say what you find at each place.</div>
  <ol class="walk">${st.items.map(x => `<li><a href="#/p/${x.c}/${x.i}?set=${id}"><span class="loc">${esc(x.loc)}</span><span><span class="wl">${esc(x.l)}</span>${x.cap ? ` <span class="muted small">${esc(x.cap)}</span>` : ''}<br><span class="ww">${esc(x.why)}</span>${S.hooks[ck(x.c, x.i)] ? `<br><span class="tiny" style="color:var(--warn)">Your picture: ${esc(S.hooks[ck(x.c, x.i)])}</span>` : ''}</span><i class="dot ${status(ck(x.c, x.i))}"></i></a></li>`).join('')}</ol>
  <div class="pn"><a class="btn" href="#/field/${f.id}">Back to ${esc(f.name)}</a><a class="btn primary" href="#/p/${first.c}/${first.i}?set=${id}">Start the walk →</a></div></div>`;
}

function library() {
  setNav('library');
  main.innerHTML = `<div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><span>All codes</span></div><h1>All codes</h1><p class="muted">Every instrument in the library, by field. Open a field to see its list.</p>
  <div class="path">${CUR.fields.map(f => { const ids = fieldCodes(f); return `<details class="track f-${f.id}"><summary><span class="tn">${esc(f.name)}</span><span class="cnt">${ids.length} codes</span></summary><ul class="items">${ids.map(id => itemRow({ t: 'code', id }, f)).join('')}</ul></details>`; }).join('')}</div>`;
}

function tocHTML(d, cid, openDiv) {
  const open = new Set();
  let v = openDiv; while (v != null) { open.add(v); v = d.divisions[v].p; }
  const provList = arr => arr.length ? `<ul class="plist">${arr.map(p => `<li><a href="#/p/${cid}/${p.i}"><span class="dot ${status(ck(cid, p.i))}"></span><span class="pl">${esc(p.l)}</span><span class="pc">${esc(p.c || firstWords(p))}${p.st ? ` <span class="chip ${p.st === 'superseded' ? 'warn' : 'bad'}" style="font-size:.68rem">${p.st === 'void' ? 'struck down' : p.st}</span>` : ''}</span></a></li>`).join('')}</ul>` : '';
  const node = i => {
    const dv = d.divisions[i];
    const n = countUnder(d, i);
    return `<details class="lvl${Math.min(dv.l, 4)}" data-div="${i}" ${open.has(i) ? 'open' : ''}><summary><span class="dt">${esc(dv.t)}</span><span class="tiny muted">${n}</span></summary><div class="kids" data-lazy="${i}">${open.has(i) ? divInner(d, i, cid, open, provList, node) : ''}</div></details>`;
  };
  d._node = node; d._provList = provList;
  const firstDiv = Math.min(1e9, ...d.provisions.filter(p => p.d != null).map(p => p.ix));
  return `<div class="toc">${provList(d.loose.filter(p => p.ix < firstDiv))}${d.roots.map(node).join('')}${provList(d.loose.filter(p => p.ix >= firstDiv))}</div>`;
}
function divInner(d, i, cid, open, provList, node) { return provList(d.divProv[i]) + d.kids[i].map(node).join(''); }
function countUnder(d, i) { let n = d.divProv[i].length; for (const k of d.kids[i]) n += countUnder(d, k); return n; }
function firstWords(p) { const t = plain(inForce(p).ps.find(x => typeof x === 'string') || ''); return t.length > 110 ? t.slice(0, 107) + '…' : t; }

async function codeView(cid, q) {
  setNav('library');
  const d = await loadCode(cid); const m = meta(cid);
  const k = counts(cid);
  // repealed or superseded provisions are not offered as new material
  const next = d.provisions.find(p => !p.st && !S.cards[ck(cid, p.i)]);
  const sitting = next ? d.provisions.slice(next.ix).filter(p => !p.st && !S.cards[ck(cid, p.i)]).slice(0, 5) : [];
  const openDiv = q.get('div') != null ? +q.get('div') : null;
  main.innerHTML = `${crumbs(d, null, cid)}
  <div class="codehead"><h1>${esc(d.title)}</h1><div class="muted">${esc(d.citation)}</div></div>
  <div class="grid" style="grid-template-columns:minmax(0,1fr) 320px;align-items:start" id="cv">
    <div class="card">${tocHTML(d, cid, openDiv)}</div>
    <aside class="grid">
      <div class="card"><div class="row"><div class="progress-ring" style="--p:${Math.round(k.touched / k.total * 100)}"><span>${Math.round(k.touched / k.total * 100)}%</span></div><div class="small"><b>${k.m}</b> mastered · <b>${k.l}</b> learning · <b>${k.s}</b> read<br><span class="muted">${k.total.toLocaleString()} provisions · ${m.words.toLocaleString()} words</span></div></div>
        <div class="row" style="margin-top:12px">${next ? `<a class="btn primary" href="#/p/${cid}/${next.i}">${k.touched ? 'Continue' : 'Start'}: ${esc(next.l)}</a>` : '<span class="chip ok">Every provision opened</span>'}<a class="btn" href="#/drill?code=${cid}">Drill</a></div>
        ${sitting.length > 1 ? `<h3 style="margin:14px 0 4px">Your next sitting</h3><p class="tiny muted" style="margin:0 0 6px">Five provisions at a time is enough. Stop there and review tomorrow.</p><ul class="plist sitting" style="padding:0">${sitting.map(p => `<li><a href="#/p/${cid}/${p.i}"><span class="pl">${esc(p.l)}</span><span class="pc">${esc(p.c || firstWords(p))}</span></a></li>`).join('')}</ul>` : ''}</div>
      ${d.note ? `<div class="note">${esc(d.note)}</div>` : ''}
      <div class="card flat small"><b>Source</b><br>${esc(d.source.name)}${d.source.url ? `<br><a href="${esc(d.source.url)}" target="_blank" rel="noopener">${esc(d.source.url.replace(/^https?:\/\//, '').slice(0, 60))}</a>` : ''}
        <p class="muted tiny" style="margin:8px 0 0">Verbatim text, typographic clean-up only. Corrections are marked on the provision they touch. See <a href="#/about">About → Proofreading</a>.</p></div>
      ${d.preamble && d.preamble.length ? `<details class="card flat"><summary class="small"><b>Enacting clause & preamble</b></summary><div class="law" style="box-shadow:none;border:0;padding:8px 0 0"><div class="text">${d.preamble.map(x => `<p>${esc(x)}</p>`).join('')}</div></div></details>` : ''}
      ${d.closing && d.closing.length ? `<details class="card flat"><summary class="small"><b>Closing text</b></summary><div class="small" style="margin-top:8px">${d.closing.map(x => `<p>${esc(x)}</p>`).join('')}</div></details>` : ''}
    </aside></div>`;
  if (window.innerWidth < 900) $('#cv').style.gridTemplateColumns = '1fr';
  if (tocHandler) main.removeEventListener('toggle', tocHandler, true);
  tocHandler = lazyToc;
  main.addEventListener('toggle', lazyToc, true);
  function lazyToc(e) {
    if (!location.hash.startsWith('#/code/' + cid)) return;
    const det = e.target; if (!det.matches || !det.matches('details[data-div]') || !det.open) return;
    const box = det.querySelector(':scope > .kids'); if (box.dataset.done) return;
    const i = +det.dataset.div;
    box.innerHTML = divInner(d, i, cid, new Set(), d._provList, d._node); box.dataset.done = 1;
  }
  if (openDiv != null) { const el = $(`details[data-div="${openDiv}"]`); el && el.scrollIntoView({ block: 'start' }); }
}

/* ---- provision page */
let tutorOK = null, tocHandler = null;
async function checkTutor() {
  if (tutorOK !== null) return tutorOK;
  try { const r = await fetch('api/tutor', { method: 'GET' }); tutorOK = r.ok && (await r.json()).ok === true; } catch (e) { tutorOK = false; }
  return tutorOK;
}
const LABK = { article: 'Art.', section: 'Sec.', rule: 'Rule', canon: 'Canon', art: 'Art.', sec: 'Sec.' };
function labelParts(l) {
  l = l || '';
  const c = /^(.*?),\s*(Sec\.|Section)\s*(.+)$/.exec(l);
  if (c) return { k: c[1] + ' · Sec.', n: c[3] };
  const m = /^(Article|Section|Rule|Canon|Art\.|Sec\.)\s*(.+)$/i.exec(l);
  return m ? { k: LABK[m[1].toLowerCase().replace('.', '')] || m[1], n: m[2] } : { k: '', n: l };
}
function divCap(d, p) {
  if (!d || p.d == null || !d.divisions[p.d]) return null;
  const t = d.divisions[p.d].t; const m = /^(.*?)\s*[—–-]\s+(.+)$/.exec(t);
  const tc = x => x === x.toUpperCase() ? x.toLowerCase().replace(/(^|[\s(])([a-z])/g, (a, b, c) => b + c.toUpperCase()).replace(/\b(Of|And|The|In|On|To|For|By|A|An|Or|With|Under)\b/g, w => w.toLowerCase()).replace(/^./, c => c.toUpperCase()) : x;
  const fix = x => x.replace(/^([A-Z]\.) the\b/, '$1 The');
  return m ? [tc(m[1]), fix(tc(m[2]))] : ['', fix(tc(t))];
}
function lawHTML(d, p, cid, on) {
  const fn = p.f || [];
  const lp = labelParts(p.l); const fld = fieldOf(cid);
  const F = inForce(p), cur = !!(F.a && !F.partial);
  const cap = cur || F.partial ? F.cap : p.c;
  const stat = (p.e || []).filter(e => e.k === 'status'), notes = (p.e || []).filter(e => e.k !== 'status');
  const amendSec = (a, label) => `<section class="amend"><div class="row"><span class="ak">${label}</span><span class="chip ok">${esc(a.by)}${a.sec ? ` · Sec. ${esc(a.sec)}` : ''}${a.y ? ` · ${esc(a.y)}` : ''}</span><span class="spacer"></span>${a.ref ? `<a class="small" href="#/code/${a.ref}">open ${esc(a.by)}</a>` : ''}</div><p class="tiny muted" style="margin:4px 0 10px">Verbatim from the amending law.</p><div class="text">${lawBody(a.p, on, null, cid)}</div></section>`;
  const nA = (p.a || []).length;
  return `<article class="law${fld ? ' f-' + fld.id : ''}${p.st ? ' gone' : ''}" id="law">
    <h1 class="lh"><span class="lnum${lp.n.length > 6 ? ' long' : ''}">${lp.k ? `<small>${esc(lp.k)}</small>` : ''}<b>${esc(lp.n)}</b></span>${cap ? `<span class="lcap">${esc(cap)}</span>` : divCap(d, p) ? `<span class="lcap dim"><small>${esc(divCap(d, p)[0])}</small>${esc(divCap(d, p)[1])}</span>` : ''}${p.o ? `<span class="lold">formerly ${esc(p.o)}</span>` : ''}</h1>
    ${stat.map(e => `<div class="status st-${esc(p.st || 'note')}">${/^(Repealed|Superseded|Declared unconstitutional)\b/.test(e.t) ? '' : `<b>${p.st === 'repealed' ? 'Repealed' : p.st === 'superseded' ? 'Superseded' : p.st === 'void' ? 'Struck down' : 'Status'}.</b> `}${esc(e.t)}${e.b ? ` <span class="muted">Basis: ${esc(e.b)}</span>` : ''}<span class="tiny">${p.st === 'void' ? 'Know that it was struck down and why; you do not need to memorize its text.' : 'You do not need to memorize this text; learn the law that replaced it.'}</span></div>`).join('')}
    ${cur ? `<div class="inforce${p.st ? ' part' : ''}"><span class="ak">${p.st ? 'Last text before repeal' : 'Text in force'}</span><span class="chip ok">as amended by ${esc(F.a.by)}${F.a.y ? ` (${esc(F.a.y)})` : ''}</span>${F.a.cons ? '<span class="chip">consolidated</span>' : ''}</div>` : F.partial ? `<div class="inforce part"><span class="ak">Partly amended</span>${F.parts.map(a => `<span class="chip warn">${esc(a.by)}${a.y ? ` (${esc(a.y)})` : ''}</span>`).join('')}<span class="tiny muted">${F.parts.length > 1 ? 'Later laws rewrote parts of this provision. Read the latest changes first.' : 'A later law rewrote part of this provision. Read the change first.'} Where a change shows “x x x”, the words it left out are unchanged. Everything a change does not touch still reads as in the text below it.</span></div>
      ${F.parts.slice().reverse().map((a, k) => `<section class="amend chg"><div class="row"><span class="ak">${k === 0 ? 'Latest change' : 'Earlier change'}</span><span class="chip warn">${esc(a.by)}${a.sec ? ` · Sec. ${esc(a.sec)}` : ''}${a.y ? ` · ${esc(a.y)}` : ''}</span><span class="spacer"></span>${a.ref ? `<a class="small" href="#/code/${a.ref}">open ${esc(a.by)}</a>` : ''}</div><div class="text">${lawBody(a.p, on, null, cid)}</div></section>`).join('')}
      <div class="inforce base"><span class="ak">The text these changes amend</span><span class="chip">${F.base ? `as restated by ${esc(F.base.by)}${F.base.y ? ` (${esc(F.base.y)})` : ''}` : 'as enacted'}</span></div>` : ''}
    <div class="text">${lawBody(cur || F.partial ? F.ps : p.p, on, d, cid)}</div>
    ${fn.length ? `<div class="fnlist">${fn.map(f => `<p id="fn${f.n}"><sup>${f.n}</sup> ${esc(f.t)}</p>`).join('')}<p class="tiny muted">Footnotes are the publisher’s (DOLE), not part of the law.</p></div>` : ''}
    <div class="verify">${verifyChips(cid, p)}</div>
    ${notes.map(e => `<div class="note ${/missing|omitted|restored|absent/i.test(e.t) ? 'blue' : ''}" style="margin-top:10px"><b>${(p.a || []).length && (/amend|rewrote|restated|raised|repealed|added|changed|limited|replaced/i.test(e.t) || /\b(RA|CA|BP|PD|EO|Act No\.)\s*\d/.test(e.t)) ? 'History note.' : 'Proofreading note.'}</b> ${esc(e.t)}${e.b ? ` <span class="muted">Basis: ${esc(e.b)}</span>` : ''}</div>`).join('')}
    ${cur ? `<details class="hist"><summary><b>How the text read before</b> <span class="muted small">the earlier text${nA > 1 ? ` and ${nA - 1} earlier amendment${nA > 2 ? 's' : ''}` : ''}, and the amending law verbatim</span></summary>
      <section class="amend orig"><div class="row"><span class="ak">Earlier text</span><span class="chip">as in the source</span></div><div class="text">${lawBody(p.p, on, d, cid)}</div></section>
      ${(p.a || []).map((a, k) => amendSec(a, k === nA - 1 ? 'Latest amendment' : 'Amended')).join('')}
      <p class="tiny muted">Read in order: each later law controls the earlier one.</p></details>`
      : F.partial ? `<details class="hist"><summary><b>How the text read before</b> <span class="muted small">every amending law, verbatim, in order</span></summary>
        ${F.base ? `<section class="amend orig"><div class="row"><span class="ak">Text as enacted</span><span class="chip">as in the source</span></div><div class="text">${lawBody(p.p, on, d, cid)}</div></section>` : ''}
        ${(p.a || []).map(a => amendSec(a, 'Amended')).join('')}<p class="tiny muted">Read in order: each later law controls the earlier one.</p></details>`
      : (p.a || []).map(a => amendSec(a, 'Amended text')).join('')}
  </article>`;
}
function verifyChips(cid, p) {
  const m = meta(cid); const out = [];
  if (m.kind === 'admin') out.push(p.v === 'ok' ? '<span class="chip ok" title="Every word was found in a dictionary or in the other codes. Real-word OCR slips (e.g. “of” for “or”) are still possible.">OCR · machine-checked</span>' : `<span class="chip warn" title="${esc('Words to verify against your scan: ' + (p.u || []).join(', '))}">OCR · check: ${esc((p.u || []).slice(0, 4).join(', '))}</span>`);
  else if (m.kind === 'family') out.push('<span class="chip ok">Your PDF · text layer decoded exactly</span>');
  else if (m.kind === 'labor') out.push('<span class="chip ok">DOLE 2022 edition</span>');
  else if (m.kind === 'sc') out.push('<span class="chip ok" title="Transcription published by Justitia (University of Makati School of Law) of the Supreme Court’s text; OCR slips corrected and logged on the About page">Supreme Court issuance · proofread</span>');
  else out.push('<span class="chip">LawPhil transcription</span>');
  if (p.x) out.push(`<span class="chip warn" title="${esc(p.x.join('; '))}">Proofreading flag</span>`);
  if ((p.e || []).length) out.push('<span class="chip blue">Corrected / annotated</span>');
  if (p.xc) out.push(`<span class="chip ok" title="${esc(p.xc)}">Cross-checked</span>`);
  return out.join('');
}

async function provView(cid, pid, q) {
  setNav('library');
  const d = await loadCode(cid); await loadExtras(cid); await Promise.all([loadSylIndex(), loadRecent(), cid === 'rpc' ? loadB2().catch(() => null) : null]);
  const p = d.byId[pid];
  if (!p) { main.innerHTML = `<div class="empty">That provision is not in this code. <a href="#/code/${cid}">Back to ${esc(d.short)}</a></div>`; return; }
  const key = ck(cid, pid);
  if (!S.cards[key]) { S.cards[key] = { reps: 0, lapses: 0, seen: Date.now() }; }
  S.last = { c: cid, p: pid, l: `${d.short} · ${p.l}` };
  const fld = fieldOf(cid); if (fld) S.lastBy[fld.id] = { c: cid, p: pid, l: `${d.short} · ${p.l}` };
  save();
  let prev = d.provisions[p.ix - 1], next = d.provisions[p.ix + 1];
  const setId = q && q.get('set'); const st = setId && CUR.sets[setId]; let setBar = '', sfx = '', loc = '';
  const href = x => `#/p/${x.c || cid}/${x.i}${sfx}`;
  if (st) {
    const ix = st.items.findIndex(x => x.c === cid && x.i === pid);
    if (ix >= 0) { sfx = `?set=${setId}`; prev = st.items[ix - 1]; next = st.items[ix + 1]; loc = st.items[ix].loc;
      setBar = `<div class="setbar"><span>${esc(st.title)}</span><span>${ix + 1} of ${st.items.length}</span><span>Place: ${esc(loc)}</span><span class="spacer"></span><a href="#/set/${setId}">See the whole walk</a></div>`; }
  }
  const notes = (NOTES[cid] || {})[pid];
  const cases = (CASES[cid] || {})[pid] || [];
  const syl = SYX[ck(cid, pid)] || [], rec = REC.by[ck(cid, pid)] || [];
  const ncase = cases.length + syl.length + rec.length + (((notes || {}).d) || []).length;
  const on = S.settings.hl;
  const tabs = [['guide', 'Step 2', 'Understand'], ['recall', 'Step 3', 'Recall'], ['cases', 'Step 4', `Cases${ncase ? ' (' + ncase + ')' : ''}${rec.length ? ' <span class="newdot" title="has 2023–2026 rulings">new</span>' : ''}`], ['notes', 'Yours', 'My notes']];
  main.innerHTML = `${crumbs(d, p, cid)}${setBar}
  <div class="pv"><div>
    <div class="row" style="margin-bottom:8px"><span class="eyebrow">Step 1 · Read</span><span class="spacer"></span><details class="hlbox"><summary>Highlights</summary><div class="legend">${HLORDER.map(k => `<label><input type="checkbox" data-hl="${k}" ${on[k] ? 'checked' : ''}><span class="${HLCLASS[k]}">${HLNAME[k]}</span></label>`).join('')}</div></details></div>
    <div id="lawbox">${lawHTML(d, p, cid, on)}</div>
    <div class="steps" role="tablist">${tabs.map(([k, sm, n], i) => `<button role="tab" data-tab="${k}" class="${i ? '' : 'on'}"><small>${sm}</small><span>${n}</span></button>`).join('')}</div>
    <div id="tabbox"></div>
    <div class="pn">${prev ? `<a class="btn" href="${href(prev)}">← ${esc(prev.l)}</a>` : '<span></span>'}${next ? `<a class="btn primary" href="${href(next)}">${esc(next.l)} →</a>` : (sfx ? `<a class="btn primary" href="#/set/${setId}">Finish the walk</a>` : '')}</div>
  </div>
  <aside class="side">
    <div class="card"><h3>How well do you know it?</h3><p class="small muted" style="margin:0">Recall it first (Recall tab), then rate honestly. The schedule adapts.</p>
      <div class="rate">${['Again', 'Hard', 'Good', 'Easy'].map((n, i) => `<button class="r${i + 1}" data-rate="${i + 1}">${n}<small>${preview(key)[i]}</small></button>`).join('')}</div>
      <p class="tiny muted" id="cstat" style="margin:10px 0 0">${cardLine(key)}</p></div>
    <div class="card"><div class="row"><button class="btn sm" id="mark">${S.marks[key] ? '★ Bookmarked' : '☆ Bookmark'}</button><button class="btn sm" id="flag">${S.flags[key] ? '⚑ Flagged' : '⚑ Report a text error'}</button></div>
      <div id="flagbox" class="small" style="margin-top:8px">${S.flags[key] ? `<div class="note bad">${esc(S.flags[key].t)}</div>` : ''}</div></div>
    ${sibling(d, p, cid)}
  </aside></div>`;
  const tabbox = $('#tabbox');
  const show = k => { $$('.steps button').forEach(b => b.classList.toggle('on', b.dataset.tab === k)); renderTab(k); };
  function renderTab(k) {
    if (k === 'guide') tabbox.innerHTML = guideHTML(d, p, cid, notes, loc);
    if (k === 'cases') tabbox.innerHTML = casesHTML(cid, pid, notes, cases, syl, rec);
    if (k === 'notes') { tabbox.innerHTML = `<div class="panel"><textarea id="mynote" placeholder="Your own words: what the provision says, the elements, a case that applies it, a mnemonic…">${esc(S.notes[key] || '')}</textarea><p class="tiny muted">Saved on this device as you type. Writing it in your own words is one of the strongest ways to learn it.</p></div>`; $('#mynote').addEventListener('input', e => { S.notes[key] = e.target.value; save(); }); }
    if (k === 'recall') { recallPanel(tabbox, d, p, cid); if (S.hooks[key]) $('.panel', tabbox).insertAdjacentHTML('afterbegin', `<div class="hookcue"><b>Your picture:</b> ${esc(S.hooks[key])}</div>`); }
    if (k === 'guide') { $$('[data-av]', tabbox).forEach(b => b.onclick = () => { S.settings.anatView = b.dataset.av; save(); $$('[data-av]', tabbox).forEach(x => x.classList.toggle('on', x === b)); $('#av-judge').hidden = b.dataset.av !== 'judge'; $('#av-text').hidden = b.dataset.av !== 'text'; }); }
    if (k === 'guide') { wireTutor(d, p, cid, cases); const hk = $('#hookin'); if (hk) hk.addEventListener('input', e => { const v = e.target.value.trim(); if (v) S.hooks[key] = v.slice(0, 200); else delete S.hooks[key]; save(); }); }
  }
  show('guide');
  $$('.steps button').forEach(b => b.onclick = () => show(b.dataset.tab));
  $$('[data-hl]').forEach(c => c.onchange = () => { S.settings.hl[c.dataset.hl] = c.checked; save(); $('#lawbox').innerHTML = lawHTML(d, p, cid, S.settings.hl); });
  $$('[data-rate]').forEach(b => b.onclick = () => { const c = rate(key, +b.dataset.rate); toast(`Next review in ${fmtIvl(c.ivl)}.`); $('#cstat').textContent = cardLine(key); if (next) setTimeout(() => location.hash = href(next), 450); });
  $('#mark').onclick = () => { if (S.marks[key]) delete S.marks[key]; else S.marks[key] = Date.now(); save(); $('#mark').textContent = S.marks[key] ? '★ Bookmarked' : '☆ Bookmark'; };
  $('#flag').onclick = async () => {
    const t = await askText('Report a text error', S.flags[key]?.t || '', 'What the text says here vs. what the official text says, and your source');
    if (t === null) return; if (t.trim()) S.flags[key] = { t: t.trim(), at: Date.now(), l: `${d.short} ${p.l}` }; else delete S.flags[key]; save(); provView(cid, pid, q);
  };
  main.onclick = e => { const s = e.target.closest('sup.fn'); if (s) { const f = $('#fn' + s.dataset.fn); f && f.scrollIntoView({ behavior: 'smooth', block: 'center' }); } };
}
function cardLine(key) { const c = upgrade(S.cards[key]); if (!c || !c.reps || c.s == null) return 'Not yet rated.'; const r = recallNow(c); return `Recall today ≈ ${Math.round(r * 100)}% · holds ${fmtIvl(c.s)} at 90% · difficulty ${c.d.toFixed(1)}/10 · ${c.lapses || 0} lapse${c.lapses === 1 ? '' : 's'} · next ${c.due <= Date.now() ? 'now' : new Date(c.due).toLocaleDateString()}`; }
function sibling(d, p, cid) {
  const arr = p.d == null ? d.loose : d.divProv[p.d];
  if (!arr || arr.length < 2) return '';
  const dv = p.d != null ? d.divisions[p.d].t : d.short;
  const i = arr.indexOf(p); const win = arr.slice(Math.max(0, i - 6), i + 7);
  return `<div class="card"><h3 class="small">${esc(shortDiv(dv))}</h3><ul class="plist" style="padding:0">${win.map(x => `<li><a href="#/p/${cid}/${x.i}" ${x === p ? 'style="background:var(--brand-soft)"' : ''}><span class="dot ${status(ck(cid, x.i))}"></span><span class="pl">${esc(x.l)}</span><span class="pc">${esc(x.c || '')}</span></a></li>`).join('')}</ul></div>`;
}
function crimeHTML(c, fam, foot = '') {
  const isBase = c.id === fam.base; const base = fam.crimes.find(x => x.id === fam.base);
  const chips = c.refs.map(r => `<a class="pref" href="#/p/${r.c}/${r.i}">${esc(r.l)}</a>`).join('');
  return `<article class="crime${isBase ? ' base' : ''}" id="c-${c.id}">
    <header class="ch"><div class="cht"><span class="ck">${isBase ? 'Base crime' : `Compare: ${esc(base.name)}`}</span><h3>${esc(c.name)}</h3></div><div class="refs">${chips}</div></header>
    <div class="delta"><span class="dl">${isBase ? 'The base' : 'Sets it apart'}</span><p>${esc(c.key)}</p></div>
    <span class="dl">${c.els.length} element${c.els.length === 1 ? '' : 's'}</span>
    <ol class="els">${c.els.map(e => `<li>${esc(e)}</li>`).join('')}</ol>
    <div class="penalty"><span class="dl">Penalty</span><p>${esc(c.pen)}</p></div>${foot}
  </article>`;
}
function b2Card(cid, pid) {
  if (cid !== 'rpc' || !B2 || !B2.byArt[pid]) return '';
  const seen = new Set();
  return B2.byArt[pid].filter(x => { const k = x.f + x.c; if (seen.has(k)) return false; seen.add(k); return true; }).map(({ f, c }) => {
    const fam = B2.families.find(x => x.id === f); const cr = fam.crimes.find(x => x.id === c);
    return `<div class="f-crim b2el"><div class="row" style="margin:0 0 6px"><span class="eyebrow" style="color:var(--f)">Book Two Studio · ${esc(fam.title)}</span></div>${crimeHTML(cr, fam, `<div class="row" style="margin-top:12px"><a class="btn sm" href="#/b2/${f}?tab=compare">Compare with its neighbours</a><a class="btn sm ghost" href="#/b2/${f}?tab=practice">Practise sorting facts</a></div>`)}</div>`;
  }).join('');
}
const ANATK = { 'Definition': 'k-def', 'Penalty': 'k-pen', 'Prohibition': 'k-pro', 'Exception': 'k-exc', 'Proviso': 'k-exc', 'Condition': 'k-cond', 'Duty / rule': 'k-op', 'Power / right': 'k-pow', 'Element / item': 'k-el', 'Statement': 'k-st' };
function anatSummary(items) {
  const c = {}; items.forEach(([k]) => { c[k] = (c[k] || 0) + 1; });
  const order = Object.keys(ANATK).filter(k => c[k] && k !== 'Statement');
  if (!order.length) return '';
  const PL = { 'Definition': 'Definitions', 'Penalty': 'Penalties', 'Prohibition': 'Prohibitions', 'Exception': 'Exceptions', 'Proviso': 'Provisos', 'Condition': 'Conditions', 'Duty / rule': 'Duties / rules', 'Power / right': 'Powers / rights', 'Element / item': 'Elements / items' };
  return `<div class="anatsum" aria-label="What this provision is made of">${order.map(k => `<span class="${ANATK[k]}"><b>${c[k]}</b> ${esc(c[k] === 1 ? k : PL[k])}</span>`).join('')}</div>`;
}
function anatRow(k, s, mk, nolabel) { return `<div class="it ${ANATK[k] || 'k-st'}${nolabel ? ' nl' : ''}">${nolabel ? '' : `<b>${esc(k)}</b>`}<span>${mk ? `<i class="amk">${esc(mk)}</i>` : ''}${hlText(s, S.settings.hl)}</span></div>`; }
/* the order of judicial reading, each step with the canon of construction that governs it */
const JUDGE = [
  { ks: ['Definition'], q: 'Which words does it define?', c: 'A term the law defines carries that meaning wherever the law uses it, not its everyday sense.' },
  { ks: ['Duty / rule', 'Prohibition', 'Power / right', 'Statement'], q: 'What is the rule?', c: 'Where the words are clear, apply them as written; there is no room for construction (verba legis).' },
  { ks: ['Element / item'], q: 'What does it list?', c: 'A list excludes what it does not name (expressio unius est exclusio alterius). Read the lead-in to know whether every item must be present or any one is enough.', all: 'Here the items must all be present: if one is missing, the provision does not apply.', any: 'Here any one item is enough.' },
  { ks: ['Condition'], q: 'When does it apply?', c: 'A condition is part of the rule: if it is not met, the rule does not operate.' },
  { ks: ['Exception', 'Proviso'], q: 'What is qualified or carved out?', c: 'Exceptions and provisos are read strictly. Whatever they do not clearly cover stays under the general rule, and the one who claims an exception must prove it.' },
  { ks: ['Penalty'], q: 'What follows?', c: '', pc: 'Penal laws are read strictly against the State and liberally in favour of the accused.' },
];
function judgeHTML(items, fld, mode) {
  const crim = fld && fld.id === 'crim';
  let n = 0;
  return `<ol class="judge">${JUDGE.map(g => {
    const rows = items.filter(i => g.ks.includes(i[0]));
    if (!rows.length) return '';
    n++;
    const canon = g.pc ? (crim ? g.pc : 'A consequence attaches only when every part of the rule above is met.') : g.c + (mode && g[mode] ? ' ' + g[mode] : '');
    const one = g.ks.length === 1 || g.ks.every(k => ANATK[k] === ANATK[g.ks[0]]);
    return `<li><div class="jh"><span class="jn">${n}</span><span class="jq">${esc(g.q)}</span><span class="jc">${rows.length}</span></div>
      <p class="canon">${esc(canon)}</p><div class="anat">${rows.map(([k, s, mk]) => anatRow(k, s, mk, one)).join('')}</div></li>`;
  }).join('')}</ol>`;
}
/* ---- evolution: where the text came from, how it changed, how it is carried out and read */
const DERIV = { civil: ['Spanish Civil Code of 1889', '1889'], family: ['Civil Code of 1950', '1950'] };
const ENACT = { labor: [1974, 'Presidential Decree No. 442 (May 1, 1974), in force November 1, 1974; renumbered by RA 10151 (2011)'], civil: [1949, 'Republic Act No. 386 (June 18, 1949), in force August 30, 1950'], family: [1987, 'Executive Order No. 209 (July 6, 1987), in force August 3, 1988'], rpc: [1930, 'Act No. 3815 (December 8, 1930), in force January 1, 1932'] };
// what an old-rule note (n.o) points to: the 1988 Code of Professional Responsibility, the Rules of Court
// provisions the CPRA repealed and absorbed (Rule 138, Rule 139-B), or both
function oldRule(o) {
  const cpr = /\b(Rules? \d+\.\d+|Canons? \d+)\b/.test(o), roc = /\bRule 13[89]\b/.test(o);
  const lab = cpr && roc ? 'Before the CPRA: the 1988 Code and the Rules of Court' : roc ? 'Before the CPRA: the Rules of Court' : 'Under the 1988 Code';
  return { lab, y: cpr || /139-B/.test(o) ? 1988 : 1964, h: cpr && roc ? 'Before the CPRA — 1988 Code and Rules of Court' : roc ? 'Before the CPRA — Rules of Court' : 'Under the 1988 Code of Professional Responsibility' };
}
const yearOf = s => { const m = /\b(1[89]\d\d|20\d\d)\b/.exec(s || ''); return m ? +m[1] : null; };
function evolution(d, p, cid, n) {
  const m = meta(cid) || {}; const ev = [];
  const txt = p.p.filter(x => typeof x === 'string');
  const y0 = (ENACT[cid] || [])[0] || yearOf(m.citation) || yearOf((d.closing || []).join(' '));
  ev.push({ y: y0, k: 'enact', h: `Enacted in the ${(m.title || d.title || '').replace(/^The /, '')}`, s: (ENACT[cid] || [])[1] || m.citation || '' });
  const src = txt.map(t => splitSrc(t)[1]).find(Boolean);
  if (src) {
    const codes = src.replace(/[()]/g, '').split(/,\s*/);
    const dv = DERIV[cid];
    if (codes.every(c => c === 'n')) ev.push({ y: y0, k: 'src', h: 'A new provision', s: `The source note “${src}” marks it as new: it has no counterpart in the earlier code.` });
    else ev.push({ y: dv ? +dv[1] : null, k: 'src', h: `Drawn from ${dv ? dv[0] : 'the earlier law'}, Art. ${codes.filter(c => c !== 'n').map(c => c.replace(/a$/, '')).join(', ')}`, s: `The source note “${src}” traces it there${codes.some(c => /a$/.test(c)) ? '; the letter “a” means it was amended when carried over' : '; it was carried over without change in substance'}.` });
  }
  for (const t of txt) for (const mm of t.matchAll(/\((?:As )?amended by ([^)]{3,120})\)/gi)) ev.push({ y: yearOf(mm[1]), k: 'amend', h: `Amended by ${mm[1].replace(/[;,].*$/, '')}`, s: 'Noted in the text itself.' });
  for (const a of p.a || []) ev.push({ y: a.y ? +a.y : null, k: 'amend', h: `Amended by ${a.by}${a.sec ? ', Sec. ' + a.sec : ''}`, s: a.why || a.tt || 'See the amended text above.' });
  if (n && n.o && n.o !== '—') { const r = oldRule(n.o); ev.push({ y: r.y, k: 'src', h: r.h, s: n.o }); }
  for (const i of (n && n.i) || []) ev.push({ y: yearOf(i.t), k: 'issu', h: i.t, s: i.s });
  const cases = [...((n && n.d) || []).map(c => ({ y: yearOf(c.c), h: c.n, s: c.h })), ...((REC.by || {})[ck(cid, p.i)] || []).map(r => ({ y: yearOf(r.d), h: r.n, s: r.h }))];
  const seen = new Set();
  for (const c of cases.filter(c => c.y).sort((a, b) => a.y - b.y)) { if (seen.has(c.h)) continue; seen.add(c.h); if (seen.size > 7) break; ev.push({ y: c.y, k: 'case', h: c.h, s: c.s.split(/(?<=\.)\s/)[0] }); }
  if (ev.length < 2) return '';
  const order = { enact: 0, src: 1, amend: 2, issu: 3, case: 4 };
  ev.sort((a, b) => (a.y ?? 9999) - (b.y ?? 9999) || order[a.k] - order[b.k]);
  const KN = { enact: 'Enacted', src: 'Origin', amend: 'Amended', issu: 'Implemented', case: 'Interpreted' };
  return `<div class="card flat evo" style="margin-bottom:12px"><div class="row"><h3 style="margin:0">How this provision evolved</h3><span class="spacer"></span><span class="chip">${ev.length} events</span></div>
    <p class="small muted" style="margin:4px 0 12px">Law is built in layers. Learn the newest layer, but know the older ones: older cases, and many examination questions, were decided under them.</p>
    <ol class="tl">${ev.map(e => `<li class="t-${e.k}"><span class="ty">${e.y || '—'}</span><div><span class="tk">${e.k === 'case' && y0 && e.y < y0 ? 'Decided under the earlier law' : KN[e.k]}</span><b>${esc(e.h)}</b>${e.s ? `<span>${esc(e.s)}</span>` : ''}</div></li>`).join('')}
    <li class="t-now"><span class="ty">Now</span><div><span class="tk">In force</span><b>${(p.a || []).length ? 'The latest amended text above is the law today.' : 'The text above is the law today.'}</b>${(n && n.i && n.i.length) ? '<span>Read it with the implementing rules listed below.</span>' : ''}</div></li></ol></div>`;
}
function guideHTML(d, p, cid, n, loc) {
  const an = anatomy(p);
  const fld = fieldOf(cid); const key = ck(cid, p.i);
  let h = `<div class="panel${fld ? ' f-' + fld.id : ''}">` + b2Card(cid, p.i);
  h += `<div class="card flat hook" style="margin-bottom:12px"><div class="row"><h3 style="margin:0">Make it a picture</h3><span class="spacer"></span>${loc ? `<span class="chip ok">${esc(loc)}</span>` : fld ? `<span class="chip f-${fld.id}" style="background:color-mix(in srgb,var(--f) 14%,transparent);color:var(--f)">${esc(fld.pname)}</span>` : ''}</div>
    <p class="small muted" style="margin:0">${loc ? `In this walk, the provision’s place is the <b>${esc(loc.toLowerCase())}</b>.` : fld ? `${esc(fld.name)} lives at the ${esc(fld.pname.toLowerCase())} of the House of Law.` : ''} In a few words, what do you see happening there that stands for this rule? Odd pictures last longest.</p>
    <input id="hookin" maxlength="200" value="${esc(S.hooks[key] || '')}" placeholder="e.g. a stopwatch hanging on the column: three months to decide" aria-label="Your picture for this provision"></div>`;
  if (n && (n.x || n.k)) {
    h += `<div class="card flat plain" style="margin-bottom:12px"><div class="row"><h3 style="margin:0">In plain language</h3><span class="spacer"></span><span class="chip ok">Written for this provision</span></div>
      <div class="explain" style="margin-top:8px">${(n.x || '').split('\n\n').map(x => `<p>${esc(x)}</p>`).join('')}</div>
      ${n.k ? `<span class="dl">${n.k.length} ${n.k.length === 1 ? 'key point' : 'elements / key points'}</span><ol class="els">${n.k.map(x => `<li>${esc(x)}</li>`).join('')}</ol>` : ''}
      ${n.w ? `<span class="dl">Why it exists</span><p class="why">${esc(n.w)}</p>` : ''}
      ${n.o && n.o !== '—' ? `<span class="dl">${oldRule(n.o).lab}</span><p class="oldrule">${esc(n.o)}</p>` : ''}
      ${n.t ? `<span class="dl warnh">Exam traps</span><ul class="traps">${n.t.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}
      ${n.q ? `<details class="selftest"><summary><b>Self-test</b> <span class="small muted">answer before opening</span></summary><ol class="els q">${n.q.map(x => `<li>${esc(x)}</li>`).join('')}</ol></details>` : ''}
      <p class="tiny muted" style="margin:10px 0 0">Explanations are study aids, not the law. The verbatim text above controls.</p></div>`;
  }
  h += evolution(d, p, cid, n);
  if (n && n.i && n.i.length) h += `<div class="card flat issu" style="margin-bottom:12px"><div class="row"><h3 style="margin:0">Implementing rules and issuances</h3><span class="spacer"></span><span class="chip">${n.i.length}</span></div>
    <p class="small muted" style="margin:4px 0 10px">The rules, orders and circulars that carry this provision out. Summaries are in our own words; the issuance controls.</p>
    <ol class="isl">${n.i.map(x => `<li><b>${x.u ? `<a href="${esc(x.u)}"${/^#/.test(x.u) ? '' : ' target="_blank" rel="noopener"'}>${esc(x.t)}</a>` : esc(x.t)}</b><span>${esc(x.s)}</span></li>`).join('')}</ol></div>`;
  h += `<div class="card flat" id="tutorbox" style="margin-bottom:12px" hidden></div>`;
  h += `<div class="card flat"><div class="row"><h3 style="margin:0">Take it apart</h3><span class="spacer"></span><span class="chip">auto-parsed from the text</span></div>
    <p class="small muted" style="margin:4px 0 10px">A judge reads a provision in a fixed order: the words it defines, the rule, what must be present, when it applies, what is carved out, and what follows. Each sentence of the provision is sorted into that order below.</p>
    ${anatSummary(an.items)}
    <div class="seg" role="tablist" aria-label="How to show the parts"><button data-av="judge" class="${S.settings.anatView === 'text' ? '' : 'on'}">As a judge reads it</button><button data-av="text" class="${S.settings.anatView === 'text' ? 'on' : ''}">In the order written</button></div>
    <div id="av-judge" ${S.settings.anatView === 'text' ? 'hidden' : ''}>${judgeHTML(an.items, fld, an.mode)}</div>
    <div id="av-text" ${S.settings.anatView === 'text' ? '' : 'hidden'}><div class="anat">${an.items.map(([k, s, mk]) => anatRow(k, s, mk)).join('')}</div></div>
    ${an.periods.length ? `<span class="dl">Numbers to remember</span><div class="nums">${an.periods.map(x => `<span>${esc(x)}</span>`).join('')}</div>` : ''}
    <span class="dl">Ask yourself</span>
    <ol class="els q">
      <li>Restate ${esc(p.l)} in one sentence without looking.</li>
      <li>What problem was this provision written to solve? What would go wrong without it?</li>
      <li>Invent a short set of facts where it applies — then change one fact so it no longer does.</li>
      ${an.items.some(i => i[0] === 'Exception' || i[0] === 'Proviso') ? '<li>State the general rule, then the exception or proviso, then why it exists.</li>' : ''}
      ${an.periods.length ? '<li>Recite every number and period in it, and what happens when each runs out.</li>' : ''}
    </ol></div>`;
  return h + '</div>';
}
function recentHTML(rec, withProv) {
  return rec.map(r => `<div class="case recent"><div class="row" style="gap:6px"><div class="cn" style="flex:1;min-width:200px">${esc(r.n)}</div>${r.st === 'decision' ? '<span class="chip ok" title="Docket and date checked against the decision or an official/library listing">verified: decision</span>' : '<span class="chip warn" title="From a Supreme Court release or a news report of the ruling — read the full text before citing">verified: SC release / news</span>'}</div>
    <div class="cc">${esc([r.g, r.d, r.ct].filter(Boolean).join(' · '))}</div>
    <div class="dg"><div class="d-r"><b>Ruling</b>${esc(r.h)}</div>${r.rel ? `<div class="d-w"><b>Why it matters here</b>${esc(r.rel)}</div>` : ''}${withProv ? withProv(r) : ''}</div>
    <div class="tiny muted" style="margin-top:6px">Source: ${r.src.map(x => x.u ? `<a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t)}</a>` : esc(x.t)).join(' · ')}</div></div>`).join('');
}
function sylHTML(syl) {
  const by = {};
  syl.forEach(c => (by[c.k] = by[c.k] || []).push(c));
  return Object.entries(by).map(([k, arr]) => `<div class="card flat" style="margin-bottom:10px"><div class="row"><b>${esc(COURSE[k] || k)}</b><span class="spacer"></span><a class="tiny" href="#/syllabus/${k}">open the syllabus</a></div>
    <ul style="margin:8px 0 0;padding-left:1.1em">${arr.map(c => `<li><span style="font-family:var(--serif)">${esc(c.n)}</span>${c.c ? `, <span class="muted">${esc(c.c)}</span>` : ''}${c.note ? ` <span class="small muted">— ${esc(c.note)}</span>` : ''}${c.topic ? `<div class="tiny muted">${esc(c.topic)}${c.d ? ' · filed by the outline section' : ''}</div>` : ''}</li>`).join('')}</ul></div>`).join('');
}
function casesHTML(cid, pid, n, cases, syl = [], rec = []) {
  let h = '<div class="panel">';
  if (rec.length) h += `<h3>Recent rulings (2023–2026)</h3><p class="small muted">Added after a check of recent Supreme Court decisions (last checked ${esc(REC.checked || '')}). Holdings are summarised in our own words.</p>` + recentHTML(rec);
  if (syl.length) h += `<h3 style="margin-top:14px">In your syllabus</h3><p class="small muted">Cases your professors assigned under this provision.</p>` + sylHTML(syl);
  const dg = (n && n.d) || [];
  if (dg.length) {
    h += `<h3 style="margin-top:14px">Case digests</h3>` + dg.map(c => `<div class="case"><div class="cn">${esc(c.n)}</div><div class="cc">${esc(c.c || '')}</div><div class="dg">${c.f ? `<div class="d-f"><b>Facts</b>${esc(c.f)}</div>` : ''}${c.i ? `<div class="d-i"><b>Issue</b>${esc(c.i)}</div>` : ''}${c.h ? `<div class="d-r"><b>Ruling & doctrine</b>${esc(c.h)}</div>` : ''}${c.r ? `<div class="d-w"><b>Why it matters here</b>${esc(c.r)}</div>` : ''}</div></div>`).join('');
  }
  if (cases.length) {
    const byBook = {};
    cases.forEach(c => (byBook[c.b] = byBook[c.b] || []).push(c));
    h += `<h3 style="margin-top:14px">Cases your textbooks discuss under this provision</h3><p class="small muted">Turn to the page in your own copy for the author’s full discussion. Citations are as printed in the book.</p>`;
    for (const [b, arr] of Object.entries(byBook)) {
      h += `<div class="card flat" style="margin-bottom:10px"><div class="row"><b>${esc(b)}</b><span class="spacer"></span><span class="tiny muted">${arr.length} citation${arr.length === 1 ? '' : 's'}</span></div><ul style="margin:8px 0 0;padding-left:1.1em">${arr.map(c => `<li><span style="font-family:var(--serif)">${esc(c.n)}</span>${c.c ? `, <span class="muted">${esc(c.c)}</span>` : ''} <span class="chip">p. ${esc(c.pg)}</span></li>`).join('')}</ul></div>`;
    }
  }
  if (!dg.length && !cases.length && !syl.length && !rec.length) h += `<div class="empty">No cases indexed for this provision yet.</div>`;
  return h + '</div>';
}
async function wireTutor(d, p, cid, cases) {
  if (!(await checkTutor())) return;
  const box = $('#tutorbox'); if (!box) return;
  const key = ck(cid, p.i);
  box.hidden = false;
  const cached = S.tutor[key];
  box.innerHTML = `<div class="row"><h3 style="margin:0">AI tutor</h3><span class="spacer"></span><span class="chip violet">AI-generated · verify</span></div>
    <div id="tout" class="explain" style="margin-top:8px">${cached ? fmtAI(cached) : '<p class="small muted">Ask for a plain-language explanation grounded only on the verbatim text above, or ask your own question.</p>'}</div>
    <div class="row" style="margin-top:8px"><button class="btn sm" id="texp">Explain simply</button><input id="tq" placeholder="Ask about this provision…" style="flex:1;min-width:160px;padding:6px 10px;border-radius:8px;border:1px solid var(--line2);background:var(--card)"><button class="btn sm" id="task">Ask</button></div>`;
  const go = async (mode, question) => {
    let pass = S.settings.passcode;
    if (!pass) { pass = ((await askText('Tutor passcode (set by the site owner in Cloudflare)')) || '').trim(); if (!pass) return; S.settings.passcode = pass; save(); }
    $('#tout').innerHTML = '<p class="muted small">Thinking…</p>';
    try {
      const r = await fetch('api/tutor', { method: 'POST', headers: { 'content-type': 'application/json', 'x-tutor-pass': pass }, body: JSON.stringify({ mode, question, code: { title: d.title, citation: d.citation }, provision: { label: p.l, caption: p.c || '', text: provText(p) }, cases: cases.slice(0, 25).map(c => c.n + (c.c ? ', ' + c.c : '')) }) });
      const j = await r.json();
      if (!r.ok) throw new Error(j.error || r.status);
      if (mode === 'explain') { S.tutor[key] = j.text; save(); }
      $('#tout').innerHTML = fmtAI(j.text);
    } catch (e) { $('#tout').innerHTML = `<div class="note bad">${esc(String(e.message || e))}</div>`; if (/pass/i.test(String(e))) { S.settings.passcode = ''; save(); } }
  };
  $('#texp').onclick = () => go('explain');
  $('#task').onclick = () => { const q = $('#tq').value.trim(); if (q) go('ask', q); };
}
function fmtAI(t) { return esc(t).split(/\n{2,}/).map(x => `<p>${x.replace(/\n/g, '<br>').replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')}</p>`).join(''); }

/* ---- recall panel: three graded difficulties */
/* ---- metacognition: say how sure you are before you check; the app keeps your calibration */
const CONF = ['Guessing', 'Fairly sure', 'Certain'];
function confHTML() { return `<div class="conf" role="group" aria-label="How sure are you?"><span>Before you check, how sure are you?</span>${CONF.map((c, i) => `<button type="button" data-cf="${i}">${c}</button>`).join('')}</div>`; }
function wireConf(root) { $$('[data-cf]', root).forEach(b => b.onclick = () => $$('[data-cf]', root).forEach(x => x.classList.toggle('on', x === b))); }
function takeConf(root, key, pct) {
  const b = $('[data-cf].on', root); if (!b) return '';
  const c = +b.dataset.cf; S.cal = S.cal || []; S.cal.push({ c, s: pct, k: key, t: Date.now() }); if (S.cal.length > 600) S.cal.splice(0, S.cal.length - 600); save();
  if (c === 2 && pct < 80) return `<div class="note bad" style="margin-top:10px"><b>You were certain, and missed part of it.</b> Look hard at the red words now: errors made with high confidence are the ones that stick best once corrected.</div>`;
  if (c === 0 && pct >= 80) return `<div class="note blue" style="margin-top:10px"><b>You knew more than you thought.</b> Trust it, and space this one out.</div>`;
  return '';
}
function calibration() {
  const L = S.cal || []; if (L.length < 3) return '';
  const rows = CONF.map((c, i) => { const xs = L.filter(x => x.c === i); return { c, n: xs.length, avg: xs.length ? Math.round(xs.reduce((a, x) => a + x.s, 0) / xs.length) : null }; });
  const cert = rows[2];
  const msg = cert.n >= 3 && cert.avg < 75 ? 'When you feel certain, you are still missing a quarter or more. Recall before you rate, and do not stop studying a provision just because it feels familiar.' : rows[0].n >= 3 && rows[0].avg >= 70 ? 'You tend to underrate yourself: your guesses are mostly right.' : 'Your confidence tracks your accuracy reasonably well. Keep checking it.';
  return `<div class="card" style="margin-top:14px"><h3>How well you judge your own memory</h3><p class="small muted" style="margin:0 0 10px">From the confidence you gave before checking a recall (${L.length} checks). Learners who misjudge what they know stop studying too early.</p>
    <div class="calib">${rows.map(r => `<div><span>${r.c}</span><i style="--w:${r.avg ?? 0}%"></i><b>${r.avg === null ? '—' : r.avg + '%'}</b><small>${r.n} check${r.n === 1 ? '' : 's'}</small></div>`).join('')}</div>
    <p class="small" style="margin:10px 0 0">${msg}</p></div>`;
}
/* ---- a bar-style answer: Answer, Legal basis, Application, Conclusion, graded against the provision's own parts */
function alacPanel(rbox, p, cid, n) {
  const an = anatomy(p); const els = an.items.filter(i => i[0] === 'Element / item').length;
  const q = (n && n.q && n.q.length) ? n.q[Math.floor(Math.random() * n.q.length)] : `Invent a short set of facts that raises ${p.l}${p.c ? ' (' + p.c + ')' : ''}, then answer it as you would in the bar examination.`;
  const checks = [`I gave a direct answer first (yes or no, liable or not) before any explanation.`, `I cited ${p.l}${meta(cid) ? ' of the ' + meta(cid).short : ''} as the legal basis.`, `I stated the rule in the provision’s own key words.`]
    .concat(els ? [`I applied each of the ${els} listed items or elements to the facts, one by one.`] : [])
    .concat(an.items.some(i => i[0] === 'Condition') ? ['I checked whether the condition is met on these facts.'] : [])
    .concat(an.items.some(i => i[0] === 'Exception' || i[0] === 'Proviso') ? ['I asked whether an exception or proviso takes the facts out of the rule.'] : [])
    .concat(an.items.some(i => i[0] === 'Penalty') ? ['I stated the consequence or penalty.'] : [])
    .concat(['My conclusion answers the question asked, in one sentence.']);
  rbox.innerHTML = `<p class="small muted">Philippine bar answers are graded for a clear answer, the correct legal basis, and the application of the law to the facts. Write in four parts, then grade yourself against the checklist.</p>
    <div class="card flat"><b>Question</b><p class="explain" style="margin:6px 0 0">${esc(q)}</p></div>
    <div class="alac">${[['A', 'Answer', 'Yes or no; liable or not; valid or void.'], ['L', 'Legal basis', 'The provision, and the rule in its key words.'], ['A', 'Application', 'Apply each element to the facts.'], ['C', 'Conclusion', 'One sentence that answers the question.']].map(([k, h, ph], i) => `<label><span class="ak">${k}</span><b>${h}</b><textarea data-al="${i}" rows="${i === 2 ? 5 : 2}" placeholder="${esc(ph)}"></textarea></label>`).join('')}</div>
    ${confHTML()}
    <div class="row" style="margin-top:8px"><button class="btn primary sm" id="alg">Grade my answer</button></div><div id="alout"></div>`;
  wireConf(rbox);
  $('#alg', rbox).onclick = () => {
    const txt = $$('[data-al]', rbox).map(t => t.value.trim());
    if (!txt.some(Boolean)) return toast('Write your answer first.');
    $('#alout', rbox).innerHTML = `<div class="card flat" style="margin-top:12px"><h3 style="margin:0 0 8px">Grade yourself honestly</h3><div class="checks">${checks.map((c, i) => `<label><input type="checkbox" data-ck="${i}"> <span>${esc(c)}</span></label>`).join('')}</div>
      <div class="row" style="margin-top:10px"><button class="btn sm" id="alshow">Show the provision to compare</button><button class="btn primary sm" id="aldone">Save my grade</button></div><p id="alres" class="small"></p></div>`;
    $('#alshow', rbox).onclick = () => { const l = $('#law'); if (l) { l.style.filter = ''; l.scrollIntoView({ behavior: 'smooth' }); } };
    $('#aldone', rbox).onclick = () => {
      const got = $$('[data-ck]:checked', rbox).length; const pct = Math.round(got / checks.length * 100);
      const extra = takeConf(rbox, ck(cid, p.i), pct);
      $('#alres', rbox).innerHTML = `<b>${got} of ${checks.length}</b>. ${pct >= 85 ? 'A complete answer. Rate <b>Good</b> or <b>Easy</b>.' : pct >= 60 ? 'Most of the parts are there. Rewrite the missing ones tomorrow.' : 'Rate <b>Again</b>; reread the provision and write it once more.'}` + extra;
    };
  };
}
function recallPanel(box, d, p, cid, onDone) {
  const nw = words(provText(p)).length;
  const F = inForce(p);
  const head = p.st ? `<div class="status st-${esc(p.st)}" style="margin-bottom:10px"><b>${p.st === 'repealed' ? 'Repealed' : p.st === 'void' ? 'Struck down' : 'Superseded'}.</b> Recall is optional here: ${p.st === 'void' ? 'learn the ruling that struck it down instead.' : 'spend the effort on the law that replaced it.'}</div>`
    : F.a && !F.partial ? `<p class="tiny muted" style="margin:0 0 8px">Recall uses the text in force (as amended by ${esc(F.a.by)}${F.a.y ? `, ${esc(F.a.y)}` : ''}).</p>`
    : F.partial ? `<p class="tiny muted" style="margin:0 0 8px">Partly amended (latest: ${esc(F.a.by)}${F.a.y ? `, ${esc(F.a.y)}` : ''}). Recall uses ${F.base ? `the text as restated by ${esc(F.base.by)}` : 'the earlier text'}; learn the changed parts shown above it with the provision.</p>` : '';
  box.innerHTML = `<div class="panel">${head}<div class="row" style="margin-bottom:10px">
    <button class="btn sm" data-m="c1">Cloze · light</button><button class="btn sm" data-m="c2">Cloze · medium</button><button class="btn sm" data-m="c3">Cloze · heavy</button>
    <button class="btn sm" data-m="fl">First letters</button><button class="btn sm" data-m="fr">Write it out</button><button class="btn sm" data-m="al">Bar answer (ALAC)</button></div>
    <div id="rbox"></div></div>`;
  const rbox = $('#rbox', box);
  const law = $('#law');
  const hideLaw = h => { if (law) law.style.filter = h ? 'blur(7px)' : ''; if (law) law.style.userSelect = h ? 'none' : ''; };
  const modes = {
    c1: () => cloze(1), c2: () => cloze(2), c3: () => cloze(3),
    al: () => { hideLaw(true); alacPanel(rbox, p, cid, (NOTES[cid] || {})[p.i]); },
    fl: () => {
      hideLaw(true);
      rbox.innerHTML = `<p class="small muted">Recite each word aloud from its first letter. Tap a word to check it.</p><div class="card flat fl rtext">${(() => { const ps = inForce(p).ps.filter(x => typeof x === 'string'); const { ms, info } = lawLayout(ps); return ps.map((x, i) => layoutWrap(ms[i], info[i], words(plain(ms[i] && ms[i].key !== 'ord' ? ms[i].body : x)).map(w => `<span class="h">${esc(w)}</span>`).join(' '))).join(''); })()}</div><div class="row" style="margin-top:8px"><button class="btn sm" id="flall">Reveal all</button></div>`;
      rbox.onclick = e => { const s = e.target.closest('.fl span'); if (s) s.classList.remove('h'); };
      $('#flall').onclick = () => { $$('.fl span', rbox).forEach(s => s.classList.remove('h')); hideLaw(false); };
    },
    fr: () => {
      hideLaw(true);
      rbox.innerHTML = `<p class="small muted">Write the provision from memory${nw > 220 ? ' (long provision: write as much as you can — the first paragraph counts most)' : ''}. Then check it word by word against the verbatim text.</p><textarea id="frt" placeholder="${esc(p.l)}…"></textarea>${confHTML()}<div class="row" style="margin-top:8px"><button class="btn primary sm" id="frc">Check</button><button class="btn sm" id="frs">Show the text</button></div><div id="frout" style="margin-top:12px"></div>`;
      $('#frs').onclick = () => hideLaw(false); wireConf(rbox);
      $('#frc').onclick = () => {
        const truth = words(provText(p)); const att = words($('#frt').value);
        if (!att.length) return toast('Write something first.');
        const lim = Math.min(truth.length, Math.max(att.length + 40, 60));
        const r = lcsDiff(truth.slice(0, lim), att);
        const pct = Math.round(r.score * 100);
        $('#frout').innerHTML = `<div class="row"><span class="stat">${pct}%</span><span class="small muted">of ${lim < truth.length ? 'the first ' + lim + ' words' : 'the text'} recalled in order · ${Math.round(r.precision * 100)}% of your words matched</span></div>
          <p class="small">${pct >= 95 ? 'Verbatim-level. Rate <b>Easy</b> or <b>Good</b>.' : pct >= 80 ? 'Strong. Rate <b>Good</b>; fix the red words.' : pct >= 55 ? 'Partial. Rate <b>Hard</b> and re-read the red words.' : 'Not yet. Rate <b>Again</b>, read it once more, then try again.'}</p>
          <div class="card flat diff">${r.out.map(o => o.t === 'ok' ? `<span class="okw">${esc(o.w)}</span>` : o.t === 'miss' ? `<span class="miss">${esc(o.w)}</span>` : `<span class="extra">${esc(o.w)}</span>`).join(' ')}</div>
          <p class="tiny muted">Green: recalled · red: missed · struck: not in the text.</p>` + takeConf(rbox, ck(cid, p.i), pct);
        hideLaw(false); onDone && onDone(pct);
      };
    },
  };
  function cloze(level) {
    hideLaw(true);
    const seed = p.i + ':' + level + ':' + Math.floor(Date.now() / DAY);
    const paras = inForce(p).ps.filter(x => typeof x === 'string');
    const { ms, info } = lawLayout(paras);
    let total = 0;
    const html = paras.map((x, bi) => {
      const m = ms[bi], f = info[bi];
      let b = plain(m && m.key !== 'ord' ? m.body : x), pre = '';
      if (m && m.key === 'ord') { const o = /^\S+\s*/.exec(b); pre = o[0]; b = b.slice(pre.length); }
      const [main, src] = splitSrc(b);
      const { toks, picked } = clozeModel({ p: [main] }, level, seed + bi);
      const inner = esc(pre) + toks.map((t, i) => {
        if (!picked.has(i)) return esc(t);
        const mm = t.match(/^([“"(‘'[]*)(.*?)([”"),.;:!?’'\]]*)$/);
        total++;
        return `${esc(mm[1])}<input data-a="${esc(mm[2])}" size="${Math.max(3, mm[2].length)}" aria-label="blank">${esc(mm[3])}`;
      }).join('') + (src ? ` <span class="srcn">${esc(src)}</span>` : '');
      return layoutWrap(m, f, inner);
    }).join('');
    rbox.innerHTML = `<p class="small muted">Fill every blank, then check. ${total} blank${total === 1 ? '' : 's'}.</p><div class="card flat cloze rtext">${html}</div>${confHTML()}<div class="row" style="margin-top:8px"><button class="btn primary sm" id="cc">Check</button><button class="btn sm" id="cr">Reveal</button></div><p id="cres" class="small"></p>`;
    const ins = $$('input', rbox); wireConf(rbox);
    ins[0] && ins[0].focus();
    ins.forEach((inp, k) => inp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); (ins[k + 1] || $('#cc')).focus(); } }));
    $('#cc').onclick = () => {
      let ok = 0;
      ins.forEach(i => { const g = normWord(i.value) === normWord(i.dataset.a); i.classList.toggle('ok', g); i.classList.toggle('bad', !g); if (g) ok++; });
      $('#cres').innerHTML = `<b>${ok}/${ins.length}</b> correct. ${ok === ins.length ? 'Rate <b>Good</b> or <b>Easy</b>.' : ok >= ins.length * .7 ? 'Rate <b>Hard</b> or <b>Good</b>.' : 'Rate <b>Again</b> and re-read.'}` + takeConf(rbox, ck(cid, p.i), Math.round(ok / Math.max(1, ins.length) * 100));
      hideLaw(false); onDone && onDone(Math.round(ok / Math.max(1, ins.length) * 100));
    };
    $('#cr').onclick = () => { ins.forEach(i => { if (normWord(i.value) !== normWord(i.dataset.a)) { i.value = i.dataset.a; i.classList.add('bad'); } }); hideLaw(false); };
  }
  $$('[data-m]', box).forEach(b => b.onclick = () => { $$('[data-m]', box).forEach(x => x.classList.toggle('primary', x === b)); modes[b.dataset.m](); });
  const def = nw <= 70 ? 'fr' : 'c2';
  $(`[data-m="${def}"]`, box).click();
}

/* ---- review session */
async function reviewView() {
  setNav('review');
  let queue = dueKeys();
  let fresh = [];
  const room = Math.max(0, S.settings.newPerDay - newToday());
  if (room > 0) {
    // new cards: provisions opened but never rated, oldest first
    fresh = Object.entries(S.cards).filter(([, c]) => !c.reps && !c.due).sort((a, b) => (a[1].seen || 0) - (b[1].seen || 0)).slice(0, room).map(([k]) => k);
  }
  queue = queue.concat(fresh);
  if (!queue.length) {
    main.innerHTML = `<div class="reviewcard card"><h1>All caught up.</h1><p class="muted">Nothing is due. New provisions enter review once you open them under Learn. Today: ${newToday()} new, ${(S.days[today()] || {}).r || 0} reviews.</p><div class="row"><a class="btn primary" href="#/learn">Learn new provisions</a><a class="btn" href="#/drill">Drill anyway</a></div></div>`;
    return;
  }
  let i = 0;
  const step = async () => {
    if (i >= queue.length) { main.innerHTML = `<div class="reviewcard card"><h1>Session complete.</h1><p class="muted">${queue.length} provisions reviewed. Come back tomorrow — spacing is what makes it stick.</p><a class="btn primary" href="#/">Home</a></div>`; return; }
    const key = queue[i]; const [cid, pid] = key.split('|');
    if (!meta(cid)) { i++; return step(); }
    const d = await loadCode(cid); const p = d.byId[pid];
    if (!p) { delete S.cards[key]; save(); i++; return step(); }
    main.innerHTML = `<div class="reviewcard"><div class="row small muted"><span>${i + 1} / ${queue.length}</span><span class="spacer"></span><span>${esc(d.short)}</span></div>
      <div class="card" style="margin-top:8px">${crumbs(d, p, cid)}<div class="prompt">${esc(p.l)}${p.c ? ' — ' + esc(p.c) : ''}</div>
      <p class="small muted">Recall it before you look. Use a mode below, or just say it aloud and reveal.</p>
      <div id="rv"></div>
      <div class="row" style="margin-top:12px"><button class="btn" id="reveal">Reveal the text <span class="kbd">space</span></button><a class="btn ghost sm" href="#/p/${cid}/${pid}">Open study page</a></div>
      <div id="full" hidden style="margin-top:12px"></div>
      <div class="rate">${['Again', 'Hard', 'Good', 'Easy'].map((n, k) => `<button class="r${k + 1}" data-rate="${k + 1}">${n}<small>${preview(key)[k]}</small></button>`).join('')}</div>
      <p class="tiny muted" style="margin:8px 0 0">Keys: <span class="kbd">1</span>–<span class="kbd">4</span> rate.</p></div></div>`;
    const rv = $('#rv');
    const fake = document.createElement('div'); fake.id = 'law'; fake.hidden = true; rv.appendChild(fake);
    recallPanel(rv, d, p, cid);
    const reveal = () => { const f = $('#full'); f.hidden = false; f.innerHTML = lawHTML(d, p, cid, S.settings.hl); };
    $('#reveal').onclick = reveal;
    const go = g => { rate(key, g); i++; step(); };
    $$('[data-rate]').forEach(b => b.onclick = () => go(+b.dataset.rate));
    document.onkeydown = e => { if (!location.hash.startsWith('#/review') || /input|textarea/i.test(e.target.tagName)) return; if (e.key === ' ') { e.preventDefault(); reveal(); } if (/^[1-4]$/.test(e.key)) go(+e.key); };
  };
  step();
}

/* ---- the map: all of law school on one screen, then zoom in, one level at a time
   Five states per provision, from the memory model: locked in (recall predicted to hold three weeks: stability ≥ 21 days
   and recall now at or above your target), learning, slipping (recall now below target), opened, not started.
   A part is locked in when every provision under it is. Repealed and superseded provisions are not counted. */
const LOCK_DAYS = 21;
function lockState(key) {
  const c = S.cards[key];
  if (!c) return 'n';
  if (c.s == null || !c.last) return 'o';
  const r = recallNow(upgrade(c));
  if (r < goal()) return 'x';
  return c.s >= LOCK_DAYS ? 'k' : 'g';
}
function tally(keys) { const t = { k: 0, g: 0, x: 0, o: 0, n: 0, total: keys.length }; for (const k of keys) t[lockState(k)]++; return t; }
/* code-level tally without loading the code: cards carry the state; the catalogue carries the count */
function codeTally(cid) {
  const m = meta(cid); const t = { k: 0, g: 0, x: 0, o: 0, n: 0, total: m.live ?? m.count }; const pre = cid + '|';
  for (const k in S.cards) if (k.startsWith(pre)) t[lockState(k)]++;
  t.n = Math.max(0, t.total - t.k - t.g - t.x - t.o); return t;
}
function addT(a, b) { for (const k of ['k', 'g', 'x', 'o', 'n', 'total']) a[k] += b[k]; return a; }
const zeroT = () => ({ k: 0, g: 0, x: 0, o: 0, n: 0, total: 0 });
function lockBar(t) {
  const w = x => (t.total ? x / t.total * 100 : 0).toFixed(2) + '%';
  return `<div class="lbar" role="img" aria-label="${t.k} locked in, ${t.g} learning, ${t.x} slipping, ${t.o} opened, ${t.n} not started"><i class="k" style="width:${w(t.k)}"></i><i class="g" style="width:${w(t.g)}"></i><i class="x" style="width:${w(t.x)}"></i><i class="o" style="width:${w(t.o)}"></i></div>`;
}
function lockLine(t) {
  const pc = t.total ? Math.floor(t.k / t.total * 100) : 0;
  if (t.total && t.k === t.total) return `<span class="lk done">🔒 Locked in</span>`;
  return `<span class="lk"><b>${pc}%</b> locked in</span>${t.x ? ` <span class="lk x">${t.x} slipping</span>` : ''}${t.g ? ` <span class="lk g">${t.g} learning</span>` : ''}<span class="lk n">${(t.total - t.k - t.g - t.x).toLocaleString()} to go</span>`;
}
/* pictures of progress: a ring, a waffle of 100 squares (each 1%), and a mosaic with one square per provision */
function ringHTML(t, size = 64, label) {
  const p = x => (t.total ? x / t.total * 100 : 0);
  const a = p(t.k), b = a + p(t.g), c = b + p(t.x), d = c + p(t.o);
  const pc = t.total ? Math.floor(t.k / t.total * 100) : 0;
  return `<span class="ring" style="--sz:${size}px;background:conic-gradient(var(--ok) 0 ${a}%,var(--blue) ${a}% ${b}%,var(--warn) ${b}% ${c}%,var(--line2) ${c}% ${d}%,var(--line) ${d}% 100%)"><span>${t.total && t.k === t.total ? '🔒' : pc + '%'}${label ? `<small>${label}</small>` : ''}</span></span>`;
}
function waffle(t) {
  const cells = []; const tot = t.total || 1; let used = 0;
  const share = x => x ? Math.max(1, Math.round(x / tot * 100)) : 0;
  for (const k of ['k', 'g', 'x', 'o']) { let n = share(t[k]); n = Math.min(n, 100 - used); for (let i = 0; i < n; i++) cells.push(k); used += n; }
  while (cells.length < 100) cells.push('n');
  return `<span class="waf" aria-hidden="true">${cells.map(c => `<i class="${c}"></i>`).join('')}</span>`;
}
const STNAME = { k: 'Locked in', g: 'Learning', x: 'Slipping', o: 'Opened', n: 'Not started' };
function mosaic(keys, d, cid, link) {
  return `<span class="mos${keys.length > 600 ? ' fine' : ''}">${keys.map(k => { const st = lockState(k); if (!link) return `<i class="${st}"></i>`; const p = d.byId[k.split('|')[1]]; return `<a class="${st}" href="#/p/${cid}/${p.i}" title="${esc(p.l)}${p.c ? ' — ' + esc(p.c) : ''}: ${STNAME[st]}"></a>`; }).join('')}</span>`;
}
const sittingMins = n => Math.max(2, Math.round(n * 1.5));
function mapFigure(rows) {
  const u = 'mf' + (++figSeq);
  const zone = ({ f, t }) => { const [px, py] = figPos(f.id) || HOUSE_PIN[f.id]; const C = 2 * Math.PI * 25; const pk = t.total ? t.k / t.total : 0, pg = t.total ? (t.k + t.g) / t.total : 0;
    return `<a class="zone f-${f.id}" href="#/map/${f.id}" aria-label="${f.n}. ${esc(f.name)}: ${Math.floor(pk * 100)}% locked in"><circle class="trk" cx="${px}" cy="${py}" r="25"/>
      <circle class="arcg" cx="${px}" cy="${py}" r="25" stroke-dasharray="${(C * pg).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 ${px} ${py})"/><circle class="arck" cx="${px}" cy="${py}" r="25" stroke-dasharray="${(C * pk).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 ${px} ${py})"/>
      <circle class="pinsh" cx="${px}" cy="${py + 2.5}" r="17"/><circle class="pin" cx="${px}" cy="${py}" r="17"/><text class="nt" x="${px}" y="${py + 0.5}">${f.n}</text></a>`; };
  return `<svg class="fig mapfig" viewBox="0 0 600 520" role="img" aria-label="The House of Law: each field’s place, ringed by how much of it you have locked in">${houseSVG(u)}${rows.map(zone).join('')}</svg>`;
}
const LEGEND = `<div class="lleg"><span><i class="k"></i>Locked in</span><span><i class="g"></i>Learning</span><span><i class="x"></i>Slipping</span><span><i class="o"></i>Opened</span><span><i class="n"></i>Not started</span></div>`;
function mapCrumbs(parts) { return `<div class="crumbs mapcr">${parts.map((p, i) => i === parts.length - 1 ? `<span>${esc(p[0])}</span>` : `<a href="${p[1]}">${esc(p[0])}</a><span class="sep">›</span>`).join('')}</div>`; }
function provKeysUnder(d, cid, i) { const out = []; const walk = j => { for (const p of d.divProv[j]) if (!p.st) out.push(ck(cid, p.i)); d.kids[j].forEach(walk); }; walk(i); return out; }
async function mapView(parts) {
  setNav('library');
  const [fid, cid, dv] = parts;
  let html = '';
  if (!fid) {
    // level 0: the whole of law school
    const foc = focusIds();
    const rows = CUR.fields.map(f => { const t = fieldCodes(f).reduce((a, c) => addT(a, codeTally(c)), zeroT()); return { f, t, mine: foc.includes(f.id) }; });
    const all = rows.filter(r => r.mine).reduce((a, r) => addT(a, r.t), zeroT());
    const nx = rows.filter(r => r.mine).sort((a, b) => (b.t.x - a.t.x) || (a.t.k / (a.t.total || 1) - b.t.k / (b.t.total || 1)))[0];
    html = `<div class="mapv zin">${mapCrumbs([['Law school', '#/map']])}
      <span class="eyebrow">The whole map</span><h1>Everything you will be examined on</h1>
      <div class="maphero"><div class="mhfig">${mapFigure(rows)}</div>
        <div class="mhside"><p class="lead" style="margin:0 0 10px">Eight fields, eight places in one building. Start from the whole, then zoom in: a field, a code, a Book or Title, a chapter, a provision. Lock in each part, then move on.</p>
          <div class="mhstat">${ringHTML(all, 84, 'locked in')}<div class="small">${lockLine(all)}<br><span class="muted">${all.total.toLocaleString()} provisions in this semester’s fields</span></div></div>
          ${nx ? `<div class="mapnext"><span class="eyebrow">Next to lock in</span><a class="btn primary" href="#/map/${nx.f.id}">${esc(nx.f.name)} →</a><span class="small muted">${nx.t.x ? `${nx.t.x} provision${nx.t.x === 1 ? ' is' : 's are'} slipping here.` : 'The least locked-in field you are taking this semester.'}</span></div>` : ''}</div></div>
      <div class="mapgrid">${rows.map(({ f, t, mine }) => `<a class="mtile f-${f.id}${mine ? '' : ' dim'}" href="#/map/${f.id}"><span class="mth"><span><span class="p">${f.n} · ${esc(f.pname)}</span><span class="t">${esc(f.name)}</span></span>${ringHTML(t, 52)}</span>${waffle(t)}<span class="ml">${lockLine(t)}</span></a>`).join('')}</div>
      ${LEGEND}<p class="tiny muted">Each square in a tile is 1% of that field. Faded fields are outside this semester. <a href="#/learn">Change your fields</a> · <a href="#/about">What “locked in” means</a></p></div>`;
  } else if (!cid) {
    // level 1: one field, its codes by tier
    const f = CUR.byId[fid]; if (!f) return mapView([]);
    const tierName = { start: 'Start here', core: 'Core', deep: 'Go deeper when you need it' };
    const ft = fieldCodes(f).reduce((a, c) => addT(a, codeTally(c)), zeroT());
    let nxt = null;
    const tiers = ['start', 'core', 'deep'].map(tier => {
      const items = f.tracks.filter(t => t.tier === tier).flatMap(t => t.items.filter(i => i.t === 'code' && !i.x).map((i, k) => ({ id: i.id, track: t.name, pic: k === 0 ? t.pic : '' })));
      if (!items.length) return '';
      return `<div class="tier">${tierName[tier]}</div><div class="mcodes">${items.map(({ id, track, pic }) => { const m = meta(id); const t = codeTally(id); if (!nxt && t.k < t.total) nxt = id;
        return `<a class="mcode" href="#/map/${fid}/${id}">${ringHTML(t, 56)}<span class="mt"><b>${esc(m.short)}</b><span class="tiny muted">${esc(track)} · ${(m.live ?? m.count).toLocaleString()} provisions${m.live != null && m.live < m.count ? ` in force (${(m.count - m.live).toLocaleString()} repealed)` : ''}</span><span class="ml">${lockLine(t)}</span>${pic ? `<span class="mpic">Picture: ${esc(pic)}</span>` : ''}</span>${waffle(t)}</a>`; }).join('')}</div>`;
    }).join('');
    html = `<div class="mapv zin f-${f.id}">${mapCrumbs([['Law school', '#/map'], [f.name, '']])}
      <div class="fieldhero"><div class="fhfig">${figure(f.id, true)}</div><div><span class="eyebrow" style="color:var(--f)">${f.n} · ${esc(f.pname)}</span><h1>${esc(f.name)}</h1><p class="hook" style="margin:0 0 8px">${esc(f.q)}</p>
      <div class="mhstat">${ringHTML(ft, 72, 'locked in')}<div class="small">${lockLine(ft)}</div></div></div></div>
      ${nxt ? `<div class="mapnext"><span class="eyebrow">Next to lock in</span><a class="btn primary" href="#/map/${fid}/${nxt}">${esc(meta(nxt).short)} →</a><span class="small muted">In the order this field is best learned: foundations first.</span></div>` : ''}
      ${tiers}
      <p class="small" style="margin-top:14px"><a href="#/field/${fid}">Open this field’s study path</a> for its lessons and memory walks.</p></div>`;
  } else {
    // level 2+: a code, or a division inside it
    const f = CUR.byId[fid] || fieldOf(cid); const d = await loadCode(cid); const m = meta(cid);
    const at = dv != null && dv !== '' ? +dv : null;
    const chain = []; let v = at; while (v != null) { chain.unshift(v); v = d.divisions[v].p; }
    const kids = at == null ? d.roots : d.kids[at];
    const direct = (at == null ? d.loose : d.divProv[at]).filter(p => !p.st);
    const allKeys = at == null ? d.provisions.filter(p => !p.st).map(p => ck(cid, p.i)) : provKeysUnder(d, cid, at);
    const T = tally(allKeys);
    const kidRows = kids.map(i => { const keys = provKeysUnder(d, cid, i); return { i, keys, t: tally(keys) }; }).filter(r => r.keys.length);
    const nx = kidRows.find(r => r.t.k < r.t.total);
    const title = at == null ? d.title : d.divisions[at].t;
    const cr = [['Law school', '#/map']]; if (f) cr.push([f.name, `#/map/${f.id}`]); cr.push([m.short, `#/map/${fid}/${cid}`]);
    chain.forEach((j, k) => cr.push([shortDiv(d.divisions[j].t), `#/map/${fid}/${cid}/${j}`]));
    cr[cr.length - 1][1] = '';
    const scope = at == null ? `c=${cid}` : `c=${cid}&d=${at}`;
    const due = allKeys.filter(k => lockState(k) === 'x').length;
    html = `<div class="mapv zin${f ? ' f-' + f.id : ''}">${mapCrumbs(cr)}
      <span class="eyebrow">${at == null ? esc(m.citation) : esc(m.short)}</span><h1>${esc(title)}</h1>
      <div class="card mapsum"><div class="mhstat">${ringHTML(T, 76, 'locked in')}<div class="small">${lockLine(T)}<br><span class="muted">${T.total.toLocaleString()} provisions${T.total <= 15 ? ` · one sitting, about ${sittingMins(T.total - T.k)} minutes` : ''}</span></div></div>
        <div class="row" style="margin-top:10px">${T.k < T.total ? `<a class="btn primary" href="#/sprint?${scope}">${due ? `Bring back ${due} slipping` : T.k + T.g ? 'Lock in the next ones' : 'Start locking this in'}</a>` : '<span class="chip ok">Every provision here is locked in</span>'}<a class="btn" href="#/code/${cid}${at != null ? '?div=' + at : ''}">Read it in order</a></div></div>
      ${nx && kidRows.length > 1 ? `<div class="mapnext"><span class="eyebrow">Next to lock in</span><a class="btn" href="#/map/${fid}/${cid}/${nx.i}">${esc(shortDiv(d.divisions[nx.i].t))} →</a></div>` : ''}
      ${kidRows.length ? `<div class="mblocks">${kidRows.map(r => `<a class="mblock${r.t.k === r.t.total ? ' done' : ''}" href="#/map/${fid}/${cid}/${r.i}"><span class="mbh">${ringHTML(r.t, 44)}<span class="mt"><b>${esc(d.divisions[r.i].t)}</b><span class="tiny muted">${r.keys.length} provision${r.keys.length === 1 ? '' : 's'}${r.keys.length <= 15 && r.t.k < r.t.total ? ` · one sitting` : ''}</span></span></span>${mosaic(r.keys, d, cid, false)}</a>`).join('')}</div>` : ''}
      ${direct.length ? `<div class="card flat mosdirect">${mosaic(direct.map(p => ck(cid, p.i)), d, cid, true)}<span class="tiny muted">One square per provision. Tap one to study it.</span></div><ul class="plist mapprov">${direct.map(p => { const st = lockState(ck(cid, p.i)); return `<li><a href="#/p/${cid}/${p.i}"><span class="ls ${st}" title="${{ k: 'Locked in', g: 'Learning', x: 'Slipping', o: 'Opened', n: 'Not started' }[st]}">${st === 'k' ? '🔒' : ''}</span><span class="pl">${esc(p.l)}</span><span class="pc">${esc(p.c || inForce(p).cap || firstWords(p))}</span></a></li>`; }).join('')}</ul>` : ''}
      ${LEGEND}</div>`;
  }
  main.innerHTML = html;
}

/* ---- sprint: a few minutes, one provision at a time
   Built for a short attention span. A hard time box; one item on screen; the provisions you are closest to forgetting
   come first; new material is read once, then tested at once (reading alone fades fast); an item you miss comes back
   three cards later in the same sprint until you get it (successive relearning); the sprint ends with a break. */
const fmtClock = ms => { const t = Math.ceil(ms / 1000); return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0'); };
async function sprintPool(maxNew, scope) {
  const now = Date.now();
  if (scope) {
    // a sprint on one part of the map: what is slipping there first, then the next provisions in order
    const inS = new Set(scope);
    const due = dueKeys().filter(k => inS.has(k)).map(k => [k, recallNow(upgrade(S.cards[k]), now) ?? 0]).sort((a, b) => a[1] - b[1]).map(x => x[0]);
    const fresh = scope.filter(k => !S.cards[k] || (!S.cards[k].reps && !S.cards[k].last)).slice(0, maxNew);
    return { due, fresh };
  }
  const due = dueKeys().map(k => [k, recallNow(upgrade(S.cards[k]), now) ?? 0]).sort((a, b) => a[1] - b[1]).map(x => x[0]);
  const fresh = Object.entries(S.cards).filter(([, c]) => !c.reps && !c.last && !c.due).sort((a, b) => (a[1].seen || 0) - (b[1].seen || 0)).map(([k]) => k).slice(0, maxNew);
  if (fresh.length < maxNew && S.last && meta(S.last.c)) {
    const d = await loadCode(S.last.c); const at = d.byId[S.last.p];
    if (at) for (const p of d.provisions.slice(at.ix + 1)) {
      if (fresh.length >= maxNew) break;
      const k = ck(S.last.c, p.i);
      if (S.cards[k] || p.st || words(provText(p)).length < 4) continue;
      fresh.push(k);
    }
  }
  return { due, fresh };
}
async function sprintView(q) {
  setNav('review');
  const mins = S.settings.sprint || 5;
  const room = Math.max(0, S.settings.newPerDay - newToday());
  let scope = null, scopeName = '';
  if (q && q.get('c') && meta(q.get('c'))) {
    const cid = q.get('c'); const d = await loadCode(cid); const dv = q.get('d');
    scope = dv != null ? provKeysUnder(d, cid, +dv) : d.provisions.filter(p => !p.st).map(p => ck(cid, p.i));
    scopeName = dv != null ? `${d.short} · ${shortDiv(d.divisions[+dv].t)}` : d.short;
  }
  const { due, fresh } = await sprintPool(scope ? Math.max(3, Math.min(5, room)) : Math.min(2, room), scope);
  const queue = due.slice(0, 8);
  fresh.forEach((k, j) => queue.splice(Math.min(queue.length, j === 0 ? 1 : 4), 0, k));
  if (!queue.length) {
    main.innerHTML = `<div class="reviewcard card"><span class="eyebrow">Sprint</span><h1>Nothing to do right now.</h1><p class="muted">Nothing is due and you have no new provision waiting. Open one under Learn; it joins your sprints from then on.</p><div class="row"><a class="btn primary" href="#/learn">Learn something new</a><a class="btn" href="#/drill">Drill anyway</a></div></div>`;
    return;
  }
  document.body.classList.add('focus');
  const before = memoryStats();
  let i = 0, elapsed = 0, tick = Date.now(), over = false, shown = 0;
  const done = [], missed = {};
  const left = () => Math.max(0, mins * 60000 - elapsed);
  const timer = setInterval(() => {
    if (!location.hash.startsWith('#/sprint')) { clearInterval(timer); document.body.classList.remove('focus'); return; }
    const now = Date.now();
    if (!document.hidden) elapsed += now - tick;   // time away from the tab does not count
    tick = now;
    const bar = $('#spbar'); if (bar) bar.style.width = Math.min(100, elapsed / (mins * 600)) + '%';
    const tl = $('#sptime'); if (tl) tl.textContent = fmtClock(left());
    if (!left() && !over) { over = true; const n = $('#spover'); if (n) n.hidden = false; }
  }, 500);
  const finish = () => {
    clearInterval(timer); document.body.classList.remove('focus'); document.onkeydown = null;
    const after = memoryStats();
    const ok = done.filter(x => x[1] > 1).length;
    const nd = Object.values(S.cards).filter(c => c.due && (c.reps || c.last)).map(c => c.due).sort((a, b) => a - b)[0];
    const pc = x => Math.round(x * 100) + '%';
    main.innerHTML = `<div class="reviewcard card sprintdone"><span class="eyebrow">Sprint done · ${fmtClock(elapsed)}</span><h1>${ok} of ${done.length} recalled</h1>
      ${after.n ? `<p>Across the ${after.n.toLocaleString()} provision${after.n === 1 ? '' : 's'} you are keeping, average recall now is <b>${pc(after.avg)}</b>${before.n ? ` (it was ${pc(before.avg)} when you started)` : ''}. ${after.risk ? `${after.risk} ${after.risk === 1 ? 'is' : 'are'} below ${pc(goal())} and will come up next.` : 'None is below your target.'}</p>` : ''}
      ${Object.keys(missed).length ? `<p class="small">Missed at least once: ${Object.keys(missed).map(k => { const [c, p] = k.split('|'); const pr = CODES[c] && CODES[c].byId[p]; return `<a href="#/p/${c}/${p}">${esc(meta(c).short)} ${esc(pr ? pr.l : p)}</a>`; }).join(' · ')}. Each comes back in ten minutes, then tomorrow.</p>` : ''}
      <div class="tryit small"><b>Now rest for five minutes.</b> Stand up, look at something far away, have some water, and do not pick up your phone. A few minutes of quiet rest right after learning helps the brain keep what it just took in (Dewar and others, 2012).</div>
      <p class="small muted">${nd ? `Next provision due ${nd <= Date.now() ? 'now' : new Date(nd).toLocaleString([], { weekday: 'short', hour: 'numeric', minute: '2-digit' })}.` : ''} Two or three short sprints spread over the day beat one long sitting.</p>
      <div class="row"><button class="btn primary" id="spagain">Another sprint</button><a class="btn" href="#/">Home</a></div></div>`;
    $('#spagain').onclick = () => sprintView(q);
  };
  const step = async () => {
    if (i >= queue.length || (over && shown > 0 && i >= shown)) return finish();
    const key = queue[i]; const [cid, pid] = key.split('|');
    if (!meta(cid)) { i++; return step(); }
    const d = await loadCode(cid); const p = d.byId[pid];
    if (!p) { i++; return step(); }
    shown = i + 1;
    const c0 = S.cards[key];
    const isNew = !(c0 && (c0.reps || c0.last));
    const r = recallNow(upgrade(c0));
    const F = inForce(p); const cap = F.cap || p.c;
    const hook = S.hooks[key];
    const ps = F.ps.filter(x => typeof x === 'string');
    const first = plain(ps[0] || '').split(/(?<=[.;:])\s/)[0];
    const hint = first.split(/\s+/).map(w => w.replace(/^([“"(‘'\[]*)([A-Za-z0-9])[^\s]*/, '$1$2…')).join(' ');
    main.innerHTML = `<div class="sprint">
      ${scopeName ? `<p class="tiny muted" style="margin:6px 0 0">Locking in: <b>${esc(scopeName)}</b></p>` : ''}<div class="sphead"><span id="sptime" class="sptime">${fmtClock(left())}</span><div class="spbar"><i id="spbar" style="width:${Math.min(100, elapsed / (mins * 600))}%"></i></div><span class="small muted">${queue.length - i} left</span><button class="btn sm ghost" id="spend">End</button></div>
      <p id="spover" class="small spover" ${over ? '' : 'hidden'}>Time is up. Finish this one, then rest.</p>
      <div class="card spcard">
        <div class="small muted">${esc(d.short)}${isNew ? ' · <b class="newtag">New</b>' : r != null ? ` · your recall now ≈ ${Math.round(r * 100)}%` : ''}${c0 && (c0.lapses || 0) >= LEECH ? ' · <b style="color:var(--warn)">stubborn</b>' : ''}</div>
        <div class="prompt">${esc(p.l)}${cap ? ' — ' + esc(cap) : ''}</div>
        <div id="spbody"></div>
      </div></div>`;
    $('#spend').onclick = finish;
    const body = $('#spbody');
    const rateRow = note => `<p class="small" style="margin:12px 0 0">${note || 'How well did you recall it?'}</p><div class="rate">${['Again', 'Hard', 'Good', 'Easy'].map((n, k) => `<button class="r${k + 1}" data-rate="${k + 1}">${n}<small>${preview(key)[k]}</small></button>`).join('')}</div>`;
    const go = g => {
      rate(key, g); done.push([key, g]);
      if (g === 1) { missed[key] = (missed[key] || 0) + 1; if (missed[key] <= 2) queue.splice(Math.min(queue.length, i + 3), 0, key); }
      i++; step();
    };
    const wireRate = () => $$('[data-rate]', body).forEach(b => b.onclick = () => go(+b.dataset.rate));
    let canRate = false;
    if (isNew) {
      body.innerHTML = `<p class="small muted">Read it once, slowly. See it happen: who does what, and what follows.</p><div class="law sp" id="law"><div class="text">${lawBody(F.ps, S.settings.hl, d, cid)}</div></div>
        <div class="row" style="margin-top:12px"><button class="btn primary" id="sptest">Hide it and test me</button></div><div id="sprv"></div>`;
      $('#sptest').onclick = () => {
        $('#sptest').remove();
        recallPanel($('#sprv'), d, p, cid, pct => {
          const tip = pct >= 90 ? 'Strong for a first try. <b>Good</b> brings it back in a few days.' : pct >= 60 ? 'Partly there. <b>Hard</b> brings it back tomorrow.' : 'Not yet, and that is normal on a first pass. <b>Again</b> brings it back within this sprint.';
          $('#sprv').insertAdjacentHTML('beforeend', rateRow(tip)); wireRate(); canRate = true;
        });
        const w = words(provText(p)).length; const b = $(`#sprv [data-m="${w <= 40 ? 'fr' : 'c1'}"]`); b && b.click();
      };
    } else {
      body.innerHTML = `<p class="small muted">Say it from memory, aloud or in your head, before you look. Getting it back is the workout, even when it is slow.</p>
        <div class="row"><button class="btn primary" id="spshow">Show the text <span class="kbd">space</span></button><button class="btn sm" id="sphint">Hint</button>${hook ? '<button class="btn sm" id="sphook">My picture</button>' : ''}<button class="btn sm ghost" id="sptype">Type it instead</button></div>
        <div id="spaux"></div><div id="spans"></div>`;
      const show = () => {
        if (canRate) return;
        $('#spans').innerHTML = `<div class="law sp" style="margin-top:12px"><div class="text">${lawBody(F.ps, S.settings.hl, d, cid)}</div></div>${rateRow()}${!hook && c0 && (c0.lapses || 0) >= 2 ? `<p class="tiny muted" style="margin-top:8px">Missed before. <a href="#/p/${cid}/${pid}">Give it a picture hook</a> on the study page.</p>` : ''}`;
        wireRate(); canRate = true; const sb = $('#spshow'); if (sb) sb.disabled = true;
      };
      $('#spshow').onclick = show;
      $('#sphint').onclick = () => { $('#spaux').innerHTML = `<p class="small hint">${esc(hint)}</p>`; };
      if (hook) $('#sphook').onclick = () => { $('#spaux').innerHTML = `<p class="small hint">Your picture: ${esc(hook)}</p>`; };
      $('#sptype').onclick = () => {
        $('#sptype').remove(); const box = document.createElement('div'); $('#spaux').replaceWith(box);
        const fake = document.createElement('div'); fake.id = 'law'; fake.hidden = true; box.appendChild(fake);
        recallPanel(box, d, p, cid, () => show());
        const b = $('[data-m="fr"]', box); b && b.click();
      };
    }
    document.onkeydown = e => {
      if (!location.hash.startsWith('#/sprint') || /input|textarea/i.test(e.target.tagName)) return;
      if (e.key === ' ' && !isNew) { e.preventDefault(); show2(); }
      if (canRate && /^[1-4]$/.test(e.key)) go(+e.key);
    };
    const show2 = () => { const b = $('#spshow'); if (b && !b.disabled) b.click(); };
  };
  step();
}

/* ---- drill: interleaved practice across chosen codes */
async function drillView(q) {
  setNav('drill');
  const pre = q.get('code');
  main.innerHTML = `<h1>Drill</h1><p class="muted">Interleaved practice. Mixing provisions from different chapters and codes is harder than studying them in order — and that difficulty is what builds durable recall.</p>
  <div class="grid" style="grid-template-columns:minmax(0,1fr) 300px;align-items:start" id="dgrid">
    <div class="card"><h3>Codes</h3><div class="grid g3" style="gap:6px">${CAT.codes.map(c => `<label class="small"><input type="checkbox" name="dc" value="${c.id}" ${pre ? (pre === c.id ? 'checked' : '') : (c.core ? 'checked' : '')}> ${esc(c.short)}</label>`).join('')}</div></div>
    <div class="card"><div class="field"><label>From</label><select id="dscope"><option value="seen">Provisions I have opened</option><option value="all">Anything in the chosen codes</option><option value="weak">My weak spots (lapses / hard)</option><option value="mark">My bookmarks</option></select></div>
      <div class="field"><label>Mode</label><select id="dmode"><option value="cite">Name that provision (text → citation)</option><option value="c2">Cloze</option><option value="fl">First letters</option><option value="fr">Write it out</option><option value="num">Numbers & periods</option></select></div>
      <div class="field"><label>How many</label><select id="dn"><option>10</option><option selected>20</option><option>40</option></select></div>
      <button class="btn primary" id="dgo">Start drill</button><p id="dmsg" class="small muted"></p></div></div>
  <div id="drun"></div>`;
  if (window.innerWidth < 900) $('#dgrid').style.gridTemplateColumns = '1fr';
  $('#dgo').onclick = async () => {
    const codes = $$('input[name=dc]:checked').map(i => i.value);
    if (!codes.length) return toast('Pick at least one code.');
    const scope = $('#dscope').value, mode = $('#dmode').value, n = +$('#dn').value;
    $('#dmsg').textContent = 'Loading…';
    const pool = [];
    for (const cid of codes) {
      const d = await loadCode(cid);
      for (const p of d.provisions) {
        const key = ck(cid, p.i); const c = S.cards[key];
        if (scope === 'seen' && !c) continue;
        if (scope === 'weak' && !(c && (c.lapses > 0 || (upgrade(c).d || 0) > 6.5 || (recallNow(c) ?? 1) < goal()))) continue;
        if (scope === 'mark' && !S.marks[key]) continue;
        const t = provText(p);
        if (words(t).length < 6) continue;
        if (mode === 'num' && !(t.match(RX.num) || []).some(x => /day|month|year|hour|per\s?cent|percent|pesos|₱|\d/.test(x))) continue;
        pool.push([cid, p]);
      }
    }
    if (!pool.length) { $('#dmsg').textContent = scope === 'seen' ? 'Nothing opened yet in those codes — choose “Anything in the chosen codes”.' : 'Nothing matches.'; return; }
    for (let k = pool.length - 1; k > 0; k--) { const j = Math.floor(Math.random() * (k + 1)); [pool[k], pool[j]] = [pool[j], pool[k]]; }
    $('#dmsg').textContent = '';
    runDrill(pool.slice(0, n), mode);
  };
}
async function runDrill(items, mode) {
  let i = 0, score = 0;
  const box = $('#drun'); box.scrollIntoView({ behavior: 'smooth' });
  const next = async () => {
    if (i >= items.length) { box.innerHTML = `<div class="card reviewcard" style="margin-top:16px"><h2>Drill finished</h2><p>${mode === 'cite' || mode === 'num' ? `Score: <b>${score}/${items.length}</b>.` : `${items.length} provisions practised.`} Weak ones are worth a Review rating — open them from the list below.</p><ul>${items.map(([c, p]) => `<li><a href="#/p/${c}/${p.i}">${esc(meta(c).short)} · ${esc(p.l)}</a></li>`).join('')}</ul></div>`; return; }
    const [cid, p] = items[i]; const d = await loadCode(cid);
    if (mode === 'cite') {
      const sibs = d.provisions.filter(x => x !== p && x.l !== p.l && words(provText(x)).length > 5);
      const opts = [p]; while (opts.length < 4 && sibs.length) { const x = sibs[Math.floor(Math.random() * sibs.length)]; if (!opts.includes(x)) opts.push(x); }
      opts.sort(() => Math.random() - .5);
      const t = provText(p); const shown = t.length > 700 ? t.slice(0, 680) + '…' : t;
      box.innerHTML = `<div class="card reviewcard" style="margin-top:16px"><div class="row small muted"><span>${i + 1}/${items.length} · ${esc(d.short)}</span><span class="spacer"></span><span>score ${score}</span></div><p class="prompt" style="font-size:1rem;font-weight:400;font-family:var(--serif)">${esc(shown)}</p><div class="grid" style="gap:8px">${opts.map((o, k) => `<button class="btn" data-k="${k}" style="justify-content:flex-start">${esc(o.l)}${o.c ? ' — ' + esc(o.c) : ''}</button>`).join('')}</div><p id="fb" class="small"></p></div>`;
      $$('[data-k]', box).forEach(b => b.onclick = () => {
        const o = opts[+b.dataset.k]; const good = o === p; if (good) score++;
        $$('[data-k]', box).forEach(x => { x.disabled = true; if (opts[+x.dataset.k] === p) x.style.borderColor = 'var(--ok)'; });
        if (!good) b.style.borderColor = 'var(--bad)';
        $('#fb').innerHTML = `${good ? '✓ Correct.' : `✗ It is <b>${esc(p.l)}</b>.`} <button class="btn sm" id="nx">Next</button>`;
        $('#nx').onclick = () => { i++; next(); };
      });
    } else if (mode === 'num') {
      const t = provText(p); const nums = (t.match(RX.num) || []).filter(x => /day|month|year|hour|per\s?cent|percent|pesos|₱|\d/.test(x));
      const target = nums[Math.floor(Math.random() * nums.length)];
      const idx = t.indexOf(target); const a = Math.max(0, idx - 260), b = Math.min(t.length, idx + target.length + 200);
      box.innerHTML = `<div class="card reviewcard" style="margin-top:16px"><div class="row small muted"><span>${i + 1}/${items.length} · ${esc(d.short)} · ${esc(p.l)}${p.c ? ' — ' + esc(p.c) : ''}</span><span class="spacer"></span><span>score ${score}</span></div><p style="font:1.05rem/1.8 var(--serif)">${a ? '… ' : ''}${esc(t.slice(a, idx))}<input id="na" size="${Math.max(6, target.length)}" style="border:0;border-bottom:2px dashed var(--brand);background:var(--brand-soft);font:inherit"> ${esc(t.slice(idx + target.length, b))}${b < t.length ? ' …' : ''}</p><button class="btn primary sm" id="nc">Check</button> <span id="fb" class="small"></span></div>`;
      $('#na').focus();
      const check = () => { const v = $('#na').value; const good = normWord(v).replace(/\s/g, '') === normWord(target).replace(/\s/g, '') || (v && target.toLowerCase().includes(v.toLowerCase()) && v.length >= target.length * .5); if (good) score++; $('#fb').innerHTML = `${good ? '✓' : '✗'} <b>${esc(target)}</b> <button class="btn sm" id="nx">Next</button>`; $('#nx').onclick = () => { i++; next(); }; };
      $('#nc').onclick = check; $('#na').onkeydown = e => { if (e.key === 'Enter') check(); };
    } else {
      box.innerHTML = `<div class="card reviewcard" style="margin-top:16px"><div class="row small muted"><span>${i + 1}/${items.length}</span><span class="spacer"></span><a href="#/p/${cid}/${p.i}">open</a></div><div class="prompt">${esc(d.short)} · ${esc(p.l)}${p.c ? ' — ' + esc(p.c) : ''}</div><div id="drv"></div><div class="row" style="margin-top:10px"><button class="btn primary sm" id="nx">Next</button></div></div>`;
      const rv = $('#drv'); const fake = document.createElement('div'); fake.id = 'law'; fake.hidden = true; rv.appendChild(fake);
      recallPanel(rv, d, p, cid);
      const btn = $(`[data-m="${mode}"]`, rv); btn && btn.click();
      $('#nx').onclick = () => { i++; next(); };
    }
  };
  next();
}

/* ---- search */
let searchT;
async function searchView(q) {
  setNav('search');
  const term = (q.get('q') || '').trim();
  $('#q').value = term;
  main.innerHTML = `<h1>Search</h1><form id="sf" class="row"><input id="sq" value="${esc(term)}" placeholder="Words or a phrase in quotes; Art. 1602; “equitable mortgage”" style="flex:1;padding:10px 14px;border-radius:12px;border:1px solid var(--line2);background:var(--card)"><select id="sc" style="padding:9px;border-radius:10px;border:1px solid var(--line2);background:var(--card)"><option value="">All codes</option>${CAT.codes.map(c => `<option value="${c.id}">${esc(c.short)}</option>`).join('')}</select><button class="btn primary">Search</button></form><div id="sr" style="margin-top:14px"></div>`;
  const run = async () => {
    const t = $('#sq').value.trim(); const only = $('#sc').value;
    if (!t) { $('#sr').innerHTML = '<p class="muted">Type at least one word.</p>'; return; }
    history.replaceState(null, '', '#/search?q=' + encodeURIComponent(t));
    const sr = $('#sr'); sr.innerHTML = '<p class="muted">Searching…</p>';
    const phrases = [...t.matchAll(/"([^"]+)"|“([^”]+)”/g)].map(m => (m[1] || m[2]).toLowerCase());
    const rest = t.replace(/"[^"]+"|“[^”]+”/g, ' ');
    const cite = rest.match(/\b(?:art(?:icle)?\.?|sec(?:tion)?\.?)\s*(\d+(?:-[a-z])?)/i);
    const terms = rest.replace(/\b(?:art(?:icle)?\.?|sec(?:tion)?\.?)\s*\d+(?:-[a-z])?/i, ' ').toLowerCase().split(/\s+/).filter(w => w.length > 1);
    const ids = only ? [only] : CAT.codes.map(c => c.id);
    const hits = [];
    let done = 0;
    for (const cid of ids) {
      const d = await loadCode(cid); done++;
      if (done % 10 === 0) sr.innerHTML = `<p class="muted">Searching… ${done}/${ids.length} codes</p>`;
      for (const p of d.provisions) {
        if (cite && String(p.n || '').toLowerCase() !== cite[1].toLowerCase()) continue;
        const txt = (p.l + ' ' + (p.c || '') + ' ' + provText(p)).toLowerCase();
        if (phrases.some(ph => !txt.includes(ph))) continue;
        if (terms.some(w => !txt.includes(w))) continue;
        let score = 0; for (const w of terms.concat(phrases)) { score += (txt.split(w).length - 1); if ((p.c || '').toLowerCase().includes(w)) score += 8; }
        if (meta(cid).core) score += 3;
        hits.push({ cid, p, score });
        if (hits.length > 2000) break;
      }
    }
    hits.sort((a, b) => b.score - a.score);
    const mark = s => { let h = esc(s); for (const w of terms.concat(phrases)) if (w.length > 2) h = h.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'), '<mark>$1</mark>'); return h; };
    const snip = p => { const t2 = provText(p); const low = t2.toLowerCase(); const w = (phrases[0] || terms[0] || ''); const k = w ? low.indexOf(w) : 0; const a = Math.max(0, k - 90); return (a ? '…' : '') + t2.slice(a, a + 260) + (t2.length > a + 260 ? '…' : ''); };
    const ch = await caseHits(terms.concat(phrases), only);
    sr.innerHTML = (ch.length ? `<div class="card flat" style="margin-bottom:12px"><h3 style="margin:0 0 6px">Cases named “${esc(t)}” (${ch.length})</h3><ul class="small" style="margin:0;padding-left:1.1em">${ch.slice(0, 60).map(x => `<li><span style="font-family:var(--serif)">${mark(x.n)}</span>${x.c ? `, <span class="muted">${esc(x.c)}</span>` : ''} <span class="tiny muted">${esc(x.src)}</span> → ${x.ks.slice(0, 6).map(k => { const [c, p] = k.split('|'); const pr = CODES[c] && CODES[c].byId[p]; return `<a class="chip blue" href="#/p/${c}/${p}">${esc((meta(c) || {}).short || c)} ${esc(pr ? pr.l : p)}</a>`; }).join(' ')}</li>`).join('')}</ul></div>` : '') + `<p class="small muted">${hits.length.toLocaleString()} provision${hits.length === 1 ? '' : 's'}${hits.length > 150 ? ' · showing 150' : ''}</p><ol class="results" style="padding-left:1.2em">${hits.slice(0, 150).map(h => `<li><a href="#/p/${h.cid}/${h.p.i}"><b>${esc(meta(h.cid).short)} · ${esc(h.p.l)}</b>${h.p.c ? ' — ' + mark(h.p.c) : ''}</a><div class="small" style="font-family:var(--serif)">${mark(snip(h.p))}</div></li>`).join('')}</ol>`;
  };
  $('#sf').onsubmit = e => { e.preventDefault(); run(); return false; };
  if (term) run();
}

async function caseHits(ws, only) {
  ws = ws.filter(w => w.length > 2 && !/^(the|and|people|of|vs?)$/.test(w));
  if (!ws.length) return [];
  await Promise.all([loadSylIndex(), loadRecent(), ...CAT.codes.filter(c => (c.cases || c.notes) && (!only || c.id === only)).map(c => loadExtras(c.id).catch(() => 0))]);
  const out = new Map();
  const put = (k, n, c, src) => { if (only && !k.startsWith(only + '|')) return; const low = n.toLowerCase(); if (!ws.every(w => low.includes(w))) return; const id = low.replace(/\W+/g, '') + '|' + String(c || '').replace(/\D+/g, '').slice(0, 6); if (!out.has(id)) out.set(id, { n, c, src, ks: [] }); const o = out.get(id); if (!o.ks.includes(k)) o.ks.push(k); if (!o.src.includes(src)) o.src += ' · ' + src; };
  for (const [k, arr] of Object.entries(SYX)) arr.forEach(x => put(k, x.n, x.c, 'syllabus'));
  for (const [k, arr] of Object.entries(REC.by)) arr.forEach(x => put(k, x.n, [x.g, x.d].filter(Boolean).join(', '), 'recent'));
  for (const [cid, idx] of Object.entries(CASES)) for (const [pid, arr] of Object.entries(idx || {})) (arr || []).forEach(x => put(cid + '|' + pid, x.n, x.c, 'textbook'));
  for (const [cid, idx] of Object.entries(NOTES)) for (const [pid, g] of Object.entries(idx || {})) ((g || {}).d || []).forEach(x => put(cid + '|' + pid, x.n, x.c, 'digest'));
  const need = [...new Set([...out.values()].flatMap(o => o.ks.map(k => k.split('|')[0])))];
  await Promise.all(need.map(c => loadCode(c).catch(() => 0)));
  return [...out.values()].sort((a, b) => b.ks.length - a.ks.length);
}

/* ---- progress */
function memoryCard() {
  const m = memoryStats();
  if (!m.n) return `<div class="card" style="margin-top:14px"><h3>Your memory</h3><p class="small muted">Rate a provision after you recall it and this card starts tracking how well you would remember each one today, what is slipping and what falls due.</p></div>`;
  const mx = Math.max(1, ...m.fc);
  const day = k => k === 0 ? 'today' : k === 1 ? 'tmrw' : new Date(Date.now() + k * DAY).toLocaleDateString([], { weekday: 'short' });
  return `<div class="card" style="margin-top:14px"><h3>Your memory</h3>
    <div class="grid g3"><div><div class="stat">${Math.round(m.avg * 100)}%</div><div class="small muted">average recall right now, across ${m.n.toLocaleString()} provision${m.n === 1 ? '' : 's'}</div></div>
      <div><div class="stat">${m.risk}</div><div class="small muted">below your ${Math.round(goal() * 100)}% target</div></div>
      <div><div class="stat">${m.leeches.length}</div><div class="small muted">stubborn (forgotten ${LEECH}+ times)</div></div></div>
    <p class="small" style="margin:14px 0 6px"><b>Coming due, next 14 days</b></p>
    <div class="fc" role="img" aria-label="Provisions falling due each day for the next 14 days">${m.fc.map((n, k) => `<div class="fcb" title="${day(k)}: ${n}"><span class="fcn">${n || ''}</span><i style="height:${Math.round(n / mx * 100)}%"></i><span class="fcd">${day(k)}</span></div>`).join('')}</div>
    ${m.leeches.length ? `<p class="small" style="margin:14px 0 4px"><b>Stubborn provisions.</b> Rereading will not fix these. Give each one a vivid picture hook and take it apart again.</p><ul class="small">${m.leeches.slice(0, 20).map(k => { const [c, p] = k.split('|'); const cc = S.cards[k]; return `<li><a href="#/p/${c}/${p}">${esc((meta(c) || {}).short || c)} · ${esc(CODES[c] && CODES[c].byId[p] ? CODES[c].byId[p].l : p.replace(/-/g, ' '))}</a> <span class="muted">· forgotten ${cc.lapses}×${S.hooks[k] ? ' · has a picture' : ''}</span></li>`; }).join('')}</ul>` : ''}
    <p class="tiny muted" style="margin:10px 0 0">Recall is estimated by the FSRS memory model from your own ratings. It is a forecast, not a grade: rate honestly and it gets better.</p></div>`;
}
function progressView() {
  setNav('progress');
  const rows = CAT.codes.map(c => ({ c, k: counts(c.id) })).filter(r => r.k.touched || r.c.core);
  const tot = rows.reduce((a, r) => ({ t: a.t + r.k.touched, m: a.m + r.k.m }), { t: 0, m: 0 });
  const days = []; for (let k = 83; k >= 0; k--) { const d = new Date(Date.now() - k * DAY); const key = new Date(d - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); const v = S.days[key]; const n = v ? v.r + v.n : 0; days.push(`<i class="${n > 40 ? 'm' : n > 15 ? 'l' : n ? 's' : ''}" title="${key}: ${n}"></i>`); }
  const flags = Object.entries(S.flags);
  main.innerHTML = `<h1>Progress</h1>
  <div class="grid g3"><div class="card"><div class="stat">${tot.t.toLocaleString()}</div><div class="small muted">provisions opened of ${CAT.total.toLocaleString()}</div></div><div class="card"><div class="stat">${tot.m.toLocaleString()}</div><div class="small muted">mastered (interval ≥ 21 days)</div></div><div class="card"><div class="stat">${dueKeys().length}</div><div class="small muted">due now</div></div></div>
  ${memoryCard()}
  <div class="card" style="margin-top:14px"><h3>Last 12 weeks</h3><div class="heat">${days.join('')}</div></div>
  ${calibration()}
  <div class="card" style="margin-top:14px;overflow-x:auto"><table class="table"><tr><th>Code</th><th>Opened</th><th>Learning</th><th>Mastered</th><th style="width:30%">Coverage</th></tr>${rows.map(r => `<tr><td><a href="#/code/${r.c.id}">${esc(r.c.short)}</a></td><td>${r.k.touched}/${r.k.total}</td><td>${r.k.l}</td><td>${r.k.m}</td><td>${bar(r.k)}</td></tr>`).join('')}</table></div>
  <div class="card" style="margin-top:14px"><h3>Settings</h3><div class="row" style="gap:18px"><label class="small">New provisions per day <input id="npd" type="number" min="0" max="200" value="${S.settings.newPerDay}" style="width:70px;padding:5px;border-radius:8px;border:1px solid var(--line2);background:var(--card)"></label>
    <label class="small">Sprint length <select id="spl" style="padding:5px;border-radius:8px;border:1px solid var(--line2);background:var(--card)">${[3, 5, 10, 15].map(m => `<option value="${m}" ${(S.settings.sprint || 5) === m ? 'selected' : ''}>${m} minutes</option>`).join('')}</select></label>
    <label class="small">Keep my recall at <select id="ret" style="padding:5px;border-radius:8px;border:1px solid var(--line2);background:var(--card)">${[[0.85, '85% · fewer reviews'], [0.9, '90% · recommended'], [0.95, '95% · exam is near']].map(([v, t]) => `<option value="${v}" ${goal() === v ? 'selected' : ''}>${t}</option>`).join('')}</select></label></div>
    <p class="tiny muted" style="margin:8px 0 0">A higher target brings provisions back sooner: about twice as many reviews at 95% as at 90%. Changing it applies from each provision’s next review.</p></div>
  <div class="card" style="margin-top:14px"><h3>Back up & move</h3><p class="small muted">Progress lives in this browser only. GitHub Pages and Cloudflare are different addresses, so each keeps its own progress — back up here, restore there.</p>
    <div class="row"><button class="btn" id="exp">Back up my work</button><label class="btn">Restore from a file<input type="file" id="imp" accept="application/json" hidden></label><button class="btn" id="paste">Restore by pasting</button><button class="btn ghost" id="off">Make every code available offline</button><button class="btn ghost" id="rst" style="color:var(--bad)">Reset</button></div><p id="offmsg" class="small muted"></p></div>
  ${flags.length ? `<div class="card" style="margin-top:14px"><h3>Text errors you reported (${flags.length})</h3><ul class="small">${flags.map(([k, f]) => { const [c, p] = k.split('|'); return `<li><a href="#/p/${c}/${p}">${esc(f.l)}</a>: ${esc(f.t)}</li>`; }).join('')}</ul><button class="btn sm" id="expf">Download the error report</button></div>` : ''}`;
  $('#npd').onchange = e => { S.settings.newPerDay = Math.max(0, +e.target.value || 0); save(); };
  $('#spl').onchange = e => { S.settings.sprint = +e.target.value; save(); };
  $('#ret').onchange = e => { S.settings.retention = +e.target.value; save(); toast('Target saved. It applies from each provision’s next review.'); };
  $('#exp').onclick = () => dl(`sinag-backup-${today()}.json`, JSON.stringify({ app: 'sinag-codal', v: 1, at: new Date().toISOString(), data: S }));
  $('#imp').onchange = async e => {
    const f = e.target.files[0]; if (!f) return;
    try { const j = JSON.parse(await f.text()); if (j.app !== 'sinag-codal') throw new Error('Not a Sinag Codal backup.'); if (!(await askYes('Merge this backup into the progress on this device? Newer card reviews win.', 'Merge'))) return; merge(j.data); save(); toast('Backup restored.'); progressView(); }
    catch (err) { toast(String(err.message || err)); }
  };
  $('#rst').onclick = async () => { if (await askYes('Erase all progress, notes and bookmarks on this device?', 'Erase') && await askYes('Really erase? This cannot be undone without a backup.', 'Erase everything')) { S = structuredClone(DEFAULTS); save(); progressView(); } };
  $('#paste').onclick = async () => {
    const t = await askText('Paste a backup', '', 'Paste the backup text you copied earlier');
    if (!t) return;
    try { const j = JSON.parse(t); if (j.app !== 'sinag-codal') throw new Error('Not a Sinag Codal backup.'); merge(j.data); save(); toast('Backup restored.'); progressView(); } catch (err) { toast(String(err.message || err)); }
  };
  $('#off').onclick = async () => { let n = 0; for (const c of CAT.codes) { await loadCode(c.id).catch(() => 0); await loadExtras(c.id).catch(() => 0); $('#offmsg').textContent = `Saved ${++n}/${CAT.codes.length}…`; } $('#offmsg').textContent = 'Every code is stored for offline use.'; };
  const ef = $('#expf'); if (ef) ef.onclick = () => dl(`sinag-text-errors-${today()}.json`, JSON.stringify(flags.map(([k, f]) => ({ provision: f.l, key: k, report: f.t, at: new Date(f.at).toISOString() })), null, 1));
}
function merge(o) {
  for (const [k, c] of Object.entries(o.cards || {})) if (!S.cards[k] || (c.last || 0) > (S.cards[k].last || 0)) S.cards[k] = c;
  for (const f of ['notes', 'marks', 'flags', 'tutor', 'hooks', 'lessons', 'lastBy', 'b2']) Object.assign(S[f], o[f] || {});
  for (const [d, v] of Object.entries(o.days || {})) { const a = S.days[d] || { r: 0, n: 0 }; S.days[d] = { r: Math.max(a.r, v.r), n: Math.max(a.n, v.n) }; }
}
function dl(name, text) {
  const m = modal(`<h3>${esc(name)}</h3><p class="small muted">Copy this text and keep it somewhere safe (a note, an email to yourself). To restore, use <b>Restore by pasting</b>. Or try the file download.</p><textarea id="mtxt" rows="8" readonly>${esc(text)}</textarea><div class="row" style="margin-top:10px;justify-content:flex-end"><button class="btn" id="mdl">Download file</button><button class="btn primary" id="mcp">Copy</button><button class="btn" id="mno">Close</button></div>`);
  $('#mno', m.el).onclick = m.close;
  $('#mcp', m.el).onclick = async () => { const t = $('#mtxt', m.el); try { await navigator.clipboard.writeText(text); toast('Copied.'); } catch (e) { t.focus(); t.select(); try { document.execCommand('copy'); toast('Copied.'); } catch (e2) { toast('Select the text and copy it.'); } } };
  $('#mdl', m.el).onclick = () => { try { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); } catch (e) { toast('Downloads are blocked here — use Copy.'); } };
}

/* ---- Book Two Studio */
const B2TABS = [['elements', 'Elements'], ['compare', 'Compare'], ['sort', 'Sort it'], ['practice', 'Practice'], ['cases', 'Cases']];
const b2crumbs = extra => `<div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><a href="#/field/crim">Criminal Law</a><span class="sep">›</span>${extra ? `<a href="#/b2">Book Two Studio</a><span class="sep">›</span><span>${esc(extra)}</span>` : '<span>Book Two Studio</span>'}</div>`;
const b2score = id => { const r = S.b2[id]; return r && r.n ? `${r.r}/${r.n} right last time` : 'Not practised yet'; };
async function b2View(id, q) {
  setNav('library');
  await loadB2();
  if (!id) {
    const M = B2.method;
    main.innerHTML = `<div class="f-crim">${b2crumbs()}
    <span class="eyebrow" style="color:var(--f)">Criminal Law · Revised Penal Code, Book Two</span><h1>Book Two Studio</h1><p class="lead">${esc(M.lead)}</p>
    <div class="sect"><h2>The method</h2></div>
    <ol class="method">${M.steps.map(st => `<li><b>${esc(st.h)}</b><span>${esc(st.p)}</span>${st.refs ? `<span class="row" style="gap:6px;margin-top:4px">${st.refs.map(r => `<a class="pref" href="#/p/${r.c}/${r.i}">${esc(r.l)}</a>`).join('')}</span>` : ''}</li>`).join('')}</ol>
    <div class="sect"><h2>A week per family</h2></div>
    <div class="weekgrid">${M.week.map(([d, t]) => `<div><b>${esc(d)}</b><span>${esc(t)}</span></div>`).join('')}</div>
    <div class="sect"><h2>The families</h2><span class="spacer"></span><a class="btn sm" href="#/b2/mix">Mixed drill across all families</a></div>
    <div class="tiles">${B2.families.map((f, i) => `<a class="tile f-crim" href="#/b2/${f.id}"><span class="p">${i + 1} · ${esc(f.module)}</span><span class="t">${esc(f.title)}</span><span class="q">${esc(f.q)}</span><span class="go"><b>${f.crimes.length}</b> crimes · <b>${f.drills.length}</b> drills · ${esc(b2score(f.id))}</span></a>`).join('')}</div></div>`;
    return;
  }
  if (id === 'mix') return b2Drill(null);
  const f = B2.families.find(x => x.id === id); if (!f) return b2View(null, q);
  const tab = q.get('tab') || 'elements';
  const ordered = [f.crimes.find(c => c.id === f.base), ...f.crimes.filter(c => c.id !== f.base)];
  let body = '';
  if (tab === 'elements') body = `<p class="howto">Learn the base crime first. Then read each neighbour for one thing only: the element under <b>Sets it apart</b>. That element is what the examiner is testing.</p>` + ordered.map(c => crimeHTML(c, f)).join('');
  if (tab === 'compare') body = `<div class="row" style="margin-bottom:8px"><p class="small muted" style="margin:0;flex:1">Cover the table and recite one row across every crime, then check. Tap a hidden cell to reveal it.</p><button class="btn sm" id="hide">Hide the answers</button></div>
    <div class="mxwrap"><table class="mx"><thead><tr><th></th>${ordered.map((c, j) => `<th class="${j ? '' : 'b'}">${j ? '' : '<small>Base</small>'}<a href="#/b2/${f.id}?tab=elements#c-${c.id}">${esc(c.name)}</a></th>`).join('')}</tr></thead><tbody>${f.rows.map((r, i) => `<tr class="${/makes it this crime|sets it apart|decisive/i.test(r) ? 'key' : /^penalty/i.test(r) ? 'pen' : ''}"><th>${esc(r)}</th>${ordered.map((c, j) => `<td class="${j ? '' : 'b'}">${esc(f.table[c.id][i])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
    <p class="tiny muted" style="margin-top:8px">The tinted row is the decisive one: if you can say it for every column, you can tell these crimes apart.</p>`;
  if (tab === 'sort') body = `<p class="howto">Ask these questions in order, top to bottom. The first “yes” names the crime.</p><ol class="ladder">${f.path.map(([qq, a]) => `<li><span class="lq">${esc(qq)}</span><span class="la">${ansHTML(a)}</span></li>`).join('')}</ol>
    <span class="dl warnh" style="margin-top:22px">Traps examiners set</span><ul class="traps">${f.traps.map(t => `<li>${esc(t)}</li>`).join('')}</ul>`;
  if (tab === 'cases') body = `<p class="small muted">Tie each distinction to a decided case. Cases marked as assigned are from your syllabus; read them for the holding.</p>` + f.cases.map(([n, c, w]) => `<div class="case"><div class="cn">${esc(n)}</div><div class="cc">${esc(c)}</div><div class="dg"><div class="d-w"><b>The distinction it settles</b>${esc(w)}</div></div></div>`).join('');
  main.innerHTML = `<div class="f-crim">${b2crumbs(f.title)}<span class="eyebrow" style="color:var(--f)">${esc(f.module)}</span><h1>${esc(f.title)}</h1><p class="lead">${esc(f.q)}</p>
    <div class="steps b2tabs" role="tablist">${B2TABS.map(([k, n], i) => `<button role="tab" data-t="${k}" class="${k === tab ? 'on' : ''}"><small>${i + 1}</small><span>${n}</span></button>`).join('')}</div>
    <div id="b2body">${tab === 'practice' ? '' : body}</div>
    <div class="pn"><a class="btn" href="#/b2">All families</a>${(() => { const i = B2.families.indexOf(f); const nx = B2.families[i + 1]; return nx ? `<a class="btn primary" href="#/b2/${nx.id}">Next family: ${esc(nx.title)} →</a>` : `<a class="btn primary" href="#/b2/mix">Mixed drill →</a>`; })()}</div></div>`;
  $$('.b2tabs button').forEach(b => b.onclick = () => { location.hash = `#/b2/${f.id}?tab=${b.dataset.t}`; });
  if (tab === 'practice') b2Drill(f, $('#b2body'));
  if (tab === 'compare') { const hb = $('#hide'); hb.onclick = () => { const on = !$('.mx').classList.contains('cover'); $('.mx').classList.toggle('cover', on); $$('.mx td').forEach(td => td.classList.toggle('shut', on)); hb.textContent = on ? 'Show all' : 'Hide the answers'; }; $('.mx').addEventListener('click', e => { const td = e.target.closest('td.shut'); if (td) td.classList.remove('shut'); }); }
  const anchor = location.hash.split('#')[2]; if (anchor) { const el = document.getElementById(anchor); el && el.scrollIntoView({ block: 'start' }); }
}
function ansHTML(a) { const m = /^([A-Z][^(.;:]{1,60}?)(?=\s*\(Arts?\.|\.)/.exec(a); return m ? `<b>${esc(m[1])}</b>${esc(a.slice(m[1].length))}` : esc(a); }
function b2Drill(f, box) {
  const pool = (f ? f.drills.map(d => ({ d, f })) : B2.families.flatMap(ff => ff.drills.map(d => ({ d, f: ff })))).slice();
  for (let k = pool.length - 1; k > 0; k--) { const j = Math.floor(Math.random() * (k + 1)); [pool[k], pool[j]] = [pool[j], pool[k]]; }
  const items = f ? pool : pool.slice(0, 12);
  let i = 0, right = 0;
  if (!box) { setNav('library'); main.innerHTML = `<div class="f-crim">${b2crumbs('Mixed drill')}<span class="eyebrow" style="color:var(--f)">Interleaved practice</span><h1>Mixed drill</h1><p class="lead">Twelve sets of facts drawn from every family. Name the crime and its decisive element before you choose.</p><div id="b2body"></div></div>`; box = $('#b2body'); }
  const crimeOf = id => { for (const ff of B2.families) { const c = ff.crimes.find(x => x.id === id); if (c) return { c, ff }; } return null; };
  const step = () => {
    if (i >= items.length) {
      if (f) { S.b2[f.id] = { r: right, n: items.length, at: Date.now() }; save(); }
      box.innerHTML = `<div class="drill done"><h2>${right} of ${items.length} right</h2><p class="muted">${right === items.length ? 'Every distinction held. Come back in a few days and do it mixed.' : 'Write the decisive element of each miss under My notes on its article, then try again tomorrow.'}</p><div class="row"><button class="btn primary" id="again">Shuffle and try again</button>${f ? `<a class="btn" href="#/b2/${f.id}?tab=compare">Review the table</a>` : '<a class="btn" href="#/b2">All families</a>'}</div></div>`;
      $('#again').onclick = () => b2Drill(f, f ? box : null); return;
    }
    const { d, f: ff } = items[i]; const opts = d.o.slice().sort(() => Math.random() - .5);
    box.innerHTML = `<div class="drill"><div class="row small muted"><span>${i + 1} of ${items.length}</span><span class="spacer"></span>${f ? '' : `<span>${esc(ff.title)}</span>`}</div>
      <p class="facts">${esc(d.f)}</p><p class="small muted" style="margin:0 0 8px">What crime is it?</p>
      <div class="opts">${opts.map(o => `<button class="opt" data-o="${o}">${esc(B2.names[o] || o)}</button>`).join('')}</div><div id="why"></div></div>`;
    $$('.opt', box).forEach(b => b.onclick = () => {
      if ($('.opt.picked', box)) return;
      const ok = b.dataset.o === d.a; if (ok) right++;
      b.classList.add('picked'); $$('.opt', box).forEach(x => { x.disabled = true; if (x.dataset.o === d.a) x.classList.add('right'); else if (x === b) x.classList.add('wrong'); });
      const cc = crimeOf(d.a);
      $('#why', box).innerHTML = `<div class="note ${ok ? '' : 'bad'}" style="margin-top:12px"><b>${ok ? 'Right.' : `It is ${esc(B2.names[d.a])}.`}</b> ${esc(d.w)}${cc ? `<br><span class="small"><b>Decisive element:</b> ${esc(cc.c.key)}</span><br><span class="row" style="gap:6px;margin-top:6px">${cc.c.refs.map(r => `<a class="pref" href="#/p/${r.c}/${r.i}">${esc(r.l)}</a>`).join('')}</span>` : ''}</div><button class="btn primary" id="nx" style="margin-top:10px">${i + 1 < items.length ? 'Next facts' : 'See my score'}</button>`;
      $('#nx', box).onclick = () => { i++; step(); };
    });
  };
  step();
}

/* ---- syllabus */
async function syllabusView(id, q) {
  setNav('syllabus');
  const [sy, rc] = await Promise.all([loadSyllabus(), loadRecent()]);
  if (!id) {
    const nrec = new Set(Object.values(rc.by).flat().map(r => r.n + r.g)).size;
    main.innerHTML = `<h1>Syllabus</h1><p class="muted">Your law-school syllabi, with every case filed under the provision it is taught with. Open a provision’s <b>Cases</b> tab to see them beside the text.</p>
    <div class="grid g3">${sy.courses.map(c => { const cs = c.items.filter(i => i.t === 'c'); const f = cs.filter(i => (i.links || []).some(l => l.i)).length; return `<a class="card codecard" href="#/syllabus/${c.id}"><span class="t">${esc(c.title)}</span>${c.teacher ? `<span class="c">${esc(c.teacher)}</span>` : ''}<span class="small muted">${cs.length} cases · ${f} filed under a provision</span></a>`; }).join('')}
    <a class="card codecard" href="#/syllabus/recent"><span class="t">Recent jurisprudence, 2023–2026</span><span class="c">checked ${esc(rc.checked || '')}</span><span class="small muted">${nrec} rulings filed under the provisions they apply</span></a></div>`;
    return;
  }
  if (id === 'recent') {
    const rows = [];
    for (const [k, arr] of Object.entries(rc.by)) for (const r of arr) rows.push([k, r]);
    const seen = new Map();
    rows.forEach(([k, r]) => { const key = r.n + '|' + r.g; if (!seen.has(key)) seen.set(key, { r, ks: [] }); seen.get(key).ks.push(k); });
    const items = [...seen.values()];
    await Promise.all([...new Set(items.flatMap(x => x.ks.map(k => k.split('|')[0])))].map(c => loadCode(c).catch(() => 0)));
    const lab = k => { const [c, p] = k.split('|'); const d = CODES[c]; const pr = d && d.byId[p]; return `<a class="chip blue" href="#/p/${c}/${p}">${esc((meta(c) || {}).short || c)} ${esc(pr ? pr.l : p)}</a>`; };
    const bySubj = {};
    items.forEach(x => { const s = CUR.homes[x.ks[0].split('|')[0]] || 'pol'; (bySubj[s] = bySubj[s] || []).push(x); });
    main.innerHTML = `<p class="small"><a href="#/syllabus">← Syllabus</a></p><h1>Recent jurisprudence, 2023–2026</h1>
    <p class="muted">Each ruling is filed under every provision it applies; tap a provision to study it with the text. <span class="chip ok">verified: decision</span> means the docket number and date were checked against the decision or an official listing. <span class="chip warn">verified: SC release / news</span> means the ruling was confirmed from a Supreme Court release or a news report — read the full text before you cite it.</p>
    ${CUR.fields.filter(s => bySubj[s.id]).map(s => `<div class="sect"><h2>${esc(s.name)}</h2></div>${recentHTML(bySubj[s.id].map(x => x.r).map((r, i) => Object.assign({}, r, { _ks: bySubj[s.id][i].ks })), r => `<div><b>Filed under</b>${r._ks.map(lab).join(' ')}</div>`)}`).join('')}
    ${(rc.general || []).length ? `<div class="sect"><h2>Rules of conduct (not in the codal library)</h2></div><ul class="explain">${rc.general.map(g => `<li>${esc(g.x)}${g.u ? ` <a class="small" href="${esc(g.u)}" target="_blank" rel="noopener">text</a>` : ''}</li>`).join('')}</ul>` : ''}`;
    return;
  }
  const c = sy.courses.find(x => x.id === id);
  if (!c) { main.innerHTML = '<div class="empty">That syllabus is not here. <a href="#/syllabus">All syllabi</a></div>'; return; }
  const need = [...new Set(c.items.flatMap(i => (i.links || []).map(l => l.c)))];
  await Promise.all(need.map(x => loadCode(x).catch(() => 0)));
  const lab = l => { const d = CODES[l.c]; const pr = d && l.i && d.byId[l.i]; return l.i ? `<a class="chip blue" href="#/p/${l.c}/${l.i}">${esc((meta(l.c) || {}).short || l.c)} ${esc(pr ? pr.l : (l.l || ''))}</a>` : ''; };
  const only = q.get('only') === 'cases';
  const term = (q.get('q') || '').trim().toLowerCase();
  const upd = id === 'ethics' && (rc.general || []).length ? `<div class="note blue" style="margin:10px 0"><b>Updates since this syllabus was written</b><ul style="margin:6px 0 0;padding-left:1.2em">${rc.general.filter(g => g.k === 'ethics').map(g => `<li>${esc(g.x)}${g.u ? ` <a href="${esc(g.u)}" target="_blank" rel="noopener">text</a>` : ''}</li>`).join('')}</ul></div>` : '';
  let n = 0;
  const body = c.items.map(it => {
    if (term && !(((it.n || '') + ' ' + (it.c || '') + ' ' + (it.x || '') + ' ' + (it.topic || '')).toLowerCase().includes(term))) return '';
    if (it.t === 'h') return only ? '' : `<div class="sy-h l${it.lvl || 0}">${esc(it.x)}${(it.links || []).length ? ' ' + it.links.map(lab).join(' ') : ''}${it.q ? `<div class="sy-q">${esc(it.q)}</div>` : ''}</div>`;
    if (it.t === 'c') { n++; return `<div class="sy-c"><span class="cn">${esc(it.n)}</span>${it.c ? `<span class="muted small">, ${esc(it.c)}</span>` : ''}${it.note ? ` <span class="small muted">— ${esc(it.note)}</span>` : ''}<div>${(it.links || []).map(lab).join(' ') || '<span class="tiny muted">not tied to a provision in the library</span>'}</div></div>`; }
    return only ? '' : `<div class="sy-n small">${esc(it.x)} ${(it.links || []).map(lab).join(' ')}</div>`;
  }).join('');
  main.innerHTML = `<p class="small"><a href="#/syllabus">← Syllabus</a></p><h1>${esc(c.title)}</h1>${c.teacher ? `<p class="muted">${esc(c.teacher)}</p>` : ''}${upd}
  <form id="syf" class="row" style="margin:10px 0"><input id="syq" value="${esc(q.get('q') || '')}" placeholder="Find a case or topic in this syllabus" style="flex:1;min-width:180px;padding:9px 12px;border-radius:10px;border:1px solid var(--line2);background:var(--card)"><label class="small"><input type="checkbox" id="syo" ${only ? 'checked' : ''}> cases only</label><button class="btn">Find</button></form>
  <p class="tiny muted">${n} case${n === 1 ? '' : 's'} shown. Blue chips open the provision the case is filed under. Cases filed only by their outline section (no codal reference in the syllabus line) say so on the provision page.</p>
  <div class="sy">${body || '<div class="empty">Nothing matches.</div>'}</div>`;
  $('#syf').onsubmit = e => { e.preventDefault(); const p = new URLSearchParams(); if ($('#syq').value.trim()) p.set('q', $('#syq').value.trim()); if ($('#syo').checked) p.set('only', 'cases'); location.hash = `#/syllabus/${id}` + (p.toString() ? '?' + p : ''); };
}

/* ---- about */
async function aboutView() {
  setNav('about');
  let pr = null; try { pr = await getJSON('data/proofreading.json?v=' + CAT.built); } catch (e) {}
  main.innerHTML = `<div style="max-width:820px"><h1>About Sinag · Codal Studio</h1>
  <p>The codal provision is the backbone. Everything else — explanations, cases, drills — hangs on the verbatim text.</p>
  <h2>How this is designed</h2>
  <ol class="explain"><li><b>One next step.</b> Today shows a single thing to do. New provisions are capped at a small number a day; you can change it under Progress.</li>
  <li><b>Short sprints for a short attention span.</b> A sprint lasts five minutes (three to fifteen, your choice), shows one provision at a time and hides everything else on the screen. The provisions you are closest to forgetting come first. A new one is read once and tested at once. One you miss comes back three cards later, in the same sprint, until you get it. Time away from the tab does not count, and each sprint ends with a five-minute break.</li>
  <li><b>One map, from the whole to the part.</b> The Map shows all of law school at once, with eight fields, and lets you zoom in: a field, then its codes, then a code’s Books and Titles, then chapters, then single provisions. Each level shows the same bar. <b>Locked in</b> means the memory model predicts you will still recall that provision three weeks from now (stability of 21 days or more) and your recall today is at or above your target. A part is locked in when every provision under it is. <b>Slipping</b> means recall today has dropped below your target. From any level you can start a sprint on that part alone, so you lock in a chapter before moving on to the next one.</li>
  <li><b>A memory model, not a fixed timetable.</b> Every rating updates an estimate of how well you would recall that provision today (the FSRS model). Each provision comes back on the day your recall would fall to your target, 90% by default. Under Progress you can see your average recall, what is slipping, what falls due over the next two weeks, and which provisions keep slipping. Those need a new picture, not more rereading.</li>
  <li><b>Eight fields in one building.</b> The House of Law is a memory palace drawn after the Supreme Court’s building on Padre Faura, Manila: its four columns, three doors and seven marble steps, with the Court’s motto, <i>Batas at Bayan</i>, carved above. Each field has a fixed place in it, from the pediment down to the steps, and each topic inside a field is one object at that place. Fixed places give you somewhere to look when you forget.</li>
  <li><b>A short path in each field.</b> Start here, then the core, then deeper only when you need it. A code page offers five provisions at a time.</li>
  <li><b>Four steps on each provision.</b> Read the verbatim text. Understand it by taking it apart and making your own picture. Recall it with the text hidden. Connect it to cases. Then rate yourself, and Review brings it back just before you would forget it.</li>
  <li><b>The law in force comes first.</b> Where a later law restated a provision, the amended text is what you read, take apart and recall; the text as enacted and the amending law, verbatim, sit under “How the text read before”. Repealed or superseded provisions are marked, so you do not memorize dead law.</li>
  <li><b>See how it evolved.</b> Each provision shows its history in order: where the text came from (for the Civil Code, the article of the Spanish Civil Code of 1889 that its source note names), every amending law with its year, the rules and issuances that implement it, and the decisions that interpreted it — ending with the text in force today. Older cases and many examination questions were decided under the older layers.</li>
  <li><b>Read it like a judge.</b> “Take it apart” sorts each sentence into the order a court reads a provision: the words it defines, the rule, what it lists, when it applies, what is qualified or carved out, and what follows. Each step carries the canon of construction that governs it: plain meaning (<i>verba legis</i>), a list excludes what it omits (<i>expressio unius</i>), exceptions and provisos read strictly, and penal laws read strictly against the State.</li></ol>
  <h2>The memory research behind it</h2>
  <ul class="explain small"><li><b>Places and pictures.</b> Tying items to fixed locations in an imagined building (the method of loci, the memory palace) reliably improves recall, including in people with no prior training (Dresler and others, <i>Neuron</i>, 2017). Pictures are remembered better than words alone, and words paired with an image are stored twice (Paivio’s dual coding; Shepard, 1967; Standing, 1973).</li>
  <li><b>Small groups.</b> Working memory holds only a few chunks at a time (Miller, 1956, written at Harvard; Cowan, 2001, puts it near four), which is why fields, paths and sittings are kept short.</li>
  <li><b>Make it yourself.</b> Material you generate is remembered better than material you only read (Slamecka and Graf, 1978), so the app asks for your own picture and your own words.</li>
  <li><b>Forgetting is predictable.</b> Memory for new material falls off steeply at first and then levels out (Ebbinghaus, 1885). Each successful recall makes the next fall slower. The scheduler is FSRS, a model of this curve fitted on a very large set of real reviews (Ye, Su and Cao, KDD 2022). It times each review for the point where recall would drop to your target, so effort goes where forgetting is about to happen.</li>
  <li><b>Relearn until it sticks, then space it.</b> Recalling an item correctly within a session, then again across several sessions, gives large and lasting gains: successive relearning (Rawson, Dunlosky and Sciartelli, 2013).</li>
  <li><b>Short segments, tested often.</b> Attention drifts in cycles, and the lapses come more often as a sitting goes on (Bunce and others, 2010). Short quizzes between short segments cut mind-wandering and improve learning (Szpunar, Khan and Schacter, <i>PNAS</i>, 2013). That is the shape of a sprint.</li>
  <li><b>Rest after learning.</b> A few minutes of quiet rest right after learning, with no new input, improves later recall (Dewar and others, 2012). That is why a sprint ends with a break.</li>
  <li><b>Recall, spaced and mixed.</b> Retrieving from memory beats re-reading (Roediger and Karpicke, 2006); spacing reviews over days beats cramming (Cepeda and others, 2006); mixing topics in practice beats blocking them (Rohrer and Taylor, 2007).</li>
  <li><b>Text that shows its structure.</b> Signalling how material is organised, and breaking it into short segments, helps learners build a model of it (Mayer, <i>Multimedia Learning</i>, 2009: the signalling and segmenting principles). So in each provision, enumerations hang from a numbered margin and say how many items follow, each proviso starts on its own line, and a colour always means the same thing: red for penalties, gold for numbers, violet for exceptions and provisos, blue for conditions, green for definitions. Not a word of the law is changed.</li>
  <li><b>Few highlights.</b> Marking much of a text does little for learning (Dunlosky and others, 2013, rated highlighting low in usefulness), so only a few kinds of words are marked by default. Turn each kind on or off under Highlights.</li>
  <li><b>One thing stands out.</b> An item that differs from those around it is remembered better (von Restorff, 1933). Each Book Two crime card sets off one element, the one that separates the crime from its neighbours.</li>
  <li><b>Judge your own memory.</b> Before checking a recall you say how sure you are. Learners who overrate what they know stop studying too soon (Dunlosky and Rawson, 2012), and errors made with high confidence are corrected more lastingly once shown (Butterfield and Metcalfe, 2001, the hypercorrection effect). Progress shows how well your confidence matches your accuracy.</li>
  <li><b>Write it the way you will be tested.</b> The Bar answer mode practises the Answer–Legal basis–Application–Conclusion form, graded against the provision’s own elements, conditions and exceptions: practising the retrieval you will need on the exam transfers best (transfer-appropriate processing; Morris, Bransford and Franks, 1977).</li>
  <li><b>A comfortable line.</b> Study text is kept to about 65 characters a line. On screen, moderate lines have been linked with better comprehension than very long ones (Dyson and Haselgrove, 2001).</li></ul>
  <p class="small muted">These are general findings about memory, not studies of this app. The pictures suggested for each topic are our own inventions; replace any that do not stick with your own. A place you know well works even better: use “Use a place you know” on the Today screen.</p>
  <h2>Sources</h2>
  <ul class="explain small"><li>Most statutes: The LawPhil Project (Arellano Law Foundation), as mirrored by LawCodex. LawPhil is a free, unofficial library.</li>
  <li>Labor Code: DOLE, <i>The Labor Code of the Philippines, Renumbered</i> (2022). Footnotes are DOLE’s.</li>
  <li>Family Code: your PDF of Executive Order No. 209 (text layer decoded and checked against OCR).</li>
  <li>Administrative Code of 1987: your scanned copy, read three times by OCR (once from the whole page, once from each page alone at higher contrast) and compared word by word with the LawPhil text. Where two of the three readings agree with LawPhil, LawPhil’s words are used; where they agree with each other against LawPhil, your print’s words are kept. Disputed words, tables and sections the OCR could not read were checked against the scan itself. Where your print has an evident misprint (for example “office of agency” for “office or agency”), the text is corrected and the provision says so.</li>
  <li>Case indexes: the textbooks you supplied (case names, citations and pages only — the authors’ text is not reproduced).</li>
  <li>Syllabus: your Con Law 2, Crim 1, Crim 2 (Modules 1–9), Legal & Judicial Ethics and Public International Law syllabi. Each case is filed under the provision cited in the same outline line or section; where the syllabus cites none, under the provision the case actually construes, and the provision page says how it was filed.</li>
  <li>Recent rulings (2023–2026): checked against the decisions on LawPhil, the SC E-Library and Supreme Court releases, or reputable news reports of them. Each ruling is marked by how it was verified; holdings are written in our own words.</li></ul>
  <div class="note">Statutes, decrees and executive issuances are works of the Government and carry no copyright (RA 8293, Sec. 176.1). None of these sources is the official text. Before you cite a provision in a pleading, check the Official Gazette or the certified copy.</div>
  <h2 style="margin-top:20px">Proofreading</h2>
  <p class="small">Every text went through: (1) removal of LawPhil anti-copying watermarks and markup; (2) numbering checks for gaps, duplicates and merged provisions; (3) automatic flags for repeated words, unbalanced parentheses and broken hyphenation; (4) for Civil Code Arts. 1157–1439, a word-by-word comparison with the codal text printed in De Leon; (5) separation of provisions the source had run into the preceding one (e.g. Civil Code Arts. 213, 437, 1602, 2075) — using the source’s own words. Each correction is shown on the provision it touches with its basis. Typography (dashes, spacing) is normalised; words are never silently changed.</p>
  ${pr ? `<div class="card flat small" style="overflow-x:auto"><b>Correction log (${pr.errata.length})</b><table class="table">${pr.errata.map(e => `<tr><td>${esc(e.code)}</td><td>${esc(e.n)}</td><td>${esc(e.note)}</td><td>${e.applied ? '✓' : '—'}</td></tr>`).join('')}</table>
    <b>Open numbering notes</b><ul>${Object.entries(pr.numbering).filter(([, v]) => v.length).map(([k, v]) => `<li>${esc(meta(k)?.short || k)}: ${esc(v.join('; '))}</li>`).join('')}</ul></div>` : ''}
  <h2 style="margin-top:20px">Your data</h2><p class="small">Progress, notes and bookmarks stay in this browser. Nothing is sent anywhere unless you use the optional AI tutor, which sends only the provision you are viewing and your question.</p>
  <p class="small muted">Built ${esc(CAT.built)} · ${CAT.total.toLocaleString()} provisions ${/claude|anthropic/.test(location.hostname) ? '' : '· <a href="legacy/">Open the previous Sinag Learning Studio</a>'}</p></div>`;
}

/* ------------------------------------------------------------------ router */
async function route() {
  const h = location.hash.replace(/^#\/?/, '');
  const [path, qs] = h.split('?');
  const q = new URLSearchParams(qs || '');
  const parts = path.split('/').map(decodeURIComponent);
  document.onkeydown = null; main.onclick = null; document.body.classList.remove('focus');
  try {
    if (!CAT) CAT = await getJSON('data/catalog.json?v=' + Date.now().toString().slice(0, 7));
    if (!CUR) await loadCur();
    if (!parts[0]) await home();
    else if (parts[0] === 'learn') learn();
    else if (parts[0] === 'field') fieldView(parts[1]);
    else if (parts[0] === 'lesson') lessonView(parts[1]);
    else if (parts[0] === 'set') setView(parts[1]);
    else if (parts[0] === 'b2') await b2View(parts[1], q);
    else if (parts[0] === 'library') library();
    else if (parts[0] === 'code') await codeView(parts[1], q);
    else if (parts[0] === 'p') await provView(parts[1], parts.slice(2).join('/'), q);
    else if (parts[0] === 'review') await reviewView();
    else if (parts[0] === 'sprint') await sprintView(q);
    else if (parts[0] === 'map') await mapView(parts.slice(1));
    else if (parts[0] === 'drill') await drillView(q);
    else if (parts[0] === 'search') await searchView(q);
    else if (parts[0] === 'progress') progressView();
    else if (parts[0] === 'syllabus') await syllabusView(parts[1], q);
    else if (parts[0] === 'about') await aboutView();
    else await home();
    if (!['search'].includes(parts[0])) window.scrollTo(0, 0);
    main.focus({ preventScroll: true });
  } catch (e) {
    console.error(e);
    main.innerHTML = `<div class="empty"><p>Something went wrong loading this page.</p><p class="small">${esc(e.message || e)}</p><a class="btn" href="#/">Home</a></div>`;
  }
}
window.addEventListener('hashchange', route);
$('.topsearch').addEventListener('submit', e => { e.preventDefault(); location.hash = '#/search?q=' + encodeURIComponent($('#q').value); });
$('#q').addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); location.hash = '#/search?q=' + encodeURIComponent(e.target.value); } });
route();
try { if ('serviceWorker' in navigator && location.protocol === 'https:' && !/claude|anthropic|claudeusercontent/.test(location.hostname)) navigator.serviceWorker.register('sw.js').catch(() => {}); } catch (e) { /* not available in this host */ }
})();
