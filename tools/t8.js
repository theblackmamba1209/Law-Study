const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 900 }, deviceScaleFactor: 2 });
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('http://localhost:8811/#/p/rpc/article-11', { waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
  await pg.click('[data-tab="recall"]'); await pg.waitForTimeout(300);
  await (await pg.$('#tabbox')).screenshot({ path: '/home/claude/work/shots/mrecall.png' });
  await (await pg.$('#law')).screenshot({ path: '/home/claude/work/shots/mlaw11.png' });
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
