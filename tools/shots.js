// Headless screenshots of each stage for visual checks.
const { chromium } = require('playwright');
const path = require('path');
const OUT = process.argv[2] || '/tmp/claude-0/shots';
require('fs').mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 400, height: 700 }, deviceScaleFactor: 2 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto('file://' + path.resolve(__dirname, '../test.html'));
  await page.waitForTimeout(600);
  await page.screenshot({ path: OUT + '/0-title.png' });

  const scene = async (name, fn, runMs = 60) => {
    await page.evaluate(() => { window.__god = true; window.__t.pause(false); });
    await page.evaluate(fn);
    await page.waitForTimeout(runMs);
    await page.evaluate(() => window.__t.pause(true));
    await page.waitForTimeout(80);
    await page.screenshot({ path: OUT + '/' + name + '.png' });
  };

  await scene('1-camp', () => { const t = window.__t; t.go(30, 1); t.clear();
    t.spawn('grill', 0, 7); t.spawn('tent', 2, 13); t.spawn('canopy', 1, 19); t.spawn('hammock', 0, 27); t.spawn('van', 2, 36); });
  await scene('2-vans', () => { const t = window.__t; t.go(60, 0); t.clear();
    t.spawn('van', 1, 4); t.spawn('van', 2, 13); });
  await scene('3-roof', () => { const t = window.__t; t.go(80, 1); t.clear();
    t.spawn('van', 1, 0.6); t.spawn('grill', 0, 9); }, 120);
  await scene('4-jump', () => { const t = window.__t; t.go(90, 1); t.clear();
    t.spawn('grill', 1, 1.2); t.spawn('tent', 0, 10); t.set('air', 90); }, 30);
  await scene('5-door-far', () => { const t = window.__t; t.go(150, 1); t.clear(); });
  await scene('6-door-near', () => { const t = window.__t; t.go(186, 1); t.clear(); });
  await scene('7-house', () => { const t = window.__t; t.go(240, 1); t.clear();
    t.spawn('table', 0, 7); t.spawn('chair', 1, 12); t.spawn('cat', 2, 9); t.spawn('counter', 2, 19); t.spawn('wagon', 1, 26); });
  await scene('8-backyard', () => { const t = window.__t; t.go(420, 1); t.clear();
    t.spawn('hammock', 1, 8); t.spawn('grill', 2, 12); t.spawn('tent', 0, 16); t.spawn('van', 0, 30); });
  await scene('9-roll', () => { const t = window.__t; t.go(470, 2); t.clear();
    t.spawn('tent', 2, 1.0); t.set('roll', 0.4); }, 30);

  await browser.close();
  console.log(errs.length ? 'ERRORS:\n' + errs.join('\n') : 'no page errors');
})();
