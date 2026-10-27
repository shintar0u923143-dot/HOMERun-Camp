"""Temporary placeholder art to test the scrolling engine (never shipped).
Writes PNGs into the folder given as argv[1]."""
import sys, random, pathlib
from PIL import Image, ImageDraw, ImageFilter

out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
R = random.Random(4)

def ground_tile(name, side, path, n, kind):
    W, H = 512, 1024
    im = Image.new('RGB', (W, H), side); d = ImageDraw.Draw(im)
    x0, x1 = W // 4, W * 3 // 4
    d.rectangle([x0, 0, x1, H], fill=path)
    if kind == 'camp':
        for lane in range(3):
            cx = x0 + (x1 - x0) * (lane + 0.5) / 3
            for off in (-22, 22):
                d.rectangle([cx + off - 5, 0, cx + off + 5, H], fill=(178, 135, 90))
        for _ in range(160):
            x, y = R.randint(x0, x1), R.randint(0, H); r = R.randint(2, 6)
            d.ellipse([x - r, y - r, x + r, y + r], fill=(226, 200, 158) if R.random() < .5 else (160, 125, 85))
        for _ in range(220):
            x = R.choice([R.randint(0, x0 - 6), R.randint(x1 + 6, W)]); y = R.randint(0, H)
            d.line([x, y, x + R.randint(-4, 4), y - R.randint(6, 14)], fill=(70, 140, 50), width=3)
        d.rectangle([x0 - 8, 0, x0, H], fill=(120, 170, 70)); d.rectangle([x1, 0, x1 + 8, H], fill=(120, 170, 70))
    elif kind == 'house':
        for x in range(x0 - 128, x1 + 128, 32):
            d.line([x, 0, x, H], fill=(40, 90, 30), width=3)
        for x in range(x0 - 128, x1 + 128, 32):
            for y in range((x * 7) % 200, H, 200):
                d.line([x, y, x + 32, y], fill=(40, 90, 30), width=3)
        cx0, cx1 = x0 + (x1 - x0) // 3, x0 + 2 * (x1 - x0) // 3
        d.rectangle([cx0, 0, cx1, H], fill=(214, 70, 60)); d.rectangle([cx0 + 10, 0, cx1 - 10, H], fill=(190, 55, 48))
        d.rectangle([0, 0, 18, H], fill=(235, 222, 195)); d.rectangle([W - 18, 0, W, H], fill=(235, 222, 195))
    else:
        for row in range(0, H, 128):
            for lane in range(3):
                cx = x0 + (x1 - x0) * (lane + 0.5) / 3 + R.randint(-12, 12)
                d.ellipse([cx - 34, row + 20, cx + 34, row + 108], fill=(236, 228, 204), outline=(60, 120, 50), width=4)
    d.text((10, 10), name, fill=(255, 255, 255))
    # big tile number on the side so scrolling is easy to see
    for y in range(80, H, 260):
        d.rectangle([24, y, 92, y + 60], fill=(255, 255, 255)); d.text((50, y + 22), str(n), fill=(0, 0, 0))
    im.save(out / f'{name}.png')

for i in range(1, 5):
    ground_tile(f'tile-camp-0{i}', (108, 184, 72), (201, 158, 105), i, 'camp')
    ground_tile(f'tile-house-0{i}', (79, 142, 54), (79, 142, 54), i, 'house')
    ground_tile(f'tile-backyard-0{i}', (86, 168, 66), (78, 156, 59), i, 'yard')

def horizon(name, mountains):
    W, H = 1024, 512
    im = Image.new('RGB', (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H; d.line([0, y, W, y], fill=(int(140 + 90 * t), int(210 + 35 * t), int(242 + 8 * t)))
    if mountains:
        d.polygon([(0, 400), (180, 230), (360, 400), (520, 260), (720, 400), (880, 250), (1024, 380), (1024, 512), (0, 512)], fill=(130, 175, 170))
    for x in range(0, W, 26):
        h = R.randint(30, 60); d.polygon([(x, 440), (x + 13, 440 - h), (x + 26, 440)], fill=(80, 140, 100))
    d.rectangle([0, 440, W, H], fill=(110, 160, 110))
    im.save(out / f'{name}.png')
horizon('horizon-camp', True); horizon('horizon-backyard', False)

def wall(name, kind, n):
    W, H = 1024, 512
    if kind == 'house':
        im = Image.new('RGBA', (W, H), (243, 233, 210, 255)); d = ImageDraw.Draw(im)
        d.rectangle([0, H - 40, W, H], fill=(160, 112, 70)); d.rectangle([0, 0, W, 24], fill=(255, 255, 255))
        d.rectangle([300, 120, 520, 330], fill=(170, 225, 255), outline=(255, 255, 255), width=12)
        d.rectangle([680, 180, 900, 220], fill=(230, 220, 200)); d.rectangle([700, 120, 720, 180], fill=(80, 160, 60))
    else:
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for x in range(0, W, 64):
            d.polygon([(x + 6, H), (x + 6, 120), (x + 32, 80), (x + 58, 120), (x + 58, H)], fill=(245, 238, 220))
            d.rectangle([x + 28, 80, x + 36, H], fill=(46, 125, 50))
        d.rectangle([0, 220, W, 250], fill=(46, 125, 50)); d.rectangle([0, 400, W, 430], fill=(46, 125, 50))
    d.text((20, 40), name, fill=(0, 0, 0, 255)); d.text((W // 2, H // 2), str(n), fill=(0, 0, 0, 255))
    im.save(out / f'{name}.png')
for s in ('left', 'right'):
    for i in (1, 2):
        wall(f'wall-house-{s}-0{i}', 'house', i)
        wall(f'wall-yard-{s}-0{i}', 'yard', i)

def tree(name, kind):
    im = Image.new('RGBA', (300, 500), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == 'pine':
        d.rectangle([135, 400, 165, 500], fill=(110, 70, 40))
        for i, (w, y) in enumerate([(140, 420), (115, 320), (90, 220), (60, 130)]):
            d.polygon([(150 - w, y), (150, y - 160), (150 + w, y)], fill=(46 + i * 18, 125 + i * 15, 50))
    elif kind == 'bush':
        im = Image.new('RGBA', (300, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse([10, 20, 290, 200], fill=(60, 140, 55)); d.ellipse([60, 0, 220, 120], fill=(90, 170, 70))
    else:
        d.rectangle([135, 300, 165, 500], fill=(110, 70, 40)); d.ellipse([20, 20, 280, 340], fill=(150, 190, 60))
    im = im.filter(ImageFilter.GaussianBlur(0.6)); im.save(out / f'{name}.png')
for s in ('left', 'right'):
    tree(f'prop-{s}-pine-tall', 'pine'); tree(f'prop-{s}-pine-round', 'pine')
    tree(f'prop-{s}-bush', 'bush'); tree(f'prop-{s}-leafy-tree', 'leafy')
    tree(f'prop-{s}-round-tree', 'leafy'); tree(f'prop-{s}-hedge-ball', 'bush')
print('placeholders in', out)
