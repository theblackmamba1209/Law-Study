const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const S = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message)); pg.on('dialog', d => { errs.push('DIALOG'); d.dismiss(); });
    const go = async (h, f, full) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(450); if (f) await pg.screenshot({ path: S + tag + f + '.png', fullPage: !!full });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    await go('#/field/eth', 'eth', true);
    await go('#/code/cpra');
    await go('#/p/cpra/canon-iii-sec-13', 'cpra13');
    console.log(tag, 'notes card:', await pg.isVisible('.plain'), '| old rule:', await pg.isVisible('.oldrule'), '| digest in cases:', (await pg.innerText('[data-tab="cases"]')).replace(/\s+/g, ' '));
    await pg.click('[data-tab="cases"]'); await pg.waitForTimeout(200); console.log(tag, 'cases:', (await pg.$$eval('#tabbox .case', x => x.length)));
    await go('#/p/cpra/canon-vi-sec-37'); await go('#/p/cpra/canon-vi-sec-40'); await go('#/p/cpra/lawyers-oath');
    await go('#/p/labor/article-40', 'aep');
    console.log(tag, 'issuances:', await pg.$$eval('.isl li', x => x.length));
    await pg.click('[data-tab="recall"]'); await pg.waitForTimeout(150); await pg.click('[data-m="al"]'); await pg.waitForTimeout(150);
    await pg.fill('[data-al="0"]', 'Yes, the employer needs an AEP.'); await pg.click('[data-cf="2"]'); await pg.click('#alg'); await pg.waitForTimeout(100);
    await pg.click('[data-ck="0"]'); await pg.click('[data-ck="1"]'); await pg.click('#aldone'); await pg.waitForTimeout(100);
    console.log(tag, 'ALAC result:', (await pg.innerText('#alres')).slice(0, 90).replace(/\n/g, ' '));
    if (tag === 'm') await (await pg.$('#tabbox')).screenshot({ path: S + 'malac.png' });
    await pg.click('[data-m="c2"]'); await pg.waitForTimeout(150); await pg.click('[data-cf="0"]'); await pg.click('#cc'); await pg.waitForTimeout(100);
    await pg.click('[data-m="fr"]'); await pg.waitForTimeout(150); await pg.fill('#frt', 'Any alien seeking admission'); await pg.click('[data-cf="1"]'); await pg.click('#frc'); await pg.waitForTimeout(150);
    await go('#/lesson/lab-aep', 'lesaep'); await go('#/set/lab-aep-walk'); await go('#/set/eth-cpra-core');
    await go('#/p/ca613/section-9'); await go('#/code/notarial'); await go('#/p/notarial/rule-iv-sec-2');
    await go('#/progress', 'prog', true); console.log(tag, 'calibration shown:', await pg.isVisible('.calib'));
    await go('#/about');
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS'); await b.close();
})();
