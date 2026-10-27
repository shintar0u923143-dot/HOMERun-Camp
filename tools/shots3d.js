// Headless screenshots of the 3D build (serve /tmp/claude-0/www on :8765 first).
const { chromium } = require('playwright');
const OUT = process.argv[2] || '/tmp/claude-0/s3d';
require('fs').mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 400, height: 700 }, deviceScaleFactor: 1.5 });
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
  await page.goto('http://127.0.0.1:8765/test.html');
  await page.waitForFunction(() => !!window.__t, null, { timeout: 30000 });
  await page.waitForTimeout(800);
  await page.screenshot({ path: OUT + '/00-title.png' });
  const scene = async (name, setup, wait = 120, run = 0) => {
    await page.evaluate(() => { window.__god = true; window.__pause = false; });
    await page.evaluate(setup);
    if (run) { await page.waitForTimeout(run); }
    await page.evaluate(() => { window.__pause = true; });
    await page.waitForTimeout(wait);
    await page.screenshot({ path: `${OUT}/${name}.png` });
  };
  await scene('01-camp', () => { const t = window.__t; t.go(60, 1); t.clear(); t.spawn('grill', 1, 12); t.spawn('tent', 0, 22); t.spawn('hammock', 2, 30); t.spawn('canopy', 1, 42); t.spawn('van', 2, 58); });
  await scene('02-vans', () => { const t = window.__t; t.go(80, 1); t.clear(); t.spawn('van', 0, 9); t.spawn('van', 2, 16); t.spawn('van', 1, 40); });
  await scene('03-roof', () => { const t = window.__t; t.go(100, 1); t.clear(); t.spawn('van', 1, 1); t.spawn('tent', 0, 20); }, 120, 250);
  await scene('04-jump', () => { const t = window.__t; t.go(120, 1); t.clear(); t.spawn('grill', 1, 2); t.set('air', 1.4); });
  await scene('05-house-door', () => { const t = window.__t; t.go(395.2 - 24, 1); t.clear(); });
  await scene('06-kitchen', () => { const t = window.__t; t.go(440, 1); t.clear(); t.spawn('table', 1, 14); t.spawn('chair', 0, 20); t.spawn('cat', 2, 26); });
  await scene('07-living', () => { const t = window.__t; t.go(580, 0); t.clear(); t.spawn('counter', 2, 16); t.spawn('wagon', 1, 26); });
  await scene('08-backdoor', () => { const t = window.__t; t.go(707.2 - 20, 1); t.clear(); });
  await scene('09-pool-ahead', () => { const t = window.__t; t.go(811.2 - 16, 1); t.clear(); });
  await scene('10-swim', () => { const t = window.__t; t.go(830, 1); t.clear(); t.spawn('float', 1, 10); t.spawn('float', 2, 18); });
  await scene('11-yard', () => { const t = window.__t; t.go(925, 0); t.clear(); t.spawn('hammock', 1, 14); t.set('bear', 0.4); });
  const fps = await page.evaluate(() => new Promise(res => { window.__pause = false; window.__t.go(40, 1); let n = 0; const t0 = performance.now(); (function f() { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else res(n / 2); })(); }));
  console.log('fps (headless software GL):', fps);
  await browser.close();
  console.log(errs.length ? 'CONSOLE:\n' + [...new Set(errs)].slice(0, 15).join('\n') : 'no errors');
})();
