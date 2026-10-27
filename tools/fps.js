const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const dsf of [1, 2]) {
    const p = await b.newPage({ viewport: { width: 400, height: 700 }, deviceScaleFactor: dsf });
    await p.goto('file://' + process.cwd() + '/test.html'); await p.waitForTimeout(500);
    const r = await p.evaluate(() => {
      window.__god = true; window.__t.go(20, 1); window.__t.pause(true);
      const ts = [];
      for (let i = 0; i < 20; i++) { const t0 = performance.now(); window.__t.pause(false); window.__t.pause(true); }
      return null;
    });
    // time render() directly via frames
    const ms = await p.evaluate(() => new Promise(res => {
      window.__t.pause(false); let n = 0; const t0 = performance.now();
      (function f() { n++; if (n < 40) requestAnimationFrame(f); else res((performance.now() - t0) / n); })();
    }));
    console.log('dsf', dsf, 'ms/frame', ms.toFixed(1));
    await p.close();
  }
  await b.close();
})();
