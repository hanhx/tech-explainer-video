"""Editable, supersampled native icons with matching rounded strokes and geometry."""
from pathlib import Path
import math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'assets/native-icons';out.mkdir(parents=True,exist_ok=True)
S=4
def point(p):return tuple(v*S for v in p)
def cubic(p0,p1,p2,p3,n=24):
 return [tuple((1-t)**3*p0[j]+3*(1-t)**2*t*p1[j]+3*(1-t)*t*t*p2[j]+t**3*p3[j] for j in [0,1]) for t in [k/n for k in range(n+1)]]
def rounded_line(d,pts,color,width=7):
 d.line([point(p) for p in pts],fill=color,width=width*S,joint='curve')
 for p in [pts[0],pts[-1]]:
  x,y=point(p);r=width*S/2;d.ellipse((x-r,y-r,x+r,y+r),fill=color)
for name,color,fill in [('like','#087F6E','#DDF4EA'),('save','#AB7010','#FFF1C9'),('follow','#2B6DA4','#E2EFFB')]:
 im=Image.new('RGBA',(256*S,256*S),(0,0,0,0));d=ImageDraw.Draw(im)
 if name=='like':
  pts=[(82,209),(82,118)]
  for curve in [((82,118),(82,108),(88,102),(98,98)),((98,98),(118,89),(126,64),(131,41)),((131,41),(133,30),(146,32),(152,42)),((152,42),(162,58),(157,80),(152,98))]:pts+=cubic(*curve)
  pts += [(196,98)];pts+=cubic((196,98),(213,98),(221,111),(217,126));pts += [(201,193)];pts+=cubic((201,193),(198,204),(191,210),(179,210));pts += [(82,209)]
  d.polygon([point(p) for p in pts],fill=fill);rounded_line(d,pts,color)
  d.rounded_rectangle(tuple(v*S for v in (39,108,79,211)),radius=10*S,fill='white',outline=color,width=7*S)
  d.ellipse(tuple(v*S for v in (53,188,62,197)),fill=color)
 elif name=='save':
  vertices=[(128+(83 if i%2==0 else 39)*math.cos(-math.pi/2+i*math.pi/5),126+(83 if i%2==0 else 39)*math.sin(-math.pi/2+i*math.pi/5)) for i in range(10)]
  pts=[]
  for i,v in enumerate(vertices):
   prev=vertices[i-1];nxt=vertices[(i+1)%10];a=(v[0]+(prev[0]-v[0])*.12,v[1]+(prev[1]-v[1])*.12);b=(v[0]+(nxt[0]-v[0])*.12,v[1]+(nxt[1]-v[1])*.12)
   pts.append(a);pts+=cubic(a,v,v,b,n=8)
  pts.append(pts[0]);d.polygon([point(p) for p in pts],fill=fill);rounded_line(d,pts,color)
 else:
  d.ellipse(tuple(v*S for v in (61,31,133,103)),fill=fill,outline=color,width=7*S)
  pts=cubic((30,207),(30,153),(66,128),(101,128))+cubic((101,128),(137,128),(168,153),(169,193))
  rounded_line(d,pts,color,7)
  d.ellipse(tuple(v*S for v in (145,146,227,228)),fill=color)
  rounded_line(d,[(186,166),(186,207)],'white',6);rounded_line(d,[(166,187),(206,187)],'white',6)
 im.resize((512,512),Image.Resampling.LANCZOS).save(out/(name+'.png'))
print('Three native 512px icons drawn from editable curves.')
