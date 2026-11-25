"""One-off patch: turns the codal app into the field / path / figure design. Run once against assets/app.js."""
import sys
P = sys.argv[1]
s = open(P).read()


def rep(old, new, count=1):
    global s
    assert old in s, old[:90]
    s = s.replace(old, new, count)


def cut(start, end):
    a = s.index(start); b = s.index(end, a)
    return a, b


# ---- defaults
rep("const DEFAULTS = { cards: {}, notes: {}, marks: {}, flags: {}, days: {}, last: null, tutor: {},\n  settings: { newPerDay: 15,",
    "const DEFAULTS = { cards: {}, notes: {}, marks: {}, flags: {}, days: {}, last: null, tutor: {}, hooks: {}, lessons: {}, lastBy: {},\n  settings: { newPerDay: 10, focus: null, figure: '',")
rep("for (const f of ['notes', 'marks', 'flags', 'tutor']) Object.assign(S[f], o[f] || {});",
    "for (const f of ['notes', 'marks', 'flags', 'tutor', 'hooks', 'lessons', 'lastBy']) Object.assign(S[f], o[f] || {});")

# ---- curriculum loader + figure
rep("const COURSE = {", r"""let CUR = null;
async function loadCur() {
  if (!CUR) { CUR = await getJSON('data/curriculum.json?v=' + (CAT.chash || CAT.built)); CUR.byId = Object.fromEntries(CUR.fields.map(f => [f.id, f])); }
  return CUR;
}
const fieldOf = cid => CUR.byId[CUR.homes[cid]];
const focusIds = () => (S.settings.focus && S.settings.focus.length ? S.settings.focus : CUR.focus);
const figName = () => (S.settings.figure || '').trim() || 'the Advocate';
const fieldCodes = f => f.tracks.flatMap(t => t.items.filter(i => i.t === 'code' && !i.x).map(i => i.id));
function fieldCount(f) { let total = 0, touched = 0, m = 0; for (const id of fieldCodes(f)) { const k = counts(id); total += k.total; touched += k.touched; m += k.m; } return { total, touched, m, pct: total ? touched / total * 100 : 0 }; }
const rich = t => esc(t).replace(/⟦([^|⟧]+)\|([^|⟧]+)\|([^⟧]+)⟧/g, (m, c, i, l) => `<a class="pref" href="#/p/${c}/${i}">${l}</a>`);
/* The memory figure: one standing figure, read head to toe. Each field of law has a fixed place on it. */
function figure(active) {
  const z = (id, n, shape, bx, by) => `<a class="zone f-${id}${active === id ? ' on' : ''}" href="#/field/${id}" aria-label="${esc(CUR.byId[id].name)}: ${esc(CUR.byId[id].pname)}">${shape}<circle class="num" cx="${bx}" cy="${by}" r="10"/><text x="${bx}" y="${by}">${n}</text></a>`;
  return `<svg class="fig${active ? ' dim' : ''}" viewBox="0 0 200 404" role="img" aria-label="The memory figure: eight fields of law on eight parts of the body">
    <rect class="skin" x="91" y="70" width="18" height="18" rx="4"/>
    <path class="skin" d="M58 98 Q100 84 142 98 L134 226 Q100 234 66 226 Z"/>
    <path class="skin2" stroke-width="17" d="M58 104 L37 222 M142 104 L163 222"/>
    <path class="skin2" stroke-width="23" d="M84 232 L80 372 M116 232 L120 372"/>
    ${z('pol', 1, '<circle class="fillf" cx="100" cy="46" r="28"/>', 140, 22)}
    ${z('craft', 2, '<rect class="fillf" x="74" y="36" width="52" height="12" rx="6"/><rect class="fillf" x="90" y="58" width="20" height="5" rx="2.5"/>', 58, 42)}
    ${z('lab', 3, '<path class="strokef" stroke-width="15" d="M54 102 Q100 82 146 102"/>', 160, 84)}
    ${z('eth', 4, '<path class="fillf" d="M112 140 l-13 -13 a8 8 0 0 1 13 -9 a8 8 0 0 1 13 9 z"/>', 137, 136)}
    ${z('civ', 7, '<rect class="fillf" x="62" y="212" width="76" height="15" rx="4"/>', 100, 219.5)}
    ${z('crim', 5, '<circle class="fillf" cx="35" cy="236" r="13"/>', 14, 250)}
    ${z('com', 6, '<circle class="fillf" cx="165" cy="236" r="13"/>', 186, 250)}
    ${z('intl', 8, '<ellipse class="fillf" cx="73" cy="386" rx="21" ry="10"/><ellipse class="fillf" cx="127" cy="386" rx="21" ry="10"/>', 100, 388)}
  </svg>`;
}
function partsList() {
  const foc = focusIds();
  return `<ol class="parts">${CUR.fields.map(f => { const k = fieldCount(f); const lb = S.lastBy[f.id]; return `<li class="f-${f.id}${foc.includes(f.id) ? '' : ' off'}"><a href="#/field/${f.id}"><span class="n">${f.n}</span><span><span class="t">${esc(f.name)}</span><br><span class="p">${esc(f.pname)}</span>${lb ? ` <span class="tiny muted">· last: ${esc(lb.l)}</span>` : ''}</span><span class="pct">${k.touched ? k.touched.toLocaleString() + ' studied' : ''}</span></a></li>`; }).join('')}</ol>`;
}
async function nameFigure() {
  const t = await askText('Name your figure', S.settings.figure || '', 'A name you will remember. Picture him or her as vividly as you can.');
  if (t === null) return false; S.settings.figure = t.trim().slice(0, 40); save(); return true;
}
async function chooseFocus() {
  const foc = focusIds();
  return new Promise(res => {
    const m = modal(`<h3>This semester</h3><p class="small muted">Tick the fields you are taking now. The others stay available but step back.</p><div class="stack" style="gap:6px">${CUR.fields.map(f => `<label class="f-${f.id}"><input type="checkbox" value="${f.id}" ${foc.includes(f.id) ? 'checked' : ''}> <b>${esc(f.name)}</b> <span class="tiny muted">${esc(f.pname)}</span></label>`).join('')}</div><div class="row" style="margin-top:12px;justify-content:flex-end"><button class="btn" id="mno">Cancel</button><button class="btn primary" id="mok">Save</button></div>`);
    $('#mno', m.el).onclick = () => { m.close(); res(false); };
    $('#mok', m.el).onclick = () => { S.settings.focus = $$('input:checked', m.el).map(i => i.value); save(); m.close(); res(true); };
  });
}
const COURSE = {""")

# ---- crumbs
a, b = cut("function crumbs(d, p, cid) {", "function shortDiv(t)")
s = s[:a] + r"""function crumbs(d, p, cid) {
  const chain = []; let v = p ? p.d : null;
  while (v != null) { chain.unshift(v); v = d.divisions[v].p; }
  const f = fieldOf(cid);
  return `<div class="crumbs"><a href="#/learn">Learn</a>${f ? `<span class="sep">›</span><a href="#/field/${f.id}">${esc(f.name)}</a>` : ''}<span class="sep">›</span><a href="#/code/${cid}">${esc(d.short)}</a>${chain.slice(-2).map(i => `<span class="sep">›</span><a href="#/code/${cid}?div=${i}">${esc(shortDiv(d.divisions[i].t))}</a>`).join('')}</div>`;
}
""" + s[b:]

# ---- home + learn + field + lesson + set + library
a, b = cut("async function home() {", "function tocHTML(d, cid, openDiv) {")
s = s[:a] + r"""async function home() {
  setNav('home');
  const due = dueKeys().length, nt = newToday(), st = streak();
  const last = S.last;
  let head, sub, btn, second = '';
  if (due) { head = `${due} provision${due === 1 ? ' is' : 's are'} due for review`; sub = `About ${Math.max(1, Math.ceil(due * 0.75))} minutes. Recall each one before you look.`; btn = `<a class="btn primary" href="#/review">Review now</a>`; if (last) second = `<a class="btn" href="#/p/${last.c}/${last.p}">Continue ${esc(last.l)}</a>`; }
  else if (last) { head = `Continue where you stopped`; sub = esc(last.l); btn = `<a class="btn primary" href="#/p/${last.c}/${last.p}">Continue</a>`; second = `<a class="btn" href="#/learn">Choose a field</a>`; }
  else { head = 'Start with ten minutes'; sub = 'One short lesson on how to read any provision. It makes everything after it easier.'; btn = `<a class="btn primary" href="#/lesson/read-provision">Read the first lesson</a>`; second = `<a class="btn" href="#/learn">Choose a field</a>`; }
  main.innerHTML = `
  <section class="next"><span class="eyebrow">Your next step</span><h1>${head}</h1><p class="muted" style="margin:0">${sub}</p>
    <div class="row">${btn}${second}</div>
    <div class="meters"><span><b>${due}</b> due</span><span><b>${nt}</b> of ${S.settings.newPerDay} new today</span><span><b>${st}</b> day streak</span><a href="#/progress">Progress</a></div></section>
  <div class="sect"><h2>The body of law</h2><span class="spacer"></span><button class="btn sm ghost" id="foc">This semester</button><button class="btn sm ghost" id="nm">Name the figure</button></div>
  <p class="small muted" style="margin:-4px 0 12px;max-width:65ch">Eight fields, eight places on ${esc(figName())}, read from head to toe. A fixed place is a fixed cue: when you forget, walk down the body.</p>
  <div class="bodymap">${figure()}${partsList()}</div>
  <div class="more"><a href="#/syllabus">Syllabus cases</a><a href="#/syllabus/recent">Recent rulings</a><a href="#/drill">Drill</a><a href="#/search">Find a case</a><a href="#/about">How this works</a></div>`;
  $('#foc').onclick = async () => { if (await chooseFocus()) home(); };
  $('#nm').onclick = async () => { if (await nameFigure()) home(); };
}

function learn() {
  setNav('library');
  const foc = focusIds();
  const tile = f => { const k = fieldCount(f); const lb = S.lastBy[f.id]; const first = f.tracks[0].items[0];
    const start = first.t === 'code' ? meta(first.id).short : first.t === 'lesson' ? CUR.lessons[first.id].title : first.title || '';
    return `<a class="tile f-${f.id}" href="#/field/${f.id}"><span class="p">${f.n} · ${esc(f.pname)}</span><span class="t">${esc(f.name)}</span><span class="q">${esc(f.q)}</span><div class="thin"><i style="width:${Math.min(100, k.pct).toFixed(1)}%"></i></div><span class="go">${lb ? `Continue: <b>${esc(lb.l)}</b>` : `Start here: <b>${esc(start)}</b>`}</span></a>`; };
  const mine = CUR.fields.filter(f => foc.includes(f.id)), rest = CUR.fields.filter(f => !foc.includes(f.id));
  main.innerHTML = `<h1>Learn</h1><p class="lead">Pick one field. Inside it you will find a short path: start here, then the core, then deeper only when you need it.</p>
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
    return `${head}<details class="track" ${t.tier === 'deep' ? '' : 'open'}><summary><span class="tn">${esc(t.name)}</span><span class="cnt">${n} item${n === 1 ? '' : 's'}</span><span class="pic">Picture: ${esc(t.pic)}</span>${t.why ? `<span class="why">${esc(t.why)}</span>` : ''}</summary><ul class="items">${t.items.map(i => itemRow(i, f)).join('')}</ul></details>`;
  }).join('');
  main.innerHTML = `<div class="f-${f.id}"><div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><span>${esc(f.name)}</span></div>
  <div class="fhead"><div><span class="eyebrow" style="color:var(--f)">${f.n} · ${esc(f.pname)}</span><h1>${esc(f.name)}</h1><p class="hook" style="margin:0 0 6px">${esc(f.hook)}</p><p class="small" style="margin:0 0 10px">${esc(f.q)}</p>
    <div class="thin" style="max-width:320px"><i style="width:${Math.min(100, k.pct).toFixed(1)}%"></i></div><p class="tiny muted" style="margin:6px 0 10px">${k.touched.toLocaleString()} of ${k.total.toLocaleString()} provisions studied</p>
    ${lb ? `<a class="btn primary" href="#/p/${lb.c}/${lb.p}">Continue ${esc(lb.l)}</a>` : ''}</div>${figure(f.id)}</div>
  <div class="path">${tracks}</div></div>`;
}
function findItem(type, id) { for (const f of CUR.fields) for (const t of f.tracks) { const ix = t.items.findIndex(i => i.t === type && i.id === id); if (ix >= 0) return { f, t, ix }; } return null; }
function lessonView(id) {
  setNav('library');
  const l = CUR.lessons[id]; if (!l) return learn();
  const at = findItem('lesson', id); const f = at.f; const nx = at.t.items[at.ix + 1];
  const nxLink = nx && nx.t !== 'missing' ? (nx.t === 'code' ? [`#/code/${nx.id}`, meta(nx.id).short] : nx.t === 'lesson' ? [`#/lesson/${nx.id}`, CUR.lessons[nx.id].title] : nx.t === 'set' ? [`#/set/${nx.id}`, CUR.sets[nx.id].title] : [`#/syllabus/${nx.id}`, nx.title]) : null;
  main.innerHTML = `<article class="lesson f-${f.id}"><div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><a href="#/field/${f.id}">${esc(f.name)}</a><span class="sep">›</span><span>${esc(at.t.name)}</span></div>
  <span class="eyebrow" style="color:var(--f)">Lesson · ${l.mins} minutes</span><h1>${esc(l.title)}</h1><p class="lead">${rich(l.lead)}</p>
  ${l.sections.map(x => `<h2>${esc(x.h)}</h2><div class="explain">${x.p.map(p => `<p>${rich(p)}</p>`).join('')}${x.l.length ? `<ul>${x.l.map(p => `<li>${rich(p)}</li>`).join('')}</ul>` : ''}</div>`).join('')}
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
  <div class="tryit small" style="margin:12px 0"><b>How to use the walk.</b> Start at the crown of ${esc(figName())} and move down. At each place, see the provision’s key idea happening on that part of the body, the stranger the better. To recall the list later, walk down the body again and say what you find at each place.</div>
  <ol class="walk">${st.items.map(x => `<li><a href="#/p/${x.c}/${x.i}?set=${id}"><span class="loc">${esc(x.loc)}</span><span><span class="wl">${esc(x.l)}</span>${x.cap ? ` <span class="muted small">${esc(x.cap)}</span>` : ''}<br><span class="ww">${esc(x.why)}</span>${S.hooks[ck(x.c, x.i)] ? `<br><span class="tiny" style="color:var(--warn)">Your picture: ${esc(S.hooks[ck(x.c, x.i)])}</span>` : ''}</span><i class="dot ${status(ck(x.c, x.i))}"></i></a></li>`).join('')}</ol>
  <div class="pn"><a class="btn" href="#/field/${f.id}">Back to ${esc(f.name)}</a><a class="btn primary" href="#/p/${first.c}/${first.i}?set=${id}">Start the walk →</a></div></div>`;
}

function library() {
  setNav('library');
  main.innerHTML = `<div class="crumbs"><a href="#/learn">Learn</a><span class="sep">›</span><span>All codes</span></div><h1>All codes</h1><p class="muted">Every instrument in the library, by field. Open a field to see its list.</p>
  <div class="path">${CUR.fields.map(f => { const ids = fieldCodes(f); return `<details class="track f-${f.id}"><summary><span class="tn">${esc(f.name)}</span><span class="cnt">${ids.length} codes</span></summary><ul class="items">${ids.map(id => itemRow({ t: 'code', id }, f)).join('')}</ul></details>`; }).join('')}</div>`;
}

""" + s[b:]

# ---- code view: next sitting
rep("""<a class="btn" href="#/drill?code=${cid}">Drill</a></div></div>
      ${d.note ?""", """<a class="btn" href="#/drill?code=${cid}">Drill</a></div>
        ${sitting.length > 1 ? `<h3 style="margin:14px 0 4px">Your next sitting</h3><p class="tiny muted" style="margin:0 0 6px">Five provisions at a time is enough. Stop there and review tomorrow.</p><ul class="plist sitting" style="padding:0">${sitting.map(p => `<li><a href="#/p/${cid}/${p.i}"><span class="pl">${esc(p.l)}</span><span class="pc">${esc(p.c || firstWords(p))}</span></a></li>`).join('')}</ul>` : ''}</div>
      ${d.note ?""")
rep("""  const next = d.provisions.find(p => !S.cards[ck(cid, p.i)]);
  const openDiv""", """  const next = d.provisions.find(p => !S.cards[ck(cid, p.i)]);
  const sitting = next ? d.provisions.slice(next.ix).filter(p => !S.cards[ck(cid, p.i)]).slice(0, 5) : [];
  const openDiv""")

# ---- provision view
rep("async function provView(cid, pid) {", "async function provView(cid, pid, q) {")
rep("""  S.last = { c: cid, p: pid, l: `${d.short} · ${p.l}` }; save();
  const prev = d.provisions[p.ix - 1], next = d.provisions[p.ix + 1];""", """  S.last = { c: cid, p: pid, l: `${d.short} · ${p.l}` };
  const fld = fieldOf(cid); if (fld) S.lastBy[fld.id] = { c: cid, p: pid, l: `${d.short} · ${p.l}` };
  save();
  let prev = d.provisions[p.ix - 1], next = d.provisions[p.ix + 1];
  const setId = q && q.get('set'); const st = setId && CUR.sets[setId]; let setBar = '', sfx = '', loc = '';
  const href = x => `#/p/${x.c || cid}/${x.i}${sfx}`;
  if (st) {
    const ix = st.items.findIndex(x => x.c === cid && x.i === pid);
    if (ix >= 0) { sfx = `?set=${setId}`; prev = st.items[ix - 1]; next = st.items[ix + 1]; loc = st.items[ix].loc;
      setBar = `<div class="setbar"><span>${esc(st.title)}</span><span>${ix + 1} of ${st.items.length}</span><span>Place: ${esc(loc)}</span><span class="spacer"></span><a href="#/set/${setId}">See the whole walk</a></div>`; }
  }""")
a, b = cut("  const tabs = [['guide', 'Study guide']", "  <aside class=\"side\">")
s = s[:a] + r"""  const tabs = [['guide', 'Step 2', 'Understand'], ['recall', 'Step 3', 'Recall'], ['cases', 'Step 4', `Cases${ncase ? ' (' + ncase + ')' : ''}${rec.length ? ' <span class="newdot" title="has 2023–2026 rulings">new</span>' : ''}`], ['notes', 'Yours', 'My notes']];
  main.innerHTML = `${crumbs(d, p, cid)}${setBar}
  <div class="pv"><div>
    <div class="row" style="margin-bottom:8px"><span class="eyebrow">Step 1 · Read</span><span class="spacer"></span><details class="hlbox"><summary>Highlights</summary><div class="legend">${HLORDER.map(k => `<label><input type="checkbox" data-hl="${k}" ${on[k] ? 'checked' : ''}><span class="${HLCLASS[k]}">${HLNAME[k]}</span></label>`).join('')}</div></details></div>
    <div id="lawbox">${lawHTML(d, p, cid, on)}</div>
    <div class="steps" role="tablist">${tabs.map(([k, sm, n], i) => `<button role="tab" data-tab="${k}" class="${i ? '' : 'on'}"><small>${sm}</small><span>${n}</span></button>`).join('')}</div>
    <div id="tabbox"></div>
    <div class="pn">${prev ? `<a class="btn" href="${href(prev)}">← ${esc(prev.l)}</a>` : '<span></span>'}${next ? `<a class="btn primary" href="${href(next)}">${esc(next.l)} →</a>` : (sfx ? `<a class="btn primary" href="#/set/${setId}">Finish the walk</a>` : '')}</div>
  </div>
""" + s[b:]
rep("$$('.tabs button').forEach(b => b.classList.toggle('on', b.dataset.tab === k)); renderTab(k); };", "$$('.steps button').forEach(b => b.classList.toggle('on', b.dataset.tab === k)); renderTab(k); };")
rep("""    if (k === 'recall') recallPanel(tabbox, d, p, cid);
    if (k === 'guide') wireTutor(d, p, cid, cases);""", """    if (k === 'recall') { recallPanel(tabbox, d, p, cid); if (S.hooks[key]) $('.panel', tabbox).insertAdjacentHTML('afterbegin', `<div class="hookcue"><b>Your picture:</b> ${esc(S.hooks[key])}</div>`); }
    if (k === 'guide') { wireTutor(d, p, cid, cases); const hk = $('#hookin'); if (hk) hk.addEventListener('input', e => { const v = e.target.value.trim(); if (v) S.hooks[key] = v.slice(0, 200); else delete S.hooks[key]; save(); }); }""")
rep("$$('.tabs button').forEach(b => b.onclick = () => show(b.dataset.tab));", "$$('.steps button').forEach(b => b.onclick = () => show(b.dataset.tab));")
rep("if (next) setTimeout(() => location.hash = `#/p/${cid}/${next.i}`, 450); });", "if (next) setTimeout(() => location.hash = href(next), 450); });")
rep("if (k === 'guide') tabbox.innerHTML = guideHTML(d, p, cid, notes);", "if (k === 'guide') tabbox.innerHTML = guideHTML(d, p, cid, notes, loc);")
rep("save(); provView(cid, pid);", "save(); provView(cid, pid, q);")
rep("""function guideHTML(d, p, cid, n) {
  const an = anatomy(p);
  let h = '<div class="panel">';""", """function guideHTML(d, p, cid, n, loc) {
  const an = anatomy(p);
  const fld = fieldOf(cid); const key = ck(cid, p.i);
  let h = '<div class="panel">';
  h += `<div class="card flat hook" style="margin-bottom:12px"><div class="row"><h3 style="margin:0">Make it a picture</h3><span class="spacer"></span>${fld ? `<span class="chip f-${fld.id}" style="background:color-mix(in srgb,var(--f) 14%,transparent);color:var(--f)">${esc(fld.pname)}</span>` : ''}</div>
    <p class="small muted" style="margin:0">${loc ? `This provision sits at the <b>${esc(loc.toLowerCase())}</b> of ${esc(figName())}.` : fld ? `${esc(fld.name)} lives at the ${esc(fld.pname.toLowerCase())} of ${esc(figName())}.` : ''} In a few words, what do you see happening there that stands for this rule? Odd pictures last longest.</p>
    <input id="hookin" maxlength="200" value="${esc(S.hooks[key] || '')}" placeholder="e.g. a stopwatch strapped to the wrist: three months to decide" aria-label="Your picture for this provision"></div>`;""")
rep('<h3 style="margin:0">Reading guide</h3>', '<h3 style="margin:0">Take it apart</h3>')

# ---- recent view grouping by field
rep("items.forEach(x => { const s = (meta(x.ks[0].split('|')[0]) || {}).subject || 'oth'; (bySubj[s] = bySubj[s] || []).push(x); });",
    "items.forEach(x => { const s = CUR.homes[x.ks[0].split('|')[0]] || 'pol'; (bySubj[s] = bySubj[s] || []).push(x); });")
rep("""${CAT.subjects.filter(s => bySubj[s.id]).map(s => `<div class="subject"><h2>${esc(s.name)}</h2></div>""", """${CUR.fields.filter(s => bySubj[s.id]).map(s => `<div class="sect"><h2>${esc(s.name)}</h2></div>""")
rep('<div class="subject"><h2>Rules of conduct (not in the codal library)</h2></div>', '<div class="sect"><h2>Rules of conduct (not in the codal library)</h2></div>')

# ---- review empty state
rep('<a class="btn primary" href="#/library">Learn new provisions</a>', '<a class="btn primary" href="#/learn">Learn new provisions</a>')
rep("New provisions enter review once you open them in the Library.", "New provisions enter review once you open them under Learn.")

# ---- about
a, b = cut("  <h2>How to study here</h2>", "  <h2>Sources</h2>")
s = s[:a] + r"""  <h2>How this is designed</h2>
  <ol class="explain"><li><b>One next step.</b> Today shows a single thing to do. New provisions are capped at a small number a day; you can change it under Progress.</li>
  <li><b>Eight fields on one figure.</b> Each field of law has a fixed place on the body, head to toe, and each topic inside a field is one object at that place. Fixed places give you somewhere to look when you forget.</li>
  <li><b>A short path in each field.</b> Start here, then the core, then deeper only when you need it. A code page offers five provisions at a time.</li>
  <li><b>Four steps on each provision.</b> Read the verbatim text. Understand it by taking it apart and making your own picture. Recall it with the text hidden. Connect it to cases. Then rate yourself, and Review brings it back just before you would forget it.</li></ol>
  <h2>The memory research behind it</h2>
  <ul class="explain small"><li><b>Places and pictures.</b> Tying items to fixed locations (the method of loci; a body is one such set of places) reliably improves recall, including in people with no prior training (Dresler and others, <i>Neuron</i>, 2017). Pictures are remembered better than words alone, and words paired with an image are stored twice (Paivio’s dual coding; Shepard, 1967; Standing, 1973).</li>
  <li><b>Small groups.</b> Working memory holds only a few chunks at a time (Miller, 1956, written at Harvard; Cowan, 2001, puts it near four), which is why fields, paths and sittings are kept short.</li>
  <li><b>Make it yourself.</b> Material you generate is remembered better than material you only read (Slamecka and Graf, 1978), so the app asks for your own picture and your own words.</li>
  <li><b>Recall, spaced and mixed.</b> Retrieving from memory beats re-reading (Roediger and Karpicke, 2006); spacing reviews over days beats cramming (Cepeda and others, 2006); mixing topics in practice beats blocking them (Rohrer and Taylor, 2007).</li></ul>
  <p class="small muted">These are general findings about memory, not studies of this app. The pictures suggested for each topic are our own inventions; replace any that do not stick with your own.</p>
""" + s[b:]

# ---- router
rep("""    if (!parts[0]) await home();
    else if (parts[0] === 'library') library();""", """    if (!CUR) await loadCur();
    if (!parts[0]) await home();
    else if (parts[0] === 'learn') learn();
    else if (parts[0] === 'field') fieldView(parts[1]);
    else if (parts[0] === 'lesson') lessonView(parts[1]);
    else if (parts[0] === 'set') setView(parts[1]);
    else if (parts[0] === 'library') library();""")
rep("else if (parts[0] === 'p') await provView(parts[1], parts.slice(2).join('/'));", "else if (parts[0] === 'p') await provView(parts[1], parts.slice(2).join('/'), q);")
open(P, 'w').write(s)
print('patched')
