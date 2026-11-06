"""Pillow frame-by-frame engine for tech-explainer-video (no Manim needed).

A project provides `scenes.py` with:
    STYLE = dict(bg=(r,g,b), ink=(r,g,b), font='/path/to/cjk.ttc')   # optional overrides
    def draw_<scene_id>(ctx): ...      # one function per scene id in project.json
    CAMERA = {scene_id: [(t0, t1, zoom0, zoom1, (cx, cy)), ...]}       # optional, scene-local seconds
    CROSSFADE = {scene_id: seconds}                                     # optional, blend from previous scene

`ctx` gives: ctx.t (scene-local s), ctx.d (ImageDraw), ctx.img, ctx.at('phrase') -> scene-local time
when that phrase starts (pause-aligned to the real WAV), ctx.sfx(t, kind, gain) to place a sound,
and helpers: seg/smooth/ease_out/back/lerp/lerp_c/lerp_r/rr/text/font.

Run:
  python3 pillow_engine.py PROJECT [--draft] [--still 3.5 12] [--only SCENE]
Reads PROJECT/project.json + timeline.json (from build_timeline.py). Writes PROJECT/out/:
  video.mp4 | draft.mp4, stills, actual-timeline.json (same cue fields as timeline.json, flattened),
  subtitles.srt, word-times.json.
Audio: narration WAVs + SFX (assets/sfx/*.wav if present, else synthesized) + optional
project.json "music": {"file": ..., "gain_db": -22}, ducked under speech; loudnorm -16 LUFS.
"""
import argparse
import importlib.util
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SR = 48000
FONT_CANDIDATES = ['/System/Library/Fonts/Hiragino Sans GB.ttc', '/System/Library/Fonts/STHeiti Medium.ttc',
                   '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
                   '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc', 'C:/Windows/Fonts/msyh.ttc']

# ---------------------------------------------------------------- math helpers
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a)) if b > a else float(t >= a)
def smooth(p): return p * p * (3 - 2 * p)
def ease_out(p): return 1 - (1 - p) ** 3
def back(p): return 1 + 2.70158 * (p - 1) ** 3 + 1.70158 * (p - 1) ** 2
def lerp(a, b, p): return a + (b - a) * p
def lerp_c(c1, c2, p): return tuple(int(lerp(a, b, p)) for a, b in zip(c1, c2))
def lerp_r(r1, r2, p): return tuple(lerp(a, b, p) for a, b in zip(r1, r2))


class Fonts:
    def __init__(self, path):
        self.path = path or next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
        if not self.path:
            raise SystemExit('No CJK font found; set STYLE["font"] in scenes.py')
        self.cache = {}

    def __call__(self, size, bold=False):
        key = (size, bold)
        if key not in self.cache:
            try:
                self.cache[key] = ImageFont.truetype(self.path, size, index=1 if bold else 0)
            except OSError:
                self.cache[key] = ImageFont.truetype(self.path, size)
        return self.cache[key]


# ---------------------------------------------------------------- pause-aligned phrase timing
def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def speech_spans(x, win=0.02, floor_db=-40, min_gap=0.14):
    """Return [(start, end)] of voiced spans separated by pauses >= min_gap seconds."""
    n = int(SR * win)
    frames = len(x) // n
    if frames == 0:
        return [(0.0, len(x) / SR)]
    rms = np.sqrt(np.mean(x[:frames * n].reshape(frames, n) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms / (rms.max() + 1e-12))
    on = db > floor_db
    spans, start, quiet = [], None, 0
    for i, v in enumerate(on):
        if v:
            if start is None: start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet * win >= min_gap:
                spans.append((start * win, (i - quiet + 1) * win)); start, quiet = None, 0
    if start is not None:
        spans.append((start * win, (frames - quiet) * win))
    return spans or [(0.0, len(x) / SR)]


CLAUSE = re.compile(r'[，。？！；：、,.?!;:]')


def clause_times(text, wav):
    """Map text clauses (split at punctuation) onto voiced spans; char-proportional inside a clause.
    Returns list of (char_index, seconds) anchor points."""
    x = decode(wav)
    spans = speech_spans(x)
    pieces, pos = [], 0
    for m in CLAUSE.finditer(text):
        if m.end() - pos > 0: pieces.append((pos, m.end()))
        pos = m.end()
    if pos < len(text): pieces.append((pos, len(text)))
    pieces = [p for p in pieces if text[p[0]:p[1]].strip(' ，。？！；：、,.?!;:')]
    total = sum(len(text[a:b]) for a, b in pieces)
    s0, s1 = spans[0][0], spans[-1][1]
    gaps = [((spans[i][1] + spans[i + 1][0]) / 2, spans[i][1], spans[i + 1][0]) for i in range(len(spans) - 1)]
    # clause boundaries: proportional estimate, snapped to the nearest real pause within 0.8 s
    bounds, acc = [s0], 0
    for a, b in pieces[:-1]:
        acc += len(text[a:b]); est = s0 + (s1 - s0) * acc / total
        near = min(gaps, key=lambda g: abs(g[0] - est), default=None)
        bounds.append(near[2] if near and abs(near[0] - est) < 0.8 and near[2] > bounds[-1] else max(est, bounds[-1]))
    bounds.append(s1)
    anchors = []
    for k, (a, b) in enumerate(pieces):
        anchors += [(a, bounds[k]), (b, bounds[k + 1])]
    return anchors


def char_time(anchors, i):
    for (a, s), (b, e) in zip(anchors[::2], anchors[1::2]):
        if a <= i <= b:
            return s + (e - s) * (i - a) / max(1, b - a)
    return anchors[-1][1]


# ---------------------------------------------------------------- sound effects
def synth(kind):
    if kind in ('motion_swish', 'motion_sweep', 'motion_land', 'mouse_down',
                'mouse_up', 'mouse_click', 'keyboard_tap', 'clock_tick', 'clock_tock'):
        from action_sounds import synth_action
        return synth_action(kind, SR)
    n = lambda s: int(SR * s)
    t = lambda s: np.arange(n(s)) / SR
    def env(m, a=0.005, r=0.1):
        tt = np.arange(m) / SR
        return np.minimum(1, tt / a) * np.exp(-tt / r)
    rng = np.random.default_rng(abs(hash(kind)) % 2**32)
    if kind == 'pop':
        tt = t(0.09); return np.sin(2 * np.pi * np.cumsum(900 - 3000 * tt) / SR) * env(len(tt), 0.002, 0.03)
    if kind == 'whoosh':
        x = rng.standard_normal(n(0.5)); return np.convolve(x, np.ones(24) / 24, 'same') * np.hanning(len(x)) * 0.9
    if kind == 'thud':
        tt = t(0.45); return np.sin(2 * np.pi * (70 - 30 * tt) * tt) * env(len(tt), 0.004, 0.14) * 1.4
    if kind == 'buzz':
        tt = t(0.35); return np.sign(np.sin(2 * np.pi * 110 * tt)) * env(len(tt), 0.01, 0.12) * 0.35
    if kind == 'ding':
        tt = t(0.9); return (np.sin(2 * np.pi * 1320 * tt) + 0.4 * np.sin(2 * np.pi * 2640 * tt)) * env(len(tt), 0.002, 0.25) * 0.6
    if kind == 'scan':
        tt = t(1.2); return np.sin(2 * np.pi * (400 + 800 * tt) * tt) * 0.12 * np.hanning(len(tt))
    if kind == 'tick':
        out = np.zeros(n(1.6))
        for k in range(10):
            s = int(k * 0.16 * SR); out[s:s + 400] += rng.standard_normal(400) * env(400, 0.0005, 0.003)
        return out * 0.8
    if kind == 'rise':
        tt = t(1.8); return np.sin(2 * np.pi * (60 + 80 * tt) * tt) * np.minimum(1, tt / 1.6) * 0.5
    m = re.fullmatch(r'note(\d)', kind)
    if m:
        f = [523.25, 587.33, 659.25, 783.99, 880.0][int(m.group(1)) % 5]
        tt = t(0.8); return (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt)) * env(len(tt), 0.003, 0.22) * 0.6
    raise KeyError(f'unknown sfx {kind}; add assets/sfx/{kind}.wav')


def sfx_clip(kind, project):
    for d in (project / 'sfx', SKILL / 'assets' / 'sfx'):
        p = d / f'{kind}.wav'
        if p.exists():
            return decode(p)
    return synth(kind)


# ---------------------------------------------------------------- engine
class Ctx:
    pass


class Engine:
    def __init__(self, project):
        self.root = Path(project).resolve()
        self.plan = json.loads((self.root / 'project.json').read_text())
        self.tl = json.loads((self.root / 'timeline.json').read_text())
        spec = importlib.util.spec_from_file_location('scenes', self.root / 'scenes.py')
        self.mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(self.mod)
        style = getattr(self.mod, 'STYLE', {})
        self.W, self.H = style.get('size', (1920, 1080))
        self.fps = self.tl['fps']
        self.bg = style.get('bg', (17, 24, 48)); self.ink = style.get('ink', (236, 240, 250))
        self.font = Fonts(style.get('font'))
        self.scenes = self.tl['scenes']
        self.plan_cues = {c['id']: c for s in self.plan['scenes'] for c in s['cues']}
        self.camera = getattr(self.mod, 'CAMERA', {})
        self.cross = getattr(self.mod, 'CROSSFADE', {})
        self.sfx = []
        self.words = {}
        for s in self.scenes:
            for c in s['cues']:
                if c.get('audio'):
                    self.words[c['id']] = clause_times(c['spoken_text'], self.root / c['audio'])
        for s in self.scenes:
            if not hasattr(self.mod, 'draw_' + s['id']):
                raise SystemExit(f'scenes.py lacks draw_{s["id"]}')

    # phrase timing ------------------------------------------------------
    def at(self, scene, phrase):
        for c in scene['cues']:
            i = c['spoken_text'].find(phrase)
            if i >= 0:
                if c['id'] in self.words:
                    return c['start_s'] + char_time(self.words[c['id']], i)
                return c['start_s'] + c['duration_s'] * i / len(c['spoken_text'])
        raise KeyError(f'phrase {phrase!r} not in scene {scene["id"]}')

    # drawing ------------------------------------------------------------
    def ctx(self, scene, t, img, collect):
        c = Ctx(); c.t = t; c.img = img; c.d = ImageDraw.Draw(img); c.W, c.H = self.W, self.H
        c.scene = scene; c.duration = scene['duration_s']
        c.at = lambda p: self.at(scene, p)
        c.sfx = (lambda tt, kind, gain=1.0: self.sfx.append((scene['start_s'] + tt, kind, gain))) if collect else (lambda *a, **k: None)
        c.font = self.font
        c.seg, c.smooth, c.ease_out, c.back, c.lerp, c.lerp_c, c.lerp_r, c.clamp = seg, smooth, ease_out, back, lerp, lerp_c, lerp_r, clamp
        c.fade = lambda col, a: lerp_c(self.bg, col, a)
        def rr(rect, fill=None, outline=None, width=0, radius=8):
            x, y, w, h = rect
            if w > 0.5 and h > 0.5:
                c.d.rounded_rectangle([x, y, x + w, y + h], radius=min(radius, w / 2, h / 2), fill=fill, outline=outline, width=width)
        def text(xy, s, size, fill=None, anchor='mm', bold=False):
            c.d.text(xy, s, font=self.font(size, bold), fill=fill or self.ink, anchor=anchor)
        c.rr, c.text = rr, text
        return c

    def draw_scene(self, scene, t, collect=False):
        img = Image.new('RGB', (self.W, self.H), self.bg)
        getattr(self.mod, 'draw_' + scene['id'])(self.ctx(scene, t, img, collect))
        return img

    def frame(self, T):
        i = max(k for k, s in enumerate(self.scenes) if T >= s['start_s'] - 1e-9)
        scene = self.scenes[i]; t = T - scene['start_s']
        img = self.draw_scene(scene, t)
        cf = self.cross.get(scene['id'])
        if cf and t < cf and i > 0:
            prev = self.scenes[i - 1]
            img = Image.blend(self.draw_scene(prev, prev['duration_s'] - 1 / self.fps), img, smooth(t / cf))
        z, center = 1.0, (self.W / 2, self.H / 2)
        for t0, t1, z0, z1, cxy in self.camera.get(scene['id'], []):
            if t >= t0:
                z, center = lerp(z0, z1, smooth(seg(t, t0, t1))), cxy
        if z > 1.001:
            cw, ch = self.W / z, self.H / z
            x0 = clamp(center[0] - cw / 2, 0, self.W - cw); y0 = clamp(center[1] - ch / 2, 0, self.H - ch)
            img = img.resize((self.W, self.H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
        return self.subtitle(img, T)

    def subtitle(self, img, T):
        for s in self.scenes:
            for c in s['cues']:
                if c['absolute_start_s'] <= T < c['absolute_start_s'] + c['duration_s'] + 0.15:
                    line = self.subtitle_text(s, c, T - s['start_s'])
                    d = ImageDraw.Draw(img); f = self.font(44, True)
                    w = d.textlength(line, font=f); y = self.H - 81
                    d.rounded_rectangle([self.W / 2 - w / 2 - 28, y - 37, self.W / 2 + w / 2 + 28, y + 37], radius=14, fill=(8, 12, 26))
                    d.text((self.W / 2, y), line, font=f, fill=(236, 240, 250), anchor='mm')
        return img

    def subtitle_text(self, scene, cue, t):
        """Optional cue["subtitle_parts"] = [{"from": phrase, "text": ...}] switches lines at real pause-aligned times."""
        parts = self.plan_cues.get(cue['id'], {}).get('subtitle_parts')
        if not parts:
            return cue['subtitle']
        line = parts[0]['text']
        for p in parts:
            if t >= self.at(scene, p['from']) - 0.05:
                line = p['text']
        return line

    def collect_sfx(self):
        """Run every scene once at fine steps so draw functions can register sfx via ctx.sfx.
        Draw code should call ctx.sfx only for events; duplicates at the same time/kind are merged."""
        self.sfx = []
        for s in self.scenes:
            self.draw_scene(s, 0.0, collect=True)
        self.sfx = sorted(set((round(a, 3), k, g) for a, k, g in self.sfx))

    # audio --------------------------------------------------------------
    def audio(self, out):
        dur = self.tl['duration_s']; N = int(dur * SR)
        voice = np.zeros(N + SR)
        for s in self.scenes:
            for c in s['cues']:
                if c.get('audio'):
                    v = decode(self.root / c['audio']); i = int(c['absolute_start_s'] * SR); voice[i:i + len(v)] += v
        peak = np.max(np.abs(voice)) or 1.0
        fx = np.zeros_like(voice)
        for at, kind, gain in self.sfx:
            x = sfx_clip(kind, self.root); i = int(at * SR); x = x[:max(0, len(fx) - i)]; fx[i:i + len(x)] += x * gain
        mix = voice + fx * 0.16 * peak
        music = self.plan.get('music') or {}
        if music.get('file'):
            m = decode((self.root / music['file']).resolve())
            m = np.tile(m, int(np.ceil(len(mix) / len(m))))[:len(mix)]
            m = m / (np.max(np.abs(m)) or 1) * peak * 10 ** (music.get('gain_db', -22) / 20)
            env = np.convolve(np.abs(voice) > 0.02 * peak, np.ones(SR // 5) / (SR // 5), 'same')
            m *= 1 - 0.6 * np.clip(env * 3, 0, 1)                       # duck under speech
            fade_n = min(SR * 2, len(m) // 4); m[:fade_n] *= np.linspace(0, 1, fade_n); m[N - fade_n:N] *= np.linspace(1, 0, fade_n)
            mix += m
        mix = mix[:N]; mix = (mix / (np.max(np.abs(mix)) or 1) * 0.9).astype(np.float32)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', str(out)],
                       input=mix.tobytes(), check=True)

    # outputs ------------------------------------------------------------
    def write_meta(self, out):
        cues = []
        for s in self.scenes:
            for c in s['cues']:
                cues.append(dict(c, scene=s['id'], title=s.get('title', s['id'])))
        (out / 'actual-timeline.json').write_text(json.dumps(
            dict(fps=self.fps, duration_s=self.tl['duration_s'], cues=cues, sfx=self.sfx), ensure_ascii=False, indent=1))
        (out / 'word-times.json').write_text(json.dumps(self.words, ensure_ascii=False))
        ts = lambda x: f'{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{int(x % 60):02d},{int(round(x % 1 * 1000)) % 1000:03d}'
        (out / 'subtitles.srt').write_text(''.join(
            f"{i + 1}\n{ts(c['absolute_start_s'])} --> {ts(c['absolute_start_s'] + c['duration_s'])}\n{c['subtitle']}\n\n"
            for i, c in enumerate(cues)))

    def render(self, draft=False, only=None):
        out = self.root / 'out'; out.mkdir(exist_ok=True)
        self.collect_sfx()
        fps = 15 if draft else self.fps
        size = (self.W // 2, self.H // 2) if draft else (self.W, self.H)
        t0, t1 = 0.0, self.tl['duration_s']
        if only:
            s = next(x for x in self.scenes if x['id'] == only); t0, t1 = s['start_s'], s['start_s'] + s['duration_s']
        wav = out / 'mix.wav'; self.audio(wav)
        name = out / (f'scene-{only}.mp4' if only else 'draft.mp4' if draft else 'video.mp4')
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{size[0]}x{size[1]}',
                               '-r', str(fps), '-i', '-', '-ss', f'{t0:.3f}', '-t', f'{t1 - t0:.3f}', '-i', str(wav),
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                               '-c:a', 'aac', '-b:a', '192k', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-shortest', str(name)],
                              stdin=subprocess.PIPE)
        for k in range(int(round((t1 - t0) * fps))):
            T = t0 + k / fps
            img = self.frame(T)
            if draft: img = img.resize(size, Image.BILINEAR)
            ff.stdin.write(img.tobytes())
            if k % (fps * 10) == 0: print(f'{T:.0f}s', file=sys.stderr, flush=True)
        ff.stdin.close()
        if ff.wait(): raise SystemExit('ffmpeg failed')
        self.write_meta(out)
        print(name)

    def stills(self, times):
        out = self.root / 'out'; out.mkdir(exist_ok=True)
        for T in times:
            p = out / f'still-{T:06.2f}.png'; self.frame(T).save(p); print(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('project', type=Path)
    ap.add_argument('--draft', action='store_true', help='half size, 15 fps')
    ap.add_argument('--still', type=float, nargs='+', help='write PNG stills at these absolute seconds')
    ap.add_argument('--only', help='render a single scene id')
    a = ap.parse_args()
    e = Engine(a.project)
    if a.still:
        e.stills(a.still)
    else:
        e.render(a.draft, a.only)


if __name__ == '__main__':
    main()
