"""Apply the opt-in afftdn-hiss-v1 narration preset to a NEW WAV.

Input must already have its chosen tempo applied. Keeps a 48 kHz mono version
of the same duration, compensates afftdn's 25 ms latency and pads the tail.
Does not change TTS identity/reference or overwrite the source. Standard Python
plus FFmpeg; no new model or Python dependency is required.
"""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

PRESET = 'afftdn-hiss-v1'
RATE = 48000
DELAY = 1200
FILTER = 'apad=pad_dur=0.1,afftdn=nr=8:nf=-42:tn=0:gs=8'


def validate_denoise(value):
    if value is None:
        return None
    if not isinstance(value, dict) or value != {'preset': PRESET}:
        raise ValueError(f'denoise must be {{"preset": "{PRESET}"}} or omitted')
    return value


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def floats(blob):
    result = array('f')
    result.frombytes(blob)
    if sys.byteorder != 'little':
        result.byteswap()
    if not result or not all(math.isfinite(v) for v in result):
        raise ValueError('Empty or nonfinite audio')
    return result


def rms(values):
    return math.sqrt(math.fsum(v * v for v in values) / len(values))


def process(source, output, preset=PRESET):
    source, output = Path(source).resolve(), Path(output).resolve()
    validate_denoise({'preset': preset})
    report = output.with_suffix('.processing.json')
    if source == output or output.exists() or report.exists():
        raise ValueError('Use a new output path; existing audio/provenance is never overwritten')
    base = ['ffmpeg', '-v', 'error', '-i', str(source), '-ac', '1', '-ar', str(RATE)]
    src = floats(subprocess.check_output(base + ['-f', 'f32le', '-']))
    filtered = floats(subprocess.check_output(base + ['-af', 'aresample=48000,' + FILTER, '-f', 'f32le', '-']))
    if len(filtered) < DELAY + len(src):
        raise ValueError('Filtered output is too short after delay compensation')
    cleaned = filtered[DELAY:DELAY + len(src)]
    src_rms, cleaned_rms = rms(src), rms(cleaned)
    gain = src_rms / cleaned_rms if cleaned_rms > 1e-12 else 1.0
    peak = max(abs(v) for v in cleaned)
    desired_gain = gain
    if peak > 0:
        gain = min(gain, 0.999 / peak)
    cleaned = array('f', (v * gain for v in cleaned))
    if sys.byteorder != 'little':
        cleaned.byteswap()
    output.parent.mkdir(parents=True, exist_ok=True)
    meta = dict(preset=PRESET, filter=FILTER, sample_rate=RATE,
                delay_compensation_samples=DELAY, frames=len(src),
                duration_s=len(src) / RATE, level_matching='whole-cue RMS; peak capped',
                gain_db=20 * math.log10(gain), peak_cap_applied=gain < desired_gain,
                source_sha256=digest(source),
                ffmpeg_version=subprocess.check_output(['ffmpeg', '-version'], text=True).splitlines()[0],
                human_listening_accepted=False)
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        tmp = Path(temp) / 'processed.wav'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(RATE),
                        '-ac', '1', '-i', '-', '-c:a', 'pcm_s16le', str(tmp)],
                       input=cleaned.tobytes(), check=True)
        meta['output_sha256'] = digest(tmp)
        staged_report = Path(temp) / 'processing.json'
        staged_report.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
        staged_report.replace(report)
        tmp.replace(output)
    return meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--preset', default=PRESET, choices=[PRESET])
    args = parser.parse_args()
    try:
        print(json.dumps(process(args.source, args.output, args.preset), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Narration processing failed: {error}\n')


if __name__ == '__main__':
    main()
