// Which law governs? The module, the date tool, the land gates, worked problems, case files in memory,
// its place in the path, its cards on the provisions it rests on; and the corrected statute repeal flags.
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const SH = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    const U = 'http://localhost:8811/';
    await pg.goto(U, { waitUntil: 'networkidle' }); await pg.evaluate(() => localStorage.clear()); await pg.reload({ waitUntil: 'networkidle' });
    const go = async (h, f, wait = 700) => { await pg.goto(U + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(wait);
      if (f && tag === 'm') await pg.screenshot({ path: SH + 'g_' + f + '.png', fullPage: true });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    const ev = f => pg.evaluate(f);

    // the main page
    await go('#/govern', 'main', 900);
    let r = await ev(() => ({ h1: document.querySelector('h1')?.textContent, steps: document.querySelectorAll('.govm > li').length, rules: document.querySelectorAll('.govrule').length, probs: document.querySelectorAll('a[href^="#/govern/p/"]').length, crumbs: [...document.querySelectorAll('.crumbs a')].map(a => a.getAttribute('href')), next: document.querySelector('.pn .btn.primary')?.textContent }));
    console.log(tag, 'main', JSON.stringify(r));
    if (r.h1 !== 'Which law governs?' || r.steps !== 8 || r.rules !== 16 || r.probs < 6 || !r.crumbs.includes('#/map/craft') || !/Next in/.test(r.next || '')) errs.push(tag + ' main page ' + JSON.stringify(r));
    // the inline date tool: succession, death in 1949 -> Spanish Civil Code
    await pg.fill('#tmd', '1949-07-15'); await pg.dispatchEvent('#tmd', 'change'); await pg.waitForTimeout(150);
    r = await ev(() => ({ ans: document.querySelector('.tmans b')?.textContent, on: document.querySelector('.clock li.on .tc')?.textContent }));
    console.log(tag, 'tool 1949', JSON.stringify(r));
    if (!/Spanish Civil Code/.test(r.ans || '') || !/Spanish/.test(r.on || '')) errs.push(tag + ' date tool succession 1949');
    await pg.fill('#tmd', '1970-01-10'); await pg.dispatchEvent('#tmd', 'change'); await pg.waitForTimeout(150);
    r = await ev(() => document.querySelector('.tmans b')?.textContent);
    if (!/Civil Code \(RA 386\)/.test(r || '')) errs.push(tag + ' date tool succession 1970: ' + r);
    await pg.fill('#tmd', '2005-03-01'); await pg.dispatchEvent('#tmd', 'change'); await pg.waitForTimeout(150);
    r = await ev(() => document.querySelector('.tmans b')?.textContent);
    if (!/Family Code/.test(r || '')) errs.push(tag + ' date tool succession 2005: ' + r);
    // switch to imperfect titles, 2015 filing -> PD 1073 / 1945 cut-off; 2022 -> RA 11573
    await pg.selectOption('#tmk', 'imperfect'); await pg.fill('#tmd', '2015-05-05'); await pg.dispatchEvent('#tmd', 'change'); await pg.waitForTimeout(150);
    r = await ev(() => ({ ans: document.querySelector('.tmans b')?.textContent, ev: document.querySelector('#tmev')?.textContent }));
    console.log(tag, 'tool imperfect 2015', JSON.stringify(r));
    if (!/June 12, 1945/.test(r.ans || '') || !/filed/.test(r.ev || '')) errs.push(tag + ' date tool imperfect 2015');
    await pg.fill('#tmd', '2022-02-01'); await pg.dispatchEvent('#tmd', 'change'); await pg.waitForTimeout(150);
    r = await ev(() => document.querySelector('.tmans b')?.textContent);
    if (!/RA 11573/.test(r || '')) errs.push(tag + ' date tool imperfect 2022: ' + r);
    // a method step opens
    r = await ev(() => { const d = document.querySelectorAll('.govm details')[3]; d.querySelector('summary').click(); return d.open; });
    if (!r) errs.push(tag + ' method step does not open');

    // the standalone tool keeps its state in the address
    await go('#/govern/clock?k=agrarian&d=2009-07-15', 'clock', 900);
    r = await ev(() => ({ ans: document.querySelector('.tmans b')?.textContent, sel: document.querySelector('#tmk').value }));
    console.log(tag, 'clock page', JSON.stringify(r));
    if (r.sel !== 'agrarian' || !/RA 9700/.test(r.ans || '')) errs.push(tag + ' clock page from URL');
    await pg.fill('#tmd', '1975-01-01'); await pg.dispatchEvent('#tmd', 'change'); await pg.waitForTimeout(150);
    r = await ev(() => location.hash);
    if (!/k=agrarian&d=1975-01-01/.test(r)) errs.push(tag + ' clock URL not updated: ' + r);
    r = await ev(() => document.querySelector('.tmans b')?.textContent);
    if (!/PD 27/.test(r || '')) errs.push(tag + ' agrarian 1975: ' + r);
    // a date before every row says so
    await pg.selectOption('#tmk', 'corp'); await pg.fill('#tmd', '1900-01-01'); await pg.dispatchEvent('#tmd', 'change'); await pg.waitForTimeout(150);
    r = await ev(() => document.querySelector('.tmans')?.className);
    if (!/bad/.test(r || '')) errs.push(tag + ' corp 1900 should be outside the timeline');

    // a rule page with its drill
    await go('#/govern/r/t5', 'rule', 900);
    r = await ev(() => ({ h1: document.querySelector('h1')?.textContent, why: document.querySelectorAll('ol.explain li').length, cases: document.querySelectorAll('.case').length, chk: document.querySelectorAll('.case .chip.warn').length, quiz: !!document.querySelector('#gq'), links: [...document.querySelectorAll('.movev .chip.violet, .movev .chip.blue')].map(a => a.getAttribute('href')) }));
    console.log(tag, 'rule t5', JSON.stringify(r));
    if (!/Curative/.test(r.h1) || r.why < 2 || r.cases < 2 || r.chk < 1 || !r.links.includes('#/law/ra-11573') || !r.links.includes('#/p/pd1529/section-14')) errs.push(tag + ' rule page');
    // t4 has a drill: answer it and it joins memory
    await go('#/govern/r/t4', '', 900);
    await pg.click('#gq .opt[data-o="1"]'); await pg.waitForTimeout(200);
    r = await ev(() => { const k = Object.keys(localStorage).find(k => (localStorage.getItem(k) || '').includes('"cards"')); const st = k ? JSON.parse(localStorage.getItem(k)) : {}; return { res: (document.querySelector('#gq .qres')?.textContent || '').slice(0, 40), card: !!(st.cards || {})['q|gov:g5'] }; });
    console.log(tag, 'rule drill', JSON.stringify(r));
    if (!/Right/.test(r.res || '') || !r.card) errs.push(tag + ' rule drill grading or memory ' + JSON.stringify(r));

    // land gates
    await go('#/govern/land', 'land', 900);
    r = await ev(() => ({ gates: document.querySelectorAll('section.gate').length, rows: document.querySelectorAll('.gtab tbody tr').length, nav: document.querySelectorAll('.stagepath button').length, links: [...document.querySelectorAll('.gate a')].map(a => a.getAttribute('href')), next: document.querySelector('.pn .btn.primary')?.textContent, crumbs: [...document.querySelectorAll('.crumbs a')].map(a => a.textContent) }));
    console.log(tag, 'land', JSON.stringify({ ...r, links: r.links.length }));
    if (r.gates !== 7 || r.rows !== 10 || r.nav !== 7 || !r.links.includes('#/p/carl/section-50-a') || !r.links.includes('#/law/ra-11576')) errs.push(tag + ' land page');
    // deep link to a gate scrolls there
    await go('#/govern/land#g4', '', 900);
    r = await ev(() => Math.abs(document.getElementById('g4').getBoundingClientRect().top) < 200);
    if (!r) errs.push(tag + ' gate anchor did not scroll');

    // a worked problem reveals step by step, then the lesson
    await go('#/govern/p/p4', 'problem', 900);
    r = await ev(() => ({ hidden: document.querySelectorAll('.gsteps .sa[hidden]').length, lesson: document.querySelector('#lesson').hidden }));
    if (r.hidden !== 3 || !r.lesson) errs.push(tag + ' problem should start hidden ' + JSON.stringify(r));
    for (let k = 0; k < 3; k++) { await pg.click('[data-rev]'); await pg.waitForTimeout(60); }
    r = await ev(() => ({ hidden: document.querySelectorAll('.gsteps .sa[hidden]').length, lesson: document.querySelector('#lesson').hidden, txt: document.querySelector('.gsteps .sa').textContent.slice(0, 40) }));
    console.log(tag, 'problem p4', JSON.stringify(r));
    if (r.hidden !== 0 || r.lesson) errs.push(tag + ' problem reveal');

    // case files: all sixteen, graded, into memory; then they come back in review
    await go('#/govern/drills', 'drills', 700);
    const keyA = await ev(async () => (await (await fetch('data/govern.json')).json()).drills.map(d => d.a));
    for (let k = 0; k < 16; k++) {
      const a = await ev(() => { const q = document.querySelector('#gq'); return q ? 1 : -1; });
      if (a < 0) { errs.push(tag + ' drill missing at ' + k); break; }
      await pg.click(`#gq .opt[data-o="${keyA[k]}"]`); await pg.waitForTimeout(80);
      await pg.click('#nx'); await pg.waitForTimeout(120);
    }
    r = await ev(() => document.querySelector('.reviewcard h1')?.textContent);
    console.log(tag, 'drills score', r);
    if (r !== '16 of 16') errs.push(tag + ' drills: answered with the key, expected 16 of 16, got ' + r);
    // the options are not always in the authored order
    await go('#/govern/drills', '', 500);
    const orders = new Set(); for (let k = 0; k < 6; k++) { await pg.reload({ waitUntil: 'networkidle' }); await pg.waitForTimeout(250); orders.add(await ev(() => [...document.querySelectorAll('#gq .opt')].map(b => b.dataset.o).join(''))); }
    if (orders.size < 2) errs.push(tag + ' options never shuffle');
    r = await ev(() => { const k = Object.keys(localStorage).find(k => localStorage.getItem(k).includes('"cards"')); const s = JSON.parse(localStorage.getItem(k)); return Object.keys(s.cards).filter(x => x.startsWith('q|gov:')).length; });
    if (r !== 16) errs.push(tag + ' drills in memory: ' + r);
    // they come due in review: make one due now and open review
    await ev(() => { const k = Object.keys(localStorage).find(k => localStorage.getItem(k).includes('"cards"')); const s = JSON.parse(localStorage.getItem(k)); for (const x of Object.keys(s.cards)) if (x.startsWith('q|gov:')) s.cards[x].due = Date.now() - 1000; localStorage.setItem(k, JSON.stringify(s)); });
    await pg.reload({ waitUntil: 'networkidle' });
    await go('#/review', 'review', 1200);
    r = await ev(() => ({ kind: document.body.textContent.includes('which law governs'), quiz: !!document.querySelector('.quiz') }));
    console.log(tag, 'review', JSON.stringify(r));
    if (!r.kind || !r.quiz) errs.push(tag + ' governing-law case files do not appear in review');

    // the path: craft has the track, the civil field has the land gates after the land-title codes
    await go('#/map/craft', '', 900);
    r = await ev(() => [...document.querySelectorAll('a[href^="#/govern"]')].map(a => a.getAttribute('href')));
    if (!r.includes('#/govern') || !r.includes('#/govern/drills')) errs.push(tag + ' craft path lacks the track: ' + r.join(' '));
    await go('#/map/civ', '', 900);
    r = await ev(() => [...document.querySelectorAll('a[href^="#/govern"]')].map(a => a.getAttribute('href')));
    if (!r.includes('#/govern/land')) errs.push(tag + ' civil path lacks the land gates');
    // map root tile
    await go('#/map', '', 700);
    r = await ev(() => !!document.querySelector('.mapextra a[href="#/govern"]'));
    if (!r) errs.push(tag + ' map tile');

    // provision pages carry the card: Civil Code Art. 1116 and PD 1529 Sec. 14
    for (const [p, want] of [['#/p/civil/article-1116', '#/govern/land#g5'], ['#/p/pd1529/section-14', '#/govern/r/t5'], ['#/p/civil/article-2263', '#/govern/clock?k=succession']]) {
      await go(p, '', 1200);
      await ev(() => { const t = [...document.querySelectorAll('.tabs button, [data-tab]')].find(b => /Cases/.test(b.textContent)); if (t) t.click(); });
      await pg.waitForTimeout(300);
      r = await ev(() => [...document.querySelectorAll('.panel .movecard')].map(a => a.getAttribute('href')));
      console.log(tag, p, r.length);
      if (!r.includes(want)) errs.push(tag + ' ' + p + ' lacks the governing-law card ' + want + ' (has ' + r.join(' ') + ')');
    }

    // search finds the rules
    await go('#/search?q=curative', '', 1500);
    r = await ev(() => [...document.querySelectorAll('a[href^="#/govern"]')].map(a => a.getAttribute('href')));
    if (!r.includes('#/govern/r/t5')) errs.push(tag + ' search "curative" ' + r.join(' '));

    // the statute library no longer calls the core codes repealed
    for (const id of ['act-3815', 'ra-7160', 'ra-8424', 'pd-442', 'bp-881']) {
      await go('#/law/' + id, '', 1500);
      r = await ev(() => [...document.querySelectorAll('.lawv .chip.bad')].some(c => /Repealed \(detected/.test(c.textContent)));
      if (r) errs.push(tag + ' ' + id + ' still shows Repealed');
    }
    await go('#/law/ra-9184', '', 1500);
    r = await ev(() => [...document.querySelectorAll('.lawv .chip.bad')].some(c => /Repealed \(detected/.test(c.textContent)));
    if (!r) errs.push(tag + ' RA 9184 should show Repealed (by RA 12009)');
    // a later amendment brought into the study text: PD 1529 Sec. 14 now reads as RA 11573 has it
    await go('#/p/pd1529/section-14', '', 1200);
    r = await ev(() => document.querySelector('main').textContent.includes('twenty (20) years'));
    if (!r) errs.push(tag + ' PD 1529 Sec. 14 not in its RA 11573 text');
    // CARL now has Sec. 50-A
    await go('#/p/carl/section-50-a', '', 1200);
    r = await ev(() => document.querySelector('main').textContent.includes('Exclusive Jurisdiction on Agrarian Dispute'));
    if (!r) errs.push(tag + ' CARL Sec. 50-A missing');
    await pg.close();
  }
  await b.close();
  console.log(errs.length ? 'FAIL\n' + errs.join('\n') : 'PASS');
  process.exit(errs.length ? 1 : 0);
})();
