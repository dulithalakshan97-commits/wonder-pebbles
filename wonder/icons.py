"""Original cartoon icon library, drawn with Pillow.

Every icon is drawn in a 100x100 unit space on a large canvas and
downsampled, which gives smooth anti-aliased edges.
"""
import math
from functools import lru_cache
from PIL import Image, ImageDraw

INK = (59, 47, 74, 255)
SS = 1024  # supersampled canvas
OUT = 384  # sprite size


class Pen:
    def __init__(self, img):
        self.d = ImageDraw.Draw(img)
        self.k = SS / 100.0

    def _p(self, pts):
        return [(x * self.k, y * self.k) for x, y in pts]

    def ellipse(self, cx, cy, rx, ry, fill, ow=2.4, outline=INK):
        k = self.k
        self.d.ellipse([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k],
                       fill=fill, outline=outline if ow else None, width=int(ow * k) if ow else 0)

    def circle(self, cx, cy, r, fill, ow=2.4, outline=INK):
        self.ellipse(cx, cy, r, r, fill, ow, outline)

    def poly(self, pts, fill, ow=2.4, outline=INK):
        self.d.polygon(self._p(pts), fill=fill, outline=outline if ow else None,
                       width=int(ow * self.k) if ow else 0)

    def rect(self, x0, y0, x1, y1, fill, ow=2.4, r=0, outline=INK):
        k = self.k
        self.d.rounded_rectangle([x0 * k, y0 * k, x1 * k, y1 * k], radius=r * k, fill=fill,
                                 outline=outline if ow else None, width=int(ow * k) if ow else 0)

    def line(self, pts, color=INK, w=2.4):
        k = self.k
        self.d.line(self._p(pts), fill=color, width=int(w * k), joint="curve")
        for x, y in (pts[0], pts[-1]):
            r = w / 2
            self.d.ellipse([(x - r) * k, (y - r) * k, (x + r) * k, (y + r) * k], fill=color)

    def arc(self, cx, cy, r, a0, a1, color=INK, w=2.4):
        k = self.k
        self.d.arc([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], a0, a1,
                   fill=color, width=int(w * k))

    def pieslice(self, cx, cy, r, a0, a1, fill, ow=2.4):
        k = self.k
        self.d.pieslice([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], a0, a1,
                        fill=fill, outline=INK if ow else None, width=int(ow * k) if ow else 0)

    def face(self, cx, cy, s=1.0, smile=True):
        """Small cute face: two eyes + smile."""
        self.circle(cx - 6 * s, cy, 2.6 * s, INK, 0)
        self.circle(cx + 6 * s, cy, 2.6 * s, INK, 0)
        self.circle(cx - 5.2 * s, cy - 0.9 * s, 0.9 * s, (255, 255, 255, 255), 0)
        self.circle(cx + 6.8 * s, cy - 0.9 * s, 0.9 * s, (255, 255, 255, 255), 0)
        if smile:
            self.arc(cx, cy + 2 * s, 4.5 * s, 20, 160, INK, 1.6 * s)
        self.circle(cx - 10 * s, cy + 4 * s, 2.2 * s, (255, 150, 170, 150), 0)
        self.circle(cx + 10 * s, cy + 4 * s, 2.2 * s, (255, 150, 170, 150), 0)


def star_pts(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def reg_pts(cx, cy, r, n, rot=-90):
    return [(cx + r * math.cos(math.radians(rot + i * 360 / n)),
             cy + r * math.sin(math.radians(rot + i * 360 / n))) for i in range(n)]


def heart_pts(cx, cy, s):
    pts = []
    for i in range(80):
        t = i / 80 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((cx + x * s, cy + y * s))
    return pts


# ---------------------------------------------------------------- icons
def apple(p, c=(232, 62, 62, 255)):
    p.line([(50, 28), (53, 14)], (120, 80, 40, 255), 3.5)
    p.ellipse(62, 18, 9, 5, (90, 190, 90, 255), 2)
    p.ellipse(38, 56, 24, 28, c)
    p.ellipse(62, 56, 24, 28, c)
    p.ellipse(50, 58, 30, 28, c, 0)
    p.ellipse(38, 46, 6, 9, (255, 255, 255, 110), 0)


def ball(p):
    p.circle(50, 52, 38, (70, 150, 240, 255))
    p.pieslice(50, 52, 38, 200, 340, (255, 210, 60, 255), 0)
    p.pieslice(50, 52, 38, 20, 160, (240, 80, 90, 255), 0)
    p.circle(50, 52, 38, None)
    p.circle(38, 38, 7, (255, 255, 255, 120), 0)


def balloon(p, c=(240, 90, 140, 255)):
    p.line([(50, 70), (46, 82), (54, 90), (50, 98)], INK, 1.5)
    p.poly([(45, 74), (55, 74), (50, 66)], c, 1.5)
    p.ellipse(50, 40, 26, 32, c)
    p.ellipse(41, 28, 5, 9, (255, 255, 255, 120), 0)


def banana(p):
    outer = [(50 + 44 * math.cos(math.radians(a)), 22 + 44 * math.sin(math.radians(a))) for a in range(15, 166, 5)]
    inner = [(50 + 40 * math.cos(math.radians(a)), 8 + 40 * math.sin(math.radians(a))) for a in range(160, 19, -5)]
    p.poly(outer + inner, (255, 220, 70, 255))
    p.line([(92, 32), (96, 26)], (120, 90, 40, 255), 3)


def butterfly(p):
    for sx in (-1, 1):
        p.ellipse(50 + sx * 20, 36, 18, 20, (250, 130, 200, 255))
        p.ellipse(50 + sx * 16, 66, 13, 14, (140, 120, 240, 255))
        p.circle(50 + sx * 22, 34, 6, (255, 230, 120, 255), 0)
    p.ellipse(50, 52, 5, 26, (90, 70, 110, 255))
    p.line([(48, 28), (40, 14)], INK, 1.8)
    p.line([(52, 28), (60, 14)], INK, 1.8)


def car(p):
    p.rect(14, 46, 86, 72, (240, 80, 70, 255), r=8)
    p.poly([(28, 46), (36, 28), (66, 28), (74, 46)], (240, 80, 70, 255))
    p.poly([(34, 45), (39, 32), (49, 32), (49, 45)], (180, 230, 255, 255), 1.6)
    p.poly([(53, 45), (53, 32), (64, 32), (69, 45)], (180, 230, 255, 255), 1.6)
    p.circle(32, 74, 10, (70, 70, 80, 255))
    p.circle(68, 74, 10, (70, 70, 80, 255))
    p.circle(32, 74, 4, (200, 200, 210, 255), 0)
    p.circle(68, 74, 4, (200, 200, 210, 255), 0)


def cat(p):
    c = (255, 170, 80, 255)
    p.poly([(22, 40), (26, 12), (44, 30)], c)
    p.poly([(78, 40), (74, 12), (56, 30)], c)
    p.ellipse(50, 52, 34, 30, c)
    p.face(50, 50, 1.2)
    p.line([(18, 56), (32, 58)], INK, 1.2)
    p.line([(82, 56), (68, 58)], INK, 1.2)
    p.poly([(47, 55), (53, 55), (50, 58)], (240, 110, 130, 255), 0)


def cloud(p, c=(255, 255, 255, 255)):
    for cx, cy, r in ((30, 58, 16), (50, 46, 22), (70, 58, 16)):
        p.circle(cx, cy, r, c)
    for cx, cy, r in ((30, 58, 14.6), (50, 46, 20.6), (70, 58, 14.6)):
        p.circle(cx, cy, r, c, 0)
    p.rect(30, 50, 70, 72.8, c, 0)
    p.line([(30, 73.4), (70, 73.4)], INK, 2.4)


def happy_cloud(p):
    cloud(p)
    p.face(50, 58, 0.9)


def duck(p):
    y = (255, 215, 60, 255)
    p.ellipse(52, 64, 30, 20, y)
    p.circle(36, 38, 16, y)
    p.poly([(18, 38), (8, 42), (18, 46)], (255, 140, 40, 255), 1.8)
    p.circle(32, 34, 2.6, INK, 0)
    p.ellipse(58, 62, 12, 8, (240, 190, 40, 255), 1.6)


def egg(p):
    p.ellipse(50, 54, 28, 36, (255, 248, 230, 255))
    p.ellipse(42, 42, 6, 10, (255, 255, 255, 200), 0)


def fish(p, c=(255, 140, 60, 255)):
    p.poly([(74, 50), (94, 32), (94, 68)], c)
    p.ellipse(46, 50, 32, 22, c)
    p.circle(30, 46, 4, INK, 0)
    p.circle(31, 45, 1.3, (255, 255, 255, 255), 0)
    p.arc(46, 50, 14, 300, 60, INK, 1.6)


def flower(p, c=(250, 110, 160, 255)):
    p.line([(50, 56), (50, 96)], (70, 160, 80, 255), 4)
    p.ellipse(60, 82, 10, 5, (90, 190, 90, 255), 1.6)
    for i in range(6):
        a = math.radians(i * 60)
        p.circle(50 + 17 * math.cos(a), 38 + 17 * math.sin(a), 12, c)
    p.circle(50, 38, 11, (255, 210, 60, 255))


def grapes(p):
    p.line([(50, 22), (54, 8)], (120, 80, 40, 255), 3)
    p.ellipse(64, 16, 10, 5, (90, 190, 90, 255), 1.8)
    rows = [(4, 30), (3, 44), (2, 58), (1, 72)]
    for n, y in rows:
        for i in range(n):
            x = 50 + (i - (n - 1) / 2) * 15
            p.circle(x, y, 9, (150, 80, 200, 255))


def heart(p, c=(240, 70, 110, 255)):
    p.poly(heart_pts(50, 52, 2.4), c)
    p.circle(36, 40, 5, (255, 255, 255, 120), 0)


def house(p):
    p.rect(22, 48, 78, 88, (255, 220, 160, 255))
    p.poly([(14, 50), (50, 16), (86, 50)], (230, 80, 70, 255))
    p.rect(43, 64, 57, 88, (150, 100, 60, 255), r=2)
    p.rect(28, 56, 38, 66, (180, 230, 255, 255), 1.6)
    p.rect(62, 56, 72, 66, (180, 230, 255, 255), 1.6)


def ice_cream(p):
    p.poly([(32, 50), (68, 50), (50, 96)], (230, 180, 110, 255))
    p.line([(40, 60), (58, 72)], INK, 1)
    p.line([(60, 60), (44, 78)], INK, 1)
    p.circle(50, 38, 20, (255, 180, 210, 255))
    p.circle(50, 22, 7, (230, 50, 70, 255))


def jellyfish(p):
    c = (190, 140, 250, 255)
    for x in (32, 42, 52, 62, 70):
        p.line([(x, 54), (x - 4, 68), (x + 2, 80), (x - 2, 92)], c, 3)
    p.pieslice(50, 56, 28, 180, 360, c)
    p.face(50, 44, 0.8)


def kite(p):
    p.line([(50, 84), (44, 92), (52, 96), (46, 100)], INK, 1.4)
    p.poly([(50, 8), (78, 40), (50, 84), (22, 40)], (255, 120, 80, 255))
    p.poly([(50, 8), (78, 40), (50, 40)], (255, 220, 80, 255))
    p.poly([(50, 40), (22, 40), (50, 84)], (255, 220, 80, 255))
    p.line([(50, 8), (50, 84)], INK, 1.4)
    p.line([(22, 40), (78, 40)], INK, 1.4)


def leaf(p, c=(90, 190, 90, 255)):
    pts = []
    for i in range(41):
        t = i / 40 * math.pi
        pts.append((50 + 22 * math.sin(t), 10 + 80 * i / 40))
    for i in range(41):
        t = (40 - i) / 40 * math.pi
        pts.append((50 - 22 * math.sin(t), 10 + 80 * (40 - i) / 40))
    p.poly(pts, c)
    p.line([(50, 14), (50, 94)], (60, 130, 60, 255), 1.8)


def moon(p):
    p.circle(50, 50, 36, (255, 230, 120, 255))
    p.circle(68, 40, 30, (0, 0, 0, 0), 0)
    p.d.ellipse([(68 - 30) * p.k, (40 - 30) * p.k, (68 + 30) * p.k, (40 + 30) * p.k], fill=(0, 0, 0, 0))
    p.arc(68, 40, 30, 110, 225, INK, 2.4)
    p.circle(30, 52, 2.4, INK, 0)
    p.arc(32, 60, 4, 30, 150, INK, 1.4)


def nest(p):
    p.ellipse(38, 50, 10, 13, (200, 230, 255, 255))
    p.ellipse(60, 48, 10, 13, (200, 230, 255, 255))
    p.ellipse(50, 66, 38, 18, (170, 120, 70, 255))
    for x in range(20, 82, 10):
        p.line([(x, 58), (x + 8, 76)], (120, 80, 40, 255), 1.2)


def orange(p):
    p.circle(50, 54, 34, (255, 150, 40, 255))
    p.ellipse(56, 20, 9, 5, (90, 190, 90, 255), 1.8)
    p.circle(40, 42, 6, (255, 255, 255, 110), 0)


def pear(p):
    c = (190, 220, 80, 255)
    p.line([(50, 20), (52, 8)], (120, 80, 40, 255), 3)
    p.circle(50, 34, 15, c)
    p.circle(50, 64, 26, c)
    p.ellipse(50, 48, 14, 14, c, 0)


def quilt(p):
    cols = [(255, 140, 160, 255), (120, 200, 255, 255), (255, 220, 90, 255), (150, 220, 140, 255)]
    for i in range(3):
        for j in range(3):
            p.rect(14 + i * 24, 14 + j * 24, 38 + i * 24, 38 + j * 24, cols[(i + j) % 4], 1.8)


def rainbow(p):
    cols = [(240, 70, 70), (255, 150, 50), (255, 220, 60), (90, 200, 90), (70, 150, 240), (150, 90, 220)]
    for i, c in enumerate(cols):
        r = 44 - i * 5.5
        p.pieslice(50, 72, r, 180, 360, c + (255,), 0)
    p.pieslice(50, 72, 44 - 6 * 5.5, 180, 360, (0, 0, 0, 0), 0)
    p.d.pieslice([(50 - 11) * p.k, (72 - 11) * p.k, (50 + 11) * p.k, (72 + 11) * p.k], 180, 360, fill=(0, 0, 0, 0))
    p.arc(50, 72, 44, 180, 360, INK, 2.2)
    for cx in (14, 86):
        p.circle(cx, 74, 10, (255, 255, 255, 255))
        p.circle(cx + (8 if cx < 50 else -8), 78, 8, (255, 255, 255, 255))


def raindrop(p, c=(80, 160, 250, 255)):
    pts = [(50, 8)] + [(50 + 28 * math.cos(math.radians(a)), 62 + 28 * math.sin(math.radians(a)))
                       for a in range(-55, 236, 5)]
    p.poly(pts, c)
    p.ellipse(40, 58, 4, 8, (255, 255, 255, 140), 0)


def rocket(p):
    p.poly([(36, 66), (22, 86), (38, 80)], (240, 80, 70, 255))
    p.poly([(64, 66), (78, 86), (62, 80)], (240, 80, 70, 255))
    p.poly([(42, 80), (50, 98), (58, 80)], (255, 180, 50, 255), 1.6)
    p.ellipse(50, 50, 16, 34, (235, 240, 250, 255))
    p.poly([(38, 30), (50, 8), (62, 30)], (240, 80, 70, 255), 0)
    p.ellipse(50, 50, 16, 34, None)
    p.circle(50, 46, 7, (120, 200, 255, 255))


def snowflake(p):
    c = (120, 190, 255, 255)
    for i in range(6):
        a = math.radians(i * 60)
        x, y = 50 + 40 * math.cos(a), 50 + 40 * math.sin(a)
        p.line([(50, 50), (x, y)], c, 4)
        for f in (0.55, 0.78):
            bx, by = 50 + 40 * f * math.cos(a), 50 + 40 * f * math.sin(a)
            for s in (-1, 1):
                b = a + s * math.radians(40)
                p.line([(bx, by), (bx + 11 * math.cos(b), by + 11 * math.sin(b))], c, 3)
    p.circle(50, 50, 6, c, 0)


def star(p, c=(255, 210, 50, 255)):
    p.poly(star_pts(50, 54, 44, 20), c)
    p.face(50, 56, 0.8)


def strawberry(p):
    p.poly([(18, 34), (82, 34), (50, 94)], (240, 60, 80, 255))
    p.ellipse(50, 38, 32, 14, (240, 60, 80, 255), 0)
    p.ellipse(50, 30, 18, 8, (90, 190, 90, 255), 1.8)
    for x, y in ((36, 48), (50, 50), (64, 48), (42, 62), (58, 62), (50, 76)):
        p.ellipse(x, y, 1.6, 2.4, (255, 240, 150, 255), 0)


def sun(p):
    c = (255, 200, 40, 255)
    for i in range(12):
        a = math.radians(i * 30)
        p.poly([(50 + 30 * math.cos(a - 0.18), 50 + 30 * math.sin(a - 0.18)),
                (50 + 46 * math.cos(a), 50 + 46 * math.sin(a)),
                (50 + 30 * math.cos(a + 0.18), 50 + 30 * math.sin(a + 0.18))], (255, 160, 40, 255), 1.6)
    p.circle(50, 50, 30, c)
    p.face(50, 50, 1.1)


def tree(p):
    p.rect(43, 56, 57, 94, (150, 100, 60, 255), r=2)
    for cx, cy, r in ((34, 46, 18), (66, 46, 18), (50, 30, 22), (50, 52, 18)):
        p.circle(cx, cy, r, (80, 180, 90, 255))
    for cx, cy, r in ((34, 46, 16.6), (66, 46, 16.6), (50, 30, 20.6), (50, 52, 16.6)):
        p.circle(cx, cy, r, (80, 180, 90, 255), 0)
    for cx, cy in ((40, 36), (60, 50), (48, 50)):
        p.circle(cx, cy, 3.5, (240, 70, 70, 255), 1)


def umbrella(p):
    p.line([(50, 46), (50, 86)], INK, 3)
    p.arc(56, 86, 6, 0, 180, INK, 3)
    p.pieslice(50, 50, 40, 180, 360, (150, 100, 230, 255))
    for x in (30, 50, 70):
        p.line([(50, 12), (x, 50)], INK, 1.2)


def volcano(p):
    p.poly([(8, 92), (38, 30), (62, 30), (92, 92)], (160, 110, 80, 255))
    p.poly([(38, 30), (62, 30), (58, 42), (52, 36), (46, 44), (42, 36)], (240, 80, 40, 255), 1.6)
    for cx, cy, r in ((44, 18, 7), (56, 14, 8), (50, 6, 5)):
        p.circle(cx, cy, r, (200, 200, 210, 255), 1.6)


def watermelon(p):
    p.pieslice(50, 34, 44, 0, 180, (90, 180, 80, 255))
    p.pieslice(50, 34, 38, 0, 180, (255, 245, 220, 255), 0)
    p.pieslice(50, 34, 34, 0, 180, (250, 80, 100, 255), 0)
    for x, y in ((36, 46), (50, 52), (64, 46), (44, 60), (58, 60)):
        p.ellipse(x, y, 1.8, 3, INK, 0)
    p.pieslice(50, 34, 44, 0, 180, None)


def xylophone(p):
    cols = [(240, 70, 70), (255, 150, 50), (255, 220, 60), (90, 200, 90), (70, 150, 240), (150, 90, 220)]
    for i, c in enumerate(cols):
        x = 14 + i * 12.5
        h = 60 - i * 6
        p.rect(x, 50 - h / 2, x + 10, 50 + h / 2, c + (255,), 1.8, r=3)
    p.line([(70, 86), (90, 70)], (150, 100, 60, 255), 2.5)
    p.circle(91, 69, 4, (240, 70, 70, 255), 1.4)


def yoyo(p):
    p.line([(50, 50), (50, 4)], INK, 1.5)
    p.circle(50, 58, 32, (70, 200, 160, 255))
    p.circle(50, 58, 20, (255, 220, 80, 255))
    p.circle(50, 58, 5, INK, 0)


def zigzag(p):
    p.line([(10, 70), (26, 30), (42, 70), (58, 30), (74, 70), (90, 30)], (240, 80, 140, 255), 8)


def zebra(p):
    # stylised zebra face
    p.ellipse(50, 50, 24, 34, (255, 255, 255, 255))
    p.ellipse(50, 74, 18, 12, (80, 80, 90, 255))
    p.ellipse(28, 22, 6, 12, (255, 255, 255, 255))
    p.ellipse(72, 22, 6, 12, (255, 255, 255, 255))
    for y in (28, 40, 52):
        p.line([(30, y), (40, y + 4)], INK, 3)
        p.line([(70, y), (60, y + 4)], INK, 3)
    p.circle(40, 48, 3, INK, 0)
    p.circle(60, 48, 3, INK, 0)


def earth(p):
    p.circle(50, 50, 40, (80, 160, 250, 255))
    p.poly([(28, 30), (44, 24), (50, 38), (40, 52), (26, 46)], (90, 200, 100, 255), 0)
    p.poly([(56, 54), (72, 48), (80, 62), (66, 78), (56, 70)], (90, 200, 100, 255), 0)
    p.circle(50, 50, 40, None)
    p.face(50, 50, 1.0)


def planet(p):
    p.ellipse(50, 52, 46, 12, (255, 200, 120, 255), 2.4)
    p.circle(50, 50, 28, (250, 170, 90, 255))
    p.d.rectangle([4 * p.k, 52 * p.k, 96 * p.k, 70 * p.k], fill=None)
    p.ellipse(50, 56, 46, 10, (0, 0, 0, 0), 0)
    p.arc(50, 50, 28, 180, 360, INK, 2.4)
    p.line([(8, 54), (92, 54)], (255, 200, 120, 255), 4)


def seed(p):
    p.ellipse(50, 80, 40, 10, (150, 100, 60, 255))
    p.ellipse(50, 66, 12, 9, (200, 150, 90, 255))


def sprout(p):
    p.ellipse(50, 84, 40, 10, (150, 100, 60, 255))
    p.line([(50, 84), (50, 44)], (70, 160, 80, 255), 4)
    p.ellipse(36, 42, 14, 7, (90, 190, 90, 255))
    p.ellipse(64, 36, 14, 7, (90, 190, 90, 255))


def caterpillar(p):
    cols = [(120, 210, 90, 255), (160, 230, 100, 255)]
    for i in range(5):
        p.circle(20 + i * 13, 62 - (6 if i % 2 else 0), 11, cols[i % 2])
    p.circle(84, 50, 14, (120, 210, 90, 255))
    p.circle(80, 47, 2.4, INK, 0)
    p.circle(89, 47, 2.4, INK, 0)
    p.arc(84, 52, 5, 20, 160, INK, 1.4)
    p.line([(80, 36), (76, 26)], INK, 1.5)
    p.line([(88, 36), (92, 26)], INK, 1.5)


def cocoon(p):
    p.line([(50, 4), (50, 20)], (120, 80, 40, 255), 3)
    p.ellipse(50, 54, 18, 34, (180, 150, 100, 255))
    for y in (34, 46, 58, 70):
        p.arc(50, y - 10, 15, 50, 130, (130, 100, 60, 255), 1.4)


def bee(p):
    p.ellipse(38, 30, 12, 16, (220, 240, 255, 230))
    p.ellipse(60, 28, 12, 16, (220, 240, 255, 230))
    p.ellipse(50, 56, 30, 22, (255, 210, 50, 255))
    for x in (42, 56):
        p.rect(x - 4, 36, x + 2, 76, INK, 0)
    p.ellipse(50, 56, 30, 22, None)
    p.circle(22, 52, 4, (255, 255, 255, 0), 0)
    p.circle(26, 50, 2.6, INK, 0)
    p.poly([(80, 54), (92, 56), (80, 60)], INK, 0)


def frog(p):
    c = (100, 200, 90, 255)
    p.ellipse(50, 62, 36, 26, c)
    p.circle(32, 36, 12, c)
    p.circle(68, 36, 12, c)
    p.circle(32, 36, 6, (255, 255, 255, 255), 1.4)
    p.circle(68, 36, 6, (255, 255, 255, 255), 1.4)
    p.circle(32, 37, 3, INK, 0)
    p.circle(68, 37, 3, INK, 0)
    p.arc(50, 56, 16, 20, 160, INK, 2)


def tadpole(p):
    p.line([(56, 52), (70, 44), (82, 56), (94, 48)], (70, 90, 70, 255), 5)
    p.circle(42, 52, 18, (70, 90, 70, 255))
    p.circle(36, 48, 3, (255, 255, 255, 255), 0)


def waves(p):
    for j, y in enumerate((44, 62, 80)):
        pts = [(x, y + 5 * math.sin(x / 7 + j)) for x in range(8, 93, 3)]
        p.line(pts, (70, 150, 240, 255), 5)


def cookie(p):
    p.circle(50, 50, 38, (215, 160, 90, 255))
    for x, y in ((36, 36), (60, 34), (66, 58), (42, 62), (52, 48)):
        p.circle(x, y, 4.5, (100, 60, 30, 255), 0)


def cupcake(p):
    p.poly([(26, 56), (74, 56), (66, 92), (34, 92)], (120, 190, 240, 255))
    for cx, cy, r in ((34, 50, 12), (66, 50, 12), (50, 40, 16)):
        p.circle(cx, cy, r, (255, 190, 220, 255))
    p.circle(50, 22, 6, (240, 60, 80, 255))


def lemon(p):
    p.ellipse(50, 52, 36, 26, (255, 230, 60, 255))
    p.ellipse(88, 52, 4, 3, (255, 230, 60, 255), 1.6)
    p.ellipse(12, 52, 4, 3, (255, 230, 60, 255), 1.6)


ICONS = {
    "apple": apple, "ball": ball, "balloon": balloon, "banana": banana, "butterfly": butterfly,
    "car": car, "cat": cat, "cloud": happy_cloud, "plain_cloud": cloud, "duck": duck, "egg": egg,
    "fish": fish, "flower": flower, "grapes": grapes, "heart": heart, "house": house,
    "ice cream": ice_cream, "jellyfish": jellyfish, "kite": kite, "leaf": leaf, "moon": moon,
    "nest": nest, "orange": orange, "pear": pear, "quilt": quilt, "rainbow": rainbow,
    "raindrop": raindrop, "rocket": rocket, "snowflake": snowflake, "star": star,
    "strawberry": strawberry, "sun": sun, "tree": tree, "umbrella": umbrella, "volcano": volcano,
    "watermelon": watermelon, "xylophone": xylophone, "yo-yo": yoyo, "zigzag": zigzag,
    "zebra": zebra, "earth": earth, "planet": planet, "seed": seed, "sprout": sprout,
    "caterpillar": caterpillar, "cocoon": cocoon, "bee": bee, "frog": frog, "tadpole": tadpole,
    "waves": waves, "cookie": cookie, "cupcake": cupcake, "lemon": lemon,
}


@lru_cache(maxsize=256)
def sprite(name, color=None):
    """Return an RGBA sprite (OUT x OUT) for an icon. Optional color tint for some icons."""
    img = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    p = Pen(img)
    fn = ICONS[name]
    if color is not None:
        fn(p, tuple(color) + (255,))
    else:
        fn(p)
    return img.resize((OUT, OUT), Image.LANCZOS)


# ---------------------------------------------------------------- shapes
SHAPES = {
    "circle": {"sides": 0}, "square": {"sides": 4}, "triangle": {"sides": 3},
    "rectangle": {"sides": 4}, "star": {"sides": 10}, "heart": {"sides": 0},
    "oval": {"sides": 0}, "diamond": {"sides": 4}, "pentagon": {"sides": 5},
    "hexagon": {"sides": 6},
}


def shape_points(name):
    if name == "square":
        return [(18, 18), (82, 18), (82, 82), (18, 82)]
    if name == "rectangle":
        return [(8, 28), (92, 28), (92, 72), (8, 72)]
    if name == "triangle":
        return [(50, 10), (90, 84), (10, 84)]
    if name == "diamond":
        return [(50, 6), (86, 50), (50, 94), (14, 50)]
    if name == "pentagon":
        return reg_pts(50, 54, 42, 5)
    if name == "hexagon":
        return reg_pts(50, 50, 42, 6, rot=0)
    if name == "star":
        return star_pts(50, 54, 46, 20)
    return None


@lru_cache(maxsize=128)
def shape_sprite(name, color, highlight_side=-1):
    img = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    p = Pen(img)
    c = tuple(color) + (255,)
    pts = shape_points(name)
    if name == "circle":
        p.circle(50, 50, 42, c, 3)
    elif name == "oval":
        p.ellipse(50, 50, 44, 30, c, 3)
    elif name == "heart":
        p.poly(heart_pts(50, 52, 2.6), c, 3)
    else:
        p.poly(pts, c, 3)
    p.ellipse(36, 34, 7, 5, (255, 255, 255, 110), 0)
    if highlight_side >= 0 and pts:
        a = pts[highlight_side % len(pts)]
        b = pts[(highlight_side + 1) % len(pts)]
        p.line([a, b], (255, 255, 255, 255), 6)
        p.line([a, b], (255, 90, 120, 255), 3.4)
        for q in (a, b):
            p.circle(q[0], q[1], 3.5, (255, 255, 255, 255), 1.6)
    return img.resize((OUT, OUT), Image.LANCZOS)
