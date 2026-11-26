const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = [];
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: 2 });
    pg.on('pageerror', e => errs.push(e.message));
    await pg.goto('http://localhost:8811/#/', { waitUntil: 'networkidle' }); await pg.waitForTimeout(600);
    await (await pg.$('.bodymap')).screenshot({ path: `/home/claude/work/shots/${tag}fig.png` });
    await pg.goto('http://localhost:8811/#/field/eth', { waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
    await (await pg.$('.fhead')).screenshot({ path: `/home/claude/work/shots/${tag}fhead.png` });
    for (const h of ['#/', '#/learn', '#/field/crim']) { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); }
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
