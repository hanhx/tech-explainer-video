"""Review gate: block the full render until every shot passes the picture-only recap test.

Record the zero-context recap result (visual-craft.md §9) in PROJECT/review.json:
  {"round": 2, "contact_sheet": "out/contact.png",
   "shots": {"hook": "半懂", "pain": "懂", "level3": "不懂", ...},
   "notes": {"level3": "脚本在窗外运行只靠文字"}}

  python3 review_gate.py PROJECT            # exit 1 if any shot is 不懂 / missing, or the sheet is stale

Rules: every cue id in timeline.json must have a verdict; 不懂 blocks; the contact sheet must be
newer than scenes.py and timeline.json (i.e. the verdict is about the current draft).
Passing this gate is not proof that viewers understand; only real viewers can say that.
"""
import argparse
import json
import sys
from pathlib import Path

OK = {'懂', '半懂'}


def check(root):
    root = Path(root).resolve()
    problems = []
    path = root / 'review.json'
    if not path.exists():
        return [f'missing {path.name}: run the recap test on the current contact sheet first']
    review = json.loads(path.read_text())
    tl = json.loads((root / 'timeline.json').read_text())
    ids = [c['id'] for s in tl['scenes'] for c in s['cues']]
    shots = review.get('shots', {})
    for i in ids:
        v = shots.get(i)
        if v is None:
            problems.append(f'{i}: no verdict')
        elif v not in OK:
            problems.append(f'{i}: {v} - {review.get("notes", {}).get(i, "fix the picture, not the wording")}')
    sheet = root / review.get('contact_sheet', 'out/contact.png')
    if not sheet.exists():
        problems.append(f'contact sheet not found: {sheet}')
    else:
        for src in ('scenes.py', 'timeline.json'):
            p = root / src
            if p.exists() and p.stat().st_mtime > sheet.stat().st_mtime:
                problems.append(f'{src} changed after the contact sheet; re-render the draft and re-test')
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('project', type=Path)
    a = ap.parse_args()
    problems = check(a.project)
    if problems:
        print('REVIEW GATE: BLOCKED'); [print('  -', p) for p in problems]; sys.exit(1)
    print('REVIEW GATE: passed (picture-only recap has no 不懂 shots)')


if __name__ == '__main__':
    main()
