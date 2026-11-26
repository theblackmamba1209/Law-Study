const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage();
  await pg.goto('http://localhost:8811/#/p/labor/article-141', { waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
  console.log(await pg.evaluate(() => ({ hl: JSON.parse(localStorage.getItem('sinag.codal.v1')||'{}').settings, n: document.querySelectorAll('#law .hl-num').length, html: document.querySelector('#law .en.l2 p').innerHTML.slice(0,200), bg: getComputedStyle(document.querySelector('#law .hl-num')||document.body).backgroundImage })));
  await b.close();
})();
