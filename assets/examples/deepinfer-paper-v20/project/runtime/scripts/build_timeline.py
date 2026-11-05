"""Measure prepared audio and allocate explicit action/observation time."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seconds(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f'{label}: expected seconds')
    if not math.isfinite(value) or value < 0:
        raise ValueError(f'{label}: seconds must be finite and nonnegative')
    return float(value)


def measure(path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type',
         '-of', 'json', str(path)], check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    if not any(s['codec_type'] == 'audio' for s in data.get('streams', [])):
        raise ValueError(f'No audio stream: {path}')
    duration = seconds(float(data['format']['duration']), str(path))
    if duration <= 0:
        raise ValueError(f'Empty audio: {path}')
    return duration


def build(plan_path):
    plan_path = Path(plan_path).resolve()
    root = plan_path.parent
    data = json.loads(plan_path.read_text())
    fps = data.get('fps', 30)
    if isinstance(fps, bool) or not isinstance(fps, int) or fps <= 0:
        raise ValueError('fps must be a positive integer')
    if not isinstance(data.get('narration'), bool):
        raise ValueError('narration must explicitly be true or false')
    if not isinstance(data.get('scenes'), list) or not data['scenes']:
        raise ValueError('scenes must be a nonempty list')
    rounded = lambda value: math.ceil((value - 1e-9) * fps) / fps
    names, cue_names, scenes, cursor = set(), set(), [], 0.0
    for scene in data['scenes']:
        ident = scene.get('id')
        if not isinstance(ident, str) or not ident.strip() or ident in names:
            raise ValueError(f'Invalid or duplicate scene id: {ident}')
        names.add(ident)
        if not isinstance(scene.get('cues'), list) or not scene['cues']:
            raise ValueError(f'{ident}: cues must be a nonempty list')
        lead = rounded(seconds(scene.get('lead_s', 0), f'{ident}.lead_s'))
        tail = rounded(seconds(scene.get('tail_s', 0), f'{ident}.tail_s'))
        local, cues = lead, []
        for cue in scene['cues']:
            cid = cue.get('id')
            if not isinstance(cid, str) or not cid.strip() or cid in cue_names:
                raise ValueError(f'Invalid or duplicate cue id: {cid}')
            cue_names.add(cid)
            action = seconds(cue.get('action_s', 0), f'{cid}.action_s')
            hold = seconds(cue.get('hold_s', 0), f'{cid}.hold_s')
            path, digest = None, None
            if data['narration']:
                if not isinstance(cue.get('audio'), str) or not cue['audio']:
                    raise ValueError(f'{cid}: narration requires audio')
                path = (root / cue['audio']).resolve()
                if not path.is_file():
                    raise ValueError(f'{cid}: missing audio: {path}')
                digest = sha256(path)
                locked = cue.get('locked_sha256')
                if locked is not None and locked != digest:
                    raise ValueError(f'{cid}: locked_sha256 mismatch; approved audio changed')
                duration = measure(path)
            else:
                duration = seconds(cue.get('estimated_s', action), f'{cid}.estimated_s')
            if max(duration, action) <= 0:
                raise ValueError(f'{cid}: cue needs a positive exposure or action duration')
            slot = rounded(max(duration, action) + hold)
            cues.append(dict(
                id=cid, spoken_text=cue.get('spoken_text', ''),
                subtitle=cue.get('subtitle', cue.get('spoken_text', '')),
                start_s=round(local, 8), absolute_start_s=round(cursor + local, 8),
                duration_s=duration, action_s=action, hold_s=hold, slot_s=slot,
                audio=cue.get('audio') if path else None, audio_sha256=digest))
            local += slot
        total = rounded(local + tail)
        scenes.append(dict(id=ident, title=scene.get('title', ident), start_s=cursor,
                           duration_s=total, lead_s=lead, tail_s=tail, cues=cues))
        cursor += total
    return dict(schema_version=1, fps=fps, narration=data['narration'],
                voice_profile=data.get('voice_profile'),
                source_plan_sha256=sha256(plan_path), duration_s=cursor, scenes=scenes)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        timeline = build(args.plan)
        target = args.output or args.plan.resolve().parent / 'timeline.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(target.name + '.new')
        temporary.write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + '\n')
        temporary.replace(target)
        print(f'{len(timeline["scenes"])} scenes, '
              f'{sum(len(s["cues"]) for s in timeline["scenes"])} cues, '
              f'{timeline["duration_s"]:.3f}s -> {target}')
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Timeline failed: {error}\n')


if __name__ == '__main__':
    main()
