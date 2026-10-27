"""Build the single-file game with every image in assets/ inlined as a data URI.

python3 tools/build.py                  -> index.html (release, assets/ only)
python3 tools/build.py --test [dir ...] -> test.html  (assets/ plus extra folders, and a debug hook)
"""
import base64, json, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
src = (root / 'src' / 'game.html').read_text()
MIME = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}

test = '--test' in sys.argv
dirs = [root / 'assets'] + [pathlib.Path(a) for a in sys.argv[1:] if not a.startswith('--')]
assets = {}
for d in dirs:
    for p in sorted(d.glob('*')):
        if p.suffix.lower() in MIME:
            assets[p.stem] = 'data:%s;base64,%s' % (MIME[p.suffix.lower()], base64.b64encode(p.read_bytes()).decode())

out = src.replace('/*ASSETS*/{}', json.dumps(assets))

if test:
    out = out.replace("function die(reason) {", "function die(reason) {\n  if (window.__god) return;")
    out = out.replace("/*TEST_HOOK*/", """
window.__t = {
  go(d, lane) { playerName = 'Test'; startGame(); dist = d; lastStage = stageIndexAt(d); if (lane !== undefined) { player.lane = lane; player.xw = laneX(lane); } },
  spawn(type, lane, z) { const o = { type, lane, z, done:false, tight:false, bonus:false, used:false }; obstacles.push(o); addCoinsOn(o); },
  clear() { obstacles = []; coins = []; },
  set(k, v) { if (k === 'h') player.h = v; if (k === 'roll') player.roll = v; if (k === 'air') { player.airborne = true; player.h = v; player.vh = 0; } },
  info() { return { dist, state, h: player.h, lane: player.lane, n: obstacles.length }; },
  pause(p) { window.__pause = p; },
  step(dd) { dist += dd; time += dd / 7; for (const o of obstacles) o.z -= dd; for (const c of coins) c.z -= dd; lastStage = stageIndexAt(dist); }
};
""")
    out = out.replace("if (state === 'play') update(dt);", "if (state === 'play' && !window.__pause) update(dt);")
    name = 'test.html'
else:
    name = 'index.html'

(root / name).write_text(out)
print(name, round(len(out) / 1024), 'KB,', len(assets), 'images')
