"""Check text against the final canvas and stationary world viewport, not comprehension."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import scene
records=[];original=scene.Canvas.text;original_rect=scene.Canvas.rect

def rect(self,x,y,w,h,fill=None,color=scene.INK,width=2,r=15):
 result=original_rect(self,x,y,w,h,fill,color,width,r)
 if fill is not None:
  world=self.im.width==3200
  records[:]=[v for v in records if not (v["world"]==world and v["bounds"][0]>=x and v["bounds"][1]>=y and v["bounds"][2]<=x+w and v["bounds"][3]<=y+h)]
 return result
scene.Canvas.rect=rect

def text(self,x,y,t,size=28,color=scene.INK,anchor='lt',mono=False):
 if '\n' not in t:
  f=scene.font(round(size*self.s),mono and all(ord(c)<128 for c in t));b=self.d.textbbox((round(x*self.s),round(y*self.s)),t,font=f,anchor=anchor)
  records.append(dict(world=self.im.width==3200,text=t,bounds=[v/self.s for v in b]))
 return original(self,x,y,t,size,color,anchor,mono)
scene.Canvas.text=text
violations=[];checked=0
for i,s in enumerate(scene.SHOTS):
 for p in [.32,.72,.98]:
  records.clear();scene.world_base.cache_clear();c=scene.Canvas();scene.hud(c,i,p);w,cam=scene.world(i,p)
  for r in records:
   b=r['bounds'];v=cam if r['world'] else (0,0,1600,900)
   x,y,width,height=v;intersection=max(0,min(b[2],x+width)-max(b[0],x))*max(0,min(b[3],y+height)-max(b[1],y))
   area=(b[2]-b[0])*(b[3]-b[1])
   if intersection==0:continue
   checked+=1
   # Partly visible labels during a camera move are not a stationary-layout failure.
   if intersection<area*.97:violations.append(dict(id=s['id'],p=p,**r,viewport=list(v)))
report=dict(samples=len(scene.SHOTS)*3,texts_checked=checked,partly_clipped_text=violations,scope='Visible text at .32/.72/.98 world-phase samples, ignoring text fully covered by later opaque rectangles. Does not test every frame or detect all overlaps.')
(ROOT/'checks/text-bounds.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(checked=checked,partly_clipped=violations),ensure_ascii=False))
