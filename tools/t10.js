const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = [];
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    await pg.goto('http://localhost:8811/#/p/labor/article-141', { waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
    const card = (await pg.$$('#tabbox .card')).pop(); await card.screenshot({ path: `/home/claude/work/shots/${tag}judge.png` });
    await pg.click('[data-av="text"]'); await pg.waitForTimeout(400);
    const vis = await pg.isVisible('#av-text .anat'); await pg.reload({ waitUntil: 'networkidle' }); await pg.waitForTimeout(300);
    console.log(tag, 'toggle shows text view:', vis, '| remembered:', await pg.isVisible('#av-text .anat'));
    await pg.click('[data-av="judge"]');
    const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(tag + ' overflow ' + ov);
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
