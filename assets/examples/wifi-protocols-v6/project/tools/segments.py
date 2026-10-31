"""Resume exact-duration procedural picture segments; no voice or timing estimates."""
from pathlib import Path
import sys,json,hashlib,math,subprocess,os
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scene import frame
import calm
from tools.build_timeline import measure
CACHE=ROOT/'.local/picture-segments';CACHE.mkdir(exist_ok=True)
def key(scene,index,fps,width,height):
 src=[hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['scene.py','drawing.py','shots.json','calm.py','timing-v6.json']]
 return hashlib.sha256(json.dumps([src,scene,index,fps,width,height],ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:18]
def segment(scene,index,fps,width,height):
 q=scene['cues'][0];k=key(scene,index,fps,width,height);path=CACHE/f'{q["id"]}-{k}.mp4'
 if path.is_file():print('cached picture',q['id'],flush=True);return path
 temp=path.with_name(path.stem+f'.{os.getpid()}.part.mp4');count=round(scene['duration_s']*fps)
 p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(fps),'-i','-','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','19' if fps==24 else '24','-pix_fmt','yuv420p',str(temp)],stdin=subprocess.PIPE)
 for n in range(count):
  phase=min(1,max(0,(n/fps-q['start_s'])/max(q['duration_s'],q['action_s'])));p.stdin.write(frame(index,phase,width,height).tobytes())
 p.stdin.close();assert p.wait()==0;temp.replace(path);print('picture',q['id'],f'{count/fps:.2f}s',flush=True);return path

def main():
 plan=json.loads((ROOT/'project.json').read_text());fps=24
 rounded=lambda t:math.ceil((t-1e-9)*fps)/fps
 for i,s in enumerate(plan['scenes']):
  c=s['cues'][0];audio=ROOT/c['audio']
  if not audio.is_file():continue
  duration=measure(audio);lead=rounded(s.get('lead_s',0));tail=rounded(s.get('tail_s',0));slot=rounded(max(duration,c.get('action_s',0))+c.get('hold_s',0))
  scene=dict(id=s['id'],title=s['title'],duration_s=rounded(lead+slot+tail),lead_s=lead,tail_s=tail,cues=[dict(id=c['id'],start_s=round(lead,8),duration_s=duration,action_s=float(c.get('action_s',0)),hold_s=float(c.get('hold_s',0)),slot_s=slot,audio=c['audio'],audio_sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),spoken_text=c['spoken_text'],subtitle=c['subtitle'])])
  # start_s/absolute_start_s are removed in final as they don't affect local rendering.
  segment(scene,i,24,1920,1080)
if __name__=='__main__':main()
