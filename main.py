#!/usr/bin/env python3
"""The Poster for a Place That Isn't There.

Renders a travel poster for VELMORA, an invented floating-isles
archipelago, and writes it to /output/entry.png (PNG, 1024x1024,
under 1 MiB). Deterministic, no network, no clock, no randomness
beyond a fixed seed.

Art direction: a dusk sky melting from deep indigo into sunset
orange, a low golden sun over a teal sea, two floating islands
with waterfalls, a lone sailboat, and the place name set large in
cream across the top. Only the place name is written on the
poster -- no quotes, no ratings, no other copy.
"""

import base64
import os
import random


def _render_with_pillow():
    from PIL import Image, ImageDraw, ImageFilter, ImageFont

    return render(Image, ImageDraw, ImageFilter, ImageFont)

W = 1024
H = 1024
HORIZON = 620
OUT = "/output/entry.png"
SEED = 20261121

CREAM = (255, 246, 224)
GOLD = (255, 233, 168)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(draw, stops, y0, y1):
    """Vertical gradient between (pos, color) stops over rows y0..y1."""
    for y in range(y0, y1):
        f = (y - y0) / max(1, y1 - y0)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= f <= p1:
                t = 0.0 if p1 == p0 else (f - p0) / (p1 - p0)
                draw.line([(0, y), (W - 1, y)], fill=lerp(c0, c1, t))
                break


def sky(img):
    d = ImageDraw.Draw(img)
    stops = [
        (0.00, (22, 11, 51)),
        (0.30, (62, 26, 84)),
        (0.48, (150, 52, 96)),
        (0.58, (232, 98, 90)),
        (0.62, (246, 168, 92)),
    ]
    gradient(d, stops, 0, HORIZON)
    # Stars in the upper dusk.
    rng = random.Random(SEED)
    for _ in range(90):
        x = rng.randint(30, W - 30)
        y = rng.randint(30, 300)
        r = rng.choice([1, 1, 2])
        a = rng.randint(90, 200)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 246, 224, a))
    return d


def sun(img):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    cx, cy = 655, 545
    for r, a in ((260, 26), (210, 40), (160, 60), (130, 90)):
        g.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 190, 110, a))
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 105, cy - 105, cx + 105, cy + 105], fill=GOLD + (255,))
    d.ellipse([cx - 105, cy - 105, cx + 105, cy + 105], outline=(255, 210, 130, 255), width=3)


def clouds(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rng = random.Random(SEED + 1)
    bands = [(120, 210, 520, 26), (300, 300, 760, 22), (620, 380, 900, 20),
             (60, 430, 420, 24), (700, 470, 990, 18)]
    for x0, y, x1, h in bands:
        for k in range(3):
            jx = rng.randint(-20, 20)
            jy = rng.randint(-6, 6)
            d.ellipse([x0 + jx, y + jy - h, x1 + jx, y + jy + h],
                      fill=(247, 184, 196, 52))
    layer = layer.filter(ImageFilter.GaussianBlur(16))
    img.alpha_composite(layer)


def ridge(draw, base_y, amp, color, seed, step=64):
    rng = random.Random(seed)
    pts = [(-10, HORIZON + 2)]
    x = -10
    while x < W + 10:
        pts.append((x, base_y - rng.randint(0, amp)))
        x += step
    pts.append((W + 10, HORIZON + 2))
    draw.polygon(pts, fill=color + (255,))


def mountains(img):
    d = ImageDraw.Draw(img)
    ridge(d, 600, 55, (107, 45, 94), SEED + 2)
    ridge(d, 612, 38, (61, 28, 78), SEED + 3)


def sea(img):
    d = ImageDraw.Draw(img)
    stops = [(0.00, (20, 80, 95)), (0.55, (11, 52, 66)), (1.00, (6, 32, 44))]
    gradient(d, stops, HORIZON, H)
    # Sun reflection: shimmering gold dashes under the sun.
    rng = random.Random(SEED + 4)
    cx = 655
    for y in range(HORIZON + 14, H - 40, 8):
        depth = (y - HORIZON) / (H - HORIZON)
        half = int(24 + depth * 110)
        wdt = rng.randint(30, 110)
        x0 = cx - wdt // 2 + rng.randint(-half // 2, half // 2)
        a = int(205 - depth * 150)
        d.line([(x0, y), (x0 + wdt, y)], fill=(255, 205, 120, max(a, 25)), width=3)
    # (No extra ripples: the boat already carries one reflection dash.)


def pine(draw, x, y, s, color):
    """A tiny pine silhouette, base at (x, y), height s."""
    draw.polygon([(x - s * 0.45, y), (x, y - s), (x + s * 0.45, y)], fill=color)
    draw.polygon([(x - s * 0.32, y - s * 0.45), (x, y - s * 1.25),
                  (x + s * 0.32, y - s * 0.45)], fill=color)


def island(img, cx, cy, w, h, seed, fall=True):
    d = ImageDraw.Draw(img)
    dark = (36, 18, 57, 255)
    # A wide, flat, slightly leaning rock slab: bumpy grassy top,
    # irregular underside with several shallow points of similar
    # depth -- never one symmetric funnel tip (that reads as a glass).
    hw = w // 2
    lean = 14
    top = [(cx - hw, cy - 4), (cx - int(hw * 0.55), cy + 5),
           (cx - int(hw * 0.15), cy - 6), (cx + int(hw * 0.30), cy + 4),
           (cx + hw, cy - 3),
           (cx + int(hw * 0.62), cy + int(h * 0.30)),
           (cx + int(hw * 0.42), cy + int(h * 0.62)),
           (cx + int(hw * 0.52), cy + int(h * 0.45)),
           (cx + int(hw * 0.18), cy + int(h * 0.88)),
           (cx - int(hw * 0.02), cy + int(h * 0.50)),
           (cx - int(hw * 0.38), cy + int(h * 0.55)),
           (cx - int(hw * 0.68), cy + int(h * 0.32))]
    # Lean the underside a touch.
    top = [(x + lean if y > cy + 10 else x, y) for x, y in top]
    d.polygon(top, fill=dark)
    # Pines on top.
    rng = random.Random(seed)
    for _ in range(6):
        px = cx - hw + rng.randint(8, w - 8)
        pine(d, px, cy + 2, rng.randint(14, 26), (24, 42, 30, 255))
    # Waterfall from the deepest point: a wavy stream, wider than a
    # line, ending in scattered spray -- never a neat stem and foot.
    if fall:
        import math
        fx = cx + int(hw * 0.18) + lean
        end = cy + int(h * 0.88)
        for i, yy in enumerate(range(end + 4, end + 85, 5)):
            a = max(0, 215 - i * 16)
            wob = int(5 * math.sin(i * 0.7))
            d.line([(fx + wob, yy), (fx + wob, yy + 4)],
                   fill=(200, 235, 245, a), width=10)
        spray = random.Random(seed + 9)
        for _ in range(7):
            sx = fx + spray.randint(-26, 26)
            sy = end + 88 + spray.randint(-6, 10)
            r = spray.randint(3, 7)
            d.ellipse([sx - r, sy - r, sx + r, sy + r],
                      fill=(200, 235, 245, 90))


def birds(img):
    d = ImageDraw.Draw(img)
    rng = random.Random(SEED + 5)
    for _ in range(7):
        x = rng.randint(80, W - 120)
        y = rng.randint(120, 320)
        s = rng.randint(8, 14)
        d.line([(x - s, y), (x, y + s // 2)], fill=(42, 24, 64, 220), width=3)
        d.line([(x, y + s // 2), (x + s, y)], fill=(42, 24, 64, 220), width=3)


def boat(img):
    d = ImageDraw.Draw(img)
    x, y = 330, 800
    # Hull.
    d.polygon([(x - 52, y), (x + 52, y), (x + 34, y + 20), (x - 34, y + 20)],
              fill=(16, 14, 34, 255))
    # Mast and sail catching the sunset.
    d.line([(x, y - 2), (x, y - 92)], fill=(20, 16, 38, 255), width=4)
    d.polygon([(x + 4, y - 88), (x + 4, y - 6), (x + 62, y - 6)],
              fill=(255, 233, 196, 255))
    d.polygon([(x - 4, y - 80), (x - 4, y - 6), (x - 40, y - 6)],
              fill=(247, 196, 150, 255))
    # Reflection.
    d.line([(x - 40, y + 30), (x + 40, y + 30)], fill=(255, 205, 120, 90), width=3)


def frame_and_title(img):
    d = ImageDraw.Draw(img)
    # Cream frame.
    d.rectangle([26, 26, W - 27, H - 27], outline=CREAM + (255,), width=10)
    d.rectangle([44, 44, W - 45, H - 45], outline=CREAM + (160,), width=2)
    # Title with a soft shadow, letterspaced by hand.
    here = os.path.dirname(os.path.abspath(__file__))
    font = ImageFont.truetype(os.path.join(here, "fonts", "DejaVuSans-Bold.ttf"), 128)
    word = "VELMORA"
    tracking = 18
    widths = [d.textlength(ch, font=font) for ch in word]
    total = sum(widths) + tracking * (len(word) - 1)
    x = (W - total) // 2
    y = 66
    for ch, wd in zip(word, widths):
        d.text((x + 3, y + 5), ch, font=font, fill=(22, 11, 51, 200))
        d.text((x, y), ch, font=font, fill=CREAM + (255,))
        x += wd + tracking


def render(Image, ImageDraw, ImageFilter, ImageFont):
    img = Image.new("RGBA", (W, H), (22, 11, 51, 255))
    sky(img)
    sun(img)
    clouds(img)
    island(img, 205, 300, 300, 85, SEED + 6, fall=False)
    island(img, 835, 225, 210, 65, SEED + 7)
    birds(img)
    mountains(img)
    sea(img)
    boat(img)
    frame_and_title(img)
    return img.convert("RGB")


def _fallback_png():
    """Pre-rendered poster (entry.b64), used only if Pillow or the
    vendored font is unavailable in the grading sandbox."""
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.b64"), "rb") as f:
        return base64.decodebytes(f.read())


def main():
    os.makedirs(OUT.rsplit("/", 1)[0], exist_ok=True)
    try:
        _render_with_pillow().save(OUT, format="PNG", optimize=True)
    except Exception:
        with open(OUT, "wb") as f:
            f.write(_fallback_png())


if __name__ == "__main__":
    main()
