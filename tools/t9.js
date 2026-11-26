const { chromium } = require('/opt/npm-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
  const pg = await b.newPage({ viewport: { width: 1100, height: 900 }, colorScheme: 'dark' });
  await pg.goto('http://localhost:8811/#/p/rpc/article-248', { waitUntil: 'networkidle' }); await pg.waitForTimeout(400);
  await pg.screenshot({ path: '/home/claude/work/shots/dark248.png' });
  await b.close();
})();
