const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const S = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    const go = async (h, f) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(400); if (f) await pg.screenshot({ path: S + tag + f + '.png', fullPage: true });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    const look = async () => pg.evaluate(() => ({ cap: document.querySelector('#law .lcap')?.textContent, inforce: document.querySelector('#law .inforce')?.textContent.replace(/\s+/g, ' '), status: document.querySelector('#law .status')?.textContent.slice(0, 60), first: document.querySelector('#law > .text')?.textContent.replace(/\s+/g, ' ').slice(0, 110), hist: !!document.querySelector('#law details.hist') }));
    for (const [h, f] of [['#/p/rpc/article-155', 'a155'], ['#/p/rpc/article-295', 'a295'], ['#/p/rpc/article-266-a', 'a266a'], ['#/p/rpc/article-351', 'a351'], ['#/p/rpc/article-309'], ['#/p/rpc/article-134'], ['#/p/rpc/article-210'], ['#/p/rpc/article-90'], ['#/p/nirc/section-109']]) {
      await go(h, tag === 'm' ? f : null); const r = await look(); console.log(tag, h, JSON.stringify(r));
      if (h.endsWith('351') && !r.status) errs.push('no status on 351');
      if (h.endsWith('155') && !/as amended by RA 11926/.test(r.inforce || '')) errs.push('155 not in force');
      if (h.endsWith('155') && /firearm/.test(r.first || '')) errs.push('155 still shows firearm');
      if (h.endsWith('309') && !/RA 10951/.test(r.inforce || '')) errs.push('309 not in force');
      if (h.endsWith('266-a') && !/By a person who shall have carnal knowledge of another person/.test(await pg.evaluate(() => document.querySelector('#law > .text').textContent))) errs.push('266-A not consolidated');
    }
  }
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
