const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const S = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: 2 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message)); pg.on('dialog', d => { errs.push('DIALOG'); d.dismiss(); });
    const go = async (h, f, full) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(400); if (f) await pg.screenshot({ path: S + tag + f + '.png', fullPage: !!full });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    await go('#/field/crim');
    await go('#/b2', 'b2home', true);
    await go('#/b2/life', 'b2el');
    await go('#/b2/life?tab=compare', 'b2cmp');
    await pg.click('#hide'); await pg.waitForTimeout(100); const shut = await pg.$$eval('.mx td.shut', x => x.length); await pg.click('.mx td.shut'); const shut2 = await pg.$$eval('.mx td.shut', x => x.length);
    console.log(tag, 'cover cells', shut, '→', shut2);
    await go('#/b2/authority?tab=sort', 'b2sort');
    await go('#/b2/property?tab=practice');
    for (let k = 0; k < 7; k++) { await pg.click('.opt >> nth=0'); await pg.waitForTimeout(60); if (k === 0) await pg.screenshot({ path: S + tag + 'b2drill.png' }); await pg.click('#nx'); await pg.waitForTimeout(60); }
    console.log(tag, 'drill end:', (await pg.innerText('.drill h2')));
    await go('#/b2/mix'); await pg.click('.opt >> nth=1'); await pg.waitForTimeout(80); console.log(tag, 'mix shows why:', await pg.isVisible('#why .note'));
    await go('#/b2/honor?tab=cases'); await go('#/b2/sexual'); await go('#/b2/liberty?tab=compare'); await go('#/b2/injury?tab=sort');
    await go('#/p/rpc/article-248', 'b2prov');
    console.log(tag, 'elements card on Art. 248:', await pg.isVisible('.b2el'));
    await go('#/p/rpc/article-152'); console.log(tag, 'note on 152:', (await pg.innerText('#law')).includes('B.P. Blg. 873') || (await pg.innerText('#law')).includes('Batas Pambansa Blg. 873'));
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
