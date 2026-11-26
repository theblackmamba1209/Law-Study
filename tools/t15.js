const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = [];
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 } });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    for (const h of ['#/code/irrlabor', '#/p/irrlabor/biii-rule-i-sec-8', '#/code/do174', '#/p/do174/section-5', '#/code/irr9165', '#/p/irr9165/article-ii-sec-21', '#/p/labor/article-87', '#/p/labor/article-96', '#/p/rpc/article-123', '#/p/rpc/article-88-a', '#/p/rpc/article-134-a', '#/field/lab', '#/field/crim']) {
      await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(250);
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`);
      if (await pg.isVisible('.empty')) errs.push(`${tag} ${h} shows empty state`);
    }
    await pg.goto('http://localhost:8811/#/p/labor/article-87', { waitUntil: 'networkidle' }); await pg.waitForTimeout(250);
    await pg.click('.isl a >> nth=0'); await pg.waitForTimeout(400); console.log(tag, 'IRR link lands on:', await pg.innerText('.lh'));
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
