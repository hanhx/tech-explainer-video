"""Read-only PCM RMS edge/gap screening; not VAD, ASR, or automatic trimming."""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import sys
import wave


def inspect_wav(path, threshold_dbfs=-38., window_ms=10.):
    if not math.isfinite(threshold_dbfs) or not -100 <= threshold_dbfs < 0:
        raise ValueError('threshold must be finite, from -100 to below 0 dBFS')
    if not math.isfinite(window_ms) or not 1 <= window_ms <= 100:
        raise ValueError('window must be finite, from 1 to 100 ms')
    with wave.open(str(path), 'rb') as wav:
        rate, channels, width, frames = wav.getframerate(), wav.getnchannels(), wav.getsampwidth(), wav.getnframes()
        data = wav.readframes(frames)
    if not frames or width not in (1, 2, 3, 4) or len(data) != frames * channels * width:
        raise ValueError('Expected a complete nonempty 8/16/24/32-bit PCM WAV: '+str(path))
    if width == 1:
        values = array('h', (x - 128 for x in data))
    elif width in (2, 4):
        values = array('h' if width == 2 else 'i'); values.frombytes(data)
        if sys.byteorder != 'little': values.byteswap()
    else:
        values = array('i', (int.from_bytes(data[i:i+3], 'little', signed=True) for i in range(0, len(data), 3)))
    scale = float(1 << (8 * width - 1)); step = max(1, round(rate * window_ms / 1000)); first = last = None
    for start in range(0, frames, step):
        end = min(frames, start + step); chunk = values[start*channels:end*channels]
        rms = math.sqrt(sum(float(x) * x for x in chunk) / len(chunk)) / scale
        if rms > 10 ** (threshold_dbfs / 20):
            if first is None: first = start / rate
            last = end / rate
    return dict(duration_s=frames/rate, sample_rate=rate, channels=channels,
                first_active_s=first, last_active_s=last,
                leading_below_threshold_s=first,
                trailing_below_threshold_s=None if last is None else frames/rate-last,
                all_below_threshold=first is None)


def inspect_timeline(timeline, root, threshold_dbfs=-38., window_ms=10.):
    if not isinstance(timeline,dict):raise ValueError('Timeline must be a JSON object')
    cues = timeline.get('cues')
    if cues is None: cues = [c for s in timeline.get('scenes', []) for c in s['cues']]
    if not cues: raise ValueError('Timeline has no cues')
    rows=[];seen=set()
    for c in cues:
        ident=c['id']
        if ident in seen: raise ValueError('Duplicate cue: '+ident)
        seen.add(ident)
        start=c.get('start_s',c.get('absolute_start_s')) if 'cues' in timeline else c.get('absolute_start_s',c.get('start_s'))
        if isinstance(start,bool) or not isinstance(start,(int,float)) or not math.isfinite(start) or start<0:
            raise ValueError('Invalid absolute cue clock: '+ident)
        source=Path(root)/c['audio'];sha=hashlib.sha256(source.read_bytes()).hexdigest()
        if c.get('audio_sha256') and sha!=c['audio_sha256']:raise ValueError('Source hash mismatch: '+ident)
        row=inspect_wav(source,threshold_dbfs,window_ms)
        rows.append(dict(id=ident,audio=c['audio'],sha256=sha,start_s=start,**row))
    rows.sort(key=lambda row:row['start_s']);gaps=[]
    for a,b in zip(rows,rows[1:]):
        gap=None if a['last_active_s'] is None or b['first_active_s'] is None else b['start_s']+b['first_active_s']-a['start_s']-a['last_active_s']
        gaps.append(dict(previous=a['id'],next=b['id'],estimated_active_gap_s=gap,
                         file_to_file_gap_s=b['start_s']-a['start_s']-a['duration_s']))
    return dict(passed=True,threshold_dbfs=threshold_dbfs,window_ms=window_ms,cues=rows,gaps=gaps,
                scope='Approximate PCM RMS activity only; not words, VAD, silence-trim approval, or listening acceptance')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('timeline',type=Path);p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--threshold-dbfs',type=float,default=-38.);p.add_argument('--window-ms',type=float,default=10.);a=p.parse_args()
    if a.output.suffix.lower()!='.json' or a.output.resolve()==a.timeline.resolve():p.error('Use a separate JSON report path')
    try:
        timeline=json.loads(a.timeline.read_text())
        sources=timeline.get('cues') or [c for scene in timeline.get('scenes',[]) for c in scene['cues']]
        protected=[a.timeline.resolve()]+[(a.root/c['audio']).resolve() for c in sources]
        if a.output.resolve() in protected:p.error('Report must not overwrite timeline or source audio')
        report=inspect_timeline(timeline,a.root,a.threshold_dbfs,a.window_ms)
    except (OSError,ValueError,KeyError,TypeError,AttributeError,wave.Error) as e:report=dict(passed=False,error=str(e))
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],output=str(a.output),error=report.get('error')),ensure_ascii=False))
    raise SystemExit(0 if report['passed'] else 1)
if __name__=='__main__':main()
