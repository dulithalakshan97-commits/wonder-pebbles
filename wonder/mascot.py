"""Pebble - the Wonder Pebbles mascot (an original character: a friendly blue pebble)."""
from functools import lru_cache
from PIL import Image
from .icons import Pen, SS, INK

SIZE = 460
BODY = (143, 170, 214, 255)
BODY_DARK = (118, 146, 194, 255)
SPECK = (120, 148, 196, 255)


@lru_cache(maxsize=32)
def pebble(mouth=0, blink=False, wave=False):
    """mouth: 0 (closed smile) .. 4 (wide open)."""
    img = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    p = Pen(img)
    # shadow
    p.ellipse(50, 92, 30, 4, (0, 0, 0, 40), 0)
    # little arms
    p.ellipse(14, 66 if not wave else 46, 8, 6, BODY_DARK)
    p.ellipse(86, 66, 8, 6, BODY_DARK)
    # body
    p.ellipse(50, 60, 38, 32, BODY, 2.6)
    p.ellipse(50, 66, 34, 24, BODY_DARK, 0)
    p.ellipse(50, 58, 35, 28, BODY, 0)
    p.ellipse(36, 42, 10, 6, (255, 255, 255, 90), 0)
    for x, y, r in ((70, 44, 2.2), (76, 52, 1.6), (26, 70, 1.8), (66, 78, 1.6)):
        p.circle(x, y, r, SPECK, 0)
    # little sprout on top (wonder!)
    p.line([(50, 29), (50, 20)], (80, 170, 90, 255), 2.4)
    p.ellipse(44, 18, 6, 3.4, (100, 200, 100, 255), 1.6)
    p.ellipse(56, 16, 6, 3.4, (100, 200, 100, 255), 1.6)
    # eyes
    for ex in (38, 62):
        if blink:
            p.arc(ex, 52, 5, 200, 340, INK, 2.2)
        else:
            p.ellipse(ex, 54, 6, 7.5, (255, 255, 255, 255), 1.6)
            p.ellipse(ex + 0.8, 55, 3.6, 4.6, INK, 0)
            p.circle(ex + 2, 53, 1.4, (255, 255, 255, 255), 0)
    # cheeks
    p.ellipse(28, 66, 5, 3, (255, 140, 160, 160), 0)
    p.ellipse(72, 66, 5, 3, (255, 140, 160, 160), 0)
    # mouth
    if mouth <= 0:
        p.arc(50, 64, 6, 25, 155, INK, 2.2)
    else:
        h = 1.5 + mouth * 1.6
        p.ellipse(50, 69, 5 + mouth * 0.6, h, (170, 60, 80, 255), 1.8)
        p.ellipse(50, 69 + h * 0.45, 3 + mouth * 0.3, h * 0.4, (255, 130, 150, 255), 0)
    return img.resize((SIZE, SIZE), Image.LANCZOS)
