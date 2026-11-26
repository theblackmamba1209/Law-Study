const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const S = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message)); pg.on('dialog', d => { errs.push('DIALOG'); d.dismiss(); });
    const go = async (h) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    const el = async (sel, f) => { const e = await pg.$(sel); if (!e) { errs.push(tag + ' missing ' + sel); return; } await e.screenshot({ path: S + tag + f + '.png' }); };
    await go('#/p/rpc/article-14'); await el('#law', 'law14');
    await go('#/p/rpc/article-266-a'); await el('#law', 'law266');
    await go('#/p/labor/article-141'); await el('#law', 'law141');
    await go('#/p/const1987/art-viii-sec-4'); await el('#law', 'lawc84');
    await go('#/p/rpc/article-248'); await el('#tabbox', 'guide248');
    await go('#/p/civil/article-1318'); await el('#tabbox', 'guide1318');
    await go('#/b2/life'); await el('#b2body', 'b2el');
    await go('#/b2/life?tab=compare'); await el('#b2body', 'b2cmp');
    await go('#/b2/life?tab=sort'); await el('#b2body', 'b2sort');
    await go('#/lesson/law-takes-effect'); await el('.lesson', 'lesson');
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
