"""Native 60 fps visual/SFX probe; no narration, no BGM, no live requests."""
import math
from pillow_kit import arrow, pill, fly

STYLE = {'size': (1280, 720), 'bg': (245, 244, 239), 'ink': (28, 44, 54)}
BG, INK = STYLE['bg'], STYLE['ink']
TEAL, AMBER, LINE, PAPER = (0, 128, 119), (235, 157, 51), (197, 210, 208), (255, 255, 252)
HIDE_COPY = False
DELAY = 2.0
RAW_KEYS = [(1 + i * .7, 'cache'[:i + 1]) for i in range(5)]
KEYS = list(zip([9.2, 10, 10.8, 11.6, 13], ['c', 'ca', 'cac', 'cach', 'cache']))
KEYS += [(19 + i, 'cache' + ' line'[:i + 1]) for i in range(5)]


def dispatches(keys, delay):
    return [(at + delay, value) for i, (at, value) in enumerate(keys)
            if i + 1 == len(keys) or keys[i + 1][0] >= at + delay]


SENDS = dispatches(KEYS, DELAY)


def events():
    out = [(at, 'keyboard_tap', .38) for at, _ in RAW_KEYS + KEYS]
    out += [(at + .08, 'motion_swish', .30) for at, _ in RAW_KEYS]
    out += [(at + .83, 'motion_land', .35) for at, _ in RAW_KEYS]
    out += [(7.85, 'mouse_down', .65), (7.92, 'mouse_up', .6)]
    out += [(8.25, 'motion_sweep', .45)]
    out += [(at, 'motion_swish', .65) for at, _ in SENDS]
    out += [(at + .75, 'motion_land', .5) for at, _ in SENDS]
    for i, (at, _) in enumerate(KEYS):
        stop = min(at + DELAY, KEYS[i + 1][0] if i + 1 < len(KEYS) else 1e10)
        for step in range(1, 5):
            tick = at + .5 * step
            if tick < stop - 1e-8:
                out.append((tick, 'clock_tick' if step % 2 else 'clock_tock', .19))
    return sorted(out)


def cursor(ctx, T):
    p = ctx.smooth(ctx.seg(T, 7.05, 7.75))
    x, y = ctx.lerp(1170, 404, p), ctx.lerp(600, 447, p)
    a = 1 - ctx.smooth(ctx.seg(T, 8, 8.3))
    if 7.05 <= T < 8.3:
        col = ctx.lerp_c(BG, INK, a)
        shrink = .84 if 7.85 <= T < 7.92 else 1
        pts = [(x, y), (x + 12 * shrink, y + 39 * shrink),
               (x + 22 * shrink, y + 27 * shrink), (x + 39 * shrink, y + 25 * shrink)]
        ctx.d.polygon(pts, fill=col)


def query_value(T):
    source = RAW_KEYS if T < 8.25 else KEYS
    return next((value for at, value in reversed(source) if T >= at), '')


def draw(ctx):
    T = ctx.scene['start_s'] + ctx.t
    for at, kind, gain in events():
        if ctx.scene['start_s'] <= at < ctx.scene['start_s'] + ctx.duration:
            ctx.sfx(at - ctx.scene['start_s'], kind, gain)

    # One persistent workspace; all scene boundaries preserve object positions.
    titles = [(0,7,'每次输入都搜索？'),(7,18,'等停下来再搜索'),(18,23,'一直输入呢？'),
              (23,25,'停下来，再等两秒'),(25,28,'发出最新输入')]
    phase_start, phase_end, title = next(item for item in titles if item[0] <= T < item[1])
    a = min(ctx.seg(T,phase_start,phase_start+.25),ctx.seg(phase_end-T,0,.25))
    if not HIDE_COPY:
        ctx.text((90, 76), title, 44, ctx.lerp_c(BG, INK, a), anchor='lm', bold=True)

    # Search editor, direct task object rather than a text capability card.
    ctx.rr((82, 192, 450, 290), PAPER, outline=LINE, width=2, radius=23)
    ctx.d.ellipse((112, 224, 134, 246), outline=TEAL, width=3)
    ctx.d.line((131, 243, 144, 256), fill=TEAL, width=3)
    ctx.text((160, 240), query_value(T) + '|', 42, INK, anchor='lm')
    ctx.d.line((111, 281, 500, 281), fill=LINE, width=2)
    for j, width in enumerate((235, 318, 270)):
        ctx.rr((114, 316 + j * 30, width, 10), fill=(225, 232, 229), radius=4)
    ctx.text((120, 445), '防抖', 27, INK, anchor='lm')
    switch = ctx.smooth(ctx.seg(T, 7.85, 8.1))
    ctx.rr((362, 423, 78, 42), ctx.lerp_c(LINE, TEAL, switch), radius=21)
    cx = 384 + 34 * switch
    ctx.d.ellipse((cx - 15, 429, cx + 15, 459), fill=PAPER)

    # Destination with arrival slots that contain actual request snapshots.
    ctx.rr((922, 192, 275, 290), PAPER, outline=LINE, width=2, radius=23)
    ctx.text((1058, 161), '搜索服务', 28, TEAL)
    arrow(ctx, (545, 310), (897, 310), LINE, width=3, head=12)
    compact = ctx.smooth(ctx.seg(T, 8.25, 8.9))
    for i, (at, value) in enumerate(RAW_KEYS):
        if T >= at + .08:
            old = ctx.t
            ctx.t = T
            rect = (946, 215 + i * ctx.lerp(47, 23, compact), 225, ctx.lerp(35, 18, compact))
            fly(ctx, (350, 222, 102, 38), rect, at + .08,
                ctx.lerp_c(AMBER, LINE, compact), value, dur=.75, arc=-50, size=round(ctx.lerp(23,16,compact)))
            ctx.t = old

    # Timer appears as a physical timing device; its hand and tick share time.
    reveal = ctx.smooth(ctx.seg(T, 8.25, 8.9))
    if reveal > 0:
        center = (700, ctx.lerp(530, 442, reveal))
        r = 73
        latest = next(((at, value) for at, value in reversed(KEYS) if at <= T), None)
        progress = min(1., (T - latest[0]) / DELAY) if latest else 0.
        active = latest is not None and 0 <= T - latest[0] < DELAY
        col = TEAL if progress >= 1 else AMBER
        ctx.d.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r), fill=PAPER, outline=LINE, width=3)
        for i in range(8):
            angle = -math.pi / 2 + i * math.pi / 4
            x, y = center[0] + 62 * math.cos(angle), center[1] + 62 * math.sin(angle)
            ctx.d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=LINE)
        if latest:
            theta = -math.pi / 2 + progress * math.tau
            ctx.d.line((center[0], center[1], center[0] + 49 * math.cos(theta), center[1] + 49 * math.sin(theta)), fill=col, width=5)
            # A reset ripple links each actual input event to the reset.
            rp = ctx.seg(T, latest[0], latest[0] + .35)
            if rp < 1:
                rr = r + rp * 17
                ctx.d.ellipse((center[0] - rr, center[1] - rr, center[0] + rr, center[1] + rr), outline=ctx.lerp_c(AMBER, BG, rp), width=3)
        ctx.d.ellipse((center[0] - 5, center[1] - 5, center[0] + 5, center[1] + 5), fill=col)
        ctx.text((center[0], center[1] + 105), '2s', 30, INK)
        for at, value in SENDS:
            if T >= at:
                old = ctx.t
                ctx.t = T
                idx = SENDS.index((at, value))
                fly(ctx, (540, 250, 125, 40), (944, 350 + idx * 61, 229, 45), at,
                    TEAL, value, dur=.75, arc=-12, size=24, ink=PAPER)
                ctx.t = old
        # Each key visibly enters the timer; no request leaves before deadline.
        for at, _ in KEYS:
            if at <= T < at + .28:
                p = ctx.smooth(ctx.seg(T, at, at + .28))
                x, y = ctx.lerp(505, 626, p), ctx.lerp(260, center[1], p)
                ctx.d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=AMBER)

    cursor(ctx, T)


draw_raw = draw
draw_reset = draw
draw_send = draw
draw_keep_typing = draw
draw_pause = draw
draw_send_again = draw
