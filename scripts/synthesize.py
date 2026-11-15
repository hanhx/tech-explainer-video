"""Generate per-cue narration for project.json with a registered local Qwen3-TTS voice.

Controller mode (any python3): resolves voice profiles, plans cache keys, skips
locked or already-present audio, then launches the profile's own TTS interpreter
in worker mode. It never downloads models, never overwrites a locked file and
never edits spoken_text / subtitle.

  python3 synthesize.py PROJECT_DIR [--profile ID] [--speed RATE] [--only CUE_ID ...] [--dry-run]

Playback speed: --speed > project narration_tempo > profile processing.tempo (default 1.0).

Per-cue fields read from project.json:
  spoken_text  formal narration (also the default subtitle)
  tts_text     optional pronunciation hint passed to TTS instead of spoken_text
  voice        optional profile id for multi-role dialogue (default: project voice)
  seed         optional integer seed (default: profile default_seed + cue index)
  locked_sha256  approved audio; this cue is never regenerated
"""
import argparse
from copy import deepcopy
import hashlib
import json
import os
import re
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import wave

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cache_key(conditions):
    return hashlib.sha256(json.dumps(conditions, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:12]


def validate_speed(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not .5 <= value <= 2:
        raise ValueError('narration speed must be a finite number from 0.5 to 2')
    return float(value)


def raw_key(profile, text, seed):
    conditions = {k: profile[k] for k in ('backend', 'model_id', 'reference_sha256', 'reference_text', 'generation')}
    runtime = profile['runtime']
    conditions['runtime'] = {k: runtime[k] for k in ('model_path', 'device', 'dtype', 'attn_implementation')
                             if k in runtime}
    return cache_key(dict(**conditions, text=text, seed=seed))


def spoken_input(cue, profile, pronunciations=None):
    text = cue.get('tts_text') or cue['spoken_text']
    if not cue.get('tts_text') and pronunciations:
        terms = sorted(pronunciations, key=len, reverse=True)
        pattern = r'(?<![A-Za-z0-9_])(?:' + '|'.join(re.escape(t) for t in terms) + r')(?![A-Za-z0-9_])'
        text = re.sub(pattern, lambda m: pronunciations[m.group()], text)
    if profile.get('processing', {}).get('sentence_ending') == 'exclamation' and text.endswith('。'):
        text = text[:-1] + '！'
    return text


def plan(root, args):
    from voice_profiles import default_config, resolve
    project_path = root / 'project.json'
    data = json.loads(project_path.read_text())
    if data.get('narration') is not True:
        raise ValueError('project.json must set narration=true before synthesis')
    speed = args.speed
    if speed is not None:
        speed = validate_speed(speed)
    elif 'narration_tempo' in data:
        speed = validate_speed(data['narration_tempo'])
    pronunciations = data.get('pronunciations', {})
    if not isinstance(pronunciations, dict) or any(
            not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip()
            for k, v in pronunciations.items()):
        raise ValueError('pronunciations must map non-empty literal terms to non-empty TTS text')
    config = args.config or default_config()
    default_voice = args.profile or (data.get('voice_profile') or {}).get('id')
    profiles, jobs, index = {}, [], 0
    for scene in data['scenes']:
        for cue in scene['cues']:
            index += 1
            cid = cue['id']
            if args.only and cid not in args.only:
                continue
            if cue.get('locked_sha256'):
                current = root / cue['audio'] if cue.get('audio') else None
                if not current or not current.is_file() or sha256(current) != cue['locked_sha256']:
                    raise ValueError(f'{cid}: locked audio missing or changed; refusing to regenerate')
                print(f'locked  {cid}', flush=True)
                continue
            voice = cue.get('voice') or default_voice
            key_name = voice or '<default>'
            if key_name not in profiles:
                profiles[key_name] = resolve(config, voice)
            prof = profiles[key_name]
            text = spoken_input(cue, prof, pronunciations)
            seed = int(cue.get('seed', prof.get('default_seed', 1234) + index))
            profile_tempo = float(prof['processing'].get('tempo', 1.0))
            tempo = profile_tempo if speed is None else speed
            conditions = dict(fp=prof['profile_fingerprint'], text=text, seed=seed)
            legacy_key = cache_key(conditions)
            key = legacy_key if tempo == profile_tempo else cache_key(dict(**conditions, tempo=tempo))
            prefix = f'{cid}-{prof["id"]}'
            out = f'audio/{prefix}-{key}.wav'
            raw = f'.local/tts-raw/{prefix}-{raw_key(prof, text, seed)}.wav'
            legacy_raw = f'.local/tts-raw/{prefix}-{legacy_key}.wav'
            jobs.append(dict(cue=cid, text=text, seed=seed, profile=prof['id'], out=out, tempo=tempo,
                             raw=raw, legacy_raw=legacy_raw, exists=(root / out).is_file()))
    return data, project_path, profiles, jobs


def apply_tempo(path, tempo):
    if abs(tempo - 1.0) < 1e-6:
        return
    tmp = path.with_suffix('.tempo.wav')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(path), '-af', f'atempo={tempo}', str(tmp)], check=True)
    tmp.replace(path)


def raw_audio_ready(path, cue):
    if not path.exists():
        return False
    try:
        with wave.open(str(path), 'rb') as audio:
            count, rate = audio.getnframes(), audio.getframerate()
            valid = (.2 < count / rate < 60 and audio.getcomptype() == 'NONE'
                     and len(audio.readframes(count)) == count * audio.getnchannels() * audio.getsampwidth())
    except (OSError, EOFError, wave.Error, ZeroDivisionError) as error:
        raise ValueError(f'{cue}: retained raw WAV is invalid; preserved for inspection: {path}') from error
    if not valid:
        raise ValueError(f'{cue}: retained raw WAV is incomplete; preserved for inspection: {path}')
    return True


def prepare_narration(raw, staging, processing):
    from process_narration import process, trim_edges_and_apply_tempo

    denoise = processing.get('denoise')
    edge_trim = processing.get('edge_trim')
    tempo = processing['tempo']
    source = staging / 'prepared.wav'
    shutil.copyfile(raw, source)
    raw_digest = sha256(source) if denoise or edge_trim else None
    if not edge_trim:
        apply_tempo(source, tempo)
    meta = None
    if denoise:
        cleaned = staging / 'clean.wav'
        meta = process(source, cleaned, denoise['preset'])
        source = cleaned
    if edge_trim:
        final = staging / 'trimmed.wav'
        trim_meta = trim_edges_and_apply_tempo(source, final, tempo)
        meta = dict(denoise=meta, edge_trim=trim_meta, output_sha256=sha256(final))
        source = final
    if meta is not None:
        meta.update(tts_raw_sha256=raw_digest, processing=processing)
    return source, meta


def controller(args):
    root = args.project.resolve()
    data, project_path, profiles, jobs = plan(root, args)
    original = deepcopy(data)
    todo = [j for j in jobs if not j['exists']]
    for j in jobs:
        j['raw_ready'] = False
        if not j['exists']:
            for source in (j['raw'], j['legacy_raw']):
                if raw_audio_ready(root / source, j['cue']):
                    j['raw_ready'] = True
                    j['raw_source'] = source
                    break
        status = 'cached' if j['exists'] else 'process raw' if j['raw_ready'] else 'generate'
        print(f'{status:<12} {j["cue"]:<20} [{j["profile"]}, {j["tempo"]:g}x] {j["text"]}', flush=True)
    if args.dry_run:
        return
    (root / 'audio').mkdir(exist_ok=True)
    by_profile = {}
    for j in todo:
        by_profile.setdefault(j['profile'], []).append(j)
    generated = 0
    for pid, batch in by_profile.items():
        prof = next(p for p in profiles.values() if p['id'] == pid)
        missing = [{**j, 'out': j['raw']} for j in batch if not j['raw_ready']]
        if missing:
            with tempfile.NamedTemporaryFile('w', suffix='.json', delete=False) as fh:
                json.dump(dict(profile=prof, root=str(root), jobs=missing), fh, ensure_ascii=False)
            print(f'Generating {len(missing)} cue(s) with {pid} ...', flush=True)
            try:
                subprocess.run([prof['runtime']['python'], '-I', str(Path(__file__).resolve()), '--worker', fh.name],
                               check=True)
                generated += len(missing)
            finally:
                os.unlink(fh.name)
        for j in batch:
            out = root / j['out']
            raw = root / j['raw']
            source = root / j.get('raw_source', j['raw'])
            processing = {**prof['processing'], 'tempo': j['tempo']}
            with tempfile.TemporaryDirectory(dir=root / '.local') as temp:
                temp = Path(temp)
                if source != raw:
                    # Preserve the old file while making this raw reusable after future tempo changes.
                    migrated = temp / 'raw.wav'
                    shutil.copyfile(source, migrated)
                    migrated.replace(raw)
                prepared, meta = prepare_narration(raw, temp, processing)
                if meta is not None:
                    report = temp / 'prepared.processing.json'
                    report.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
                    report.replace(out.with_suffix('.processing.json'))
                prepared.replace(out)
    # Point cues at their audio. Locked cues and text fields are untouched.
    paths = {j['cue']: j['out'] for j in jobs}
    seeds = {j['cue']: j['seed'] for j in jobs}
    changed = []
    for scene in data['scenes']:
        for cue in scene['cues']:
            if cue['id'] in seeds:
                cue.setdefault('seed', seeds[cue['id']])
            if cue['id'] in paths and cue.get('audio') != paths[cue['id']]:
                cue['audio'] = paths[cue['id']]
                changed.append(cue['id'])
    voices = sorted({j['profile'] for j in jobs})
    if len(voices) == 1 and not args.only:
        prof = next(p for p in profiles.values() if p['id'] == voices[0])
        data['voice_profile'] = dict(id=prof['id'], reference_sha256=prof['reference_sha256'],
                                     profile_fingerprint=prof['profile_fingerprint'],
                                     processing=prof.get('processing', {}))
        if prof.get('delivery_style'):
            data['voice_profile']['delivery_style'] = prof['delivery_style']
    if data != original:
        with tempfile.TemporaryDirectory(dir=root) as temp:
            tmp = Path(temp) / project_path.name
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            if json.loads(project_path.read_text()) != original:
                raise ValueError('project.json changed during synthesis; retry to reuse the completed audio')
            tmp.replace(project_path)
    print(f'Done: {generated} generated, {len(todo)} processed, {len(jobs) - len(todo)} cached, '
          f'audio path updated for {changed or "none"}')
    print('Next: build_timeline.py, then listen to the new clips before locking them.')


def worker(spec_path):
    spec = json.loads(Path(spec_path).read_text())
    prof, root = spec['profile'], Path(spec['root'])
    rt = prof['runtime']
    for name, value in dict(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', TOKENIZERS_PARALLELISM='false',
                            PYTORCH_ENABLE_MPS_FALLBACK='1').items():
        os.environ.setdefault(name, value)
    import numpy as np
    import soundfile as sf
    import torch
    from qwen_tts import Qwen3TTSModel
    device = rt.get('device', 'auto')
    if device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
    dtype = getattr(torch, rt.get('dtype', 'float16' if device != 'cpu' else 'float32'))
    model = Qwen3TTSModel.from_pretrained(rt['model_path'], device_map=device, dtype=dtype,
                                          attn_implementation=rt.get('attn_implementation', 'sdpa'),
                                          local_files_only=True)
    prompt = model.create_voice_clone_prompt(ref_audio=prof['reference_audio'], ref_text=prof['reference_text'],
                                             x_vector_only_mode=False)
    gen = dict(prof.get('generation', {}))
    for job in spec['jobs']:
        torch.manual_seed(job['seed'])
        with torch.inference_mode():
            wavs, sr = model.generate_voice_clone(text=job['text'], voice_clone_prompt=prompt, **gen)
        wav = np.asarray(wavs[0], dtype=np.float32)
        if not np.isfinite(wav).all() or np.abs(wav).max() < 1e-3 or not .2 < len(wav) / sr < 60:
            raise ValueError(f'{job["cue"]}: suspicious output ({len(wav) / sr:.2f}s)')
        out = root / job['out']
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=out.parent) as temp:
            part = Path(temp) / out.name
            sf.write(part, wav, sr, subtype='PCM_16')
            part.replace(out)
        print(f'  {job["cue"]}: {len(wav) / sr:.2f}s', flush=True)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        return worker(sys.argv[2])
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project', type=Path)
    parser.add_argument('--profile', help='voice profile id; overrides project voice_profile.id')
    parser.add_argument('--speed', type=float, metavar='RATE', help='narration speed for this run (0.5 to 2)')
    parser.add_argument('--config', type=Path)
    parser.add_argument('--only', nargs='+', help='regenerate only these cue ids')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        controller(args)
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Synthesis failed: {error}\n')


if __name__ == '__main__':
    main()
