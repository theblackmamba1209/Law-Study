// The Map: zoom levels, lock states, next-to-lock-in, scoped sprint
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const SH = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    await pg.goto('http://localhost:8811/', { waitUntil: 'networkidle' });
    await pg.evaluate(() => {
      const DAY = 864e5, now = Date.now(); const cards = {};
      // Civil Code Arts. 1156-1162: locked, learning, slipping, opened
      cards['civil|article-1156'] = { s: 40, d: 4, ivl: 40, reps: 4, lapses: 0, last: now - 2 * DAY, due: now + 38 * DAY };
      cards['civil|article-1157'] = { s: 30, d: 4, ivl: 30, reps: 3, lapses: 0, last: now - DAY, due: now + 29 * DAY };
      cards['civil|article-1158'] = { s: 4, d: 5, ivl: 4, reps: 2, lapses: 0, last: now - DAY, due: now + 3 * DAY };
      cards['civil|article-1159'] = { s: 2, d: 6, ivl: 2, reps: 1, lapses: 0, last: now - 9 * DAY, due: now - 7 * DAY };
      cards['civil|article-1160'] = { reps: 0, lapses: 0, seen: now };
      localStorage.setItem('sinag.codal.v1', JSON.stringify({ cards, settings: { newPerDay: 10 } }));
    });
    await pg.reload({ waitUntil: 'networkidle' });
    const go = async (h, f) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(450); if (f && tag === 'm') await pg.screenshot({ path: SH + 'map_' + f + '.png', fullPage: true });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`);
      return pg.evaluate(() => ({ h1: document.querySelector('.mapv h1')?.textContent, tiles: document.querySelectorAll('.mtile').length, rows: document.querySelectorAll('.mcode, .mblock').length, provs: document.querySelectorAll('.mapprov li').length, next: document.querySelector('.mapnext a')?.getAttribute('href'), sum: document.querySelector('.mhstat')?.textContent.replace(/\s+/g, ' '), crumbs: document.querySelector('.mapcr')?.textContent.replace(/\s+/g, ' '), nav: document.querySelector('.topnav .on, .bottomnav .on')?.textContent })); };
    let r = await go('#/map', 'top'); console.log(tag, 'top', JSON.stringify(r));
    if (r.tiles !== 8) errs.push(tag + ' expected 8 field tiles');
    r = await go('#/map/civ', 'field'); console.log(tag, 'field', JSON.stringify(r));
    if (!r.rows) errs.push(tag + ' no codes in field');
    r = await go('#/map/civ/civil', 'code'); console.log(tag, 'code', JSON.stringify(r));
    if (!r.rows) errs.push(tag + ' no books in code');
    // find the division holding Art. 1156 and zoom to it
    const dv = await pg.evaluate(async () => { const d = await (await fetch('data/codes/civil.json')).json(); return d.provisions.find(p => p.i === 'article-1156').d; });
    r = await go('#/map/civ/civil/' + dv, 'div'); console.log(tag, 'div', JSON.stringify(r));
    const states = await pg.$$eval('.mapprov .ls', xs => xs.slice(0, 6).map(x => x.className));
    console.log(tag, 'states', states.join(' '));
    if (!states.includes('ls k') || !states.includes('ls x') || !states.includes('ls g')) errs.push(tag + ' lock states missing');
    if (!/slipping/.test(r.sum || '')) errs.push(tag + ' summary does not show slipping');
    // scoped sprint from this division
    await pg.click('.mapsum .btn.primary'); await pg.waitForTimeout(800);
    const sp = await pg.evaluate(() => ({ scope: document.querySelector('.sprint p.tiny')?.textContent, prompt: document.querySelector('.sprint .prompt')?.textContent }));
    console.log(tag, 'sprint', JSON.stringify(sp));
    if (!/Locking in/.test(sp.scope || '') || !/Article 1159/.test(sp.prompt || '')) errs.push(tag + ' scoped sprint did not start with the slipping article');
    if (tag === 'm') await pg.screenshot({ path: SH + 'map_sprint.png', fullPage: true });
    await pg.close();
  }
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
