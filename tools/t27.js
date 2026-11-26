// Proofreading regression checks on the built data (no browser needed).
const fs = require('fs');
const D = '/home/claude/site/data/codes/';
const load = id => JSON.parse(fs.readFileSync(D + id + '.json', 'utf8'));
const errs = [];
const text = p => [p.c || ''].concat(p.p.filter(x => typeof x === 'string'), (p.a || []).flatMap(a => a.p.filter(x => typeof x === 'string'))).join(' \n ');
const find = (d, n) => d.provisions.find(p => p.n === n);
function has(id, n, s) { const d = load(id); const p = find(d, n); if (!p || !text(p).includes(s)) errs.push(`${id} ${n}: missing “${s}”`); }
function hasnt(id, n, s) { const d = load(id); const p = find(d, n); if (p && text(p).includes(s)) errs.push(`${id} ${n}: still has “${s}”`); }

// slips fixed in LawPhil-sourced texts
has('pd1083', '27', 'not more than four at a time, no Muslim male can have more than one wife');
has('pd1083', '32', 'marad-ul-maut');
has('rpc', '21', 'No felony shall be punishable by any penalty');
hasnt('rpc', '21', 'imposed. be');
has('rpc', '150', 'ranging from 200 to 1,000 pesos');
has('nil', '47', 'An instrument negotiable in its origin continues to be negotiable');
has('nirc', '113', 'in lieu of');
has('ra11165', '6', 'data protection');
has('ra9285', '46', 'appellate court');
hasnt('rcc', '145', 'with he Commission');

// Administrative Code: OCR debris, headings, a table, misprints noted
const ac = load('admincode');
const all = ac.provisions.map(text).join('\n');
for (const junk of ['Cuaprer', 'Cuapter', 'SSSS', 'heb ema kegs', 'perauan', 'ternat scutive', 'Punoaited', 'Starr', ' ee! ea', '} Staff', 'shall]'])
  if (all.includes(junk) || ac.divisions.some(d => d.t.includes(junk))) errs.push('admincode still has ' + junk);
for (const t of ['D — Presidential Assistants/Advisers System', 'Chapter 3 — Department Services', 'Chapter 4 — Budget Authorization', 'Chapter 2 — Rules and Regulations', 'A — The Private Office'])
  if (!ac.divisions.some(d => d.t === t)) errs.push('admincode heading missing: ' + t);
const byId = Object.fromEntries(ac.provisions.map(p => [p.i, p]));
if (!byId['book-iv-ch-3-sec-12']) errs.push('Book IV, Ch. 3, Sec. 12 not under Chapter 3');
if ((ac.alias || {})['book-iv-ch-2-sec-12'] !== 'book-iv-ch-3-sec-12') errs.push('alias for the moved Book IV sections missing');
const s31 = byId['book-iv-title-i-sec-31'];
if (!s31 || !s31.p.some(x => x && x.rows && x.rows.length === 5)) errs.push('Book IV, Title I, Sec. 31 table not set out');
if (!text(byId['book-ii-sec-19']).includes('security of tenure of its Members') || !(byId['book-ii-sec-19'].e || []).some(e => /printed copy/.test(e.t))) errs.push('Book II, Sec. 19 misprint not corrected with a note');
if (!/Done in the City of Manila/.test((ac.closing || []).join(' '))) errs.push('signing clause not in the closing');
for (const p of ac.provisions) for (const x of p.p) if (typeof x === 'string' && !/[A-Za-z]{3,}/.test(x) && !/\(\w{1,4}\)/.test(x)) errs.push('debris paragraph left in ' + p.i + ': ' + x);

// every spelling entry applied
const pr = JSON.parse(fs.readFileSync('/home/claude/site/data/proofreading.json', 'utf8'));
const miss = pr.errata.filter(e => e.op && /^(spelling|ocr-|heading)/.test(e.op) && !e.applied);
if (miss.length) errs.push('proofreading entries not applied: ' + miss.map(e => e.code + ' ' + e.note).join('; '));

console.log(errs.length ? 'FAIL\n' + errs.join('\n') : 'NO ERRORS');
