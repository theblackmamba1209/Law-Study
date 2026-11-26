const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const S = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message)); pg.on('dialog', d => { errs.push('DIALOG'); d.dismiss(); });
    const go = async (h, f) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(450); if (f) await pg.screenshot({ path: S + tag + f + '.png', fullPage: true });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    // every CPRA section opens, shows an explanation, and has no overflow
    const ids = JSON.parse(require('fs').readFileSync('/home/claude/site/data/codes/rpc.json', 'utf8')).provisions.filter(p => p.l.startsWith('Article')).map(p => p.i);
    let noexp = [];
    for (const i of (tag === 'm' ? ids : ids.slice(0, 30))) {
      await go('#/p/rpc/' + i);
      const has = await pg.evaluate(() => !!document.querySelector('.explain'));
      if (!has) noexp.push(i);
    }
    if (noexp.length) errs.push(tag + ' no explanation: ' + noexp.join(', '));
  }
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
