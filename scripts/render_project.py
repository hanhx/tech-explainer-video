"""Render an authored Manim CE project using a measured timeline."""
import argparse
import configparser
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid
from build_timeline import build


def stamp(seconds):
    ms = round(seconds * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def render(args):
    root = args.project.resolve()
    timeline = build(root / 'project.json')
    (root / 'timeline.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=2) + '\n')
    if not (root / 'scene.py').is_file():
        raise ValueError('Missing authored scene.py')
    if not re.fullmatch(r'[A-Za-z_]\w*', args.scene):
        raise ValueError('scene must be a Python class name')
    width, height = map(int, args.resolution.split(','))
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError('Resolution must contain positive even pixel dimensions')
    output = root / 'out' / args.mode
    run = output / ('run-' + uuid.uuid4().hex[:10])
    run.mkdir(parents=True)
    media = run / 'media'
    fps = 15 if args.mode == 'draft' else timeline['fps']
    scale = min(1.0, 854 / width, 854 / height)
    draft_width = max(2, round(width * scale / 2) * 2)
    draft_height = max(2, round(height * scale / 2) * 2)
    dimensions = f'{draft_width},{draft_height}' if args.mode == 'draft' else args.resolution
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
           'MANIM_PROJECT': str(root), 'MANIM_OUTPUT': str(run),
           'MANIM_STILLS': '1' if args.mode == 'stills' else '0'}
    command = [args.python, '-m', 'manim', '--renderer', 'cairo',
               '--progress_bar', 'none', '-v', 'WARNING', '--media_dir', str(media),
               '-r', dimensions, '--fps', str(fps), '-o', 'video']
    if not args.cache:
        command.append('--disable_caching')
    else:
        # Unique final media directories must not also isolate every cache.
        # Preserve authored project config and share ONLY native play fragments.
        settings = configparser.ConfigParser(interpolation=None)
        settings.read(root / 'manim.cfg')
        if not settings.has_section('CLI'):
            settings.add_section('CLI')
        cache = root / '.local' / 'manim-cache' / args.scene / (dimensions.replace(',', 'x') + f'-{fps}fps')
        cache.mkdir(parents=True, exist_ok=True)
        settings.set('CLI', 'partial_movie_dir', str(cache))
        settings.set('CLI', 'disable_caching', 'False')
        cache_config = run / 'cache.cfg'
        with cache_config.open('w') as stream:
            settings.write(stream)
        command += ['--config_file', str(cache_config)]
    if args.mode == 'stills':
        command.append('-s')
    subprocess.run(command + ['scene.py', args.scene], cwd=root, env=env, check=True)
    actual_path = run / 'actual-timeline.json'
    actual = json.loads(actual_path.read_text())
    if actual.get('narration') != timeline['narration']:
        raise ValueError('Authored scene changed narration mode')
    expected_ids = [c['id'] for s in timeline['scenes'] for c in s['cues']]
    if [c['id'] for c in actual['cues']] != expected_ids:
        raise ValueError('Authored scene did not execute the complete cue sequence')
    actual['project_root'] = os.path.relpath(root, output)
    if args.mode != 'stills':
        movies = list((media / 'videos' / 'scene').glob('*/video.mp4'))
        if len(movies) != 1:
            raise ValueError(f'Expected one new rendered MP4, got {movies}')
        source = movies[0]
        probe = json.loads(subprocess.check_output(
            ['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(source)]))
        if timeline['narration'] and not any(s['codec_type'] == 'audio' for s in probe['streams']):
            raise ValueError('Narration required but rendered source has no audio')
        temporary = run / 'video.new.mp4'
        command = ['ffmpeg', '-y', '-v', 'error', '-i', str(source), '-map', '0:v:0', '-c:v', 'copy']
        music = json.loads((root / 'project.json').read_text()).get('music') or {}
        if timeline['narration'] and music.get('file') and args.mode == 'final':
            # Optional BGM: looped, attenuated, ducked under narration, then loudness-normalised.
            track = (root / music['file']).resolve()
            if not track.is_file():
                raise ValueError(f'music.file not found: {track}')
            gain = float(music.get('gain_db', -22))
            duck = ('[m][v]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[md];'
                    if music.get('duck', True) else '[m]anull[md];[v]anullsink;')
            graph = (f'[1:a]aloop=loop=-1:size=2000000000,volume={gain}dB,afade=t=in:d=1[m];'
                     '[0:a]asplit=2[v][vm];' + duck +
                     '[vm][md]amix=inputs=2:duration=first:normalize=0,'
                     'loudnorm=I=-17:TP=-1.5:LRA=11[a]')
            command = command[:6] + ["-i", str(track)] + command[6:]
            command += ['-filter_complex', graph, '-map', '[a]', '-c:a', 'aac', '-ar', '48000']
        elif timeline['narration']:
            command += ['-map', '0:a:0', '-c:a', 'aac', '-ar', '48000',
                        '-af', 'loudnorm=I=-17:TP=-1.5:LRA=11']
        else:
            command += ['-an']
        subprocess.run(command + ['-movflags', '+faststart', str(temporary)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(temporary), '-f', 'null', '-'], check=True)
        temporary.replace(output / 'video.mp4')
    (output / 'actual-timeline.json').write_text(json.dumps(actual, ensure_ascii=False, indent=2) + '\n')
    captions = []
    for i, cue in enumerate(actual['cues'], 1):
        captions += [str(i), f'{stamp(cue["start_s"])} --> '
                     f'{stamp(cue["start_s"] + cue["duration_s"])}', cue['subtitle'], '']
    (output / 'subtitles.srt').write_text('\n'.join(captions))
    for path in run.glob('*.png'):
        shutil.copy2(path, output / path.name)
    print(f'Layout checkpoints only: {output}' if args.mode == 'stills'
          else f'Video rendered: {output / "video.mp4"}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--python', default=sys.executable)
    parser.add_argument('--mode', choices=['draft', 'stills', 'final'], default='draft')
    parser.add_argument('--scene', default='Explainer')
    parser.add_argument('--cache', action='store_true',
                        help='opt in to Manim play caching for a project with reviewed dependencies')
    parser.add_argument('--resolution', default='1920,1080')
    args = parser.parse_args()
    try:
        render(args)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Render failed: {error}\n')


if __name__ == '__main__':
    main()
