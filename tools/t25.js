// The statute library, its detected histories, the eras, the treaty registry, and their joins to the map and search
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const SH = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    const U = 'http://localhost:8811/';
    await pg.goto(U, { waitUntil: 'networkidle' }); await pg.evaluate(() => localStorage.clear()); await pg.reload({ waitUntil: 'networkidle' });
    const go = async (h, f, wait = 600) => { await pg.goto(U + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(wait);
      if (f && tag === 'm') await pg.screenshot({ path: SH + 'l_' + f + '.png', fullPage: true });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    const ev = f => pg.evaluate(f);

    await go('#/laws', 'hub');
    let r = await ev(() => ({ h1: document.querySelector('h1')?.textContent, series: document.querySelectorAll('.grid .codecard').length, top: document.querySelectorAll('.lawlist li').length, lead: document.querySelector('.lead')?.textContent.slice(0, 40) }));
    console.log(tag, 'hub', JSON.stringify(r));
    if (r.series !== 7 || r.top < 10 || !/25,223/.test(await ev(() => document.querySelector('.lead').textContent))) errs.push(tag + ' statute hub');
    // search by number
    await pg.fill('#lsq', 'RA 9262'); await pg.click('#lsf button'); await pg.waitForTimeout(300);
    r = await ev(() => [...document.querySelectorAll('#lsr .lawlist a')].map(a => a.getAttribute('href')));
    console.log(tag, 'search RA 9262', JSON.stringify(r.slice(0, 3)));
    if (r[0] !== '#/law/ra-9262') errs.push(tag + ' number search');
    await pg.fill('#lsq', 'hazing'); await pg.click('#lsf button'); await pg.waitForTimeout(300);
    r = await ev(() => [...document.querySelectorAll('#lsr .lawlist a')].map(a => a.getAttribute('href')));
    if (!r.includes('#/law/ra-11053') || !r.includes('#/law/ra-8049')) errs.push(tag + ' title search: ' + r.slice(0, 5).join(' '));

    // a law with a detected repeal: RA 6425, repealed by RA 9165
    await go('#/law/ra-6425', 'law', 1200);
    r = await ev(() => ({ eyebrow: document.querySelector('.lawv .eyebrow')?.textContent, rep: !!document.querySelector('.lawv .chip.bad'), hist: [...document.querySelectorAll('.lawhist .tl > li')].map(li => li.textContent.replace(/\s+/g, ' ').slice(0, 60)), text: document.querySelectorAll('.lawtext .text p').length }));
    console.log(tag, 'RA 6425', JSON.stringify({ ...r, hist: r.hist.slice(0, 4) }));
    if (!/Republic Act No. 6425/.test(r.eyebrow) || !r.rep || !r.hist.some(h => /RA9165repealed/.test(h.replace(/\s/g, ''))) || r.text < 20) errs.push(tag + ' RA 6425 page');
    // a study-library law: the Family Code shows its written history and a study link
    await go('#/law/eo-209-1987', '', 1200);
    r = await ev(() => ({ study: document.querySelector('.lawv .btn.primary')?.getAttribute('href'), hist: !!document.querySelector('.hist'), inc: document.querySelectorAll('.lawhist .tl > li').length }));
    console.log(tag, 'Family Code', JSON.stringify(r));
    if (r.study !== '#/map/civ/family' || !r.hist || r.inc < 3) errs.push(tag + ' Family Code statute page');
    // the code's map page carries the same history and links to the statute
    await go('#/map/civ/family', 'codehist', 900);
    r = await ev(() => ({ hist: document.querySelector('.hist .eyebrow')?.textContent, link: [...document.querySelectorAll('.hist a')].map(a => a.getAttribute('href')).pop() }));
    console.log(tag, 'code page', JSON.stringify(r));
    if (r.hist !== 'How this law came to be' || r.link !== '#/law/eo-209-1987') errs.push(tag + ' history on the code page');
    // a big law renders in parts
    await go('#/law/ra-8424', '', 2000);
    r = await ev(() => ({ more: !!document.querySelector('#more'), p: document.querySelectorAll('.lawtext .text p').length }));
    console.log(tag, 'NIRC', JSON.stringify(r));
    if (!r.more) errs.push(tag + ' long law not paged');

    // series browse
    await go('#/laws/bp');
    r = await ev(() => ({ years: document.querySelectorAll('details.track').length, first: document.querySelectorAll('details.track[open] .lawlist li').length }));
    console.log(tag, 'BP', JSON.stringify(r));
    if (r.years < 5 || r.first < 1) errs.push(tag + ' series browse');

    // eras
    await go('#/history', 'history', 900);
    r = await ev(() => ({ eras: document.querySelectorAll('.tl.eras > li').length, codes: document.querySelectorAll('.grid .codecard').length, next: [...document.querySelectorAll('.pn a')].map(a => a.textContent).join('|') }));
    console.log(tag, 'history', JSON.stringify(r));
    if (r.eras !== 9 || r.codes < 20 || !/Next in The Lawyer’s Craft/.test(r.next)) errs.push(tag + ' history page');

    // treaties
    await go('#/treaties', 'treaties', 700);
    r = await ev(() => ({ cards: document.querySelectorAll('.shiftcard').length, crumbs: document.querySelector('.mapcr')?.textContent, next: [...document.querySelectorAll('.pn a')].map(a => a.textContent).join('|') }));
    console.log(tag, 'treaties', JSON.stringify(r));
    if (r.cards !== 32 || !/International Law/.test(r.crumbs) || !/Next in International Law/.test(r.next)) errs.push(tag + ' treaty index');
    await go('#/treaties/unclos', 'treaty', 700);
    r = await ev(() => ({ h1: document.querySelector('h1')?.textContent, laws: [...document.querySelectorAll('.movev .chip.blue')].map(a => a.getAttribute('href')), cases: document.querySelectorAll('.case').length }));
    console.log(tag, 'UNCLOS', JSON.stringify(r));
    if (!r.laws.includes('#/law/ra-9522') || !r.laws.includes('#/law/ra-12064') || r.cases !== 2) errs.push(tag + ' UNCLOS page');

    // the path: International Law starts with the treaties; the Lawyer's Craft has history and the statute library
    await go('#/map/intl');
    r = await ev(() => [...document.querySelectorAll('.mtrack')][0]?.textContent.replace(/\s+/g, ' '));
    if (!/Treaties binding the Philippines/.test(r || '')) errs.push(tag + ' treaties not in the International Law path');
    await go('#/map/craft');
    r = await ev(() => document.querySelector('.mapv')?.textContent);
    if (!/How Philippine law evolved/.test(r) || !/Every Philippine statute/.test(r)) errs.push(tag + ' history or statute library not in the Craft path');

    // site search finds statutes
    await go('#/search?q=RA%2011053', '', 3000);
    r = await ev(() => [...document.querySelectorAll('#sr .lawlist a')].map(a => a.getAttribute('href')));
    console.log(tag, 'site search', JSON.stringify(r.slice(0, 3)));
    if (r[0] !== '#/law/ra-11053') errs.push(tag + ' site search for a statute');

    // about: coverage statement
    await go('#/about');
    r = await ev(() => document.querySelector('#coverage')?.nextElementSibling?.textContent.replace(/\s+/g, ' '));
    if (!/25,223 national statutes/.test(r || '') || !/ordinances/.test(r || '')) errs.push(tag + ' coverage statement');
    await pg.close();
  }
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
