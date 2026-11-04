"""DeepInfer request journey, editable paper cutaway film; uses prepared WAVs, Pillow and FFmpeg.
Run: python scene.py --mode stills|animatic|pilot|draft|final --skill SKILL_DIR
"""
from pathlib import Path
from functools import lru_cache
import argparse, json, math, hashlib, subprocess, sys, random, textwrap, inspect
from PIL import Image, ImageDraw, ImageFont
from director_v10 import Paper

ROOT=Path(__file__).resolve().parent
BG='#F2F9FC'; PAPER='#fffaf0'; INK='#292e39'; MUTED='#686e76'; BLUE='#126782'; GOLD='#b26220'; RED='#ae493c'; LINE='#aaa89d'
import os
FONT=os.environ.get('EXPLAINER_FONT','/System/Library/Fonts/STHeiti Medium.ttc')
def ease(p):
    p=max(0,min(1,p));return p*p*(3-2*p)
def point(path,p):
    lengths=[math.dist(a,b) for a,b in zip(path,path[1:])];left=max(0,min(.999999,p))*sum(lengths)
    for a,b,n in zip(path,path[1:],lengths):
        if left<=n:return (a[0]+(b[0]-a[0])*left/n,a[1]+(b[1]-a[1])*left/n)
        left-=n
    return path[-1]
@lru_cache(None)
def font(size):return ImageFont.truetype(FONT,size)

def caption_parts(s):
    import re
    # Keep Chinese words together at the few longer semantic phrases.
    for a,b in [
        ('看DeepInfer怎样','看DeepInfer，怎样'),
        ('DeepSeek把自家用的推理引擎开源了','DeepSeek把自家用的，推理引擎开源了'),
        ('它为什么可能影响美国AI公司的生意','它为什么可能影响，美国AI公司的生意'),
        ('这些运行方法一旦被更多服务复用','这些运行方法，一旦被更多服务复用'),
        ('如果这趟旅程帮你把模型能力和运行成本连起来','如果这趟旅程，帮你把模型能力和运行成本连起来'),
        ('完整的长期缓存系统没有随这份代码开源','完整的长期缓存系统，没有随这份代码开源'),
        ('窗口注意力缓存有单独的主机内存路径','窗口注意力缓存，有单独的主机内存路径')]:s=s.replace(a,b)
    phrases=[x for x in re.split('[。；，？：、]',s) if x]
    return [a for x in phrases for a in textwrap.wrap(x,16)]

def caption_edges(parts):
    weights=[len(s)+2 for s in parts];total=sum(weights);edges=[0]
    for w in weights:edges.append(edges[-1]+w/total)
    return edges

def load():
    project=json.loads((ROOT/'project.json').read_text());timeline=json.loads((ROOT/'timeline.json').read_text());cues=[]
    lookup={c['id']:c for s in project['scenes'] for c in s['cues']}
    for s in timeline['scenes']:
        for c in s['cues']:cues.append(dict(c, title=lookup[c['id']]['title'], visual=lookup[c['id']]['visual'], chapter=lookup[c['id']]['chapter'],chapter_title=lookup[c['id']]['chapter_title'], start_s=c['absolute_start_s'],source_duration_s=lookup[c['id']]['source_duration_s'],shot_number=lookup[c['id']]['shot_number'],shot_total=lookup[c['id']]['shot_total']))
    return project,timeline,cues

def visual_clip(film,c,width,fps,animatic=False):
    # Reuse explicitly verified silent shots only when local cue data and drawing dependencies match.
    reuse_path=ROOT/'visual-reuse.json'
    if not animatic and width==1920 and fps==30 and reuse_path.exists():
        proof=json.loads(reuse_path.read_text());item=proof['cues'].get(c['id'])
        spec={k:c[k] for k in ['id','title','visual','chapter','chapter_title','spoken_text','duration_s','slot_s','source_duration_s','shot_number','shot_total']}
        deps_ok=all(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha for name,sha in proof['dependencies'].items())
        deps_ok=deps_ok and proof['captions_sha256']==hashlib.sha256((inspect.getsource(caption_parts)+inspect.getsource(caption_edges)).encode()).hexdigest()
        if item and spec==item['spec'] and deps_ok:
            path=ROOT/item['file']
            if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']:return path,True
    # Local time only: a change to an earlier cue doesn't invalidate this shot.
    spec={k:c[k] for k in ['id','title','visual','chapter','chapter_title','spoken_text','duration_s','slot_s','source_duration_s','shot_number','shot_total']}
    deps=b''.join((ROOT/f).read_bytes() for f in ['scene.py','base.py','continuity.py','opening.py','industry.py','director_base.py','director.py','director_v10.py','typography.py'])
    deps+=b''.join(p.read_bytes() for p in sorted((ROOT/'assets/native-icons').glob('*.png')))
    key=hashlib.sha256(json.dumps(dict(cue=spec,width=width,fps=fps,animatic=animatic,renderer=hashlib.sha256(deps).hexdigest()),sort_keys=True).encode()).hexdigest()[:20]
    folder=ROOT/'.local'/'visual-cache';folder.mkdir(parents=True,exist_ok=True);dest=folder/f'{c["id"]}-{key}.mp4'
    if dest.exists():return dest,True
    import os
    staged=dest.with_name(dest.stem+f'.{os.getpid()}.part.mp4');frames=round(c['slot_s']*fps)
    draw_width=1600 if width==1920 else width
    cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{draw_width}x{draw_width*9//16}','-r',str(fps),'-i','-','-an','-vf',f'scale={width}:{width*9//16}:flags=lanczos','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p',str(staged)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for n in range(frames):proc.stdin.write(film.frame(c,n/fps,draw_width,animatic=animatic).tobytes())
    proc.stdin.close()
    if proc.wait():raise RuntimeError('shot encoding failed')
    staged.replace(dest);return dest,False

def run(mode,skill):
    sys.path.insert(0,str(Path(skill)/'scripts'));import master_voice
    project,timeline,cues=load();film=Paper();out=ROOT/'out'/mode;out.mkdir(parents=True,exist_ok=True)
    if mode=='stills':
        for c in cues:film.frame(c,c['duration_s']*.8,static=True).save(out/(c['id']+'.png'))
        sheet=Image.new('RGB',(1200,math.ceil(len(cues)/3)*225),BG)
        for i,c in enumerate(cues):sheet.paste(film.frame(c,c['duration_s']*.8,400,True),((i%3)*400,(i//3)*225))
        sheet.save(out/'contact-sheet.jpg',quality=94);return
    for c in cues:
        source=ROOT/c['audio']
        if not source.is_file():raise ValueError(f"Missing reference narration: {c['audio']}; use stills or preview.py, or restore the exact local WAVs")
        if hashlib.sha256(source.read_bytes()).hexdigest()!=c['audio_sha256']:raise ValueError(f"Changed reference narration: {c['id']}")
    if mode=='pilot':cues=[c for c in cues if c['id'] in ['opening','serial','overlap','repeat-question','cached-decode','capacity-question','fragment-question','lookup','full-question','next-prefix','closing']]
    width=1920 if mode=='final' else 960;fps=30 if mode=='final' else 15
    actual=[];clock=0
    for c in cues:
        frames=math.ceil(c['slot_s']*fps);length=frames/fps
        actual.append(dict(c,start_s=clock,slot_s=length,observation_s=length-max(c['duration_s'],c['action_s']),minimum_observation_s=c['hold_s']))
        clock+=length
    duration=clock+.8;raw=out/'silent.mp4';clips=[]
    for c in actual:
        print(mode,c['id'],round(c['start_s'],2),flush=True)
        clip,cached=visual_clip(film,c,width,fps,mode=='animatic');clips.append(clip)
        if cached:print('  visual cache',flush=True)
    # Same end-frame hold without changing source-audio clocks.
    tail=out/'tail.png';film.frame(actual[-1],actual[-1]['duration_s']+1,width).save(tail)
    tailclip=out/'tail.mp4';subprocess.run(['ffmpeg','-v','error','-y','-loop','1','-i',str(tail),'-t','0.8','-r',str(fps),'-c:v','libx264','-pix_fmt','yuv420p',str(tailclip)],check=True);clips.append(tailclip)
    listing=out/'concat.txt';listing.write_text(''.join("file '"+str(p.resolve())+"'\n" for p in clips))
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(raw)],check=True)
    # Master each changed cue clock once, then reuse it for animatic/draft/final as applicable.
    audio_spec={'clocks':[(c['id'],c['start_s'],c['audio_sha256']) for c in actual],'duration':duration,'preset':project['audio_mastering']}
    audio_key=hashlib.sha256(json.dumps(audio_spec,sort_keys=True).encode()).hexdigest()[:20]
    audio_dir=ROOT/'audio'/'masters'/audio_key;audio_dir.mkdir(parents=True,exist_ok=True)
    master=audio_dir/'narration-mobile.wav';encoded=audio_dir/'narration.m4a'
    if not master.exists():
        narration=audio_dir/'unmastered.wav';master_voice.mix_cues(ROOT,actual,duration,narration)
        master_voice.process(narration,master)
    voice_master=master
    # V6 is voice-only, with no paper accents or background noise track.
    fx_receipt=None
    if not encoded.exists():
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(master),'-c:a','aac','-b:a','192k',str(encoded)],check=True)
    matches=True
    final=out/'video.mp4'
    acodec=['-c:a','copy'] if matches else ['-c:a','aac','-b:a','192k']
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-i',str(encoded),'-map','0:v','-map','1:a','-c:v','copy',*acodec,'-movflags','+faststart','-shortest',str(final)],check=True)
    actual_data=dict(narration=True,fps=fps,project_root='../..',duration_s=duration,cues=actual,audio_mastering=dict(file=str(master.relative_to(ROOT)),sha256=master_voice.digest(master),measured_aac=master_voice.measure(final),voice_master_file=str(voice_master.relative_to(ROOT)),sound_effects_receipt=str(fx_receipt.relative_to(ROOT)) if fx_receipt else None))
    (out/'actual-timeline.json').write_text(json.dumps(actual_data,ensure_ascii=False,indent=2)+'\n')
    def stamp(t):
        n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
    srt=[]
    for c in actual:
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts)
        for j,part in enumerate(parts):
            a=c['start_s']+c['duration_s']*edges[j];b=c['start_s']+c['duration_s']*edges[j+1]
            srt.append(f'{len(srt)+1}\n{stamp(a)} --> {stamp(b)}\n{part}\n')
    (out/'subtitles.srt').write_text('\n'.join(srt))
    print('DONE',final,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['stills','pilot','animatic','draft','final'],required=True);ap.add_argument('--skill',required=True);a=ap.parse_args();run(a.mode,a.skill)
