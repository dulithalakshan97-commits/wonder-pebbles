"""Frame renderer: draws every frame with Pillow and streams it to FFmpeg."""
import math
import os
import random
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .icons import sprite, shape_sprite, shape_points, SHAPES, INK
from .mascot import pebble

W, H = 1920, 1080
FPS = 30
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "..", "assets", "fonts", "Fredoka.ttf")
FALLBACK_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

PALETTE = [(255, 99, 99), (255, 167, 38), (255, 213, 0), (102, 204, 102), (64, 160, 255),
           (160, 110, 240), (255, 120, 190), (0, 200, 190)]
STAGE_CX, STAGE_CY = 1130, 420


# ------------------------------------------------------------------ helpers
@lru_cache(maxsize=64)
def font(size, weight="Bold"):
    try:
        f = ImageFont.truetype(FONT_PATH, size)
        try:
            f.set_variation_by_name(weight)
        except Exception:
            pass
        return f
    except OSError:
        return ImageFont.truetype(FALLBACK_FONT, size)


@lru_cache(maxsize=512)
def text_sprite(text, size, color=(255, 255, 255), stroke=(59, 47, 74), sw=None, weight="Bold"):
    f = font(size, weight)
    sw = max(2, size // 12) if sw is None else sw
    l, t, r, b = f.getbbox(text, stroke_width=sw)
    img = Image.new("RGBA", (r - l + 8, b - t + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((4 - l, 4 - t), text, font=f, fill=tuple(color) + (255,), stroke_width=sw,
           stroke_fill=tuple(stroke) + (255,) if stroke else None)
    return img


@lru_cache(maxsize=64)
def rainbow_text(text, size, offset=0):
    """Each letter in a different colour, on a shared baseline."""
    f = font(size, "Bold")
    sw = max(2, size // 12)
    asc, desc = f.getmetrics()
    w = int(f.getlength(text)) + len(text) * 2 + sw * 4 + 8
    h = asc + desc + sw * 2 + 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = sw + 4
    for i, ch in enumerate(text):
        col = PALETTE[(i + offset) % len(PALETTE)]
        d.text((x, sw + 4 + asc), ch, font=f, anchor="ls", fill=col + (255,), stroke_width=sw,
               stroke_fill=(59, 47, 74, 255))
        x += f.getlength(ch) + 2
    return img.crop(img.getbbox())


def ease_out_back(x, s=1.70158):
    x = min(max(x, 0), 1) - 1
    return x * x * ((s + 1) * x + s) + 1


def ease_out_elastic(x):
    x = min(max(x, 0), 1)
    if x in (0, 1):
        return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1


def pop(t, dur=0.45, delay=0.0):
    return ease_out_elastic((t - delay) / dur) if t > delay else 0.0


_rs_cache = {}


def resized(img, size):
    size = max(2, int(size))
    key = (id(img), size)
    r = _rs_cache.get(key)
    if r is None:
        if len(_rs_cache) > 400:
            _rs_cache.clear()
        w = size
        h = max(2, int(img.height * size / img.width))
        r = img.resize((w, h), Image.BILINEAR)
        _rs_cache[key] = (img, r)  # keep img alive so id() stays valid
        return r
    return r[1]


def paste(frame, img, cx, cy, width=None, rot=0.0, alpha=1.0):
    if img is None:
        return
    if width is not None:
        if width < 3:
            return
        img = resized(img, width)
    if rot:
        img = img.rotate(rot, resample=Image.BILINEAR, expand=True)
    if alpha < 0.999:
        a = img.getchannel("A").point(lambda v: int(v * max(0.0, alpha)))
        img = img.copy()
        img.putalpha(a)
    frame.alpha_composite(img, (int(cx - img.width / 2), int(cy - img.height / 2)))


@lru_cache(maxsize=32)
def soft_circle(r, color, alpha=90):
    s = r * 2 + 8
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([4, 4, s - 4, s - 4], fill=tuple(color) + (alpha,))
    return img


@lru_cache(maxsize=32)
def glow(r, color):
    s = r * 2 + 80
    a = Image.new("L", (s, s), 0)
    ImageDraw.Draw(a).ellipse([40, 40, s - 40, s - 40], fill=170)
    img = Image.new("RGBA", (s, s), tuple(color) + (0,))
    img.putalpha(a.filter(ImageFilter.GaussianBlur(22)))
    return img


@lru_cache(maxsize=16)
def card(w, h, color=(255, 255, 255), alpha=235):
    img = Image.new("RGBA", (w * 2, h * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 10, w * 2 - 1, h * 2 - 1], radius=60, fill=(0, 0, 0, 40))
    d.rounded_rectangle([0, 0, w * 2 - 1, h * 2 - 12], radius=60, fill=tuple(color) + (alpha,),
                        outline=INK, width=8)
    return img.resize((w, h), Image.LANCZOS)


@lru_cache(maxsize=8)
def checkmark():
    img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([10, 10, 390, 390], fill=(90, 200, 110, 255), outline=INK, width=16)
    d.line([(100, 210), (170, 280), (300, 130)], fill=(255, 255, 255, 255), width=44, joint="curve")
    return img.resize((120, 120), Image.LANCZOS)


@lru_cache(maxsize=8)
def arrow_sprite():
    img = Image.new("RGBA", (400, 200), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(20, 70), (250, 70), (250, 20), (380, 100), (250, 180), (250, 130), (20, 130)],
              fill=(255, 255, 255, 255), outline=INK, width=12)
    return img.resize((140, 70), Image.LANCZOS)


@lru_cache(maxsize=64)
def blob_sprite(color, seed=0):
    rnd = random.Random(seed)
    k = [(rnd.uniform(0.04, 0.08), rnd.randint(3, 7), rnd.uniform(0, 6.28)) for _ in range(3)]
    S = 1200
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    pts = []
    for i in range(240):
        a = i / 240 * 2 * math.pi
        r = 0.40 + sum(amp * math.sin(f * a + ph) for amp, f, ph in k)
        pts.append((S / 2 + r * S * math.cos(a), S / 2 + r * S * math.sin(a)))
    d = ImageDraw.Draw(img)
    d.polygon(pts, fill=tuple(color) + (255,), outline=INK, width=22)
    d.ellipse([S * 0.28, S * 0.24, S * 0.40, S * 0.32], fill=(255, 255, 255, 120))
    return img.resize((520, 520), Image.LANCZOS)


def item_sprite(opt):
    if "shape" in opt:
        return shape_sprite(opt["shape"], tuple(opt.get("tint") or (120, 180, 250)))
    if "letter" in opt:
        return text_sprite(opt["letter"], 260, tuple(opt.get("tint") or (255, 150, 60)))
    tint = opt.get("tint")
    return sprite(opt["icon"], tuple(tint) if tint else None)


# ------------------------------------------------------------------ background
class Background:
    def __init__(self, hue, seed):
        top = tuple(int(c * 0.85 + 255 * 0.15) for c in hue)
        bot = (255, 252, 245)
        g = np.linspace(0, 1, H)[:, None, None]
        arr = (np.array(top)[None, None, :] * (1 - g) + np.array(bot)[None, None, :] * g)
        arr = np.repeat(arr, W, axis=1).astype(np.uint8)
        img = Image.fromarray(arr, "RGB").convert("RGBA")
        big = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(big)
        # soft rolling hills
        rnd = random.Random(seed)
        for k, (col, base) in enumerate((((176, 226, 160), 900), ((150, 210, 140), 960))):
            ph = rnd.uniform(0, 6)
            pts = [(x, base + 40 * math.sin(x / (260 + 60 * k) + ph)) for x in range(0, W + 20, 20)]
            d.polygon(pts + [(W, H), (0, H)], fill=col + (255,))
        img.alpha_composite(big)
        self.img = img.convert("RGB").convert("RGBA")
        self.bubbles = [(rnd.uniform(0, W), rnd.uniform(0, 820), rnd.randint(18, 60),
                         rnd.uniform(8, 25), rnd.uniform(0, 6.28), rnd.choice(PALETTE)) for _ in range(14)]

    def draw(self, T):
        f = self.img.copy()
        for x, y, r, spd, ph, col in self.bubbles:
            yy = (y - T * spd) % 900 - 40
            xx = x + 20 * math.sin(T * 0.5 + ph)
            f.alpha_composite(soft_circle(r, col, 60), (int(xx - r), int(yy - r)))
        return f


# ------------------------------------------------------------------ layouts
def L_title(f, p, t, d, ctx):
    s = pop(t, 0.7)
    if "letter" in p:
        spr = text_sprite(p["letter"], 420, PALETTE[ord(p["letter"]) % 8])
    elif "shape" in p:
        spr = shape_sprite(p["shape"], tuple(p["color"]))
    else:
        tint = p.get("color") if p.get("icon") in ("flower", "balloon") else None
        spr = sprite(p["icon"], tuple(tint) if tint else None)
    w = 420 if spr.width >= 300 else spr.width
    paste(f, spr, STAGE_CX, 480, max(3, w * s), rot=6 * math.sin(t * 2))
    title = rainbow_text(p["title"], 120)
    if title.width > 1400:
        title = resized(title, 1400)
    paste(f, title, STAGE_CX, 150 + 10 * math.sin(t * 3), alpha=min(1, t / 0.4))
    paste(f, text_sprite("Wonder Pebbles", 54, (255, 255, 255)), STAGE_CX, 770, alpha=min(1, t * 2))


def grid_positions(n, cx=STAGE_CX, cy=STAGE_CY + 30, size=190):
    rows = 1 if n <= 5 else 2
    per = math.ceil(n / rows)
    pos = []
    for i in range(n):
        r, c = divmod(i, per)
        cnt = per if r < rows - 1 else n - per * (rows - 1)
        x = cx + (c - (cnt - 1) / 2) * (size + 30)
        y = cy + (r - (rows - 1) / 2) * (size + 40)
        pos.append((x, y))
    return pos


def L_count(f, p, t, d, ctx):
    n, shown, item = p["n"], p["shown"], p["item"]
    size = 230 if n <= 5 else 175
    pos = grid_positions(n, size=size)
    hl = p.get("highlight", 0)
    for i in range(n):
        x, y = pos[i]
        if i >= shown:
            paste(f, soft_circle(size // 2 - 10, (255, 255, 255), 70), x, y)
            continue
        sc = 1.0
        if p.get("pop") and i == shown - 1:
            sc = pop(t, 0.5)
        bob = 6 * math.sin(t * 3 + i)
        rot = 0
        if hl and i == hl - 1:
            sc *= 1.0 + 0.25 * math.sin(min(1, t / 0.35) * math.pi)
            paste(f, glow(size // 2, (255, 255, 200)), x, y)
            rot = 8 * math.sin(t * 10) * max(0, 1 - t)
        paste(f, sprite(item), x, y + bob, size * sc, rot=rot)
        if hl and i < hl:
            paste(f, text_sprite(str(i + 1), 54, PALETTE[i % 8]), x + size * 0.38, y - size * 0.38)
    if p.get("question"):
        paste(f, text_sprite("?", 260, (255, 120, 190)), STAGE_CX, 110 + 14 * math.sin(t * 4),
              None, rot=8 * math.sin(t * 2))
    big = p.get("reveal") or (hl if p.get("pop") or hl else 0)
    if big:
        s = pop(t, 0.5)
        paste(f, text_sprite(str(big), 200, PALETTE[(big - 1) % 8]), STAGE_CX, 110, 200 * s * (1 if big < 10 else 1.6))
    if p.get("cheer"):
        confetti(f, t)


def L_numerals(f, p, t, d, ctx):
    n, hl = p["n"], p.get("highlight", 0)
    pos = grid_positions(n, size=170)
    for i in range(n):
        x, y = pos[i]
        sc = 1.0
        if i == hl - 1:
            sc = 1 + 0.35 * math.sin(min(1, t / 0.4) * math.pi)
            paste(f, glow(80, PALETTE[i % 8]), x, y)
        elif hl and i >= hl:
            sc = 0.85
        paste(f, soft_circle(80, PALETTE[i % 8], 230), x, y, 170 * sc)
        num = text_sprite(str(i + 1), 120, (255, 255, 255))
        paste(f, num, x, y, num.width * sc)
    if hl:
        from .content import NUMBER_WORDS
        paste(f, text_sprite(NUMBER_WORDS[hl], 110, PALETTE[(hl - 1) % 8]), STAGE_CX, 110, None, alpha=min(1, t * 4))


def L_color_splash(f, p, t, d, ctx):
    col = tuple(p["color"])
    s = pop(t, 0.6) if ctx["new_layout"] else 1.0
    paste(f, blob_sprite(col, 3), STAGE_CX, 400, 560 * s, rot=3 * math.sin(t * 1.5))
    paste(f, text_sprite(p["word"].upper(), 150, (255, 255, 255)), STAGE_CX, 400 + 6 * math.sin(t * 3))
    if p.get("prompt"):
        paste(f, text_sprite("?", 160, col), STAGE_CX + 330, 180 + 12 * math.sin(t * 4), rot=10 * math.sin(t * 2))


def L_object(f, p, t, d, ctx):
    tint = p.get("tint")
    s = pop(t, 0.55)
    paste(f, glow(200, tuple(p["color"])), STAGE_CX, 360)
    paste(f, sprite(p["icon"], tuple(tint) if tint else None), STAGE_CX, 360 + 8 * math.sin(t * 3), 400 * s,
          rot=5 * math.sin(t * 2))
    color_word, rest = p["word"].split(" ", 1)
    a = text_sprite(color_word, 110, tuple(p["color"]))
    b = text_sprite(rest, 110, (255, 255, 255))
    tw = a.width + b.width + 20
    paste(f, a, STAGE_CX - tw / 2 + a.width / 2, 700, alpha=min(1, t * 3))
    paste(f, b, STAGE_CX + tw / 2 - b.width / 2, 700, alpha=min(1, t * 3))


def L_choose(f, p, t, d, ctx):
    opts = p["options"]
    n = len(opts)
    xs = [STAGE_CX + (i - (n - 1) / 2) * 420 for i in range(n)]
    reveal = p.get("reveal")
    for i, (o, x) in enumerate(zip(opts, xs)):
        s = pop(t, 0.5, delay=0.12 * i) if ctx["new_layout"] else 1.0
        correct = i == p["answer"]
        y = 410
        alpha = 1.0
        sc = 1.0
        if reveal:
            if correct:
                sc = 1.0 + 0.18 * min(1, t / 0.4)
                paste(f, glow(190, (255, 240, 150)), x, y)
            else:
                alpha = max(0.35, 1 - t * 2)
                sc = 0.9
        paste(f, card(360, 400), x, y, 360 * s * sc, alpha=alpha)
        paste(f, item_sprite(o), x, y - 10 + 6 * math.sin(t * 3 + i), 260 * s * sc, alpha=alpha)
        if reveal and correct:
            paste(f, checkmark(), x + 140, y - 160, 120 * pop(t, 0.5))
    if not reveal:
        paste(f, text_sprite("?", 150, (255, 120, 190)), STAGE_CX, 110 + 10 * math.sin(t * 4))
        # gentle countdown dots while waiting
        if d > 2.5:
            left = max(0, d - t)
            for k in range(3):
                on = left > (k + 0.5) * (d / 4)
                paste(f, soft_circle(16, (255, 255, 255) if on else (200, 200, 200), 230 if on else 120),
                      STAGE_CX - 50 + k * 50, 690)
    else:
        confetti(f, t)


def L_shape(f, p, t, d, ctx):
    name, col = p["shape"], tuple(p["color"])
    side = p.get("side", -1)
    s = pop(t, 0.6) if ctx["new_layout"] else 1.0
    spr = shape_sprite(name, col, side)
    size = 470 * s
    paste(f, spr, STAGE_CX, 400 + 8 * math.sin(t * 2), size, rot=0 if side >= 0 else 3 * math.sin(t * 1.5))
    paste(f, text_sprite(name.upper(), 110, col), STAGE_CX, 720)
    if p.get("side_count"):
        paste(f, text_sprite(str(p["side_count"]), 140, (255, 255, 255)), STAGE_CX + 330, 170, 140 * pop(t, 0.4))
    if p.get("trace"):
        pts = shape_points(name)
        if pts is None:  # round shapes: trace an ellipse
            rx, ry = (42, 42) if name == "circle" else (44, 30)
            pts = [(50 + rx * math.cos(a / 40 * 2 * math.pi), 50 + ry * math.sin(a / 40 * 2 * math.pi)) for a in range(40)]
        q = (t / max(0.5, d - 0.3)) % 1
        seg = q * len(pts)
        i = int(seg) % len(pts)
        a, b = pts[i], pts[(i + 1) % len(pts)]
        fr = seg - int(seg)
        ux, uy = a[0] + (b[0] - a[0]) * fr, a[1] + (b[1] - a[1]) * fr
        k = 470 / 100
        x = STAGE_CX - 235 + ux * k
        y = 400 - 235 + uy * k
        paste(f, glow(30, (255, 255, 255)), x, y)
        paste(f, sprite("star"), x, y, 90, rot=t * 200)


def L_shape_vs(f, p, t, d, ctx):
    s1 = pop(t, 0.5)
    s2 = pop(t, 0.5, delay=0.35)
    paste(f, shape_sprite(p["shape"], tuple(p["color"])), STAGE_CX - 330, 420, 360 * s1)
    paste(f, text_sprite("=", 140, (255, 255, 255)), STAGE_CX, 420, None, alpha=min(1, t * 3))
    paste(f, sprite(p["icon"]), STAGE_CX + 330, 420 + 8 * math.sin(t * 3), 360 * s2, rot=4 * math.sin(t * 2))


def L_letter(f, p, t, d, ctx):
    L = p["letter"]
    col = PALETTE[ord(L) % 8]
    col2 = PALETTE[(ord(L) + 3) % 8]
    case = p.get("case", "both")
    s = pop(t, 0.5)
    if case == "both":
        paste(f, text_sprite(L, 420, col), STAGE_CX - 190, 420 + 8 * math.sin(t * 3), 300 * s)
        paste(f, text_sprite(L.lower(), 420, col2), STAGE_CX + 190, 440 + 8 * math.sin(t * 3 + 1), 260 * s)
    elif case == "upper":
        paste(f, text_sprite(L, 520, col), STAGE_CX, 420, 380 * s, rot=3 * math.sin(t * 2))
    else:
        paste(f, text_sprite(L.lower(), 520, col2), STAGE_CX, 440, 330 * s, rot=3 * math.sin(t * 2))
    if p.get("trace"):
        a = t * 2.2
        x = STAGE_CX + 260 * math.cos(a)
        y = 420 + 230 * math.sin(a)
        paste(f, glow(30, (255, 255, 255)), x, y)
        paste(f, sprite("star"), x, y, 90, rot=t * 200)


def L_word(f, p, t, d, ctx):
    L, word = p["letter"], p["word"]
    col = PALETTE[ord(L) % 8]
    s = pop(t, 0.55)
    paste(f, glow(180, col), STAGE_CX - 300, 400)
    paste(f, sprite(p["icon"]), STAGE_CX - 300, 400 + 8 * math.sin(t * 3), 380 * s, rot=4 * math.sin(t * 2))
    first = text_sprite(word[0].upper(), 150, col)
    rest = text_sprite(word[1:], 150, (255, 255, 255))
    tw = first.width + rest.width - 8
    x0 = STAGE_CX + 260 - tw / 2
    paste(f, first, x0 + first.width / 2, 400 + 10 * math.sin(t * 5), alpha=min(1, t * 3))
    paste(f, rest, x0 + first.width - 8 + rest.width / 2, 400, alpha=min(1, t * 3))
    paste(f, text_sprite(L, 90, col), STAGE_CX + 260, 160, 90 * pop(t, 0.5, 0.2))


def L_fact(f, p, t, d, ctx):
    icons = p["icons"]
    n = len(icons)
    size = 340 if n <= 2 else (270 if n == 3 else 220)
    gap = 120 if p.get("mode") == "seq" else 60
    xs = [STAGE_CX + (i - (n - 1) / 2) * (size + gap) for i in range(n)]
    for i, (ic, x) in enumerate(zip(icons, xs)):
        s = pop(t, 0.55, delay=0.35 * i)
        paste(f, soft_circle(size // 2 + 10, (255, 255, 255), 120), x, 400, (size + 30) * min(1, s))
        paste(f, sprite(ic), x, 400 + 8 * math.sin(t * 2.5 + i), size * s, rot=4 * math.sin(t * 1.8 + i))
        if p.get("mode") == "seq" and i < n - 1:
            a = min(1, max(0, (t - 0.35 * i - 0.25) * 3))
            paste(f, arrow_sprite(), x + (size + gap) / 2, 400, 110 * a)


def L_outro(f, p, t, d, ctx):
    paste(f, rainbow_text("Bye bye!", 170), STAGE_CX, 200 + 10 * math.sin(t * 3), alpha=min(1, t * 2))
    if "letter" in p:
        spr = text_sprite(p["letter"], 300, PALETTE[ord(p["letter"]) % 8])
    elif "shape" in p:
        spr = shape_sprite(p["shape"], tuple(p["color"]))
    else:
        tint = p.get("tint")
        spr = sprite(p.get("icon", "star"), tuple(tint) if tint else None)
    paste(f, spr, STAGE_CX, 520, 300 * pop(t, 0.6), rot=10 * math.sin(t * 3))
    paste(f, text_sprite("See you next time!", 70, (255, 255, 255)), STAGE_CX, 780, alpha=min(1, max(0, t - 0.5) * 2))
    confetti(f, t, n=30)


LAYOUTS = {"title": L_title, "count": L_count, "numerals": L_numerals, "color_splash": L_color_splash,
           "object": L_object, "choose": L_choose, "shape": L_shape, "shape_vs": L_shape_vs,
           "letter": L_letter, "word": L_word, "fact": L_fact, "outro": L_outro}


def confetti(f, t, n=40):
    rnd = random.Random(7)
    for i in range(n):
        x0 = rnd.uniform(420, 1880)
        vy = rnd.uniform(250, 420)
        y = -40 + vy * t - 30 * rnd.random()
        if y > H:
            continue
        x = x0 + 40 * math.sin(t * 3 + i)
        col = PALETTE[i % 8]
        paste(f, soft_circle(10, col, 240), x, y)


# ------------------------------------------------------------------ captions
@lru_cache(maxsize=256)
def caption_sprite(text):
    f = font(54, "SemiBold")
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if f.getlength(test) > 1180 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    lines = lines[:3]
    lh = 66
    w = int(max(f.getlength(l) for l in lines)) + 80
    h = lh * len(lines) + 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=36, fill=(255, 255, 255, 225), outline=INK, width=4)
    for i, l in enumerate(lines):
        d.text((w / 2, 20 + i * lh + lh / 2), l, font=f, fill=INK, anchor="mm")
    return img


# ------------------------------------------------------------------ main loop
def render(ep, timeline, mouth_env, out_path, ffmpeg_proc):
    """timeline: list of (start, dur, seg). mouth_env: per-frame 0..1 speech loudness."""
    bg = Background(ep["hue"], ep["seed"])
    total = timeline[-1][0] + timeline[-1][1]
    nframes = int(total * FPS)
    si = 0
    prev_layout = None
    new_layout = True
    for fi in range(nframes):
        T = fi / FPS
        while si < len(timeline) - 1 and T >= timeline[si + 1][0]:
            si += 1
            seg_layout = timeline[si][2]["layout"]
            new_layout = seg_layout != prev_layout
            prev_layout = seg_layout
        if prev_layout is None:
            prev_layout = timeline[0][2]["layout"]
        start, dur, seg = timeline[si]
        t = T - start
        frame = bg.draw(T)
        ctx = {"new_layout": new_layout or si == 0}
        LAYOUTS[seg["layout"]](frame, seg["params"], t, dur, ctx)
        # mascot
        m = mouth_env[min(fi, len(mouth_env) - 1)]
        mouth = 0 if m < 0.08 else min(4, 1 + int(m * 4))
        blink = (T % 3.7) < 0.12
        wave = seg["layout"] in ("title", "outro")
        bounce = abs(math.sin(T * 2.2)) * 14 + (8 * m)
        paste(frame, pebble(mouth, blink, wave), 230, 760 - bounce, None,
              rot=4 * math.sin(T * 1.3) + (6 * math.sin(T * 8) if wave else 0))
        # caption
        if seg["text"]:
            cap = caption_sprite(seg["text"])
            paste(frame, cap, 1150, 1000 - cap.height / 2 + 30)
        ffmpeg_proc.stdin.write(frame.convert("RGB").tobytes())
    return nframes
