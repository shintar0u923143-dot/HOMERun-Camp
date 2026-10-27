// Screenshots along the whole loop to check the scrolling tile world.
const { chromium } = require('playwright');
const path = require('path');
const OUT = process.argv[2] || '/tmp/claude-0/tiles';
require('fs').mkdirSync(OUT, { recursive: true });

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 400, height: 700 }, deviceScaleFactor: 2 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  await page.goto('file://' + path.resolve(__dirname, '../test.html'));
  await page.waitForTimeout(700);

  const shots = [
    ['a-camp-30', 30, 1, t => { t.spawn('van', 0, 6); t.spawn('grill', 2, 10); t.spawn('tent', 1, 16); }],
    ['b-camp-32', 32.6, 1, t => { t.spawn('van', 0, 3.4); t.spawn('grill', 2, 7.4); t.spawn('tent', 1, 13.4); }],
    ['c-door-150', 150, 1, null],
    ['d-door-188', 188, 1, null],
    ['e-house-230', 230, 0, t => { t.spawn('table', 1, 8); t.spawn('counter', 2, 12); }],
    ['f-house-exit-345', 345, 1, null],
    ['g-yard-390', 390, 2, t => { t.spawn('hammock', 1, 9); t.spawn('van', 0, 14); }],
    ['h-yard-end-548', 548, 1, null]
  ];
  for (const [name, d, lane, extra] of shots) {
    await page.evaluate(([d, lane]) => { window.__god = true; window.__t.pause(false); window.__t.go(d, lane); window.__t.clear(); window.__t.pause(true); }, [d, lane]);
    if (extra) await page.evaluate(`(${extra.toString()})(window.__t)`);
    await page.waitForTimeout(120);
    await page.screenshot({ path: `${OUT}/${name}.png` });
  }
  // rough frame-time check over 2 seconds of real play
  const fps = await page.evaluate(() => new Promise(res => {
    window.__t.pause(false); window.__t.go(20, 1);
    let n = 0; const t0 = performance.now();
    (function f() { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else res(n / 2); })();
  }));
  console.log('fps (headless, software render):', fps);
  await browser.close();
  console.log(errs.length ? 'ERRORS:\n' + errs.join('\n') : 'no page errors');
})();
