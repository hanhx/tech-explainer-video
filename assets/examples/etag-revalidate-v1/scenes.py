"""One conditional GET, replayed after the server's representation changes."""

import os

from pillow_kit import moving_grid

STYLE = {"size": (1280, 720), "bg": "#f5f8fa", "ink": "#182b44"}
HIDE_COPY = os.environ.get("ETAG_HIDE_COPY") == "1"

INK = "#182b44"
LINE = "#d8e5ec"
BLUE = "#1671aa"
GREEN = "#197d69"
ORANGE = "#b64f29"
WHITE = "#ffffff"
BROWSER_X = 254
SERVER_X = 1026


def plate(ctx, x, y, label, color, width=94, height=50):
    ctx.rr((x - width / 2, y - height / 2, width, height), color, radius=7)
    if not HIDE_COPY:
        ctx.text((x, y), label, 34, WHITE, bold=True)


def page(ctx, x, y, scale=1.0, fresh=False):
    """Retain the page's silhouette and landmark while it travels."""
    def block(rect, color):
        left, top, right, bottom = rect
        ctx.d.rectangle(
            (x + left * scale, y + top * scale, x + right * scale, y + bottom * scale),
            fill=color,
        )

    block((-142, -88, 142, 88), INK)
    block((-136, -82, 136, 82), WHITE)
    block((-126, -70, 126, 26), "#ffdb9a" if fresh else "#c8edff")
    if fresh:
        block((66, -60, 101, -28), "#ea6635")
        block((-96, -29, -45, 26), "#b94d32")
        block((-45, -7, 40, 26), "#dd7251")
        block((40, 7, 126, 26), "#e8985c")
    else:
        block((-102, -59, -71, -30), "#3285c2")
        block((37, -15, 89, 26), "#4898b6")
        block((-25, 3, 37, 26), "#267b9b")
        block((-126, 17, -25, 26), "#5db3c9")
    block((-126, 41, 80, 52), "#aebfcd")
    block((-126, 62, 21, 72), "#d2dce4")


def arrow(ctx, y, moving_right, color):
    start, end = (438, 842) if moving_right else (842, 438)
    sign = 1 if moving_right else -1
    ctx.d.line((start, y, end - 14 * sign, y), fill=color, width=4)
    ctx.d.polygon(((end, y), (end - 18 * sign, y - 11), (end - 18 * sign, y + 11)), fill=color)


def refresh(ctx, t, event):
    x, y = 106, 227
    pressed = event <= t < event + 0.17
    ctx.rr((x - 27, y - 27, 54, 54), BLUE if pressed else "#e9f5fb", radius=7)
    color = WHITE if pressed else BLUE
    ctx.d.arc((x - 14, y - 14, x + 14, y + 14), 22, 325, fill=color, width=4)
    ctx.d.polygon(((x + 15, y - 10), (x + 16, y + 1), (x + 5, y - 2)), fill=color)
    if event - 0.6 <= t < event + 0.28:
        p = ctx.smooth(ctx.seg(t, event - 0.6, event))
        px, py = ctx.lerp(168, x + 6, p), ctx.lerp(270, y + 7, p)
        cursor = [(px, py), (px + 5, py + 24), (px + 11, py + 17), (px + 19, py + 18)]
        ctx.d.polygon(cursor, fill=INK, outline=WHITE)


def highlight(ctx, x, color):
    ctx.rr((x - 156, 252, 312, 200), None, color, width=6, radius=9)


def compare(ctx, matches):
    color = GREEN if matches else ORANGE
    ctx.rr((869, 196, 326, 64), None, color, width=3, radius=8)
    if matches:
        ctx.d.line(((1010, 228), (1020, 238), (1041, 215)), fill=color, width=7)
    else:
        ctx.d.line((1012, 215, 1038, 241), fill=color, width=7)
        ctx.d.line((1038, 215, 1012, 241), fill=color, width=7)


def draw(ctx):
    t = ctx.scene["start_s"] + ctx.t
    for at, sound, gain in (
        (1.3, "mouse_click", 0.45), (3.2, "motion_swish", 0.60),
        (6.3, "motion_land", 0.42), (9.5, "motion_swish", 0.48),
        (11.8, "motion_land", 0.48), (15.5, "keyboard_tap", 0.42),
        (17.1, "mouse_click", 0.45), (17.7, "motion_swish", 0.60),
        (19.8, "motion_land", 0.42), (21.5, "motion_swish", 0.76),
        (24.2, "motion_land", 0.65),
    ):
        local = at - ctx.scene["start_s"]
        if 0 <= local < ctx.duration:
            ctx.sfx(local, sound, gain)

    # Keep the two copies visible throughout; only the server changes first.
    moving_grid(ctx, cell=52, speed=7, line="#e8eff3", width=1)
    if not HIDE_COPY:
        ctx.text((64, 57), "刷新网页时", 45, INK, anchor="lm", bold=True)
        if t >= 4:
            label = "ETag 缓存标签"
            if 11.8 <= t < 15.5:
                label = "304 未修改"
            elif t >= 24.2:
                label = "200 返回新页面"
            ctx.text((1216, 57), label, 36, BLUE, anchor="rm", bold=True)

    for x, label in ((64, "浏览器"), (836, "服务器")):
        ctx.rr((x + 5, 134, 380, 423), "#dfe9ee", radius=12)
        ctx.rr((x, 126, 380, 423), WHITE, LINE, width=3, radius=12)
        if not HIDE_COPY:
            ctx.text((x + 190, 164), label, 38, INK, bold=True)
    # Icons still identify the left as interactive and the right as a server.
    for y in (153, 169):
        ctx.rr((1140, y, 44, 12), LINE, radius=3)
        ctx.d.rectangle((1172, y + 3, 1177, y + 8), fill=BLUE)

    refresh(ctx, t, 1.3 if t < 15 else 17.1)
    server_fresh = t >= 15.5
    browser_fresh = t >= 24.2
    page(ctx, BROWSER_X, 352, fresh=browser_fresh)
    page(ctx, SERVER_X, 352, fresh=server_fresh)
    if 15.5 <= t < 16.6:
        highlight(ctx, SERVER_X, ORANGE)

    # The browser sends a copy of its existing validator, not its cached page.
    plate(ctx, 374, 228, '"b"' if browser_fresh else '"a"', ORANGE if browser_fresh else BLUE)
    plate(ctx, 1140, 228, '"b"' if server_fresh else '"a"', ORANGE if server_fresh else BLUE)
    for depart, arrive, compare_until in ((3.2, 6.3, 9.5), (17.7, 19.8, 21.5)):
        if depart <= t < compare_until:
            p = ctx.smooth(ctx.seg(t, depart, arrive))
            arrow(ctx, 228, True, "#81a6be")
            plate(ctx, ctx.lerp(374, 922, p), 228, '"a"', BLUE)
            if not HIDE_COPY:
                ctx.text((640, 193), "If-None-Match", 30, BLUE)
            if t >= arrive:
                compare(ctx, matches=not server_fresh)

    # Same representation: the reply chip moves; the browser's page stays put.
    if 9.5 <= t < 15.5:
        p = ctx.smooth(ctx.seg(t, 9.5, 11.8))
        if p < 1:
            arrow(ctx, 489, False, "#84b3a4")
        plate(ctx, ctx.lerp(SERVER_X, BROWSER_X, p), 489, "304", GREEN, width=98)
        if p >= 1:
            highlight(ctx, BROWSER_X, GREEN)

    # Changed representation: a large object carrying the actual page returns.
    if 21.5 <= t < 24.2:
        p = ctx.smooth(ctx.seg(t, 21.5, 24.2))
        arrow(ctx, 489, False, "#d6a28d")
        launch = ctx.smooth(ctx.seg(t, 21.5, 22.0))
        x = ctx.lerp(SERVER_X, BROWSER_X, p)
        y = ctx.lerp(352, 489, launch)
        page(ctx, x, y, scale=ctx.lerp(1, 0.52, launch), fresh=True)
        plate(ctx, x, y + 74, "200", ORANGE, width=98)
    elif browser_fresh:
        highlight(ctx, BROWSER_X, ORANGE)
        plate(ctx, BROWSER_X, 489, "200", ORANGE, width=98)


draw_hook = draw
draw_validate = draw
draw_reuse = draw
draw_replace = draw
