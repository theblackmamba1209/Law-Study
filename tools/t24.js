// Coherence: one field page (the map) with the whole path, crumbs into the map, "next in this field",
// question cards in the same memory (Review, sprints, Today, Progress), map markers, search
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const SH = '/home/claude/work/shots/';
  for (const [w, tag] of [[390, 'm'], [1280, 'd']]) {
    const pg = await b.newPage({ viewport: { width: w, height: 900 }, deviceScaleFactor: w === 390 ? 2 : 1 });
    pg.on('pageerror', e => errs.push(tag + ' ' + e.message));
    const U = 'http://localhost:8811/';
    await pg.goto(U, { waitUntil: 'networkidle' });
    await pg.evaluate(() => localStorage.clear());
    const go = async (h, f) => { await pg.goto(U + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(450);
      if (f && tag === 'm') await pg.screenshot({ path: SH + 'c_' + f + '.png', fullPage: true });
      const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push(`${tag} ${h} overflow ${ov}`); };
    const ev = f => pg.evaluate(f);

    // 1. the old field route lands on the one field page, which holds the whole path in order
    await go('#/field/civ', 'field');
    let r = await ev(() => ({ h1: document.querySelector('.mapv h1')?.textContent, tracks: [...document.querySelectorAll('.mtrack .mtrh b')].map(x => x.textContent),
      order: [...document.querySelectorAll('.mtrack')].find(t => /Persons and family/.test(t.textContent))?.querySelectorAll('.mcode .mt > b, .items .it').length,
      seq: [...([...document.querySelectorAll('.mtrack')].find(t => /Persons and family/.test(t.textContent))?.querySelectorAll('.mcode .mt > b, .items .it') || [])].map(x => x.textContent).slice(0, 4),
      next: document.querySelector('.fnext')?.textContent.replace(/\s+/g, ' ').trim(), crumbs: document.querySelector('.mapcr')?.textContent }));
    console.log(tag, 'field', JSON.stringify(r));
    if (r.h1 !== 'Civil Law' || !r.tracks.includes('Persons and family')) errs.push(tag + ' field page');
    if (r.seq[0] !== 'Family Code' || !/Foreign divorce/.test(r.seq[1]) || !/Psychological incapacity/.test(r.seq[2])) errs.push(tag + ' changes of course not right after the Family Code: ' + r.seq.join(' | '));
    if (!/Next in the path: Changing the sex entry/.test(r.next || '')) errs.push(tag + ' field next step should point to the first unanswered item in the path');
    await go('#/map/craft');
    r = await ev(() => [...document.querySelectorAll('.mtrack')].map(t => t.querySelector('.mtrh b').textContent + ': ' + [...t.querySelectorAll('.items .it, .mcode b')].map(x => x.textContent).join(', ')));
    console.log(tag, 'craft', JSON.stringify(r.filter(x => /enforcing|Courts/.test(x))));
    if (!r.some(x => /After the judgment: enforcing it: Enforcing a judgment, Case files/.test(x))) errs.push(tag + ' enforcement track missing in the Lawyer’s Craft');
    if (!r.some(x => /Courts and procedure: .*fresh period/i.test(x))) errs.push(tag + ' fresh-period not in Courts and procedure');

    // 2. crumbs everywhere lead into the map
    await go('#/p/family/article-36');
    r = await ev(() => [...document.querySelectorAll('.crumbs a')].map(a => a.getAttribute('href')));
    console.log(tag, 'prov crumbs', JSON.stringify(r));
    if (r[0] !== '#/map' || r[1] !== '#/map/civ' || r[2] !== '#/map/civ/family') errs.push(tag + ' provision crumbs do not lead into the map');
    // opening the provision put its change-of-course question in memory as new
    let st = await ev(() => JSON.parse(localStorage.getItem('sinag.codal.v1') || '{}').cards || {});
    if (!st['q|shift:psych-incapacity']) errs.push(tag + ' question not registered when the provision was opened');

    // 3. the shift page: crumbs, graded answer into memory, next in the field path
    await go('#/shifts/psych-incapacity', 'shift');
    r = await ev(() => ({ crumbs: [...document.querySelectorAll('.mapcr a, .mapcr span')].map(a => a.textContent).filter(t => t.trim() && t !== '›'), next: [...document.querySelectorAll('.pn a')].map(a => a.textContent + ' ' + a.getAttribute('href')) }));
    console.log(tag, 'shift', JSON.stringify(r));
    if (!r.crumbs.includes('Civil Law') || !r.crumbs.includes('Persons and family')) errs.push(tag + ' shift crumbs');
    if (!r.next.some(t => /Next in Civil Law: RA 11642/.test(t) || /Next in Civil Law: .*#\/map\/civ\/ra11642/.test(t))) errs.push(tag + ' shift next should be the next item in the path (RA 11642): ' + r.next.join(' | '));
    await pg.click('#sq .opt[data-o="0"]'); await pg.waitForTimeout(400);   // wrong on purpose
    r = await ev(() => ({ res: document.querySelector('#sq .qres')?.textContent, card: (JSON.parse(localStorage.getItem('sinag.codal.v1') || '{}').cards || {})['q|shift:psych-incapacity'] }));
    console.log(tag, 'graded', r.res && r.res.slice(0, 80), JSON.stringify(r.card && { reps: r.card.reps, due: r.card.due > Date.now() }));
    if (!r.card || r.card.reps !== 1 || !/In your memory now/.test(r.res || '')) errs.push(tag + ' shift answer not rated into memory');

    await pg.waitForTimeout(400);
    // 4. Today counts provisions and questions together; one next step from the path
    await ev(() => { const S = JSON.parse(localStorage.getItem('sinag.codal.v1')); const now = Date.now();
      S.cards['q|shift:psych-incapacity'].due = now - 1000;
      S.cards['civil|article-1156'] = { s: 3, d: 5, ivl: 3, reps: 2, lapses: 0, last: now - 6 * 864e5, due: now - 1000 };
      S.cards['q|enf:d2'] = { s: 2, d: 6, ivl: 2, reps: 5, lapses: 4, last: now - 5 * 864e5, due: now + 864e5 };
      S.last = { c: 'family', p: 'article-36', l: 'Family Code · Article 36' };
      localStorage.setItem('sinag.codal.v1', JSON.stringify(S)); });
    await pg.reload({ waitUntil: 'networkidle' });
    await go('#/', 'home');
    r = await ev(() => ({ h1: document.querySelector('.next h1')?.textContent, path: document.querySelector('.pathnext')?.textContent.replace(/\s+/g, ' ') }));
    console.log(tag, 'today', JSON.stringify(r));
    if (r.h1 !== '1 provision and 1 question are slipping') errs.push(tag + ' Today heading: ' + r.h1);
    if (!/Next in your path · Civil Law/.test(r.path || '')) errs.push(tag + ' Today path line');

    // 5. Review mixes the question with the provision
    await go('#/review');
    const seen = [];
    for (let k = 0; k < 3; k++) {
      const q = await ev(() => !!document.querySelector('#rq'));
      const pv = await ev(() => !!document.querySelector('.reviewcard .prompt'));
      if (q) { seen.push('q'); await pg.click('#rq .opt[data-o="1"]'); await pg.waitForTimeout(200); await pg.click('#rnx'); await pg.waitForTimeout(400); }
      else if (pv) { seen.push('p'); await pg.click('[data-rate="3"]'); await pg.waitForTimeout(400); }
      else break;
    }
    r = await ev(() => document.querySelector('.reviewcard h1')?.textContent);
    console.log(tag, 'review', seen.join(','), r);
    if (!(seen.includes('q') && seen.includes('p')) || r !== 'Session complete.') errs.push(tag + ' review did not mix and finish: ' + seen.join(','));

    // 6. sprint shows a due question card
    await ev(() => { const S = JSON.parse(localStorage.getItem('sinag.codal.v1')); S.cards['q|shift:psych-incapacity'].due = Date.now() - 1000; localStorage.setItem('sinag.codal.v1', JSON.stringify(S)); });
    await pg.reload({ waitUntil: 'networkidle' });
    await go('#/sprint', 'sprint');
    r = await ev(() => ({ q: !!document.querySelector('#spq'), time: !!document.querySelector('#sptime'), title: document.querySelector('.qtitle')?.textContent }));
    console.log(tag, 'sprint', JSON.stringify(r));
    if (!r.q || !r.time) errs.push(tag + ' sprint did not show the question card');
    await pg.keyboard.press('2'); await pg.waitForTimeout(200);
    r = await ev(() => !!document.querySelector('#spnx'));
    if (!r) errs.push(tag + ' sprint question: key 2 did not answer');
    await pg.keyboard.press('Enter'); await pg.waitForTimeout(500);
    r = await ev(() => document.querySelector('.sprintdone h1')?.textContent || document.querySelector('.sprint .prompt, #spq') && 'next');
    console.log(tag, 'sprint after', r);
    await go('#/');

    // 7. Progress lists the stubborn case file by a readable label
    await go('#/progress');
    r = await ev(() => [...document.querySelectorAll('.card ul.small li a')].map(a => a.textContent + ' ' + a.getAttribute('href')));
    console.log(tag, 'progress', JSON.stringify(r.slice(0, 3)));
    if (!r.some(t => /Case file 2, enforcing a judgment #\/enforce\/drills\?only=d2/.test(t))) errs.push(tag + ' stubborn case file label');

    // 8. map marker on a provision with a change of course
    const dv = await ev(async () => { const d = await (await fetch('data/codes/family.json')).json(); return d.provisions.find(p => p.i === 'article-36').d; });
    await go('#/map/civ/family/' + dv);
    r = await ev(() => [...document.querySelectorAll('.mapprov li')].filter(li => li.querySelector('.shx')).map(li => li.querySelector('.pl').textContent));
    console.log(tag, 'markers', JSON.stringify(r));
    if (!r.includes('Article 36')) errs.push(tag + ' map marker on Art. 36');

    // 9. search finds the change of course and the move
    await go('#/search?q=garnishment');
    await pg.waitForTimeout(2500);
    r = await ev(() => [...document.querySelectorAll('#sr a[href^="#/enforce/"], #sr a[href^="#/shifts/"]')].map(a => a.getAttribute('href')));
    console.log(tag, 'search', JSON.stringify(r.slice(0, 5)));
    if (!r.includes('#/enforce/garnish-banks')) errs.push(tag + ' search did not find the garnishment move');

    // 10. lesson next follows the path across tracks; walk and lesson crumbs lead into the map
    await go('#/lesson/reasoning');
    r = await ev(() => ({ c: [...document.querySelectorAll('.crumbs a')].map(a => a.getAttribute('href')), n: [...document.querySelectorAll('.pn a')].map(a => a.textContent) }));
    console.log(tag, 'lesson', JSON.stringify(r));
    if (r.c[0] !== '#/map' || r.c[1] !== '#/map/craft') errs.push(tag + ' lesson crumbs');
    if (!r.n.some(t => /Next in The Lawyer’s Craft: Enforcing a judgment/.test(t))) errs.push(tag + ' lesson next should cross into the enforcement track');
    await pg.close();
  }
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
