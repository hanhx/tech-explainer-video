"""Check renderer-exported rectangles at actual sampled times; standard library only.

Input: {"frames": [{"scene_id": "s1", "time_s": 1.2,
 "viewport": [0, 0, 1920, 1080],
 "elements": [{"id": "card", "box": [100, 100, 300, 80], "padding": 8},
              {"id": "label", "box": [112, 112, 90, 20], "parent": "card"}],
 "avoid_overlap": [["label", "moving-message"]]}]}.
All rectangles are [x,y,width,height] in the SAME coordinate space after camera
transforms. Export only visible elements; omit intentionally off-screen parts.
Declare collision pairs for labels/values and moving objects/important text.
This checks supplied samples, not all frames, semantics or visual quality.
"""
import argparse
import json
import math
import os
from pathlib import Path
import tempfile


def number(value, label, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label}: expected a finite number')
    if nonnegative and value < 0:
        raise ValueError(f'{label}: must be nonnegative')
    return value


def rect(value, label):
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError(f'{label}: expected [x,y,width,height]')
    x, y, w, h = [number(v, label) for v in value]
    if w <= 0 or h <= 0:
        raise ValueError(f'{label}: width and height must be positive')
    return x, y, x + w, y + h


def fits(inner, outer, padding, tolerance):
    return (inner[0] >= outer[0] + padding - tolerance
            and inner[1] >= outer[1] + padding - tolerance
            and inner[2] <= outer[2] - padding + tolerance
            and inner[3] <= outer[3] - padding + tolerance)


def check(data, tolerance=.5):
    number(tolerance, 'tolerance', True)
    frames = data.get('frames')
    if not isinstance(frames, list) or not frames:
        raise ValueError('frames must be a non-empty list of actual layout samples')
    violations, seen = [], set()
    elements_checked = pairs_checked = 0
    for index, frame in enumerate(frames):
        sid = frame.get('scene_id')
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError(f'frame {index}: missing scene_id')
        sec = number(frame.get('time_s'), f'{sid}.time_s', True)
        if (sid, sec) in seen:
            raise ValueError(f'{sid}@{sec}: duplicate sample')
        seen.add((sid, sec))
        viewport = rect(frame.get('viewport'), f'{sid}.viewport')
        items = frame.get('elements')
        if not isinstance(items, list) or not items:
            raise ValueError(f'{sid}: elements must be non-empty')
        nodes, boxes = {}, {}
        for node in items:
            ident = node.get('id')
            if not isinstance(ident, str) or not ident.strip() or ident in nodes:
                raise ValueError(f'{sid}: invalid or duplicate element id: {ident}')
            nodes[ident] = node
            boxes[ident] = rect(node.get('box'), f'{sid}.{ident}')
            number(node.get('padding', 0), f'{sid}.{ident}.padding', True)
        context = dict(scene_id=sid, time_s=sec)
        for ident, node in nodes.items():
            elements_checked += 1
            if not fits(boxes[ident], viewport, 0, tolerance):
                violations.append(dict(**context, kind='outside_viewport', element=ident))
            if node.get('parent') is not None:
                parent = node['parent']
                if parent not in nodes or parent == ident:
                    raise ValueError(f'{sid}.{ident}: invalid parent {parent}')
                if not fits(boxes[ident], boxes[parent], nodes[parent].get('padding', 0), tolerance):
                    violations.append(dict(**context, kind='outside_parent', element=ident, parent=parent))
        pairs = frame.get('avoid_overlap', [])
        if not isinstance(pairs, list):
            raise ValueError(f'{sid}: avoid_overlap must be a list')
        for pair in pairs:
            if not isinstance(pair, list) or len(pair) != 2 or pair[0] == pair[1]:
                raise ValueError(f'{sid}: collision constraints require two different element ids')
            if any(ident not in nodes for ident in pair):
                raise ValueError(f'{sid}: collision pair references a missing element: {pair}')
            a, b = [boxes[ident] for ident in pair]
            pairs_checked += 1
            if min(a[2], b[2]) - max(a[0], b[0]) > tolerance and min(a[3], b[3]) - max(a[1], b[1]) > tolerance:
                violations.append(dict(**context, kind='overlap', elements=pair))
    return dict(passed=not violations, frames_checked=len(frames), elements_checked=elements_checked,
                pairs_checked=pairs_checked, violations=violations,
                scope='Only supplied visible geometry samples and declared pairs; not all-frame, visual or human review')


def write_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', dir=path.parent, encoding='utf-8', delete=False) as out:
        json.dump(report, out, ensure_ascii=False, indent=2)
        out.write('\n')
    os.replace(out.name, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('samples', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--tolerance', type=float, default=.5)
    args = parser.parse_args()
    try:
        report = check(json.loads(args.samples.read_text()), args.tolerance)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        report = dict(passed=False, error=str(error), scope='Invalid layout input; no successful review')
    write_report(args.output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
