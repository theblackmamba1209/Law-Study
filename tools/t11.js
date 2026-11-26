const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 390, height: 900 }, deviceScaleFactor: 2 }); const errs = [];
  pg.on('pageerror', e => errs.push(e.message));
  for (const h of ['civil/article-1318', 'rpc/article-14', 'rpc/article-11', 'rpc/article-248', 'const1987/art-iii-sec-2', 'family/article-36']) {
    await pg.goto('http://localhost:8811/#/p/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(250);
    const g = await pg.$$eval('.judge>li', ls => ls.map(l => l.querySelector('.jq').textContent + ' [' + l.querySelectorAll('.it').length + '] ' + l.querySelector('.canon').textContent.slice(-70)));
    console.log(h, '\n  ' + g.join('\n  '));
  }
  await pg.goto('http://localhost:8811/#/p/rpc/article-14', { waitUntil: 'networkidle' }); await pg.waitForTimeout(250);
  await (await pg.$('#av-judge')).screenshot({ path: '/home/claude/work/shots/mjudge14.png' });
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
