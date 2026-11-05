"""Opt-in speech-mobile-v1 mastering of a complete, unmixed narration track.

Uses FFmpeg and standard Python. No TTS, tempo, denoise, or source overwrite.
The recipe is an auditioned starting point, not a platform loudness standard.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import wave

PRESET = 'speech-fuller-v10'
RATE = 48000
FILTER = 'acompressor=threshold=0.063:ratio=2.2:attack=8:release=150:knee=3:makeup=1:detection=rms,alimiter=limit=0.1:attack=3:release=90:level=false:latency=true'


def validate_mastering(value):
    if value is not None and value != {'preset': PRESET}:
        raise ValueError(f'mastering must be {{"preset": "{PRESET}"}} or null')
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    p = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-nostdin', '-n', *map(str, args)],
                       capture_output=True, text=True)
    if p.returncode:
        raise ValueError(p.stderr[-3000:])
    return p.stderr


def measure(path):
    log = run(['-i', path, '-vn', '-af', 'loudnorm=I=-15:TP=-2:LRA=5:print_format=json', '-f', 'null', '-'])
    row = json.loads(re.findall(r'\{[^{}]+\}', log)[-1])
    return {k: float(row[k]) for k in ('input_i', 'input_tp', 'input_lra')}


def select_mastering(project):
    """Explicit project null disables a preference. Existing projects aren't migrated."""
    if 'audio_mastering' in project:
        return validate_mastering(project['audio_mastering'])
    return validate_mastering((project.get('voice_profile') or {}).get('processing', {}).get('mastering'))


def process(source, output, preset=PRESET):
    source, output = Path(source).resolve(), Path(output).resolve()
    validate_mastering({'preset': preset})
    receipt = output.with_suffix('.mastering.json')
    if not source.is_file() or source == output or output.exists() or receipt.exists():
        raise ValueError('Source must exist; use a new output WAV and receipt path')
    if output.suffix.lower() != '.wav':
        raise ValueError('Master output must be WAV; encode to AAC after mixing')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as folder:
        folder = Path(folder)
        decoded = folder / 'input.wav'
        # Duration is measured in output-rate samples, not rounded container seconds.
        run(['-i', source, '-vn', '-ac', '1', '-ar', RATE, '-c:a', 'pcm_s16le', decoded])
        with wave.open(str(decoded), 'rb') as wav:
            frames = wav.getnframes()
        if frames < RATE // 5:
            raise ValueError('Narration is shorter than 0.2 seconds')
        target = 'loudnorm=I=-14:TP=-1.2:LRA=6'
        log = run(['-i', source, '-vn', '-ac', '1', '-af', FILTER+','+target+':print_format=json', '-f', 'null', '-'])
        first = json.loads(re.findall(r'\{[^{}]+\}', log)[-1])
        norm = target + ':measured_I=' + first['input_i'] + ':measured_TP=' + first['input_tp'] + ':measured_LRA=' + first['input_lra'] + ':measured_thresh=' + first['input_thresh'] + ':offset=' + first['target_offset'] + ':linear=true'
        filters = FILTER + ',' + norm + ',agate=threshold=0.0224:ratio=2.2:range=0.1:attack=12:release=180:detection=rms,alimiter=limit=0.87:attack=5:release=100:level=false:latency=true' + f',aresample={RATE},apad=whole_len={frames},atrim=end_sample={frames}'
        staged = folder / 'master.wav'
        run(['-i', source, '-vn', '-ac', '1', '-af', filters, '-ar', RATE, '-c:a', 'pcm_s24le', staged])
        with wave.open(str(staged), 'rb') as wav:
            if wav.getnframes() != frames:
                raise ValueError('Mastering changed the measured narration sample count')
        stats = measure(staged)
        if stats['input_i'] < -70:
            raise ValueError('No measurable speech loudness; inspect silent source')
        meta = dict(preset=PRESET, filter=filters, frames=frames, sample_rate=RATE,
                    duration_s=frames/RATE, source_sha256=digest(source), output_sha256=digest(staged),
                    measured=stats, first_pass=first, human_listening_accepted=False,
                    ffmpeg_version=subprocess.check_output(['ffmpeg', '-version'], text=True).splitlines()[0])
        staged_report = folder / 'receipt.json'
        staged_report.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
        staged_report.replace(receipt)
        staged.replace(output)
    return meta


def mix_cues(root, cues, duration_s, output):
    """Compose original WAVs at actual scene clocks before mastering, without AAC loss."""
    command, graph = [], []
    for i, cue in enumerate(cues):
        source = Path(root) / cue['audio']
        if digest(source) != cue['audio_sha256']:
            raise ValueError(f'{cue["id"]}: source changed before mastering')
        command += ['-i', source]
        start = round(float(cue['start_s']) * RATE)
        if start < 0:
            raise ValueError('Negative cue clock')
        graph.append(f'[{i}:a]aresample={RATE},aformat=channel_layouts=mono,adelay={start}S:all=1[a{i}]')
    if not cues:
        raise ValueError('Missing narration cues')
    graph.append(''.join(f'[a{i}]' for i in range(len(cues))) +
                 f'amix=inputs={len(cues)}:normalize=0:dropout_transition=0,'
                 f'apad=whole_len={round(duration_s*RATE)},atrim=end_sample={round(duration_s*RATE)}[mix]')
    run(command + ['-filter_complex', ';'.join(graph), '-map', '[mix]', '-ar', RATE, '-c:a', 'pcm_s24le', output])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--preset', choices=[PRESET], default=PRESET)
    args = parser.parse_args()
    try:
        print(json.dumps(process(args.source, args.output, args.preset), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Voice mastering failed: {error}\n')


if __name__ == '__main__':
    main()
