"""Remove the magenta (#FF00FF-ish) background from generated sprites.

Usage: python3 key.py <in.jpg> <out.webp> [max_side]
Keys out magenta and its darker shadow tones, softens the edge, removes
magenta spill from edge pixels, trims to content and saves as WebP with alpha.
"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
max_side = int(sys.argv[3]) if len(sys.argv) > 3 else 512

im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float32)
r, g, b = a[..., 0], a[..., 1], a[..., 2]

# "magentaness": how far red and blue both sit above green, and how balanced they are
mn = np.minimum(r, b)
m = mn - g - 0.6 * np.abs(r - b)

# full key above 70, soft ramp from 25 to 70
alpha = np.clip((70 - m) / 45, 0, 1)

# drop tiny islands / soften edge
al = Image.fromarray((alpha * 255).astype(np.uint8))
al = al.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
alpha = np.asarray(al).astype(np.float32) / 255

# despill: pull red/blue down toward green where they both exceed it
spill = np.clip(mn - g, 0, None) * np.clip(1.2 - alpha, 0, 1)
r2 = np.clip(r - spill * 0.85, 0, 255)
b2 = np.clip(b - spill * 0.85, 0, 255)
out = np.dstack([r2, g, b2, alpha * 255]).astype(np.uint8)
img = Image.fromarray(out, 'RGBA')

bbox = Image.fromarray((alpha > 0.08).astype(np.uint8) * 255).getbbox()
img = img.crop(bbox)
img.thumbnail((max_side, max_side), Image.LANCZOS)
img.save(dst, 'WEBP', quality=88, method=6)
print(dst, img.size, 'bbox', bbox)
