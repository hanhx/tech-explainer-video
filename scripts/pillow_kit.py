"""Reusable animation components for pillow_engine.py scenes.

Import in a project's scenes.py:
    import sys; sys.path.insert(0, SKILL + '/scripts')   # or copy this file next to scenes.py
    from pillow_kit import *

Every component takes `x` (the ctx passed to draw_<scene>) and a progress or time window,
so scenes stay declarative:  appear(x, rect, x.at('词'), ...).
Rect = (left, top, width, height). Colours are RGB tuples.
"""
import math

DARK = (16, 24, 44)


# ---------------------------------------------------------------- timing
def window(x, t0, dur=0.6):
    """Progress 0..1 of an action starting at scene-local t0."""
    return x.seg(x.t, t0, t0 + dur)


def stagger(i, n, total=1.0):
    """Start offset for item i of n when n items should start across `total` seconds."""
    return total * i / max(1, n - 1)


# ---------------------------------------------------------------- geometry
def arc_path(x, r1, r2, p, arc=140):
    """Rect moving from r1 to r2 along an upward arc (negative arc = downward)."""
    r = x.lerp_r(r1, r2, x.smooth(p))
    return (r[0], r[1] - math.sin(math.pi * p) * arc, r[2], r[3])


def pop_scale(x, rect, p):
    """Rect scaled about its centre with overshoot, for 'appear' moments."""
    s = x.back(p) if p < 1 else 1.0
    bx, by, w, h = rect
    return (bx + w / 2 * (1 - s), by + h / 2 * (1 - s), w * s, h * s)


def shake_dx(x, amount):
    return math.sin(x.t * 60) * 6 * amount


# ---------------------------------------------------------------- objects
def block(x, rect, fill, label=None, size=34, ink=DARK, radius=14, outline=None, width=0):
    x.rr(rect, fill=fill, outline=outline, width=width, radius=radius)
    if label and rect[2] > 30 and rect[3] > 20:
        x.text((rect[0] + rect[2] / 2, rect[1] + rect[3] / 2), label, size, ink, bold=True)


def container(x, rect, label, line=(110, 130, 190), fill=(24, 34, 66), alarm=0.0, alarm_col=(255, 82, 92), shake=0.0,
              label_size=38, muted=(128, 142, 180)):
    """A titled box (context window, cache, queue, server...). Turns red and shakes as alarm/shake -> 1."""
    dx = shake_dx(x, shake); bx, by, w, h = rect
    x.d.rounded_rectangle([bx + dx, by, bx + w + dx, by + h], radius=22, fill=fill, outline=x.lerp_c(line, alarm_col, alarm), width=5)
    x.text((bx + w / 2 + dx, by - 46), label, label_size, x.lerp_c(muted, alarm_col, alarm), bold=True)
    return dx


def pill(x, center, text, size=40, fill=(17, 24, 48), ink=(236, 240, 250), a=1.0, pad=26):
    """Readable label with its own backing so it never collides with busy art."""
    if a <= 0: return
    f = x.font(size, True); w = x.d.textlength(text, font=f)
    cx, cy = center
    x.rr((cx - w / 2 - pad, cy - size * 0.85, w + 2 * pad, size * 1.7), fill=x.fade(fill, a), radius=16)
    x.text(center, text, size, x.fade(ink, a), bold=True)


def ring(x, center, r, col, p=1.0, width=5):
    """Highlight ring that grows in with p."""
    if p <= 0: return
    rr = r * x.back(p) if p < 1 else r
    cx, cy = center
    x.d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=col, width=width)


def arrow(x, p0, p1, col, p=1.0, width=6, head=18):
    """Arrow drawn from p0 towards p1, growing with p."""
    if p <= 0: return
    ex, ey = x.lerp(p0[0], p1[0], p), x.lerp(p0[1], p1[1], p)
    x.d.line([p0, (ex, ey)], fill=col, width=width)
    ang = math.atan2(ey - p0[1], ex - p0[0])
    pts = [(ex, ey), (ex - head * math.cos(ang - 0.45), ey - head * math.sin(ang - 0.45)),
           (ex - head * math.cos(ang + 0.45), ey - head * math.sin(ang + 0.45))]
    x.d.polygon(pts, fill=col)


def gear(x, center, r, angle, col, hole=(17, 24, 48)):
    cx, cy = center; pts = []
    for k in range(16):
        a = angle + k * math.pi / 8; rad = r if k % 2 == 0 else r * 0.78
        pts += [(cx + rad * math.cos(a + d), cy + rad * math.sin(a + d)) for d in (-0.12, 0.12)]
    x.d.polygon(pts, fill=col)
    x.d.ellipse([cx - r * 0.32, cy - r * 0.32, cx + r * 0.32, cy + r * 0.32], fill=hole)


def token(x, center, col, r=18, label=None):
    """Small moving thing: packet, request, data item."""
    cx, cy = center
    x.d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    if label: x.text((cx, cy + r + 24), label, 28, col, bold=True)


# ---------------------------------------------------------------- motions (the visual events)
def appear(x, rect, t0, fill, label=None, dur=0.4, **kw):
    """Object pops in at t0. Returns progress."""
    p = window(x, t0, dur)
    if p > 0: block(x, pop_scale(x, rect, p), fill, label if p > 0.7 else None, **kw)
    return p


def fly(x, r1, r2, t0, fill, label=None, dur=0.8, arc=140, **kw):
    """Object travels r1 -> r2 starting at t0 (stays at r1 before, r2 after). Returns progress."""
    p = window(x, t0, dur)
    block(x, arc_path(x, r1, r2, p, arc), fill, label, **kw)
    return p


def morph(x, r1, r2, t0, c1, c2, label1=None, label2=None, dur=0.9, **kw):
    """Same object changes shape/colour (keeps identity). Label swaps at the midpoint."""
    p = window(x, t0, dur); s = x.smooth(p)
    block(x, x.lerp_r(r1, r2, s), x.lerp_c(c1, c2, s), label1 if p < 0.5 else label2, **kw)
    return p


def fill_up(x, rect, level, colors, item_h=9, gap=2, overflow=0.0, shake=0.0):
    """Stack of thin items filling `rect` from the bottom. level 0..1 is full; >1 spills past the top.
    Returns alarm 0..1 (how far past full)."""
    bx, by, w, h = rect; dx = shake_dx(x, shake)
    n = int(level * (h - 24) / (item_h + gap))
    for k in range(n):
        x.rr((bx + 14 + dx, by + h - 12 - (k + 1) * (item_h + gap), w - 28, item_h), fill=colors[k % len(colors)], radius=2)
    return x.clamp((level - 1.0) / 0.15)


def scan(x, rect, t0, col, dur=1.4, width=4):
    """Vertical scan line sweeping across rect. Returns current x position or None."""
    p = window(x, t0, dur)
    if 0 < p < 1:
        sx = rect[0] + rect[2] * p
        x.d.line([sx, rect[1], sx, rect[1] + rect[3]], fill=col, width=width)
        return sx
    return None


def bars(x, items, base_y, t0, max_h=500, dur=1.4, width=200, gap=120, cx=960, label_size=40, ink=(236, 240, 250)):
    """Comparison bars rising together. items = [(label, value 0..1+, colour)], value>1 overflows. Returns progress."""
    p = window(x, t0, dur); n = len(items)
    left = cx - (n * width + (n - 1) * gap) / 2
    for i, (label, value, col) in enumerate(items):
        h = max_h * value * x.ease_out(p)
        bx = left + i * (width + gap)
        x.rr((bx, base_y - h, width, h), fill=col, radius=10)
        x.text((bx + width / 2, base_y + 46), label, label_size, ink, bold=True)
    return p


def split_screen(x, t, draw_left, draw_right, divider=(60, 80, 130)):
    """Run two mini-scenes side by side (same task, two strategies). Each draw fn gets (x, offset_x)."""
    draw_left(x, 0)
    draw_right(x, 960)
    x.d.line([960, 80, 960, 900], fill=divider, width=3)


def counter(x, center, value, size=72, col=(236, 240, 250), suffix=''):
    x.text(center, f'{value:,.0f}{suffix}', size, col, bold=True)


def stamp(x, center, text, t0, col=(255, 82, 92), size=56):
    """Big verdict word that slams in (✓/✗/命中/超限)."""
    p = window(x, t0, 0.35)
    if p > 0:
        s = 1 + 0.6 * (1 - x.ease_out(p))
        x.text(center, text, int(size * s), x.fade(col, p), bold=True)
    return p
