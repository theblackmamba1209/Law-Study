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
const DEFAULTS = { cards: {}, notes: {}, marks: {}, flags: {}, days: {}, last: null, tutor: {},
  settings: { newPerDay: 15, hl: { op: true, cond: true, exc: true, num: true, pen: true, def: true }, passcode: '' } };
let S;
try { S = Object.assign(structuredClone(DEFAULTS), JSON.parse(localStorage.getItem(KEY) || '{}')); }
catch (e) { S = structuredClone(DEFAULTS); }
S.settings = Object.assign(structuredClone(DEFAULTS.settings), S.settings || {});
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
  CODES[id] = d;
  return d;
}
let SYL = null, SYX = null, REC = null;
async function loadSyllabus() { if (!SYL) SYL = await getJSON('data/syllabus.json?v=' + (CAT.shash || CAT.built)).catch(() => ({ courses: [] })); return SYL; }
async function loadSylIndex() { if (!SYX) SYX = await getJSON('data/syllabus_index.json?v=' + (CAT.shash || CAT.built)).catch(() => ({})); return SYX; }
async function loadRecent() { if (!REC) REC = await getJSON('data/recent.json?v=' + (CAT.rhash || CAT.built)).catch(() => ({ by: {}, general: [] })); return REC; }
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

/* ------------------------------------------------------------------ spaced repetition (SM-2 family) */
const ck = (cid, pid) => cid + '|' + pid;
function status(key) {
  const c = S.cards[key];
  if (!c) return '';
  if (!c.reps) return 's';
  if (c.ivl >= 21) return 'm';
  return 'l';
}
function rate(key, g) {
  const now = Date.now();
  const c = S.cards[key] || { ease: 2.5, ivl: 0, reps: 0, lapses: 0, seen: now };
  const first = !c.reps;
  if (g === 1) { c.lapses += c.reps ? 1 : 0; c.reps = 0; c.ivl = 0; c.ease = Math.max(1.3, c.ease - 0.2); c.due = now + 10 * 60000; }
  else {
    if (c.reps === 0) c.ivl = g === 2 ? 1 : g === 3 ? 1 : 4;
    else if (c.reps === 1) c.ivl = g === 2 ? 3 : g === 3 ? 6 : 9;
    else c.ivl = Math.round(c.ivl * (g === 2 ? 1.2 : g === 3 ? c.ease : c.ease * 1.35));
    c.ease = Math.max(1.3, c.ease + (g === 2 ? -0.15 : g === 4 ? 0.15 : 0));
    c.reps += 1;
    c.due = now + c.ivl * DAY - 3600000;
  }
  c.last = now; c.hist = (c.hist || []).slice(-19).concat([[now, g]]);
  S.cards[key] = c;
  bumpDay(first ? 'n' : 'r');
  save();
  return c;
}
function dueKeys() { const now = Date.now(); return Object.entries(S.cards).filter(([, c]) => c.reps !== undefined && c.due && c.due <= now).sort((a, b) => a[1].due - b[1].due).map(([k]) => k); }
function newToday() { return (S.days[today()] || {}).n || 0; }
function streak() { let n = 0, d = new Date(); for (;;) { const k = new Date(d - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); const v = S.days[k]; if (v && (v.r + v.n) > 0) { n++; d = new Date(d - DAY); } else break; } return n; }
function fmtIvl(d) { if (d < 1) return '10m'; if (d < 30) return d + 'd'; if (d < 365) return Math.round(d / 30) + 'mo'; return (d / 365).toFixed(1) + 'y'; }
function preview(key) {
  const c = S.cards[key] || { ease: 2.5, ivl: 0, reps: 0 };
  return [1, 2, 3, 4].map(g => {
    if (g === 1) return '10m';
    if (c.reps === 0) return fmtIvl(g === 4 ? 4 : 1);
    if (c.reps === 1) return fmtIvl(g === 2 ? 3 : g === 3 ? 6 : 9);
    return fmtIvl(Math.round(c.ivl * (g === 2 ? 1.2 : g === 3 ? c.ease : c.ease * 1.35)));
  });
}

/* ------------------------------------------------------------------ text helpers */
const FN = /⟨(\d+)⟩/g;
const plain = s => typeof s === 'string' ? s.replace(FN, '') : '';
const provText = p => p.p.filter(x => typeof x === 'string').map(plain).join('\n');
const words = s => s.split(/\s+/).filter(Boolean);
const NUMW = 'one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|million|half|one-half|one-third|one-fourth|two-thirds|three-fourths|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth';
const RX = {
  pen: /\b(reclusi[oó]n perpetua|reclusi[oó]n temporal|prisi[oó]n mayor|prisi[oó]n correccional|arresto mayor|arresto menor|destierro|public censure|perpetual (?:absolute|special) disqualification|temporary (?:absolute|special) disqualification|life imprisonment|imprisonment|fine of [^,;.]{1,60}|a fine|fines?|penalty of [a-z ]{3,40}|death penalty)\b/gi,
  num: new RegExp(`(?:₱|P(?=\s?\d))\s?\d[\d,]*(?:\.\d+)?|\b\d+(?:\.\d+)?\s?%|\b(?:\d[\d,]*(?:\.\d+)?|(?:${NUMW})(?:[ -](?:${NUMW}|and))*)(?:\s*\(\d[\d,.]*\))?\s+(?:calendar |working |consecutive |full )?(?:days?|months?|years?|hours?|weeks?|minutes?|per\s?cent(?:um)?|percent|pesos|centavos|hectares?|meters?|kilometers?|degrees?|times|members|votes|witnesses)\b|\b(?:${NUMW})(?:[ -](?:${NUMW}))*\s*\(\d[\d,.]*\)|\b(?:one-half|one-third|two-thirds|three-fourths|one-fourth|majority)\b`, 'gi'),
  exc: /\b(unless|except(?:ing)?|notwithstanding|however|nevertheless|without prejudice to|other than|save (?:as|those|when|in)|provided,? however)\b/gi,
  cond: /\b(if|when|whenever|in case|in the event|provided(?:,)? that|provided|as long as|so long as|only if|on condition|subject to)\b/gi,
  op: /\b(shall not|shall|may not|may|must not|must|cannot|can not|is prohibited|are prohibited|is hereby|are hereby|it shall be unlawful|null and void|void|voidable|unenforceable|rescissible|inexistent|liable|entitled)\b/gi,
  def: /\b(shall mean|means|refers? to|shall refer to|is understood|are understood|shall be understood|is defined as|are those|shall include|includes)\b/gi,
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
function renderPara(x, on, d, cid) {
  if (typeof x !== 'string') {
    if (x && x.t === 'table') return `<div style="overflow-x:auto"><table>${x.rows.map(r => `<tr>${r.map(c => `<td>${esc(c)}</td>`).join('')}</tr>`).join('')}</table></div>`;
    return '';
  }
  let h = on ? hlText(x, on) : esc(x);
  h = h.replace(/⟨(\d+)⟩/g, '<sup class="fn" data-fn="$1">$1</sup>');
  h = linkRefs(h, d, cid);
  const li = /^\(?([0-9]{1,2}|[a-z]{1,2}|[ivx]{1,4})[.)]\s/.test(x) || /^(First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth)[.,—:-]/.test(x);
  return `<p${li ? ' class="li"' : ''}>${h}</p>`;
}

/* --------- legal anatomy: an automatic reading guide built from the verbatim text */
function sentences(t) { return t.replace(/\s+/g, ' ').split(/(?<=[.;:])\s+(?=[A-Z(“"])/).map(s => s.trim()).filter(s => s.length > 2); }
function anatomy(p) {
  const t = provText(p); const out = [];
  const add = (k, s) => out.push([k, s]);
  for (const s of sentences(t)) {
    const l = s.toLowerCase();
    if (/\b(means|shall mean|refers? to|is understood|are understood|shall be understood|is defined|are those|is one)\b/.test(l)) add('Definition', s);
    else if (/\b(reclusi[oó]n|prisi[oó]n|arresto|destierro|imprisonment|fine of|shall be punished|penalty of|shall suffer)\b/.test(l)) add('Penalty', s);
    else if (/\b(shall not|may not|must not|cannot|can not|is prohibited|are prohibited|unlawful|no person shall|no .{1,40} shall)\b/.test(l)) add('Prohibition', s);
    else if (/\b(unless|except|notwithstanding|however|nevertheless|provided,? however)\b/.test(l)) add('Exception', s);
    else if (/^(if|when|whenever|in case|should|where)\b/.test(l)) add('Condition', s);
    else if (/\b(shall|must|is required|are required|is obliged|are obliged|is bound)\b/.test(l)) add('Duty / rule', s);
    else if (/\b(may|is entitled|are entitled|has the right|have the right)\b/.test(l)) add('Power / right', s);
    else if (/^\(?([0-9]{1,2}|[a-z])[.)]/.test(s)) add('Element / item', s);
    else add('Statement', s);
  }
  const periods = (t.match(RX.num) || []).filter(x => /day|month|year|hour|week|per\s?cent|percent|pesos|₱|\d{2,}/i.test(x));
  return { items: out, periods: [...new Set(periods)].slice(0, 12) };
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
  return `<div class="crumbs"><a href="#/library">Library</a><span class="sep">›</span><a href="#/code/${cid}">${esc(d.short)}</a>${chain.map(i => `<span class="sep">›</span><a href="#/code/${cid}?div=${i}">${esc(shortDiv(d.divisions[i].t))}</a>`).join('')}</div>`;
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
  const core = CAT.codes.filter(c => c.core);
  main.innerHTML = `
  <section class="hero">
    <div class="card"><h1>Magandang araw.</h1>
      <p class="muted">Every provision here is the verbatim codal text. Read it, take it apart, recall it from memory, then let spaced review bring it back before you forget it.</p>
      <div class="row" style="margin-top:12px">
        <a class="btn primary" href="#/review">${due ? `Review ${due} due` : 'Start today’s session'}</a>
        ${last ? `<a class="btn" href="#/p/${last.c}/${last.p}">Continue: ${esc(last.l)}</a>` : `<a class="btn" href="#/code/rpc">Begin with the Revised Penal Code</a>`}
        <a class="btn ghost" href="#/drill">Drill</a>
      </div></div>
    <div class="card"><div class="row" style="gap:22px">
      <div><div class="stat">${due}</div><div class="small muted">due for review</div></div>
      <div><div class="stat">${nt}<span class="small muted">/${S.settings.newPerDay}</span></div><div class="small muted">new today</div></div>
      <div><div class="stat">${st}</div><div class="small muted">day streak</div></div></div>
      <p class="small muted" style="margin:12px 0 0">${CAT.total.toLocaleString()} provisions in ${CAT.codes.length} codes and laws. Progress is saved on this device. Use <a href="#/progress">Progress → Back up</a> before switching browsers.</p></div>
  </section>
  <div class="grid g3" style="margin-top:14px">
    <a class="card codecard" href="#/syllabus"><span class="t">Your syllabus</span><span class="c">Con Law 2 · Crim 1 · Crim 2 · Ethics · PIL</span><span class="small muted">Every assigned case, filed under the provision it is taught with</span></a>
    <a class="card codecard" href="#/syllabus/recent"><span class="t">Recent jurisprudence</span><span class="c">2023–2026 rulings</span><span class="small muted">Filed under the provisions they apply, each marked by how it was verified</span></a>
    <a class="card codecard" href="#/search"><span class="t">Find a case</span><span class="c">Search by case name</span><span class="small muted">Shows every provision a case is filed under — textbook, syllabus and recent</span></a>
  </div>
  <div class="subject"><h2>Core codes</h2><span class="muted small">the backbone of the Bar</span></div>
  <div class="grid g3">${core.map(codeCard).join('')}</div>
  <p style="margin-top:22px"><a class="btn" href="#/library">Open the full library (${CAT.codes.length})</a></p>`;
}

function library() {
  setNav('library');
  const bySub = CAT.subjects.map(s => ({ s, codes: CAT.codes.filter(c => c.subject === s.id), miss: CAT.missing.filter(m => m.subject === s.id) }));
  main.innerHTML = `<h1>Library</h1><p class="muted">Grouped by Bar subject. <span class="chip gold">Core</span> marks the codes most worth mastering first.</p>
  ${bySub.map(({ s, codes, miss }) => `<div class="subject"><h2>${esc(s.name)}</h2><span class="muted small">${codes.length} instruments</span></div>
    <div class="grid g3">${codes.sort((a, b) => (b.core - a.core)).map(codeCard).join('')}
    ${miss.map(m => `<div class="card flat" style="border-style:dashed"><div class="codecard"><span class="t">${esc(m.title)}</span><span class="c">${esc(m.citation)}</span><span class="small muted">${esc(m.why)}</span></div></div>`).join('')}</div>`).join('')}`;
}

function tocHTML(d, cid, openDiv) {
  const open = new Set();
  let v = openDiv; while (v != null) { open.add(v); v = d.divisions[v].p; }
  const provList = arr => arr.length ? `<ul class="plist">${arr.map(p => `<li><a href="#/p/${cid}/${p.i}"><span class="dot ${status(ck(cid, p.i))}"></span><span class="pl">${esc(p.l)}</span><span class="pc">${esc(p.c || firstWords(p))}</span></a></li>`).join('')}</ul>` : '';
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
function firstWords(p) { const t = plain(p.p.find(x => typeof x === 'string') || ''); return t.length > 110 ? t.slice(0, 107) + '…' : t; }

async function codeView(cid, q) {
  setNav('library');
  const d = await loadCode(cid); const m = meta(cid);
  const k = counts(cid);
  const next = d.provisions.find(p => !S.cards[ck(cid, p.i)]);
  const openDiv = q.get('div') != null ? +q.get('div') : null;
  main.innerHTML = `${crumbs(d, null, cid)}
  <div class="codehead"><h1>${esc(d.title)}</h1><div class="muted">${esc(d.citation)}</div></div>
  <div class="grid" style="grid-template-columns:minmax(0,1fr) 320px;align-items:start" id="cv">
    <div class="card">${tocHTML(d, cid, openDiv)}</div>
    <aside class="grid">
      <div class="card"><div class="row"><div class="progress-ring" style="--p:${Math.round(k.touched / k.total * 100)}"><span>${Math.round(k.touched / k.total * 100)}%</span></div><div class="small"><b>${k.m}</b> mastered · <b>${k.l}</b> learning · <b>${k.s}</b> read<br><span class="muted">${k.total.toLocaleString()} provisions · ${m.words.toLocaleString()} words</span></div></div>
        <div class="row" style="margin-top:12px">${next ? `<a class="btn primary" href="#/p/${cid}/${next.i}">${k.touched ? 'Continue' : 'Start'}: ${esc(next.l)}</a>` : '<span class="chip ok">Every provision opened</span>'}<a class="btn" href="#/drill?code=${cid}">Drill</a></div></div>
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
function lawHTML(d, p, cid, on) {
  const fn = p.f || [];
  return `<article class="law" id="law">
    <div class="lab"><h1>${esc(p.l)}${p.o ? ` <span class="muted" style="font-size:.8em">[${esc(p.o)}]</span>` : ''}</h1>${p.c ? `<span class="cap">${esc(p.c)}.</span>` : ''}</div>
    <div class="text">${p.p.map(x => renderPara(x, on, d, cid)).join('')}</div>
    ${fn.length ? `<div class="fnlist">${fn.map(f => `<p id="fn${f.n}"><sup>${f.n}</sup> ${esc(f.t)}</p>`).join('')}<p class="tiny muted">Footnotes are the publisher’s (DOLE), not part of the law.</p></div>` : ''}
    <div class="verify">${verifyChips(cid, p)}</div>
    ${(p.e || []).map(e => `<div class="note ${/missing|omitted|restored|absent/i.test(e.t) ? 'blue' : ''}" style="margin-top:10px"><b>Proofreading note.</b> ${esc(e.t)}${e.b ? ` <span class="muted">Basis: ${esc(e.b)}</span>` : ''}</div>`).join('')}
    ${(p.a || []).map(a => `<div class="amend"><div class="row"><b>Amended text</b><span class="chip ok">${esc(a.by)} · Sec. ${esc(a.sec)}</span><span class="spacer"></span><a class="small" href="#/code/${a.ref}">open ${esc(a.by)}</a></div><p class="tiny muted" style="margin:4px 0 8px">Verbatim from the amending law. Where two amendments are shown, the later law controls.</p><div class="text">${a.p.map(x => renderPara(x, on, null, cid)).join('')}</div></div>`).join('')}
  </article>`;
}
function verifyChips(cid, p) {
  const m = meta(cid); const out = [];
  if (m.kind === 'admin') out.push(p.v === 'ok' ? '<span class="chip ok" title="Every word was found in a dictionary or in the other codes. Real-word OCR slips (e.g. “of” for “or”) are still possible.">OCR · machine-checked</span>' : `<span class="chip warn" title="${esc('Words to verify against your scan: ' + (p.u || []).join(', '))}">OCR · check: ${esc((p.u || []).slice(0, 4).join(', '))}</span>`);
  else if (m.kind === 'family') out.push('<span class="chip ok">Your PDF · text layer decoded exactly</span>');
  else if (m.kind === 'labor') out.push('<span class="chip ok">DOLE 2022 edition</span>');
  else out.push('<span class="chip">LawPhil transcription</span>');
  if (p.x) out.push(`<span class="chip warn" title="${esc(p.x.join('; '))}">Proofreading flag</span>`);
  if ((p.e || []).length) out.push('<span class="chip blue">Corrected / annotated</span>');
  if (p.xc) out.push(`<span class="chip ok" title="${esc(p.xc)}">Cross-checked</span>`);
  return out.join('');
}

async function provView(cid, pid) {
  setNav('library');
  const d = await loadCode(cid); await loadExtras(cid); await Promise.all([loadSylIndex(), loadRecent()]);
  const p = d.byId[pid];
  if (!p) { main.innerHTML = `<div class="empty">That provision is not in this code. <a href="#/code/${cid}">Back to ${esc(d.short)}</a></div>`; return; }
  const key = ck(cid, pid);
  if (!S.cards[key]) { S.cards[key] = { ease: 2.5, ivl: 0, reps: 0, lapses: 0, seen: Date.now() }; }
  S.last = { c: cid, p: pid, l: `${d.short} · ${p.l}` }; save();
  const prev = d.provisions[p.ix - 1], next = d.provisions[p.ix + 1];
  const notes = (NOTES[cid] || {})[pid];
  const cases = (CASES[cid] || {})[pid] || [];
  const syl = SYX[ck(cid, pid)] || [], rec = REC.by[ck(cid, pid)] || [];
  const ncase = cases.length + syl.length + rec.length + (((notes || {}).d) || []).length;
  const on = S.settings.hl;
  const tabs = [['guide', 'Study guide'], ['recall', 'Recall'], ['cases', `Cases${ncase ? ' (' + ncase + ')' : ''}${rec.length ? ' <span class="newdot" title="has 2023–2026 rulings">new</span>' : ''}`], ['notes', 'My notes']];
  main.innerHTML = `${crumbs(d, p, cid)}
  <div class="pv"><div>
    <div class="legend" style="margin-bottom:10px">${HLORDER.map(k => `<label><input type="checkbox" data-hl="${k}" ${on[k] ? 'checked' : ''}><span class="${HLCLASS[k]}">${HLNAME[k]}</span></label>`).join('')}</div>
    <div id="lawbox">${lawHTML(d, p, cid, on)}</div>
    <div class="tabs" role="tablist">${tabs.map(([k, n], i) => `<button role="tab" data-tab="${k}" class="${i ? '' : 'on'}">${n}</button>`).join('')}</div>
    <div id="tabbox"></div>
    <div class="pn">${prev ? `<a class="btn" href="#/p/${cid}/${prev.i}">← ${esc(prev.l)}</a>` : '<span></span>'}${next ? `<a class="btn primary" href="#/p/${cid}/${next.i}">${esc(next.l)} →</a>` : ''}</div>
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
  const show = k => { $$('.tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === k)); renderTab(k); };
  function renderTab(k) {
    if (k === 'guide') tabbox.innerHTML = guideHTML(d, p, cid, notes);
    if (k === 'cases') tabbox.innerHTML = casesHTML(cid, pid, notes, cases, syl, rec);
    if (k === 'notes') { tabbox.innerHTML = `<div class="panel"><textarea id="mynote" placeholder="Your own words: what the provision says, the elements, a case that applies it, a mnemonic…">${esc(S.notes[key] || '')}</textarea><p class="tiny muted">Saved on this device as you type. Writing it in your own words is one of the strongest ways to learn it.</p></div>`; $('#mynote').addEventListener('input', e => { S.notes[key] = e.target.value; save(); }); }
    if (k === 'recall') recallPanel(tabbox, d, p, cid);
    if (k === 'guide') wireTutor(d, p, cid, cases);
  }
  show('guide');
  $$('.tabs button').forEach(b => b.onclick = () => show(b.dataset.tab));
  $$('[data-hl]').forEach(c => c.onchange = () => { S.settings.hl[c.dataset.hl] = c.checked; save(); $('#lawbox').innerHTML = lawHTML(d, p, cid, S.settings.hl); });
  $$('[data-rate]').forEach(b => b.onclick = () => { const c = rate(key, +b.dataset.rate); toast(`Next review in ${fmtIvl(c.ivl)}.`); $('#cstat').textContent = cardLine(key); if (next) setTimeout(() => location.hash = `#/p/${cid}/${next.i}`, 450); });
  $('#mark').onclick = () => { if (S.marks[key]) delete S.marks[key]; else S.marks[key] = Date.now(); save(); $('#mark').textContent = S.marks[key] ? '★ Bookmarked' : '☆ Bookmark'; };
  $('#flag').onclick = async () => {
    const t = await askText('Report a text error', S.flags[key]?.t || '', 'What the text says here vs. what the official text says, and your source');
    if (t === null) return; if (t.trim()) S.flags[key] = { t: t.trim(), at: Date.now(), l: `${d.short} ${p.l}` }; else delete S.flags[key]; save(); provView(cid, pid);
  };
  main.onclick = e => { const s = e.target.closest('sup.fn'); if (s) { const f = $('#fn' + s.dataset.fn); f && f.scrollIntoView({ behavior: 'smooth', block: 'center' }); } };
}
function cardLine(key) { const c = S.cards[key]; if (!c || !c.reps) return 'Not yet rated.'; return `Interval ${fmtIvl(c.ivl)} · ease ${c.ease.toFixed(2)} · ${c.lapses} lapse${c.lapses === 1 ? '' : 's'} · due ${new Date(c.due).toLocaleDateString()}`; }
function sibling(d, p, cid) {
  const arr = p.d == null ? d.loose : d.divProv[p.d];
  if (!arr || arr.length < 2) return '';
  const dv = p.d != null ? d.divisions[p.d].t : d.short;
  const i = arr.indexOf(p); const win = arr.slice(Math.max(0, i - 6), i + 7);
  return `<div class="card"><h3 class="small">${esc(shortDiv(dv))}</h3><ul class="plist" style="padding:0">${win.map(x => `<li><a href="#/p/${cid}/${x.i}" ${x === p ? 'style="background:var(--brand-soft)"' : ''}><span class="dot ${status(ck(cid, x.i))}"></span><span class="pl">${esc(x.l)}</span><span class="pc">${esc(x.c || '')}</span></a></li>`).join('')}</ul></div>`;
}
function guideHTML(d, p, cid, n) {
  const an = anatomy(p);
  let h = '<div class="panel">';
  if (n && (n.x || n.k)) {
    h += `<div class="card flat" style="margin-bottom:12px"><div class="row"><h3 style="margin:0">In plain language</h3><span class="spacer"></span><span class="chip ok">Written for this provision</span></div>
      <div class="explain" style="margin-top:8px">${(n.x || '').split('\n\n').map(x => `<p>${esc(x)}</p>`).join('')}</div>
      ${n.k ? `<h3 style="margin-top:10px">Elements / key points</h3><ol class="explain" style="margin:0;padding-left:1.3em">${n.k.map(x => `<li>${esc(x)}</li>`).join('')}</ol>` : ''}
      ${n.w ? `<h3 style="margin-top:10px">Why it exists</h3><p class="explain">${esc(n.w)}</p>` : ''}
      ${n.t ? `<h3 style="margin-top:10px">Exam traps</h3><ul class="explain" style="margin:0;padding-left:1.2em">${n.t.map(x => `<li>${esc(x)}</li>`).join('')}</ul>` : ''}
      ${n.q ? `<details style="margin-top:10px"><summary><b>Self-test</b> <span class="small muted">(answer before opening)</span></summary><ol class="explain">${n.q.map(x => `<li>${esc(x)}</li>`).join('')}</ol></details>` : ''}
      <p class="tiny muted" style="margin:10px 0 0">Explanations are study aids, not the law. The verbatim text above controls.</p></div>`;
  }
  h += `<div class="card flat" id="tutorbox" style="margin-bottom:12px" hidden></div>`;
  h += `<div class="card flat"><div class="row"><h3 style="margin:0">Reading guide</h3><span class="spacer"></span><span class="chip">auto-parsed from the text</span></div>
    <p class="small muted" style="margin:4px 0 10px">Lawyers read a provision by asking: who is covered, what must or may they do, under what conditions, with what exceptions, and what follows. Each sentence of the provision is sorted below.</p>
    <div class="anat">${an.items.map(([k, s]) => `<div class="it"><b>${esc(k)}</b><span>${hlText(s, S.settings.hl)}</span></div>`).join('')}</div>
    ${an.periods.length ? `<p class="small" style="margin-top:10px"><b>Numbers to remember:</b> ${an.periods.map(x => `<span class="chip gold">${esc(x)}</span>`).join(' ')}</p>` : ''}
    <h3 style="margin-top:14px">Ask yourself</h3>
    <ol class="explain small" style="padding-left:1.3em;margin:0">
      <li>Restate ${esc(p.l)} in one sentence without looking.</li>
      <li>What problem was this provision written to solve? What would go wrong without it?</li>
      <li>Invent a short set of facts where it applies — then change one fact so it no longer does.</li>
      ${an.items.some(i => i[0] === 'Exception') ? '<li>State the general rule, then the exception, then why the exception exists.</li>' : ''}
      ${an.periods.length ? '<li>Recite every number and period in it, and what happens when each runs out.</li>' : ''}
    </ol></div>`;
  return h + '</div>';
}
function recentHTML(rec, withProv) {
  return rec.map(r => `<div class="case recent"><div class="row" style="gap:6px"><div class="cn" style="flex:1;min-width:200px">${esc(r.n)}</div>${r.st === 'decision' ? '<span class="chip ok" title="Docket and date checked against the decision or an official/library listing">verified: decision</span>' : '<span class="chip warn" title="From a Supreme Court release or a news report of the ruling — read the full text before citing">verified: SC release / news</span>'}</div>
    <div class="cc">${esc([r.g, r.d, r.ct].filter(Boolean).join(' · '))}</div>
    <div class="dg"><div><b>Ruling</b>${esc(r.h)}</div>${r.rel ? `<div><b>Why it matters here</b>${esc(r.rel)}</div>` : ''}${withProv ? withProv(r) : ''}</div>
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
    h += `<h3 style="margin-top:14px">Case digests</h3>` + dg.map(c => `<div class="case"><div class="cn">${esc(c.n)}</div><div class="cc">${esc(c.c || '')}</div><div class="dg">${c.f ? `<div><b>Facts</b>${esc(c.f)}</div>` : ''}${c.i ? `<div><b>Issue</b>${esc(c.i)}</div>` : ''}${c.h ? `<div><b>Ruling & doctrine</b>${esc(c.h)}</div>` : ''}${c.r ? `<div><b>Why it matters here</b>${esc(c.r)}</div>` : ''}</div></div>`).join('');
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
function recallPanel(box, d, p, cid, onDone) {
  const nw = words(provText(p)).length;
  box.innerHTML = `<div class="panel"><div class="row" style="margin-bottom:10px">
    <button class="btn sm" data-m="c1">Cloze · light</button><button class="btn sm" data-m="c2">Cloze · medium</button><button class="btn sm" data-m="c3">Cloze · heavy</button>
    <button class="btn sm" data-m="fl">First letters</button><button class="btn sm" data-m="fr">Write it out</button></div>
    <div id="rbox"></div></div>`;
  const rbox = $('#rbox', box);
  const law = $('#law');
  const hideLaw = h => { if (law) law.style.filter = h ? 'blur(7px)' : ''; if (law) law.style.userSelect = h ? 'none' : ''; };
  const modes = {
    c1: () => cloze(1), c2: () => cloze(2), c3: () => cloze(3),
    fl: () => {
      hideLaw(true);
      rbox.innerHTML = `<p class="small muted">Recite each word aloud from its first letter. Tap a word to check it.</p><div class="card flat fl">${p.p.filter(x => typeof x === 'string').map(x => '<p>' + words(plain(x)).map(w => `<span class="h">${esc(w)}</span>`).join(' ') + '</p>').join('')}</div><div class="row" style="margin-top:8px"><button class="btn sm" id="flall">Reveal all</button></div>`;
      rbox.onclick = e => { const s = e.target.closest('.fl span'); if (s) s.classList.remove('h'); };
      $('#flall').onclick = () => { $$('.fl span', rbox).forEach(s => s.classList.remove('h')); hideLaw(false); };
    },
    fr: () => {
      hideLaw(true);
      rbox.innerHTML = `<p class="small muted">Write the provision from memory${nw > 220 ? ' (long provision: write as much as you can — the first paragraph counts most)' : ''}. Then check it word by word against the verbatim text.</p><textarea id="frt" placeholder="${esc(p.l)}…"></textarea><div class="row" style="margin-top:8px"><button class="btn primary sm" id="frc">Check</button><button class="btn sm" id="frs">Show the text</button></div><div id="frout" style="margin-top:12px"></div>`;
      $('#frs').onclick = () => hideLaw(false);
      $('#frc').onclick = () => {
        const truth = words(provText(p)); const att = words($('#frt').value);
        if (!att.length) return toast('Write something first.');
        const lim = Math.min(truth.length, Math.max(att.length + 40, 60));
        const r = lcsDiff(truth.slice(0, lim), att);
        const pct = Math.round(r.score * 100);
        $('#frout').innerHTML = `<div class="row"><span class="stat">${pct}%</span><span class="small muted">of ${lim < truth.length ? 'the first ' + lim + ' words' : 'the text'} recalled in order · ${Math.round(r.precision * 100)}% of your words matched</span></div>
          <p class="small">${pct >= 95 ? 'Verbatim-level. Rate <b>Easy</b> or <b>Good</b>.' : pct >= 80 ? 'Strong. Rate <b>Good</b>; fix the red words.' : pct >= 55 ? 'Partial. Rate <b>Hard</b> and re-read the red words.' : 'Not yet. Rate <b>Again</b>, read it once more, then try again.'}</p>
          <div class="card flat diff">${r.out.map(o => o.t === 'ok' ? `<span class="okw">${esc(o.w)}</span>` : o.t === 'miss' ? `<span class="miss">${esc(o.w)}</span>` : `<span class="extra">${esc(o.w)}</span>`).join(' ')}</div>
          <p class="tiny muted">Green: recalled · red: missed · struck: not in the text.</p>`;
        hideLaw(false); onDone && onDone(pct);
      };
    },
  };
  function cloze(level) {
    hideLaw(true);
    const seed = p.i + ':' + level + ':' + Math.floor(Date.now() / DAY);
    const blocks = p.p.filter(x => typeof x === 'string').map(plain);
    let total = 0;
    const html = blocks.map((b, bi) => {
      const { toks, picked } = clozeModel({ p: [b] }, level, seed + bi);
      return '<p>' + toks.map((t, i) => {
        if (!picked.has(i)) return esc(t);
        const m = t.match(/^([“"(‘'[]*)(.*?)([”"),.;:!?’'\]]*)$/);
        total++;
        return `${esc(m[1])}<input data-a="${esc(m[2])}" size="${Math.max(3, m[2].length)}" aria-label="blank">${esc(m[3])}`;
      }).join('') + '</p>';
    }).join('');
    rbox.innerHTML = `<p class="small muted">Fill every blank, then check. ${total} blank${total === 1 ? '' : 's'}.</p><div class="card flat cloze">${html}</div><div class="row" style="margin-top:8px"><button class="btn primary sm" id="cc">Check</button><button class="btn sm" id="cr">Reveal</button></div><p id="cres" class="small"></p>`;
    const ins = $$('input', rbox);
    ins[0] && ins[0].focus();
    ins.forEach((inp, k) => inp.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); (ins[k + 1] || $('#cc')).focus(); } }));
    $('#cc').onclick = () => {
      let ok = 0;
      ins.forEach(i => { const g = normWord(i.value) === normWord(i.dataset.a); i.classList.toggle('ok', g); i.classList.toggle('bad', !g); if (g) ok++; });
      $('#cres').innerHTML = `<b>${ok}/${ins.length}</b> correct. ${ok === ins.length ? 'Rate <b>Good</b> or <b>Easy</b>.' : ok >= ins.length * .7 ? 'Rate <b>Hard</b> or <b>Good</b>.' : 'Rate <b>Again</b> and re-read.'}`;
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
    main.innerHTML = `<div class="reviewcard card"><h1>All caught up.</h1><p class="muted">Nothing is due. New provisions enter review once you open them in the Library. Today: ${newToday()} new, ${(S.days[today()] || {}).r || 0} reviews.</p><div class="row"><a class="btn primary" href="#/library">Learn new provisions</a><a class="btn" href="#/drill">Drill anyway</a></div></div>`;
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
        if (scope === 'weak' && !(c && (c.lapses > 0 || c.ease < 2.3))) continue;
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
function progressView() {
  setNav('progress');
  const rows = CAT.codes.map(c => ({ c, k: counts(c.id) })).filter(r => r.k.touched || r.c.core);
  const tot = rows.reduce((a, r) => ({ t: a.t + r.k.touched, m: a.m + r.k.m }), { t: 0, m: 0 });
  const days = []; for (let k = 83; k >= 0; k--) { const d = new Date(Date.now() - k * DAY); const key = new Date(d - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10); const v = S.days[key]; const n = v ? v.r + v.n : 0; days.push(`<i class="${n > 40 ? 'm' : n > 15 ? 'l' : n ? 's' : ''}" title="${key}: ${n}"></i>`); }
  const flags = Object.entries(S.flags);
  main.innerHTML = `<h1>Progress</h1>
  <div class="grid g3"><div class="card"><div class="stat">${tot.t.toLocaleString()}</div><div class="small muted">provisions opened of ${CAT.total.toLocaleString()}</div></div><div class="card"><div class="stat">${tot.m.toLocaleString()}</div><div class="small muted">mastered (interval ≥ 21 days)</div></div><div class="card"><div class="stat">${dueKeys().length}</div><div class="small muted">due now</div></div></div>
  <div class="card" style="margin-top:14px"><h3>Last 12 weeks</h3><div class="heat">${days.join('')}</div></div>
  <div class="card" style="margin-top:14px;overflow-x:auto"><table class="table"><tr><th>Code</th><th>Opened</th><th>Learning</th><th>Mastered</th><th style="width:30%">Coverage</th></tr>${rows.map(r => `<tr><td><a href="#/code/${r.c.id}">${esc(r.c.short)}</a></td><td>${r.k.touched}/${r.k.total}</td><td>${r.k.l}</td><td>${r.k.m}</td><td>${bar(r.k)}</td></tr>`).join('')}</table></div>
  <div class="card" style="margin-top:14px"><h3>Settings</h3><div class="row"><label class="small">New provisions per day in Review <input id="npd" type="number" min="0" max="200" value="${S.settings.newPerDay}" style="width:70px;padding:5px;border-radius:8px;border:1px solid var(--line2);background:var(--card)"></label></div></div>
  <div class="card" style="margin-top:14px"><h3>Back up & move</h3><p class="small muted">Progress lives in this browser only. GitHub Pages and Cloudflare are different addresses, so each keeps its own progress — back up here, restore there.</p>
    <div class="row"><button class="btn" id="exp">Back up my work</button><label class="btn">Restore from a file<input type="file" id="imp" accept="application/json" hidden></label><button class="btn" id="paste">Restore by pasting</button><button class="btn ghost" id="off">Make every code available offline</button><button class="btn ghost" id="rst" style="color:var(--bad)">Reset</button></div><p id="offmsg" class="small muted"></p></div>
  ${flags.length ? `<div class="card" style="margin-top:14px"><h3>Text errors you reported (${flags.length})</h3><ul class="small">${flags.map(([k, f]) => { const [c, p] = k.split('|'); return `<li><a href="#/p/${c}/${p}">${esc(f.l)}</a>: ${esc(f.t)}</li>`; }).join('')}</ul><button class="btn sm" id="expf">Download the error report</button></div>` : ''}`;
  $('#npd').onchange = e => { S.settings.newPerDay = Math.max(0, +e.target.value || 0); save(); };
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
  for (const f of ['notes', 'marks', 'flags', 'tutor']) Object.assign(S[f], o[f] || {});
  for (const [d, v] of Object.entries(o.days || {})) { const a = S.days[d] || { r: 0, n: 0 }; S.days[d] = { r: Math.max(a.r, v.r), n: Math.max(a.n, v.n) }; }
}
function dl(name, text) {
  const m = modal(`<h3>${esc(name)}</h3><p class="small muted">Copy this text and keep it somewhere safe (a note, an email to yourself). To restore, use <b>Restore by pasting</b>. Or try the file download.</p><textarea id="mtxt" rows="8" readonly>${esc(text)}</textarea><div class="row" style="margin-top:10px;justify-content:flex-end"><button class="btn" id="mdl">Download file</button><button class="btn primary" id="mcp">Copy</button><button class="btn" id="mno">Close</button></div>`);
  $('#mno', m.el).onclick = m.close;
  $('#mcp', m.el).onclick = async () => { const t = $('#mtxt', m.el); try { await navigator.clipboard.writeText(text); toast('Copied.'); } catch (e) { t.focus(); t.select(); try { document.execCommand('copy'); toast('Copied.'); } catch (e2) { toast('Select the text and copy it.'); } } };
  $('#mdl', m.el).onclick = () => { try { const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([text], { type: 'application/json' })); a.download = name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000); } catch (e) { toast('Downloads are blocked here — use Copy.'); } };
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
    items.forEach(x => { const s = (meta(x.ks[0].split('|')[0]) || {}).subject || 'oth'; (bySubj[s] = bySubj[s] || []).push(x); });
    main.innerHTML = `<p class="small"><a href="#/syllabus">← Syllabus</a></p><h1>Recent jurisprudence, 2023–2026</h1>
    <p class="muted">Each ruling is filed under every provision it applies; tap a provision to study it with the text. <span class="chip ok">verified: decision</span> means the docket number and date were checked against the decision or an official listing. <span class="chip warn">verified: SC release / news</span> means the ruling was confirmed from a Supreme Court release or a news report — read the full text before you cite it.</p>
    ${CAT.subjects.filter(s => bySubj[s.id]).map(s => `<div class="subject"><h2>${esc(s.name)}</h2></div>${recentHTML(bySubj[s.id].map(x => x.r).map((r, i) => Object.assign({}, r, { _ks: bySubj[s.id][i].ks })), r => `<div><b>Filed under</b>${r._ks.map(lab).join(' ')}</div>`)}`).join('')}
    ${(rc.general || []).length ? `<div class="subject"><h2>Rules of conduct (not in the codal library)</h2></div><ul class="explain">${rc.general.map(g => `<li>${esc(g.x)}${g.u ? ` <a class="small" href="${esc(g.u)}" target="_blank" rel="noopener">text</a>` : ''}</li>`).join('')}</ul>` : ''}`;
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
  <h2>How to study here</h2>
  <ol class="explain"><li><b>Read</b> the provision with the highlighting on: duties and powers, conditions, exceptions, numbers, penalties, definitions.</li>
  <li><b>Take it apart</b> in the Study guide: the reading guide sorts each sentence into rule, condition, exception and consequence.</li>
  <li><b>Recall</b> it with the text hidden — cloze, first letters, or write it out — <i>before</i> rating yourself. Retrieval, not re-reading, is what builds memory.</li>
  <li><b>Rate</b> it. Review brings it back just before you would forget it; intervals grow as you keep recalling it.</li>
  <li><b>Interleave</b> in Drill: mixed provisions across chapters and codes, and “name that provision” to fix citations.</li>
  <li><b>Connect</b> it to cases: the Cases tab shows recent rulings, the cases your syllabus assigns, and every case your textbooks discuss under that provision, with the page.</li></ol>
  <h2>Sources</h2>
  <ul class="explain small"><li>Most statutes: The LawPhil Project (Arellano Law Foundation), as mirrored by LawCodex. LawPhil is a free, unofficial library.</li>
  <li>Labor Code: DOLE, <i>The Labor Code of the Philippines, Renumbered</i> (2022). Footnotes are DOLE’s.</li>
  <li>Family Code: your PDF of Executive Order No. 209 (text layer decoded and checked against OCR).</li>
  <li>Administrative Code of 1987: OCR of your scanned copy.</li>
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
  document.onkeydown = null; main.onclick = null;
  try {
    if (!CAT) CAT = await getJSON('data/catalog.json?v=' + Date.now().toString().slice(0, 7));
    if (!parts[0]) await home();
    else if (parts[0] === 'library') library();
    else if (parts[0] === 'code') await codeView(parts[1], q);
    else if (parts[0] === 'p') await provView(parts[1], parts.slice(2).join('/'));
    else if (parts[0] === 'review') await reviewView();
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
