"""Silent actual-time reference preview. No audio, TTS, or original checkout needed."""
import argparse,shutil
from pathlib import Path
import scene
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--cue',default='capacity-question');p.add_argument('--seconds',type=float);p.add_argument('--output',type=Path);a=p.parse_args()
c=next((c for c in scene.load()[2] if c['id']==a.cue),None)
if c is None:p.error('Unknown cue')
if a.seconds is not None:
 if not 0<a.seconds<=c['slot_s']:p.error('seconds must be positive and no longer than the cue')
 c=dict(c,slot_s=a.seconds)
f=scene.Paper();clip,_=scene.visual_clip(f,c,960,15)
out=a.output or Path(__file__).resolve().parent/'out/visual-preview'/f"{a.cue}.mp4";out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(clip,out);print(out)
