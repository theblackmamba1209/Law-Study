// Administrative Code: restored sections, keyed tables, amendments, repeal, aliases
const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const errs = []; const SH = '/home/claude/work/shots/';
  const pg = await b.newPage({ viewport: { width: 390, height: 900 }, deviceScaleFactor: 2 });
  pg.on('pageerror', e => errs.push(e.message));
  const look = async (h, f) => { await pg.goto('http://localhost:8811/' + h, { waitUntil: 'networkidle' }); await pg.waitForTimeout(350); if (f) await pg.screenshot({ path: SH + f + '.png', fullPage: true });
    return pg.evaluate(() => ({ cap: document.querySelector('#law .lcap')?.textContent, inforce: document.querySelector('#law .inforce')?.textContent.replace(/\s+/g, ' '), status: document.querySelector('#law .status')?.textContent.slice(0, 80), tables: document.querySelectorAll('#law > .text .tbl').length, text: document.querySelector('#law > .text')?.textContent.replace(/\s+/g, ' ') })); };
  let r = await look('#/p/admincode/book-i-sec-3', 'adm3'); console.log('I-3', r.cap, r.text.slice(0, 80)); if (!/national territory comprises/i.test(r.text)) errs.push('Book I Sec 3 missing');
  r = await look('#/p/admincode/book-i-sec-26', 'adm26'); console.log('I-26', r.cap, r.inforce, r.tables); if (!/RA 9849/.test(r.inforce || '') || r.tables < 2 || !/Eidul Adha/.test(r.text)) errs.push('Sec 26 not in force');
  r = await look('#/p/admincode/book-v-title-ii-subtitle-c-sec-5', 'admneda'); console.log('V-II-C-5', r.status, r.tables); if (!/Repealed/.test(r.status || '') || r.tables !== 1) errs.push('NEDA Sec 5');
  r = await look('#/p/admincode/book-iv-title-iii-sec-16-a'); console.log('IV-III-16A', r.cap, r.text.slice(0, 80)); if (!/Chief Public Attorney/.test(r.text)) errs.push('16-A missing');
  r = await look('#/p/admincode/book-iv-title-iii-sec-14'); console.log('IV-III-14', r.inforce); if (!/RA 9406/.test(r.inforce || '')) errs.push('PAO 14 not amended');
  r = await look('#/p/admincode/book-vi-sec-1'); console.log('VI-1', r.cap, r.text.length); if (!/originate exclusively/.test(r.text)) errs.push('Book VI Sec 1 missing');
  r = await look('#/p/admincode/book-iv-title-ii-ch-5-sec-14'); console.log('alias', r.cap); if (!/Public Attorney/.test(r.cap || '')) errs.push('alias did not resolve');
  r = await look('#/p/admincode/book-iv-ch-13-sec-58', 'adm58'); console.log('IV-58', r.cap, r.tables);
  r = await look('#/p/ra7080/section-2'); if (!/Fifty million/.test(r.text)) errs.push('7080');
  const ov = await pg.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth); if (ov > 1) errs.push('overflow ' + ov);
  await b.close();
  console.log(errs.length ? errs.join('\n') : 'NO ERRORS');
})();
