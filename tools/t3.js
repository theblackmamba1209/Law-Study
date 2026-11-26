const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = [];
  const S = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: w === 390 ? 844 : 900 } });
    pg.on('pageerror', e => errs.push(tag + ' PAGEERR ' + e.message));
    pg.on('dialog', d => { errs.push('NATIVE DIALOG'); d.dismiss(); });
    const go = async (h, f, full) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(500); if (f) await pg.screenshot({ path: S + tag + f + '.png', fullPage: !!full });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflows by ${ov}px`); };
    await go('#/', 'home', true);
    await go('#/learn', 'learn', true);
    await go('#/field/crim', 'field', true);
    await go('#/field/eth', 'eth');
    await go('#/lesson/law-takes-effect', 'lesson');
    await go('#/set/statcon-effect', 'set');
    await go('#/p/civil/article-2?set=statcon-effect', 'prov', true);
    await pg.fill('#hookin', 'a newspaper wrapped round his crown'); 
    await pg.click('[data-tab="recall"]'); await pg.waitForTimeout(200);
    console.log(tag, 'cue shown:', await pg.isVisible('.hookcue'), '| next link:', await pg.getAttribute('.pn a.primary', 'href'));
    await pg.click('[data-tab="cases"]'); await pg.click('[data-tab="notes"]');
    await go('#/p/rpc/article-266-a', 'prov2');
    await go('#/code/const1987', 'code');
    await go('#/library'); await go('#/syllabus/recent'); await go('#/about', 'about'); await go('#/progress'); await go('#/review'); await go('#/drill'); await go('#/syllabus'); await go('#/search?q=due+process');
    await go('#/');
    console.log(tag, 'home after study:', (await pg.innerText('.next')).replace(/\n+/g, ' | ').slice(0, 160));
    await pg.close();
  }
  console.log(errs.join('\n') || 'NO ERRORS');
  await b.close();
})();
