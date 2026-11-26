const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 }); const errs = [];
  pg.on('pageerror', e => errs.push(e.message)); pg.on('dialog', d => { errs.push('NATIVE DIALOG'); d.dismiss(); });
  await pg.goto('http://localhost:8811/#/', { waitUntil: 'networkidle' }); await pg.waitForTimeout(500);
  await (await pg.$('.plate')).screenshot({ path: '/home/claude/work/shots/plate.png' });
  await pg.click('#pic'); await pg.waitForTimeout(200);
  await pg.setInputFiles('#fgf', '/home/claude/work/shots/dfig.png'); await pg.waitForTimeout(900);
  console.log('custom image stored:', await pg.evaluate(() => (localStorage.getItem('sinag.figure.img') || '').length > 1000), '| adjust shown:', await pg.isVisible('#fgbox svg image'));
  await pg.click('#fgbox .zone[data-id="eth"] .pin'); await pg.waitForTimeout(150);
  const bb = await (await pg.$('#fgbox svg')).boundingBox(); await pg.mouse.click(bb.x + bb.width * 0.5, bb.y + bb.height * 0.4); await pg.waitForTimeout(200);
  console.log('marker moved:', await pg.evaluate(() => JSON.stringify(JSON.parse(localStorage.getItem('sinag.codal.v1') || '{}').settings?.housePos || 'pending-save')));
  await pg.click('#fgr'); await pg.waitForTimeout(200);
  console.log('back to drawn:', await pg.evaluate(() => !localStorage.getItem('sinag.figure.img')));
  await pg.click('#mok');
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
