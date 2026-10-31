"""List or resolve this machine's optional Qwen Base voice profiles.

This helper validates reference audio and returns synthesis conditions. It does
not generate speech, change project audio, download models, or update defaults.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path


def default_config():
    explicit=os.environ.get('MANIM_VOICE_CONFIG')
    if explicit:return Path(explicit).expanduser()
    config_home=Path(os.environ.get('XDG_CONFIG_HOME',str(Path.home()/'.config')))
    return config_home/'manim-tech-explainer-video/voices.json'


def load_config(path):
    path=Path(path).expanduser()
    if not path.is_file():
        raise ValueError(f'No local voice registry: {path}; use supplied audio or configure a reference first')
    data=json.loads(path.read_text())
    if not isinstance(data,dict) or data.get('schema_version')!=1 or not isinstance(data.get('profiles'),dict):
        raise ValueError('Expected schema_version=1 and profiles mapping')
    return data


def local_path(value,label):
    if not isinstance(value,str) or not value:
        raise ValueError(f'{label}: missing path')
    path=Path(os.path.expandvars(value)).expanduser()
    if not path.is_absolute():raise ValueError(f'{label}: expected an absolute or home-relative local path')
    # Preserve the venv executable spelling rather than resolving its symlink.
    return path


def resolve(path,choice=None):
    data=load_config(path)
    name=choice or data.get('default_profile')
    if name=='candidate':name=data.get('candidate_profile')
    profiles=data['profiles']
    if name not in profiles:
        matches=[key for key,item in profiles.items() if name in item.get('aliases',[])]
        if len(matches)!=1:raise ValueError(f'Unknown or ambiguous voice profile: {name}')
        name=matches[0]
    profile=profiles[name]
    if not isinstance(profile,dict):raise ValueError(f'{name}: expected profile mapping')
    if profile.get('backend')!='qwen3-tts-base':
        raise ValueError(f'{name}: this resolver supports qwen3-tts-base references')
    ref=local_path(profile.get('reference_audio'),f'{name}.reference_audio')
    if not ref.is_file():raise ValueError(f'{name}: reference audio missing: {ref}')
    digest=hashlib.sha256(ref.read_bytes()).hexdigest()
    if digest!=profile.get('reference_sha256'):
        raise ValueError(f'{name}: reference_sha256 mismatch; selected reference changed')
    transcript=profile.get('reference_text')
    if not isinstance(transcript,str) or not transcript.strip():
        raise ValueError(f'{name}: reference_text is required')
    runtime=data.get('runtime',{})
    if not isinstance(runtime,dict):raise ValueError('runtime must be a mapping')
    python=local_path(runtime.get('python'),'runtime.python')
    model=local_path(runtime.get('model_path'),'runtime.model_path')
    if not python.is_file():raise ValueError(f'Missing local TTS interpreter: {python}')
    if not (model/'config.json').is_file():raise ValueError(f'Missing local Base model: {model}')
    model_config=json.loads((model/'config.json').read_text())
    if model_config.get('tts_model_type')!='base':raise ValueError('Configured model is not Qwen Base')
    processing=profile.get('processing',{})
    if not isinstance(processing,dict):raise ValueError(f'{name}: processing must be a mapping')
    tempo=processing.get('tempo',1.0)
    if isinstance(tempo,bool) or not isinstance(tempo,(int,float)) or not math.isfinite(tempo) or not .5<=tempo<=2:
        raise ValueError(f'{name}: tempo must be a finite number from 0.5 to 2')
    from process_narration import validate_denoise
    validate_denoise(processing.get('denoise'))
    settings=profile.get('generation',{})
    if not isinstance(settings,dict):raise ValueError(f'{name}: generation must be a mapping')
    if 'speaker' in settings or 'instruct' in settings:
        raise ValueError(f'{name}: Base reference cloning does not use speaker or instruct')
    conditions=dict(id=name,backend=profile['backend'],model_id=runtime.get('model_id'),
                    reference_sha256=digest,reference_text=transcript,
                    generation=settings,processing=processing,default_seed=profile.get('default_seed',1234))
    fingerprint=hashlib.sha256(json.dumps(conditions,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return dict(**conditions,label=profile.get('label',name),reference_audio=str(ref),
                runtime={**runtime,'python':str(python),'model_path':str(model)},
                profile_fingerprint=fingerprint,review_scope=profile.get('review_scope','not recorded'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=default_config())
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('list')
    selected=sub.add_parser('resolve')
    selected.add_argument('profile',nargs='?')
    selected.add_argument('--output',type=Path)
    args=parser.parse_args()
    try:
        if args.command=='list':
            if not args.config.is_file():
                result=dict(configured=False,profiles=[])
            else:
                data=load_config(args.config)
                result=dict(configured=True,default_profile=data.get('default_profile'),
                            candidate_profile=data.get('candidate_profile'),profiles=[
                                dict(id=name,label=item.get('label',name)) for name,item in data['profiles'].items()])
        else:
            result=resolve(args.config,args.profile)
            if args.output:
                args.output.parent.mkdir(parents=True,exist_ok=True)
                temp=args.output.with_name(args.output.name+'.new')
                temp.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
                temp.replace(args.output)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,TypeError) as error:
        parser.exit(1,f'Voice profile failed: {error}\n')


if __name__=='__main__':main()
