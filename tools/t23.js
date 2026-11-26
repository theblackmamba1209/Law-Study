// Doctrine shifts and the enforcement playbook: index pages, detail pages, quizzes, provision-page panels, drills
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const SH = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    pg.on('console', m => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errs.push(tag + ' console ' + m.text()); });
    await pg.goto('http://localhost:8811/', { waitUntil: 'networkidle' });
    await pg.evaluate(() => localStorage.clear());
    const go = async (h, f) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
      if (f && tag === 'm') await pg.screenshot({ path: SH + 'x_' + f + '.png', fullPage: true });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    // shifts index
    await go('#/shifts', 'shifts');
    let r = await pg.evaluate(() => ({ h1: document.querySelector('h1')?.textContent, cards: document.querySelectorAll('.shiftcard').length, sects: document.querySelectorAll('.sect h2').length }));
    console.log(tag, 'shifts', JSON.stringify(r));
    if (r.cards !== 19) errs.push(tag + ' expected 19 shift cards, got ' + r.cards);
    // a detail page
    await go('#/shifts/psych-incapacity', 'shift');
    r = await pg.evaluate(() => ({ h1: document.querySelector('h1')?.textContent, tl: document.querySelectorAll('.tl li').length, newr: document.querySelectorAll('.tl .r-new').length, then: !!document.querySelector('.thennow .then'), now: !!document.querySelector('.thennow .now'), why: document.querySelectorAll('.shiftv ol.explain li').length, links: [...document.querySelectorAll('.shiftv .chip.blue')].map(a => a.textContent) }));
    console.log(tag, 'shift', JSON.stringify(r));
    if (r.tl !== 4 || r.newr !== 1 || !r.then || !r.now || r.why < 3) errs.push(tag + ' psych-incapacity layout');
    if (!r.links.some(t => /Family Code Article 36/.test(t))) errs.push(tag + ' link to Family Code Art. 36 missing');
    // answer the quiz correctly (option 1)
    await pg.click('#sq .opt[data-o="1"]'); await pg.waitForTimeout(150);
    r = await pg.evaluate(() => ({ right: document.querySelectorAll('#sq .opt.right').length, wrong: document.querySelectorAll('#sq .opt.wrong').length, res: document.querySelector('#sq .qres')?.textContent.slice(0, 20), st: JSON.parse(localStorage.getItem('sinag.codal.v1') || '{}').shift }));
    await pg.waitForTimeout(300);
    const st = await pg.evaluate(() => JSON.parse(localStorage.getItem('sinag.codal.v1') || '{}').shift);
    console.log(tag, 'quiz', JSON.stringify(r), JSON.stringify(st));
    if (r.right !== 1 || r.wrong !== 0 || !/Right/.test(r.res) || !st || !st['psych-incapacity'] || !st['psych-incapacity'].ok) errs.push(tag + ' shift quiz did not record');
    // the provision page shows the cue and the Cases tab panel
    await go('#/p/family/article-36', 'prov');
    r = await pg.evaluate(() => ({ cue: document.querySelector('.shiftcue')?.textContent.replace(/\s+/g, ' '), tab: document.querySelector('[data-tab="cases"]')?.textContent }));
    console.log(tag, 'prov', JSON.stringify(r));
    if (!/Doctrine changed/.test(r.cue || '')) errs.push(tag + ' no shift cue on Art. 36');
    await pg.click('[data-tab="cases"]'); await pg.waitForTimeout(200);
    r = await pg.evaluate(() => ({ mini: document.querySelectorAll('.shiftmini').length, link: document.querySelector('.shiftmini a')?.getAttribute('href') }));
    console.log(tag, 'cases tab', JSON.stringify(r));
    if (r.mini !== 1 || r.link !== '#/shifts/psych-incapacity') errs.push(tag + ' shift card missing in Cases tab');
    // a provision linked to the playbook
    await go('#/p/civil/article-1387');
    await pg.click('[data-tab="cases"]'); await pg.waitForTimeout(200);
    r = await pg.evaluate(() => [...document.querySelectorAll('.movecard .mt')].map(x => x.textContent));
    console.log(tag, 'enf on 1387', JSON.stringify(r));
    if (!r.some(t => /accion pauliana/.test(t))) errs.push(tag + ' playbook move missing on Art. 1387');
    // enforcement index
    await go('#/enforce', 'enforce');
    r = await pg.evaluate(() => ({ stages: document.querySelectorAll('.stagepath button').length, sections: document.querySelectorAll('section.stage').length, moves: document.querySelectorAll('.movecard').length, day1: document.querySelectorAll('.day1 input').length, guard: document.querySelectorAll('.guard li').length }));
    console.log(tag, 'enforce', JSON.stringify(r));
    if (r.stages !== 9 || r.sections !== 9 || r.moves !== 32 || r.day1 !== 9 || r.guard !== 4) errs.push(tag + ' enforce index counts');
    await pg.click('.day1 input[data-d="0"]'); await pg.click('.day1 input[data-d="1"]'); await pg.waitForTimeout(300);
    r = await pg.evaluate(() => ({ c: document.querySelector('#d1c')?.textContent, st: JSON.parse(localStorage.getItem('sinag.codal.v1') || '{}').enf }));
    console.log(tag, 'day1', JSON.stringify(r));
    if (r.c !== '2/9' || !r.st || !r.st.day1['0'] || !r.st.day1['1']) errs.push(tag + ' day-one checklist did not persist');
    // a move page
    await go('#/enforce/garnish-banks', 'move');
    r = await pg.evaluate(() => ({ h1: document.querySelector('h1')?.textContent, steps: document.querySelectorAll('.movev ol.explain li').length, cases: [...document.querySelectorAll('.movev .case .cn')].map(x => x.textContent), drill: document.querySelector('a[href^="#/enforce/drills?only="]')?.getAttribute('href') }));
    console.log(tag, 'move', JSON.stringify(r));
    if (r.steps < 4 || !r.cases.includes('China Banking Corp. v. Ortega') || r.drill !== '#/enforce/drills?only=d2') errs.push(tag + ' garnish-banks page');
    // drills: answer all correctly
    await go('#/enforce/drills', 'drill');
    for (let i = 0; i < 10; i++) {
      await pg.click('#dq .opt[data-o="1"]'); await pg.waitForTimeout(80);
      await pg.click('#nx'); await pg.waitForTimeout(80);
    }
    r = await pg.evaluate(() => ({ h1: document.querySelector('.reviewcard h1')?.textContent }));
    await pg.waitForTimeout(300);
    const best = await pg.evaluate(() => JSON.parse(localStorage.getItem('sinag.codal.v1') || '{}').enf?.best);
    console.log(tag, 'drills', JSON.stringify(r), best);
    if (r.h1 !== '10 of 10' || best !== 10) errs.push(tag + ' drills score');
    // the links from home, map and syllabus
    for (const h of ['#/', '#/map', '#/syllabus']) {
      await go(h);
      const n = await pg.evaluate(() => [document.querySelector('a[href="#/shifts"]'), document.querySelector('a[href="#/enforce"]')].filter(Boolean).length);
      if (n !== 2) errs.push(`${tag} ${h} missing links to shifts/enforce`);
    }
    // about shows coverage
    await go('#/about');
    const cov = await pg.evaluate(() => document.querySelectorAll('.covt tr').length);
    console.log(tag, 'coverage rows', cov);
    if (cov < 20) errs.push(tag + ' coverage table');
    await pg.close();
  }
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
