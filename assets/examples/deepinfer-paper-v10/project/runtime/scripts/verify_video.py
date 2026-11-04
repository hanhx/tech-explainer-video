"""Technical media checks; deliberately does not grade voice identity or comprehension."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def verify(video, timeline_path=None, align=False):
    video = Path(video).resolve()
    data = json.loads(run(['ffprobe', '-v', 'error', '-show_format',
                          '-show_streams', '-of', 'json', str(video)]).stdout)
    picture = next((s for s in data['streams'] if s['codec_type'] == 'video'), None)
    sound = next((s for s in data['streams'] if s['codec_type'] == 'audio'), None)
    if not picture:
        raise ValueError('Missing video stream')
    duration = float(data['format']['duration'])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('Invalid video duration')
    run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'])
    report = dict(video=str(video), duration_s=duration, width=picture['width'],
                  height=picture['height'], fps=picture['r_frame_rate'],
                  video_codec=picture['codec_name'],
                  audio_codec=sound['codec_name'] if sound else None,
                  full_decode_passed=True, source_audio_hashes_checked=False,
                  waveform_alignment_checked=False, cue_count=None,
                  perceptual_voice_consistency='not evaluated',
                  knowledge_and_visual_comprehension='not evaluated')
    if timeline_path:
        timeline_path = Path(timeline_path).resolve()
        timeline = json.loads(timeline_path.read_text())
        root = (timeline_path.parent / timeline['project_root']).resolve()
        if not isinstance(timeline.get('narration'), bool):
            raise ValueError('Timeline must declare narration')
        if timeline['narration'] and not sound:
            raise ValueError('Narrated timeline but video has no audio')
        cues = timeline['cues']
        if not cues or len({c['id'] for c in cues}) != len(cues):
            raise ValueError('Missing or duplicate cue ids')
        previous = -1.0
        for cue in cues:
            start, length = cue['start_s'], cue['duration_s']
            if not all(math.isfinite(x) for x in [start, length]) or start < 0 or length <= 0:
                raise ValueError(f'{cue["id"]}: invalid cue time')
            if start < previous - .003 or start + length > duration + .1:
                raise ValueError(f'{cue["id"]}: cue overlaps or exceeds video')
            previous = start + length
            if 'minimum_observation_s' in cue:
                observed = cue.get('observation_s', -1)
                if not math.isfinite(observed) or observed + .001 < cue['minimum_observation_s']:
                    raise ValueError(f'{cue["id"]}: observation hold was shortened')
            if timeline['narration']:
                if not cue.get('audio') or not cue.get('audio_sha256'):
                    raise ValueError(f'{cue["id"]}: missing audio provenance')
                path = root / cue['audio']
                if hashlib.sha256(path.read_bytes()).hexdigest() != cue['audio_sha256']:
                    raise ValueError(f'{cue["id"]}: source audio changed after rendering')
        report.update(cue_count=len(cues), source_audio_hashes_checked=timeline['narration'])
        if align and timeline['narration']:
            import numpy as np
            rate = 8000
            full = np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', str(video), '-vn',
                                      '-ar', str(rate), '-ac', '1', '-f', 'f32le', '-']).stdout, dtype='<f4')
            results = []
            master = timeline.get('audio_mastering')
            master_pcm = None
            if master:
                master_path = root / master['file']
                if hashlib.sha256(master_path.read_bytes()).hexdigest() != master['sha256']:
                    raise ValueError('Mastered narration hash mismatch')
                master_pcm = np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', str(master_path),
                    '-ar', str(rate), '-ac', '1', '-f', 'f32le', '-']).stdout, dtype='<f4')
                report['mastered_reference_hash_checked'] = True
            for cue in cues:
                ref = np.frombuffer(run(['ffmpeg', '-v', 'error', '-i', str(root / cue['audio']),
                                         '-ar', str(rate), '-ac', '1', '-f', 'f32le', '-']).stdout, dtype='<f4')
                start = cue['start_s']
                if master_pcm is not None:
                    ref = master_pcm[round(start*rate):round((start+cue['duration_s'])*rate)]
                left = max(0, round((start - .15) * rate))
                window = full[left:min(len(full), round((start + .15) * rate) + len(ref))]
                if len(ref) < 2 or len(window) < len(ref) or np.linalg.norm(ref) < 1e-6:
                    raise ValueError(f'{cue["id"]}: insufficient non-silent audio for alignment')
                size = 1 << (len(window) + len(ref) - 2).bit_length()
                dots = np.fft.irfft(np.fft.rfft(window, size) *
                                    np.conj(np.fft.rfft(ref, size)), size)[:len(window)-len(ref)+1]
                best = int(np.argmax(dots))
                match = window[best:best+len(ref)]
                norm = float(np.linalg.norm(ref) * np.linalg.norm(match))
                score = float(dots[best] / norm) if norm > 1e-12 else 0.0
                error = (left + best) / rate - start
                if not math.isfinite(score) or abs(error) > .08 or score < .85:
                    raise ValueError(f'{cue["id"]}: waveform mismatch: shift={error:.3f}s, corr={score:.3f}')
                results.append(dict(id=cue['id'], offset_s=round(error, 6), correlation=round(score, 6)))
            report.update(waveform_alignment_checked=True, audio_alignment=results)
    elif align:
        raise ValueError('--align-audio requires --timeline')
    report['technical_checks_passed'] = True
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--timeline', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--align-audio', action='store_true')
    args = parser.parse_args()
    try:
        report = verify(args.video, args.timeline, args.align_audio)
        status = 0
    except (ValueError, OSError, KeyError, TypeError, ImportError,
            subprocess.SubprocessError) as error:
        report = dict(technical_checks_passed=False, error=str(error),
                      perceptual_voice_consistency='not evaluated')
        status = 1
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(status)


if __name__ == '__main__':
    main()
