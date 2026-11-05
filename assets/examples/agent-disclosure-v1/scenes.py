"""Agent 渐进式披露 · 分镜绘制（由 tech-explainer-video/scripts/pillow_engine.py 驱动）。"""
import math
import random

STYLE = dict(bg=(17, 24, 48), ink=(236, 240, 250))
BG = (17, 24, 48); BG2 = (24, 34, 66)
INK = (236, 240, 250); MUTED = (128, 142, 180); DARK = (16, 24, 44)
ORANGE = (255, 166, 48); ORANGE2 = (255, 128, 64); ORANGE3 = (255, 196, 92)
CYAN = (64, 214, 230); RED = (255, 82, 92); GREEN = (96, 220, 140)
WINDOW_LINE = (110, 130, 190)

CAMERA = {'pain': [(0.2, 1.4, 1.0, 1.14, (1180, 470))],
          'level1': [(0.0, 1.0, 1.14, 1.0, (1180, 470)), (3.6, 4.4, 1.0, 1.0, (960, 540))]}
CROSSFADE = {'compare': 0.5}

WX0, WY0, WX1, WY1 = 1080, 150, 1720, 880
IX0, IY0, IX1, IY1 = WX0 + 16, WY0 + 16, WX1 - 16, WY1 - 16
rng = random.Random(7)
BOOK_COL = [tuple(int(a + (b - a) * rng.random() * 0.8) for a, b in zip(ORANGE, ORANGE2)) for _ in range(100)]
TAG_W = (IX1 - IX0 - 9 * 6) / 10
PICK = 47
BODY = (IX0 + 24, WY0 + 150, IX1 - IX0 - 48, 300)
QCARD = (IX0 + 24, WY0 + 40, IX1 - IX0 - 48, 80)
DOC_IN = (IX0 + 24, 640, 280, 84)
RES_IN = (IX1 - 24 - 280, 640, 280, 84)


def shelf_rect(i):
    r, c = divmod(i, 10); return (190 + c * 66, 200 + r * 64, 46, 54)
def strip_rect(i): return (IX0, IY1 - (i + 1) * 8.2, IX1 - IX0, 6.6)
def tag_rect(i):
    r, c = divmod(i, 10); return (IX0 + c * (TAG_W + 6), IY1 - 70 + r * 7, TAG_W, 4.5)


def fly(x, r1, r2, p, arc=140):
    r = x.lerp_r(r1, r2, x.smooth(p))
    return (r[0], r[1] - math.sin(math.pi * p) * arc, r[2], r[3])


def book(x, rect, col, morph=0.0):
    bx, by, w, h = rect
    x.rr(rect, fill=col, radius=x.lerp(6, 2, morph))
    if morph < 0.6 and w > 20:
        a = 1 - morph / 0.6
        x.d.line([bx + 8, by + 4, bx + 8, by + h - 4], fill=x.lerp_c(col, (120, 60, 20), 0.5 * a), width=max(2, int(w / 15)))
        for k in range(3):
            yy = by + h * (0.3 + 0.18 * k)
            x.d.line([bx + w * 0.35, yy, bx + w - w * 0.17, yy], fill=x.lerp_c(col, (255, 240, 210), 0.6 * a), width=max(2, int(w / 23)))


def window(x, alarm=0.0, shake=0.0):
    dx = math.sin(x.t * 60) * 6 * shake
    col = x.lerp_c(WINDOW_LINE, RED, alarm)
    x.d.rounded_rectangle([WX0 + dx, WY0, WX1 + dx, WY1], radius=22, fill=BG2, outline=col, width=5)
    return dx


def window_label(x, alarm=0.0, shake=0.0):
    dx = math.sin(x.t * 60) * 6 * shake
    x.d.rounded_rectangle([WX0 + dx, WY0, WX1 + dx, WY1], radius=22, outline=x.lerp_c(WINDOW_LINE, RED, alarm), width=5)
    cx = (WX0 + WX1) / 2 + dx
    x.d.rounded_rectangle([cx - 130, WY0 - 76, cx + 130, WY0 - 16], radius=14, fill=BG)
    x.text((cx, WY0 - 46), '上下文窗口', 38, x.lerp_c(MUTED, RED, alarm), bold=True)


def full_stack(x, shake):
    dx = math.sin(x.t * 60) * 6 * shake
    for i in range(100):
        bx, by, w, h = strip_rect(i); book(x, (bx + dx, by, w, h), BOOK_COL[i], 1)


def card(x, rect, label, col, squash=0.0, grey=0.0):
    bx, by, w, h = rect
    if squash:
        cx, cy = bx + w / 2, by + h / 2; w, h = w * (1 + 0.25 * squash), h * (1 - 0.45 * squash); bx, by = cx - w / 2, cy - h / 2
    x.rr((bx, by, w, h), fill=x.lerp_c(col, (90, 100, 125), grey), radius=16)
    x.text((bx + w / 2, by + h / 2), label, int(36 * (1 - 0.3 * squash)), DARK, bold=True)


# ---------------------------------------------------------------- 1 hook: flash-forward, rewind, then fill
def draw_hook(x):
    t = x.t; T_fly = x.at('一股脑')
    x.sfx(0.0, 'thud', 0.9); x.sfx(1.0, 'whoosh', 0.6); x.sfx(T_fly, 'whoosh', 0.9); x.sfx(T_fly + 3.0, 'thud', 1.0)
    rewind = x.seg(t, 1.0, 1.8)                     # 0..1.0 s: show the disaster first
    if rewind < 1:
        window(x, 1 - rewind, 1 - rewind)
        for i in range(100):
            q = x.seg(rewind, i * 0.004, i * 0.004 + 0.6)
            r = fly(x, strip_rect(i), shelf_rect(i), q, -80) if q > 0 else strip_rect(i)
            dx = math.sin(t * 60) * 6 * (1 - rewind)
            book(x, (r[0] + dx * (q == 0), r[1], r[2], r[3]), BOOK_COL[i], 1 - q)
        window_label(x, 1 - rewind, 1 - rewind)
        if rewind == 0:
            x.text((540, 500), '会这样吗？', 64, RED, bold=True)
        return
    window(x)
    landed = 0
    for i in range(100):
        f0 = T_fly + i * 0.026; p = x.seg(t, f0, f0 + 0.75); landed += p >= 1
        book(x, fly(x, shelf_rect(i), strip_rect(i), p, 160) if p > 0 else shelf_rect(i), BOOK_COL[i], p)
    alarm = x.seg(landed, 80, 100)
    window_label(x, alarm, alarm * (1 - x.seg(t, T_fly + 4.0, T_fly + 5.0)))
    a = x.seg(t, 1.9, 2.4) * (1 - x.seg(t, T_fly, T_fly + 0.3))
    if a: x.text((510, 880), '技能说明书 ×100', 48, x.fade(INK, a), bold=True)


# ---------------------------------------------------------------- 2 pain
def draw_pain(x):
    t = x.t; T_grey = x.at('又贵又慢')
    x.sfx(1.5, 'thud', 0.8); x.sfx(T_grey, 'buzz', 0.5)
    window(x, 1.0, 0.3); full_stack(x, 0.3); window_label(x, 1.0, 0.3)
    p = x.seg(t, 0.4, 1.5); bx = x.lerp(-420, WX0 - 400, x.ease_out(p))
    b = x.seg(t, 1.5, 2.1); bx -= math.sin(math.pi * b) * 90 if b < 1 else 0
    grey = x.seg(t, T_grey, T_grey + 1.0)
    card(x, (bx, 460, 380, 96), '你的问题', CYAN, squash=math.sin(math.pi * x.seg(t, 1.5, 1.75)), grey=grey)
    if grey: x.text((bx + 190, 610), '挤不进去', 48, x.fade(RED, grey), bold=True)


# ---------------------------------------------------------------- 3 level1: one book close-up, then all 100
DEMO = (330, 230, 380, 450)            # close-up book
DEMO_TAG = (140, 470, 760, 74)         # its one-line summary
def draw_level1(x):
    t = x.t
    T_one = x.at('每个技能只留'); T_name = x.at('名字加用途'); T_all = x.at('一百个技能')
    x.sfx(0.3, 'whoosh', 0.6); x.sfx(T_one, 'pop', 0.6); x.sfx(T_name, 'ding', 0.5)
    for k in range(10): x.sfx(T_all + k * 0.12, 'pop', 0.3)
    x.sfx(x.at('一小条'), 'ding', 0.4)
    focus = x.seg(t, T_one - 0.4, T_one) * (1 - x.seg(t, T_all - 0.3, T_all))   # dim the rest during close-up
    alarm = 1 - x.seg(t, 0.8, 1.6)
    window(x, alarm)
    for i in range(100):
        pb = x.seg(t, 0.3 + i * 0.012, 1.0 + i * 0.012)
        pt = x.seg(t, T_all + (i % 10) * 0.05 + (i // 10) * 0.03, T_all + 0.9 + (i % 10) * 0.05 + (i // 10) * 0.03)
        if pt > 0:
            r = fly(x, shelf_rect(i), tag_rect(i), pt, 120); m = pt
        else:
            r = fly(x, strip_rect(i), shelf_rect(i), pb, -60); m = 1 - pb
        col = BOOK_COL[i] if pt < 1 else ORANGE3
        book(x, r, x.lerp_c(col, BG, 0.75 * focus), m)
    if alarm > 0: window_label(x, alarm)
    else:
        x.d.rounded_rectangle([(WX0 + WX1) / 2 - 130, WY0 - 76, (WX0 + WX1) / 2 + 130, WY0 - 16], radius=14, fill=BG)
        x.text(((WX0 + WX1) / 2, WY0 - 46), '上下文窗口', 38, x.fade(MUTED, 1 - 0.75 * focus), bold=True)
    g = 1 - x.seg(t, 0, 0.5)
    if g: card(x, (WX0 - 400, 460, 380, 96), '你的问题', CYAN, grey=1)
    # close-up: one book slowly flattens into a single summary line
    if focus > 0:
        a = x.seg(t, T_one - 0.4, T_one + 0.2) * (1 - x.seg(t, T_all - 0.3, T_all))
        m = x.seg(t, T_one + 0.6, T_name)
        r = x.lerp_r(DEMO, DEMO_TAG, x.smooth(m))
        book(x, r, x.lerp_c(BG, x.lerp_c(ORANGE, ORANGE3, m), a), m)
        if m >= 1:
            x.text((r[0] + 40, r[1] + r[3] / 2), 'pdf：处理 PDF、提取表格', 38, x.fade(DARK, a), anchor='lm', bold=True)
            g = a * x.seg(t, T_name, T_name + 0.4)
            if g:
                x.rr((300, 580, 440, 76), fill=x.fade(BG, g), radius=16)
                x.text((520, 618), '只留：名字 + 用途', 44, x.fade(INK, g), bold=True)
        else:
            x.text((520, 730), '一本完整说明书', 40, x.fade(MUTED, a * (1 - m)))
    lab = x.seg(t, x.at('一小条'), x.at('一小条') + 0.5)
    if lab:
        x.text(((IX0 + IX1) / 2, IY1 - 100), '简介 ×100', 40, x.fade(ORANGE3, lab), bold=True)
        x.text(((IX0 + IX1) / 2, (IY0 + IY1 - 120) / 2), '大片空间留给真正的任务', 42, x.fade(MUTED, lab))


# ---------------------------------------------------------------- 4 level2
def tags(x, dim=0.0, flash_x=None, glow=0.0, hide=False):
    for i in range(100):
        if i == PICK and hide: continue
        bx, by, w, h = tag_rect(i); col = ORANGE3
        if i == PICK and glow: col = x.lerp_c(ORANGE3, (255, 240, 120), glow)
        elif dim: col = x.lerp_c(ORANGE3, BG2, dim * 0.7)
        if flash_x is not None and abs(bx + w / 2 - flash_x) < 40: col = (255, 255, 255)
        x.rr((bx, by, w, h), fill=col, radius=2)


def body_lines(x, a=1.0, grow=None):
    for k in range(5):
        b = 1 if grow is None else grow(k)
        L = (BODY[2] - 90) * b * (0.6 + 0.4 * ((k * 37) % 5) / 5)
        x.d.line([BODY[0] + 30, BODY[1] + 100 + k * 36, BODY[0] + 30 + L, BODY[1] + 100 + k * 36], fill=x.fade(ORANGE, 0.55 * a), width=10)


def draw_level2(x):
    t = x.t
    T_q, T_scan, T_hit, T_open = x.at('比如你说'), x.at('Agent 对着'), x.at('只有 PDF'), x.at('这时才把')
    x.sfx(T_q, 'whoosh', 0.5); x.sfx(T_scan, 'scan', 0.5); x.sfx(T_hit, 'ding', 0.8); x.sfx(T_open, 'whoosh', 0.5)
    window(x); window_label(x)
    q = x.seg(t, T_q, T_q + 0.7)
    ps = x.seg(t, T_scan, T_scan + 1.4); flash = x.lerp(IX0, IX1, ps) if 0 < ps < 1 else None
    hit = x.seg(t, T_hit, T_hit + 0.3); op = x.seg(t, T_open, T_open + 0.9)
    tags(x, dim=hit, flash_x=flash, glow=hit, hide=op > 0)
    if flash is not None: x.d.line([flash, IY1 - 84, flash, IY1 + 4], fill=CYAN, width=4)
    if hit and op == 0:
        bx, by, w, h = tag_rect(PICK)
        x.d.ellipse([bx + w / 2 - 40, by - 40, bx + w / 2 + 40, by + 40], outline=(255, 240, 120), width=4)
        x.text((bx + w / 2, by - 70), 'pdf', 40, (255, 240, 120), bold=True)
    if op > 0:
        r = x.lerp_r(tag_rect(PICK), BODY, x.back(op) if op < 1 else 1)
        x.rr(r, fill=x.lerp_c((255, 240, 120), (70, 52, 30), x.seg(op, 0.3, 1)), outline=ORANGE, width=4, radius=14)
        a = x.seg(t, T_open + 0.7, T_open + 1.3)
        if a:
            x.text((BODY[0] + 30, BODY[1] + 44), 'PDF 技能 · 完整说明', 36, x.fade(ORANGE3, a), anchor='lm', bold=True)
            body_lines(x, 1, lambda k: x.seg(t, T_open + 0.9 + k * 0.15, T_open + 1.2 + k * 0.15))
    if q > 0:
        card(x, x.lerp_r((-600, QCARD[1], QCARD[2], QCARD[3]), QCARD, x.ease_out(q)), '把这份 PDF 转成表格', CYAN)
        if q >= 1 and t < T_scan:
            x.text((QCARD[0] - 30, QCARD[1] + 40), '你的问题 →', 36, CYAN, anchor='rm', bold=True)


# ---------------------------------------------------------------- 5 level3
def doc_icon(x, rect, name, a=1.0):
    bx, by, w, h = rect
    x.rr(rect, fill=x.fade((230, 236, 250), a), radius=10)
    if name: x.text((bx + w / 2, by + h / 2), name, 32, x.lerp_c(BG, DARK, a), bold=True)


def gear(x, cx, cy, r, ang, col):
    pts = []
    for k in range(16):
        a = ang + k * math.pi / 8; rad = r if k % 2 == 0 else r * 0.78
        pts += [(cx + rad * math.cos(a + d), cy + rad * math.sin(a + d)) for d in (-0.12, 0.12)]
    x.d.polygon(pts, fill=col); x.d.ellipse([cx - r * 0.32, cy - r * 0.32, cx + r * 0.32, cy + r * 0.32], fill=BG)


def draw_level3(x):
    t = x.t; T_doc, T_run, T_res = x.at('用到哪份'), x.at('脚本更省'), x.at('只把结果')
    x.sfx(0.2, 'pop', 0.5); x.sfx(0.5, 'pop', 0.5); x.sfx(T_doc, 'whoosh', 0.5); x.sfx(T_run + 0.6, 'thud', 0.6); x.sfx(T_run + 1.3, 'tick', 0.6); x.sfx(T_res, 'ding', 0.6)
    window(x); window_label(x); tags(x, dim=1.0, hide=True)
    x.rr(BODY, fill=(70, 52, 30), outline=ORANGE, width=4, radius=14)
    x.text((BODY[0] + 30, BODY[1] + 44), 'PDF 技能 · 完整说明', 36, ORANGE3, anchor='lm', bold=True); body_lines(x)
    card(x, QCARD, '把这份 PDF 转成表格', CYAN)
    a1 = x.back(x.seg(t, 0.2, 0.6)); a2 = x.back(x.seg(t, 0.5, 0.9))
    x.text((450, 120), '技能附带的文件', 36, x.fade(MUTED, x.seg(t, 0.2, 0.6)), bold=True)
    if a1 > 0:
        doc_icon(x, (330, 210, 240 * a1, 84), 'reference.md' if a1 > 0.6 else '', 0.55)
        u = x.seg(t, T_doc + 0.9, T_doc + 1.4)
        if u: x.text((450, 330), '这次用不到 · 不读', 36, x.fade(MUTED, u))
        pd = x.seg(t, T_doc, T_doc + 0.9)
        doc_icon(x, fly(x, (330, 400, 240 * a1, 84), DOC_IN, pd, 120), 'forms.md' if a1 > 0.6 else '')
        if pd >= 1: x.text((DOC_IN[0] + DOC_IN[2] / 2, DOC_IN[1] + DOC_IN[3] + 34), '用到了 · 读入', 32, ORANGE3, bold=True)
    if a2 > 0:
        sx, sy = 290, 580
        x.rr((sx, sy, 320 * a2, 220), fill=(32, 46, 84), outline=GREEN, width=3, radius=14)
        if a2 > 0.8:
            x.text((sx + 160, sy + 30), 'fill.py', 32, GREEN, bold=True)
            # the code itself: a tall block of lines that would be expensive to load
            for k in range(6):
                x.d.line([sx + 30, sy + 70 + k * 18, sx + 180 + (k * 47) % 90, sy + 70 + k * 18], fill=(70, 100, 120), width=8)
            gear(x, sx + 250, sy + 150, 44, x.seg(t, T_run + 1.3, T_res) * 9 + x.seg(t, T_res, T_res + 1) * 2, GREEN)
        # visible event: the code tries to enter the window and is bounced back
        tr = x.seg(t, T_run, T_run + 1.2)
        if 0 < tr < 1:
            go = x.smooth(x.seg(tr, 0, 0.5)); back_ = x.smooth(x.seg(tr, 0.55, 1))
            cx = x.lerp(sx + 30, WX0 - 210, go) - (WX0 - 240 - sx) * back_
            for k in range(6):
                x.d.line([cx, sy + 70 + k * 18, cx + 170, sy + 70 + k * 18], fill=(120, 160, 190), width=8)
        if tr > 0.45:
            stop = x.seg(tr, 0.45, 0.6) * (1 - x.seg(t, T_res, T_res + 0.4))
            if stop:
                x.d.line([WX0 - 18, sy - 10, WX0 - 18, sy + 230], fill=x.fade(RED, stop), width=8)
                x.text((WX0 - 120, sy - 40), '代码不进窗口', 40, x.fade(RED, stop), bold=True)
    pr = x.seg(t, T_res, T_res + 0.9)
    if pr > 0:
        r = fly(x, (500, 660, 120, 60), RES_IN, pr, 160); x.rr(r, fill=GREEN, radius=12)
        if pr > 0.7: x.text((r[0] + r[2] / 2, r[1] + r[3] / 2), '运行结果', 32, DARK, bold=True)
        if pr >= 1: x.text((RES_IN[0] + RES_IN[2] / 2, RES_IN[1] + RES_IN[3] + 34), '只带回结果', 32, GREEN, bold=True)


# ---------------------------------------------------------------- 6 compare (climax)
CL = (300, 230, 520, 600); CR = (1100, 230, 520, 600)
def right_layers(x, rect, lv):
    bx, by, w, h = rect
    base = by + h - 12
    return [((bx + 14, base - 60 * lv, w - 28, 60 * lv), ORANGE3, '简介'),
            ((bx + 14, base - 130 * lv, w - 28, 62 * lv), ORANGE, '正文'),
            ((bx + 14, base - 170 * lv, w - 28, 32 * lv), GREEN, '文件')]


def draw_compare(x):
    t = x.t; T_all, T_need = x.at('全部加载'), x.at('按需加载')
    x.sfx(T_all, 'rise', 0.6); x.sfx(T_all + 1.75, 'thud', 1.0); x.sfx(T_need + 0.3, 'pop', 0.6)
    pa = x.seg(t, T_all, T_all + 2.0); pn = x.seg(t, T_need, T_need + 1.4); burst = x.seg(pa, 0.86, 1.0)
    shake = burst * (1 - x.seg(t, T_all + 2.0, T_all + 3.5))
    for (bx, by, w, h), lab, al in ((CL, '全部加载', burst), (CR, '按需加载', 0)):
        dx = math.sin(t * 60) * 8 * shake * (lab == '全部加载')
        x.d.rounded_rectangle([bx + dx, by, bx + w + dx, by + h], radius=22, fill=BG2, outline=x.lerp_c(WINDOW_LINE, RED, al), width=5)
        x.text((bx + w / 2, by + h + 50), lab, 44, x.lerp_c(INK, RED, al), bold=True)
    bx, by, w, h = CL; dx = math.sin(t * 60) * 8 * shake
    for k in range(int(x.ease_out(pa) * 1.18 * (h - 24) / 9)):
        x.rr((bx + 14 + dx, by + h - 12 - (k + 1) * 9, w - 28, 7), fill=BOOK_COL[k % 100], radius=2)
    for r, col, _ in right_layers(x, CR, x.ease_out(pn)): x.rr(r, fill=col, radius=6)
    if pn >= 1: x.text((CR[0] + CR[2] / 2, CR[1] + 240), '还剩大量空间', 48, x.fade(INK, x.seg(t, T_need + 1.4, T_need + 2.0)), bold=True)
    x.text((1840, 70), '示意', 36, MUTED, anchor='rm')


# ---------------------------------------------------------------- 7 recap: the right window becomes a book's three parts
STEPS = [((260, 600, 420, 220), '目录', '简介', ORANGE3), ((750, 460, 420, 360), '章节', '正文', ORANGE),
         ((1240, 320, 420, 500), '附录', '文件 · 脚本', GREEN)]
def draw_recap(x):
    t = x.t
    times = [x.at('先看目录'), x.at('再翻到'), x.at('最后才查')]; T_take = x.at('所以写技能时')
    for i, tt in enumerate(times): x.sfx(tt, f'note{i}', 0.6)
    x.sfx(T_take, 'ding', 0.5)
    m = x.seg(t, 0.2, 1.4)                                   # morph: window layers -> three steps
    frame_a = 1 - x.seg(t, 0.2, 0.8)
    if frame_a:
        bx, by, w, h = CR
        x.d.rounded_rectangle([bx, by, bx + w, by + h], radius=22, outline=x.fade(WINDOW_LINE, frame_a), width=5)
        x.text((bx + w / 2, by + h + 50), '按需加载', 44, x.fade(INK, frame_a), bold=True)
    # book spine appears behind the steps
    sp = x.seg(t, 0.8, 1.6)
    if sp:
        x.rr((200, 860 - 40, 1520, 18), fill=x.fade((90, 70, 50), sp), radius=8)
        x.text((960, 230), '一本厚书', 44, x.fade(MUTED, sp * (1 - x.seg(t, T_take - 0.2, T_take + 0.3))), bold=True)
    src = right_layers(x, CR, 1.0)
    for k, ((rect, top, sub, col), (r0, _, _)) in enumerate(zip(STEPS, src)):
        r = x.lerp_r(r0, rect, x.smooth(m))
        lit = x.seg(t, times[k], times[k] + 0.4)
        c = x.lerp_c(x.lerp_c(col, (52, 66, 108), 0.7 * m), col, lit)
        x.rr(r, fill=c, radius=x.lerp(6, 18, m))
        if m >= 1:
            x.text((r[0] + r[2] / 2, r[1] + 60), top, 58, x.lerp_c(INK, DARK, lit), bold=True)
            x.text((r[0] + r[2] / 2, r[1] + 126), sub, 38, x.lerp_c(MUTED, (40, 40, 60), lit), bold=True)
    pos = [(470, 580), (960, 440), (1450, 300)]
    k = sum(t >= tt for tt in times) - 1
    if k >= 0:
        p = x.seg(t, times[k], times[k] + 0.5)
        x0, y0 = pos[k - 1] if k > 0 else (120, 580); x1, y1 = pos[k]
        cx = x.lerp(x0, x1, x.smooth(p)); cy = x.lerp(y0, y1, x.smooth(p)) - math.sin(math.pi * p) * 120
        x.d.ellipse([cx - 22, cy - 44, cx + 22, cy], fill=CYAN)
    g = x.seg(t, T_take, T_take + 0.6)
    if g:
        x.rr((360, 110, 1200, 150), fill=x.fade((32, 46, 84), g), radius=20)
        x.text((960, 160), '写技能时：简介写清“什么时候用”', 46, x.fade(INK, g), bold=True)
        x.text((960, 220), '细节放进正文和文件', 40, x.fade(ORANGE3, g), bold=True)
