const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = [];
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 } });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    const go = async (h) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(300);
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    for (const h of ['#/p/rpc/article-70', '#/p/rpc/article-71', '#/p/rpc/article-90', '#/p/rpc/article-89', '#/p/const1987/art-ix-sec-2-3', '#/p/const1987/section-29', '#/p/const1987/art-vii-sec-18', '#/code/const1987', '#/p/const1987/art-xii-sec-11']) {
      await go(h);
      if (h.endsWith('70')) console.log(tag, '70 amended panel:', (await pg.innerText('.amend')).includes('forty years'), '| label', (await pg.innerText('.lh')).replace(/\n/g, ' '));
      if (h.endsWith('2-3')) console.log(tag, 'IX-C label:', (await pg.innerText('.lh')).replace(/\n/g, ' '), '| notes:', await pg.isVisible('.plain'));
    }
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
