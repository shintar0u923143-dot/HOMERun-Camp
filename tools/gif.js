// Record short deterministic clips of the scrolling world as PNG frames.
const { chromium } = require('playwright');
const path = require('path');
const OUT = process.argv[2] || '/tmp/claude-0/gif';
require('fs').mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 400, height: 700 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(__dirname, '../test.html'));
  await page.waitForTimeout(700);
  const clips = [[24, 1, 36], [186, 1, 30], [338, 1, 30]];   // start meter, lane, frames
  let f = 0;
  for (const [start, lane, n] of clips) {
    await page.evaluate(([s, l]) => { window.__god = true; window.__t.pause(false); window.__t.go(s, l); window.__t.clear(); window.__t.pause(true);
      if (s < 100) { window.__t.spawn('van', 0, 14); window.__t.spawn('grill', 2, 20); window.__t.spawn('tent', 1, 28); } }, [start, lane]);
    for (let i = 0; i < n; i++) {
      await page.evaluate(() => window.__t.step(0.55));
      await page.waitForTimeout(30);
      await page.screenshot({ path: `${OUT}/f${String(f++).padStart(3, '0')}.png` });
    }
  }
  await browser.close();
  console.log(f, 'frames');
})();
