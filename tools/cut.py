"""Cut a Gemini sprite sheet into the individual game images.

python3 tools/cut.py <sheet image> <sheet name> [out dir]
python3 tools/cut.py --list            # show every sheet name and what it produces

Sprite sheets: magenta is keyed out, each object is found as a blob and assigned to its
grid cell by position, then trimmed and saved. Tile and wall sheets are split on the
magenta gutters (or evenly if Gemini skipped them) and their edges are blended so they loop.
"""
import sys, pathlib
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parent.parent

def lanes(t): return [f'obs-{l}-lane-{t}' for l in ('left', 'mid', 'right')]
RUN = ['run-01', 'run-02', 'run-03', 'run-04', 'jump', 'roll', 'climb-01', 'climb-02']

SHEETS = {}
for t in ('van', 'tent', 'grill', 'hammock', 'canopy', 'counter', 'table', 'chair', 'cat', 'wagon'):
    SHEETS[f'sheet-obs-{t}'] = dict(kind='sprites', grid=(1, 3), names=lanes(t))
for l in ('left', 'mid', 'right'):
    SHEETS[f'sheet-runner-{l}'] = dict(kind='sprites', grid=(2, 4), names=[f'runner-{l}-lane-{a}' for a in RUN])
SHEETS['sheet-bear-coin'] = dict(kind='sprites', grid=(1, 3), names=['bear-run-01', 'bear-run-02', 'coin-leaf'])
SHEETS['sheet-props-camp'] = dict(kind='sprites', grid=(2, 3), mirror=True,
    names=['pine-tall', 'pine-round', 'leafy-tree', 'bush', 'lantern-post', 'log-pile'])
SHEETS['sheet-props-yard'] = dict(kind='sprites', grid=(2, 2), mirror=True,
    names=['round-tree', 'hedge-ball', 'flower-pot', 'garden-lamp'])
SHEETS['sheet-tiles-camp-a'] = dict(kind='tiles', trail=True, names=['tile-camp-01', 'tile-camp-02'])
SHEETS['sheet-tiles-camp-b'] = dict(kind='tiles', trail=True, names=['tile-camp-03', 'tile-camp-04'])
SHEETS['sheet-tiles-house-a'] = dict(kind='tiles', names=['tile-house-01', 'tile-house-02'])
SHEETS['sheet-tiles-house-b'] = dict(kind='tiles', names=['tile-house-03', 'tile-house-enter'], loop=[True, False])
SHEETS['sheet-tiles-yard-a'] = dict(kind='tiles', names=['tile-backyard-01', 'tile-backyard-02'])
SHEETS['sheet-tiles-yard-b'] = dict(kind='tiles', names=['tile-backyard-03', 'tile-backyard-exit'], loop=[True, False])
SHEETS['sheet-walls-house-left'] = dict(kind='walls', names=[f'wall-house-left-0{i}' for i in range(1, 5)])
SHEETS['sheet-walls-house-right'] = dict(kind='walls', names=[f'wall-house-right-0{i}' for i in range(1, 5)])
SHEETS['sheet-fence'] = dict(kind='walls', key=True, names=['wall-yard-left-01', 'wall-yard-left-02', 'wall-yard-right-01', 'wall-yard-right-02'])
SHEETS['horizon-camp'] = dict(kind='single', names=['horizon-camp'])
SHEETS['horizon-backyard'] = dict(kind='single', names=['horizon-backyard'])


def magenta_alpha(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mn = np.minimum(r, b)
    m = mn - g - 0.6 * np.abs(r - b)
    return np.clip((70 - m) / 45, 0, 1)


def despill(a, alpha):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mn = np.minimum(r, b)
    spill = np.clip(mn - g, 0, None) * np.clip(1.6 - alpha, 0, 1)
    return np.dstack([np.clip(r - spill * .95, 0, 255), g, np.clip(b - spill * .95, 0, 255)])


def save(img, name, out, max_side=None, quality=88):
    if max_side:
        img.thumbnail((max_side, max_side), Image.LANCZOS)
    p = out / f'{name}.webp'
    img.save(p, 'WEBP', quality=quality, method=6)
    print(f'  {name}.webp {img.size[0]}x{img.size[1]}')


def cut_sprites(im, spec, out):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    H, W = a.shape[:2]
    alpha = magenta_alpha(a)
    al = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(0.9))
    alpha = np.asarray(al).astype(np.float32) / 255
    rgb = despill(a, alpha)
    solid = alpha > 0.5
    # merge nearby parts of one object (legs, ropes) before labelling
    grown = ndimage.binary_dilation(solid, iterations=max(3, W // 200))
    lab, n = ndimage.label(grown)
    rows, cols = spec['grid']
    cells = {}
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        comp = (lab[sl] == i) & solid[sl]
        if comp.sum() < 0.0015 * W * H:
            continue
        ys, xs = np.nonzero(comp)
        cy, cx = ys.mean() + sl[0].start, xs.mean() + sl[1].start
        cell = (min(rows - 1, int(cy / (H / rows))), min(cols - 1, int(cx / (W / cols))))
        cells.setdefault(cell, []).append(i)
    for idx, name in enumerate(spec['names']):
        cell = (idx // cols, idx % cols)
        if cell not in cells:
            print(f'  !! nothing found for {name} (row {cell[0] + 1}, column {cell[1] + 1})')
            continue
        mask = np.isin(lab, cells[cell]) & (alpha > 0.02)
        ys, xs = np.nonzero(mask)
        y0, y1, x0, x1 = max(0, ys.min() - 3), min(H, ys.max() + 4), max(0, xs.min() - 3), min(W, xs.max() + 4)
        al_c = np.where(mask, alpha, 0)[y0:y1, x0:x1]
        rgb_c = rgb[y0:y1, x0:x1]
        if 'climb' in name:
            al_c = strip_gray(rgb_c, al_c)          # Gemini likes to add a ladder; the van has its own
        if spec.get('mirror'):
            al_c = strip_ground_line(al_c)          # the thin "ground" bar Gemini draws under props
        ys2, xs2 = np.nonzero(al_c > 0.05)
        if len(ys2):
            al_c = al_c[ys2.min():ys2.max() + 1, xs2.min():xs2.max() + 1]
            rgb_c = rgb_c[ys2.min():ys2.max() + 1, xs2.min():xs2.max() + 1]
        rgba = np.dstack([rgb_c, al_c * 255]).astype(np.uint8)
        piece = Image.fromarray(rgba, 'RGBA')
        if spec.get('mirror'):
            save(piece.copy(), f'prop-right-{name}', out, 512)
            save(piece.transpose(Image.FLIP_LEFT_RIGHT), f'prop-left-{name}', out, 512)
        else:
            save(piece, name, out, 512)


def strip_gray(rgb, alpha):
    """Remove grey, unsaturated pixels (a ladder) and keep the biggest remaining body."""
    mx, mn = rgb.max(axis=2), rgb.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1)
    gray = (sat < 0.16) & (mx > 55) & (mx < 200)
    a = np.where(gray, 0, alpha)
    lab, n = ndimage.label(ndimage.binary_opening(a > 0.5, iterations=2))
    if n:
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        keep = 1 + int(np.argmax(sizes))
        body = ndimage.binary_dilation(lab == keep, iterations=3)
        a = np.where(body, a, 0)
    return a


def strip_ground_line(alpha):
    """Drop the bottom rows that span almost the whole width (a drawn ground bar)."""
    solid = alpha > 0.3
    w = max(1, solid.any(axis=0).sum())
    counts = solid.sum(axis=1)
    H = len(counts)
    wide = np.nonzero(counts[int(H * 0.8):] > 0.75 * w)[0]
    if len(wide):
        top = int(H * 0.8) + wide.min()
        alpha = alpha.copy(); alpha[max(0, top - 2):] = 0
    return alpha


def normalize_path(arr):
    """Stretch so the brown trail fills exactly the middle half of a ground tile."""
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    trail = (r > g * 1.02) & (r > b * 1.15)
    frac = trail.mean(axis=0)
    cols = np.nonzero(frac > 0.5)[0]
    W = arr.shape[1]
    if len(cols) < W * 0.15:
        return arr
    pl, pr = cols.min(), cols.max() + 1
    xs = np.arange(W) + 0.5
    src = np.interp(xs, [0, W * 0.25, W * 0.75, W], [0, pl, pr, W])
    src = np.clip(src.astype(int), 0, W - 1)
    print(f'    trail was columns {pl}-{pr} of {W}; stretched to the middle half')
    return arr[:, src]


def gutter_split(a, n, axis):
    """Split along magenta gutters; axis=1 -> side by side, axis=0 -> stacked."""
    mag = magenta_alpha(a) < 0.3
    frac = mag.mean(axis=0 if axis == 1 else 1)
    L = len(frac)
    content = frac < 0.5
    segs, start = [], None
    for i, c in enumerate(list(content) + [False]):
        if c and start is None: start = i
        if not c and start is not None:
            if i - start > L * 0.08: segs.append((start, i))
            start = None
    if len(segs) != n:
        print(f'  (gutters not clear: found {len(segs)} parts, splitting evenly into {n})')
        step = L / n
        segs = [(int(i * step), int((i + 1) * step)) for i in range(n)]
    return segs


def trim_magenta(piece):
    """Remove leftover magenta border rows/columns."""
    m = magenta_alpha(piece) > 0.7
    keep_r = np.nonzero(m.mean(axis=1) > 0.9)[0]
    keep_c = np.nonzero(m.mean(axis=0) > 0.9)[0]
    if len(keep_r) and len(keep_c):
        return piece[keep_r.min():keep_r.max() + 1, keep_c.min():keep_c.max() + 1]
    return piece


def make_loop(arr, axis, frac=0.08):
    """Crossfade one end into the other so the image repeats without a seam."""
    L = arr.shape[axis]
    b = max(4, int(L * frac))
    body = np.take(arr, range(b, L), axis=axis).astype(np.float32)
    head = np.take(arr, range(0, b), axis=axis).astype(np.float32)
    n = body.shape[axis]
    tail_idx = range(n - b, n)
    tail = np.take(body, tail_idx, axis=axis)
    w = (np.arange(b) / b).reshape((-1, 1, 1) if axis == 0 else (1, -1, 1))
    blended = tail * (1 - w) + head * w
    if axis == 0: body[n - b:] = blended
    else: body[:, n - b:] = blended
    return body


def cut_tiles(im, spec, out, axis, size):
    a = np.asarray(im.convert('RGB')).astype(np.float32)
    names = spec['names']
    segs = gutter_split(a, len(names), axis)
    loops = spec.get('loop', [True] * len(names))
    for (s, e), name, loop in zip(segs, names, loops):
        piece = a[:, s:e] if axis == 1 else a[s:e, :]
        piece = trim_magenta(piece)
        # Gemini rounds tile corners: trim 2% so no magenta or rounded edge is left
        h0, w0 = piece.shape[:2]
        piece = piece[int(h0 * .02):h0 - int(h0 * .02), int(w0 * .03):w0 - int(w0 * .03)]
        if spec.get('trail'):
            piece = normalize_path(piece)
        alpha = None
        if spec.get('key'):
            alpha = magenta_alpha(piece)
            piece = despill(piece, alpha)
        if loop:
            # tiles repeat along the run direction: vertically for ground, horizontally for walls
            la = 0 if axis == 1 else 1
            piece = make_loop(piece, la)
            if alpha is not None: alpha = make_loop(alpha[..., None], la)[..., 0]
        if alpha is not None:
            img = Image.fromarray(np.dstack([piece, alpha * 255]).astype(np.uint8), 'RGBA')
        else:
            img = Image.fromarray(piece.astype(np.uint8), 'RGB')
        img = img.resize(size, Image.LANCZOS)
        save(img, name, out, quality=86)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--list':
        for k, v in SHEETS.items(): print(f'{k:28s} -> {", ".join(v["names"])}')
        return
    src, sheet = sys.argv[1], sys.argv[2]
    out = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / 'assets'
    out.mkdir(parents=True, exist_ok=True)
    spec = SHEETS[sheet]
    im = Image.open(src)
    print(f'{sheet} ({im.size[0]}x{im.size[1]})')
    k = spec['kind']
    if k == 'sprites': cut_sprites(im, spec, out)
    elif k == 'tiles': cut_tiles(im, spec, out, axis=1, size=(640, 1280))
    elif k == 'walls': cut_tiles(im, spec, out, axis=0, size=(1024, 512))
    else:
        img = im.convert('RGB'); img.thumbnail((1400, 1400), Image.LANCZOS); save(img, spec['names'][0], out, quality=84)

if __name__ == '__main__':
    main()
