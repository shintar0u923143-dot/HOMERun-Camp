"""Make a set of ground tiles join each other without a visible line.

python3 tools/seam.py tile-camp      (uses assets/tile-camp-01.webp ... -0N)

Tile 01 already loops onto itself. Every other tile has its top and bottom bands
blended into tile 01's top and bottom bands, so any tile can follow any other.
"""
import sys, pathlib
import numpy as np
from PIL import Image

root = pathlib.Path(__file__).resolve().parent.parent / 'assets'
prefix = sys.argv[1]
frac = float(sys.argv[2]) if len(sys.argv) > 2 else 0.14
files = sorted(root.glob(f'{prefix}-0[0-9].webp'))
ref = np.asarray(Image.open(files[0]).convert('RGB')).astype(np.float32)
H, W = ref.shape[:2]
b = int(H * frac)
ramp = (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, b)))[:, None, None]   # smooth 0 -> 1
for f in files[1:]:
    a = np.asarray(Image.open(f).convert('RGB').resize((W, H), Image.LANCZOS)).astype(np.float32)
    # top band: fully tile-01 at the very top edge, fading to this tile's own art
    a[:b] = ref[:b] * (1 - ramp) + a[:b] * ramp
    # bottom band: this tile's art fading to fully tile-01 at the bottom edge
    a[H - b:] = a[H - b:] * (1 - ramp) + ref[H - b:] * ramp
    Image.fromarray(a.astype(np.uint8)).save(f, 'WEBP', quality=86, method=6)
    print('  matched edges:', f.name)
