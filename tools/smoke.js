const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const errs = [];
  pg.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  pg.on('console', m => { if (m.type() === 'error') errs.push('CONSOLE ' + m.text()); });
  const shots = process.argv.slice(2);
  for (const h of shots) {
    const [hash, file, w] = h.split('@');
    if (w) await pg.setViewportSize({ width: +w, height: 900 });
    await pg.goto('http://localhost:8811/' + hash, { waitUntil: 'networkidle' });
    await pg.waitForTimeout(700);
    if (file) await pg.screenshot({ path: '/home/claude/work/shots/' + file, fullPage: false });
    const t = await pg.evaluate(() => document.querySelector('main').innerText.slice(0, 300));
    console.log('==', hash, '\n', t.replace(/\n+/g, ' | '));
  }
  console.log(errs.join('\n') || 'NO ERRORS');
  await b.close();
})();
