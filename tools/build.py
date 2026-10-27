"""Build the single-file game with every image in assets/ inlined as a data URI.

python3 tools/build.py                  -> index.html (release, assets/ only)
python3 tools/build.py --test [dir ...] -> test.html  (assets/ plus extra folders, and a debug hook)
"""
import base64, json, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
SRC = {'index.html': 'game3d.html', 'classic.html': 'game.html'}
target = next((a for a in sys.argv[1:] if a.endswith('.html')), 'index.html')
src = (root / 'src' / SRC.get(target, 'game3d.html')).read_text()
MIME = {'.webp': 'image/webp', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg'}

test = '--test' in sys.argv
dirs = [root / 'assets'] + [pathlib.Path(a) for a in sys.argv[1:] if not a.startswith('--') and not a.endswith('.html')]
assets = {}
for d in dirs:
    for p in sorted(d.glob('*')):
        if p.suffix.lower() in MIME:
            assets[p.stem] = 'data:%s;base64,%s' % (MIME[p.suffix.lower()], base64.b64encode(p.read_bytes()).decode())

out = src.replace('/*ASSETS*/{}', json.dumps(assets))

if test and 'game3d' in SRC.get(target, ''):
    out = out.replace('https://cdn.jsdelivr.net/npm/three@0.160.0/', '/three/')
    out = out.replace("/*TEST_HOOK*/", '''
window.__t = {
  go(d, lane) { playerName = 'Test'; startGame(); dist = d; lastStage = stageAt(d).i; rebuildChunks(); if (lane !== undefined) { player.lane = lane; player.xw = laneX(lane); camX = player.xw * 0.8; } },
  spawn(type, lane, ahead) { return addObstacle(type, lane, dist + ahead); },
  clear() { clearObjects(); },
  set(k, v) { if (k === 'h') player.h = v; if (k === 'roll') player.roll = v; if (k === 'air') { player.airborne = true; player.h = v; player.vh = 0; } if (k === 'bear') { bearD = v; lastNear = time; } },
  info() { return { dist, state, h: player.h, lane: player.lane, onRamp: player.onRamp, airborne: player.airborne, n: obstacles.length, coins: coinCount }; },
  pause(p) { window.__pause = p; },
  step(dd) { dist += dd; time += dd / 12; },
  dbg() { const m = obstacles[0].mesh; const b = new THREE.Box3().setFromObject(m); return { min: b.min.toArray().map(v => +v.toFixed(2)), max: b.max.toArray().map(v => +v.toFixed(2)),
    parts: m.children.slice(0, 8).map(c => [c.geometry && c.geometry.type, c.position.toArray().map(v => +v.toFixed(2)), c.material && c.material.color && c.material.color.getHexString(), c.geometry && c.geometry.parameters && JSON.stringify(c.geometry.parameters)]) }; }
};''')
    name = 'test.html'
elif test:
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
    name = target

(root / name).write_text(out)
print(name, round(len(out) / 1024), 'KB,', len(assets), 'images')
