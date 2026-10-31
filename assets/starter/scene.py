"""Working CE example: a continuous object, a zoom reveal, then a fixed comparison.

Replace the example's content and geometry for the actual topic. The timeline
and cue helpers can be retained. A cue's audio starts when its actual frame starts.
"""
import json
import os
from pathlib import Path
import hashlib
import math

import numpy as np
import manimpango
from PIL import Image
from manim import *

ROOT = Path(os.environ.get('MANIM_PROJECT', Path(__file__).resolve().parent))
OUT = Path(os.environ.get('MANIM_OUTPUT', str(ROOT / 'out')))
DATA = json.loads((ROOT / 'timeline.json').read_text())
fonts = set(manimpango.list_fonts())
FONT = os.environ.get('MANIM_FONT') or next(
    (f for f in ['PingFang SC', 'Noto Sans CJK SC', 'Microsoft YaHei', 'Heiti SC'] if f in fonts),
    'sans-serif')
BG, INK, GREEN, BLUE, PURPLE = '#F5F6F2', '#29343A', '#397F78', '#486E8F', '#7C6596'
config.background_color = BG


def label(text, size=26, color=INK):
    return Text(text, font=FONT, font_size=size, color=color)


def card(point, text, color=BLUE):
    frame = RoundedRectangle(width=2.4, height=.9, corner_radius=.13,
                             stroke_color=color, fill_color='#FDFEFB', fill_opacity=1)
    return VGroup(frame, label(text, 26, color)).move_to(point)


class Explainer(MovingCameraScene):
    def at(self, when):
        delay = when - self.time
        if delay > .001:
            fps = float(config.frame_rate)
            frames = math.ceil(delay * fps - 1e-8)
            # Cairo freezes int(duration / dt) frames: avoid truncating the
            # requested observation hold, including binary floating-point loss.
            self.wait(frames / fps + 1e-9, frozen_frame=True)

    def start_segment(self, ident):
        self.segment = next(s for s in DATA['scenes'] if s['id'] == ident)
        self.segment_start = self.time
        self.title = self.segment['title']

    def start_cue(self, ident):
        self.cue = next(c for c in self.segment['cues'] if c['id'] == ident)
        self.at(self.segment_start + self.cue['start_s'])
        self.cue_start = self.time
        self.hud_revision += 1
        title = label(self.title, 27, GREEN).move_to([0, 3.35, 0])
        subtitle = label(self.cue['subtitle'], 24).move_to([0, -3.35, 0])
        for text in [title, subtitle]:
            if text.width > 12.8:
                text.scale_to_fit_width(12.8)
        self.hud_base = VGroup(title, subtitle)
        self.hud.update(0)
        cue = dict(id=ident, subtitle=self.cue['subtitle'], start_s=self.time,
                   duration_s=self.cue['duration_s'], audio=self.cue['audio'],
                   audio_sha256=self.cue['audio_sha256'])
        if DATA['narration']:
            path = ROOT / self.cue['audio']
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != self.cue['audio_sha256']:
                raise ValueError(f'{ident}: audio changed after timeline measurement')
            self.add_sound(str(path))
        self.actual['cues'].append(cue)

    def end_cue(self):
        content_budget = max(self.cue['duration_s'], self.cue['action_s'])
        if self.time - self.cue_start > content_budget + 1 / config.frame_rate + .005:
            raise ValueError(f'{self.cue["id"]}: actions overrun content budget and observation time')
        content_end = max(self.time, self.cue_start + self.cue['duration_s'])
        self.at(max(self.cue_start + self.cue['slot_s'], content_end + self.cue['hold_s']))
        self.actual['cues'][-1].update(slot_end_s=self.time,
            observation_s=self.time-content_end, minimum_observation_s=self.cue['hold_s'])

    def end_segment(self):
        self.at(self.segment_start + self.segment['duration_s'])
        self.renderer.update_frame(self, ignore_skipping=True)
        Image.fromarray(self.renderer.get_frame()).save(OUT / f'{self.segment["id"]}.png')

    def construct(self):
        OUT.mkdir(parents=True, exist_ok=True)
        self.actual = dict(schema_version=1, fps=config.frame_rate,
                           narration=DATA['narration'], project_root=str(ROOT), cues=[])
        self.hud = VGroup()
        self.hud_revision = 0
        self.hud_key = None
        self.hud_base = VGroup()
        # No dt argument: this updater needs changes only during camera movement.
        def follow_camera(mob):
            frame = self.camera.frame
            key = (self.hud_revision, tuple(frame.get_center()), frame.width)
            if key != self.hud_key:
                mob.become(self.hud_base.copy().scale(frame.width / (128 / 9),
                    about_point=ORIGIN).shift(frame.get_center()))
                mob.set_z_index(100, family=True)
                self.hud_key = key
        self.hud.add_updater(follow_camera)
        self.add(self.hud)
        self.camera.frame.set(width=4.8).move_to([0, .2, 0])
        self.start_segment('detail')
        self.start_cue('object')
        object_frame = RoundedRectangle(width=2.6, height=1.5, corner_radius=.13,
            stroke_color=BLUE, fill_color='#FDFEFB', fill_opacity=1).move_to([0, .2, 0])
        object_name = label('对象 X', 25, BLUE).move_to([0, .6, 0])
        count = label('引用数：2', 24).move_to([0, -.05, 0])
        self.play(FadeIn(object_frame), FadeIn(object_name), FadeIn(count), run_time=.8)
        self.end_cue()
        self.end_segment()

        self.start_segment('context')
        self.start_cue('references')
        reference_a = card([-4.2, .2, 0], '引用 A', GREEN)
        reference_b = card([4.2, .2, 0], '引用 B', PURPLE)
        arrow_a = Arrow([-2.9, .2, 0], [-1.4, .2, 0], buff=0, color=GREEN)
        arrow_b = Arrow([2.9, .2, 0], [1.4, .2, 0], buff=0, color=PURPLE)
        note = label('简化引用计数示意，省略循环引用', 18).move_to([0, -1.7, 0])
        self.play(self.camera.frame.animate.set(width=128/9).move_to(ORIGIN),
                  FadeIn(reference_a), FadeIn(reference_b),
                  GrowArrow(arrow_a), GrowArrow(arrow_b), FadeIn(note), run_time=1.2)
        self.end_cue()
        self.end_segment()

        self.start_segment('comparison')
        self.start_cue('remove-a')
        new_count = label('引用数：1', 24).move_to(count)
        self.play(FadeOut(reference_a), FadeOut(arrow_a), Transform(count, new_count), run_time=.8)
        self.end_cue()
        self.end_segment()
        self.actual['duration_s'] = self.time
        (OUT / 'actual-timeline.json').write_text(
            json.dumps(self.actual, ensure_ascii=False, indent=2) + '\n')
