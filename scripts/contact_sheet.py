"""Per-cue contact sheet for visual review: before / mid / after frames of every cue.

Usage:
  python3 contact_sheet.py VIDEO --timeline actual-timeline.json --output sheet.png [--cols 3] [--width 480]

Each row is one cue (id + title); columns are frames at 10%, 50%, 90% of the cue.
Look at the image yourself and record: single focus? on-screen words? a visible
visual event between columns? same framing as the previous row?
"""
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def grab(video, t, path, width):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', str(video),
                    '-frames:v', '1', '-vf', f'scale={width}:-2', str(path)], check=True)
    return Image.open(path).convert('RGB')


def font(size):
    for name in ['/System/Library/Fonts/PingFang.ttc', '/System/Library/Fonts/STHeiti Medium.ttc',
                 '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc']:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('video', type=Path)
    p.add_argument('--timeline', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--width', type=int, default=480)
    p.add_argument('--points', default='0.1,0.5,0.9')
    a = p.parse_args()
    cues = json.loads(a.timeline.read_text())['cues']
    points = [float(x) for x in a.points.split(',')]
    label_w, f = 260, font(20)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, c in enumerate(cues):
            start = float(c.get('absolute_start_s', c.get('start_s', 0)))
            length = float(c.get('slot_s') or c.get('duration_s'))
            frames = [grab(a.video, start + length * q, Path(tmp) / f'{i}-{j}.png', a.width)
                      for j, q in enumerate(points)]
            h = frames[0].height
            row = Image.new('RGB', (label_w + a.width * len(frames), h), 'white')
            d = ImageDraw.Draw(row)
            d.multiline_text((10, 10), f"{i + 1}. {c['id']}\n{start:.1f}s +{length:.1f}s\n{c.get('title', '')[:24]}",
                             fill='black', font=f, spacing=6)
            for j, fr in enumerate(frames):
                row.paste(fr, (label_w + j * a.width, 0))
            rows.append(row)
    sheet = Image.new('RGB', (rows[0].width, sum(r.height + 4 for r in rows)), (200, 200, 200))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height + 4
    a.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.output)
    print(json.dumps(dict(output=str(a.output), cues=len(rows), size=sheet.size)))


if __name__ == '__main__':
    main()
