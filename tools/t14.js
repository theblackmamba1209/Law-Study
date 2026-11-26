const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = [];
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    for (const h of ['#/p/rpc/article-248', '#/p/civil/article-1318', '#/p/family/article-176', '#/p/rpc/article-70', '#/p/cpra/canon-iii-sec-13', '#/p/labor/article-40', '#/p/const1987/art-iii-sec-2', '#/p/rpc/article-90']) {
      await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(300);
      const items = await pg.$$eval('.tl li', xs => xs.map(x => x.innerText.replace(/\s+/g, ' ').slice(0, 70)));
      console.log(tag, h, items.length, '|', items.slice(0, 4).join(' || '));
      if (tag === 'm' && h.endsWith('1318')) await (await pg.$('.evo')).screenshot({ path: '/home/claude/work/shots/mevo.png' });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`);
    }
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
