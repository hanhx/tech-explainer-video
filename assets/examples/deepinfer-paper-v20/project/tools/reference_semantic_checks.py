"""V20 case-specific causal-state regression. No TTS, audio or human grading."""
from pathlib import Path
import json,sys,re
import numpy as np
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));import scene

def main():
 cs={c['id']:c for c in scene.load()[2]};f=scene.Paper()
 def snap(cid,t):
  f._mobile_key=None;im=f.frame(cs[cid],t).copy();return im,[v.get('text','') for v in f.geometry]
 c=cs['model-layers'];a=c['speech_events']['才有依据回答'];_,before=snap(c['id'],a-.1);_,after=snap(c['id'],a+.3)
 assert '答复：直属主管审批' not in before and '答复：直属主管审批' in after
 c=cs['one-dependency'];read=c['speech_events']['第三层读取'];write=max(read+1.55,c['speech_events']['形成与请假审批']);_,before=snap(c['id'],write-.1);exact,after=snap(c['id'],write+.3)
 assert '新状态' not in before and '新状态' in after;assert write>=read+1.55
 c=cs['bounded-replay'];a=c['speech_events']['片段内的输入'];b0,_=snap(c['id'],a-.1);b1,tx=snap(c['id'],a+1.9);assert tx.count('省略局部读取')==2 and '近似状态 ≈' in tx
 roi=(100,530,365,690);assert exact.crop(roi).tobytes()==b1.crop(roi).tobytes()
 def greens(im):
  ar=np.asarray(im.crop((310,480,850,523))).astype(float);return int((np.linalg.norm(ar-np.array([8,127,110]),axis=2)<60).sum())
 assert greens(b1)<greens(b0)*.15
 c=cs['window-expands'];im,_=snap(c['id'],c['duration_s']*.98);ar=np.asarray(im);counts=[int(sum(np.linalg.norm(ar[425+row*106,467+j*104].astype(float)-np.array([255,177,59]))<35 for j in range(10))) for row in range(3)];assert counts==[6,4,2]
 c=cs['batch-reuse'];_,tx=snap(c['id'],c['duration_s']*.98);assert tx.count('算 1 个')==3 and tx.count('计算')==3
 norm=lambda s:''.join(re.findall(r'[a-z0-9\u4e00-\u9fff]',s.lower()))
 caches=0;captions=0
 for c in cs.values():
  assert norm(''.join(scene.caption_parts(c['spoken_text'])))==norm(c['spoken_text'])
  rr=scene.caption_ranges(c);assert len(rr)==len(scene.caption_parts(c['spoken_text']));last=0
  for a,b in rr:assert a>=last-.0001 and b>a and b<=c['duration_s']+.001;last=b;captions+=1
  _,tx=snap(c['id'],c['duration_s']*.98);assert not any('差旅' in v or '苹果' in v or '小王属于研发部' in v for v in tx)
  times=[0,c['duration_s']*.5,c['duration_s']*.98]
  for e in c.get('speech_events',{}).values():times += [max(0,e-.02),min(c['slot_s']-.01,e+.02),min(c['slot_s']-.01,e+.8),min(c['slot_s']-.01,e+1.6)]
  for t in sorted(set(round(v,6) for v in times)):
   f._mobile_key=None;f.frame(c,t);cached=f.frame(c,t+.01).copy();f._mobile_key=None;fresh=f.frame(c,t+.01).copy();assert cached.tobytes()==fresh.tobytes(),(c['id'],t);caches+=1
 out=R/'checks';out.mkdir(exist_ok=True);report={'passed':True,'cue_count':len(cs),'caption_intervals':captions,'cache_fresh_pairs':caches,'window_counts':counts,'equal_work_comparison':'3 positions on each side','global_shared_region_unchanged':True,'omitted_path_green_pixels':[greens(b0),greens(b1)],'scope':'V20 source state order, geometry text and supplied cache samples only; not all-frame encoded review, internal model interpretation or human comprehension.'};(out/'reference-semantics.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
