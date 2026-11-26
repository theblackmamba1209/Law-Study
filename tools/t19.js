// Sprint + FSRS memory model: seeded progress, a full sprint on mobile and desktop, migration of SM-2 cards
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const SH = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    pg.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(tag + ' console ' + m.text()); });
    await pg.goto('http://localhost:8811/', { waitUntil: 'networkidle' });
    const DAY = 86400000, now = Date.now();
    await pg.evaluate(([DAY, now]) => {
      const cards = {
        'rpc|article-4': { ease: 2.5, ivl: 6, reps: 2, lapses: 0, due: now - DAY, last: now - 7 * DAY, seen: now - 20 * DAY },          // SM-2 card, overdue
        'rpc|article-11': { ease: 1.9, ivl: 0, reps: 0, lapses: 5, due: now - 3600000, last: now - 2 * DAY, seen: now - 30 * DAY },    // SM-2 lapsed leech
        'civil|article-1156': { s: 3, d: 5, ivl: 3, reps: 1, lapses: 0, due: now - DAY, last: now - 4 * DAY, seen: now - 4 * DAY },     // FSRS card, overdue
        'ra7080|section-2': { reps: 0, lapses: 0, seen: now - 3600000 },                                                                 // opened, never rated
      };
      localStorage.setItem('sinag.codal.v1', JSON.stringify({ cards, hooks: { 'rpc|article-11': 'a judge pardoning a man in a cell' }, last: { c: 'rpc', p: 'article-11', l: 'RPC · Article 11' }, settings: { newPerDay: 10 } }));
    }, [DAY, now]);
    await pg.reload({ waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
    const home = await pg.evaluate(() => ({ head: document.querySelector('.next h1')?.textContent, btn: document.querySelector('.next .btn.primary')?.getAttribute('href'), meters: document.querySelector('.meters')?.textContent }));
    console.log(tag, 'home', JSON.stringify(home));
    if (home.btn !== '#/sprint') errs.push(tag + ' home primary is not the sprint');
    if (!/% recall/.test(home.meters || '')) errs.push(tag + ' no recall meter');
    await pg.click('.next .btn.primary'); await pg.waitForTimeout(700);
    const seen = [];
    for (let k = 0; k < 14; k++) {
      const st = await pg.evaluate(() => ({ prompt: document.querySelector('.sprint .prompt')?.textContent, isNew: !!document.querySelector('.newtag'), focus: document.body.classList.contains('focus'), done: !!document.querySelector('.sprintdone'), top: getComputedStyle(document.querySelector('.top')).display }));
      if (st.done) break;
      if (!st.focus || st.top !== 'none') errs.push(tag + ' focus mode off during sprint');
      seen.push((st.isNew ? 'NEW ' : '') + st.prompt);
      if (k === 0) await pg.screenshot({ path: SH + tag + 'sprint1.png', fullPage: true });
      if (st.isNew) {
        await pg.click('#sptest'); await pg.waitForTimeout(250);
        const ta = await pg.$('#frt');
        if (ta) { await ta.fill('Any public officer who amasses ill-gotten wealth of at least fifty million pesos'); await pg.click('#frc'); }
        else { const ins = await pg.$$('#sprv input[data-a]'); for (const i of ins) await i.fill('x'); await pg.click('#cc'); }
        await pg.waitForTimeout(250);
        if (k < 3) await pg.screenshot({ path: SH + tag + 'sprintnew.png', fullPage: true });
        await pg.click('#sprv [data-rate="3"]');
      } else {
        if (await pg.$('#sphook')) { await pg.click('#sphook'); const h = await pg.textContent('#spaux'); if (!/judge pardoning/.test(h)) errs.push(tag + ' hook not shown'); }
        await pg.keyboard.press(' '); await pg.waitForTimeout(200);
        const intervals = await pg.$$eval('[data-rate] small', xs => xs.map(x => x.textContent));
        if (k === 1) { console.log(tag, 'intervals', intervals.join(' ')); await pg.screenshot({ path: SH + tag + 'sprintshow.png', fullPage: true }); }
        // miss the first review once to check in-sprint relearning, pass everything else
        await pg.keyboard.press(k === 0 ? '1' : '3');
      }
      await pg.waitForTimeout(450);
    }
    console.log(tag, 'sequence', seen.join(' | '));
    const done = await pg.evaluate(() => document.querySelector('.sprintdone')?.textContent.replace(/\s+/g, ' ').slice(0, 300));
    console.log(tag, 'summary', done);
    if (!done) errs.push(tag + ' sprint did not finish');
    if (seen.length < 5) errs.push(tag + ' too few cards ' + seen.length);
    if (seen.filter(x => x === seen[0]).length < 2) errs.push(tag + ' missed card did not come back');
    await pg.screenshot({ path: SH + tag + 'sprintdone.png', fullPage: true });
    const cards = await pg.evaluate(() => JSON.parse(localStorage.getItem('sinag.codal.v1')).cards);
    for (const [k, c] of Object.entries(cards)) { console.log(tag, k, JSON.stringify({ s: c.s && +c.s.toFixed(2), d: c.d && +c.d.toFixed(2), ivl: c.ivl, reps: c.reps, lapses: c.lapses, dueIn: Math.round((c.due - Date.now()) / 60000) + 'm' })); if (c.s == null && c.reps) errs.push(tag + ' card without stability ' + k); if (c.ease != null && c.s != null) errs.push(tag + ' leftover ease ' + k); }
    if (!(cards['rpc|article-11'].lapses >= 5)) errs.push(tag + ' lapses lost');
    await pg.goto('http://localhost:8811/#/progress', { waitUntil: 'networkidle' }); await pg.waitForTimeout(300);
    const mem = await pg.evaluate(() => ({ txt: [...document.querySelectorAll('.card h3')].find(h => h.textContent === 'Your memory')?.parentElement.textContent.replace(/\s+/g, ' ').slice(0, 260), bars: document.querySelectorAll('.fc .fcb').length, top: getComputedStyle(document.querySelector('.top')).display }));
    console.log(tag, 'memory', JSON.stringify(mem));
    if (mem.bars !== 14) errs.push(tag + ' forecast bars ' + mem.bars);
    if (mem.top === 'none') errs.push(tag + ' focus class not cleared');
    if (!/Stubborn/.test(mem.txt || '') && !/stubborn/.test(mem.txt || '')) errs.push(tag + ' no stubborn count');
    await pg.screenshot({ path: SH + tag + 'memory.png', fullPage: true });
    const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(tag + ' overflow ' + ov);
    await pg.goto('http://localhost:8811/#/p/ra7080/section-2', { waitUntil: 'networkidle' }); await pg.waitForTimeout(300);
    const st = await pg.evaluate(() => ({ cs: document.querySelector('#cstat')?.textContent, inforce: document.querySelector('#law .inforce')?.textContent.replace(/\s+/g, ' '), first: document.querySelector('#law > .text')?.textContent.replace(/\s+/g, ' ') }));
    console.log(tag, 'ra7080 s2', JSON.stringify(st));
    if (!/RA 7659/.test(st.inforce || '') || !/Fifty million/.test(st.first || '')) errs.push(tag + ' RA 7080 Sec. 2 not in force');
    await pg.close();
  }
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
