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

PRESET = 'speech-mobile-v1'
RATE = 48000
FILTER = ('highpass=f=75,equalizer=f=250:t=q:w=0.9:g=-1.5,'
          'equalizer=f=2500:t=q:w=0.8:g=2,'
          'acompressor=threshold=0.1:ratio=2.5:attack=6:release=110:knee=4:makeup=1:detection=rms,'
          'loudnorm=I=-15:TP=-2:LRA=5,volume=1.7dB,'
          'alimiter=limit=0.77:attack=3:release=70:level=false:latency=true')


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
        filters = FILTER + f',aresample={RATE},apad=whole_len={frames},atrim=end_sample={frames}'
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
                    measured=stats, human_listening_accepted=False,
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
