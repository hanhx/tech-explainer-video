"""Owner-bound checks for hardware labels and data cards, rather than canvas edges only."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import scene,calm
issues=[];records=[];current=None;orig_text=scene.Canvas.text;orig_card=calm.card

def text(self,x,y,t,size=28,color=scene.INK,anchor='lt',mono=False):
 f=scene.font(round(size*self.s),mono and all(ord(c)<128 for c in t));b=self.d.textbbox((round(x*self.s),round(y*self.s)),t,font=f,anchor=anchor)
 records.append(dict(text=t,bounds=[z/self.s for z in b],owner=current))
 return orig_text(self,x,y,t,size,color,anchor,mono)
scene.Canvas.text=text

def inside(rec,box,pad=4):
 x,y,w,h=box;l,top,r,b=rec['bounds'];return l>=x+pad and top>=y+pad and r<=x+w-pad and b<=y+h-pad
owners={'无线网卡':(130,460,125,76),'B':(130,460,125,76),'有线接口':(285,460,125,76),'A':(285,460,125,76),'浏览器 / 系统程序':(144,290,272,112),'无线接入点 AP':(825,315,180,72),'Home Wi-Fi':(825,315,180,72),'DHCP 服务':(825,409,180,68),'192.168.1.1':(825,409,180,68),'LAN / 网关':(805,295,220,250),'WAN':(805,295,220,250)}
c=scene.Canvas(3200,1800);scene.computer(c);scene.gateway(c)
for r in records:
 if r['text'] in owners and not inside(r,owners[r['text']]):issues.append(dict(type='hardware label outside owner',**r))
hardware=len(records);records.clear();card_count=0

def card(c,x,y,w,h,label,value,co=calm.GREEN,fade=1):
 global current,card_count
 old=current;current=[x,y,w,h];n=len(records);out=orig_card(c,x,y,w,h,label,value,co,fade);rr=records[n:];current=old;card_count+=1
 for r in rr:
  if not inside(r,[x,y,w,h],6):issues.append(dict(type='card text outside owner',**r))
 if len(rr)==2:
  a,b=[r['bounds'] for r in rr];overlap=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
  if overlap>0:issues.append(dict(type='card label/value overlap',label=label,value=value,bounds=[a,b]))
 return out
calm.card=card
for i in range(len(scene.SHOTS)):
 for p in [.2,.6,.99]:scene.frame(i,p,640,360)
report=dict(shots=26,phases_per_shot=3,hardware_texts=hardware,card_occurrences=card_count,violations=issues,scope='Hardware labels within explicit parent boxes and individual cards at sampled phases; does not prove all inter-object overlaps absent')
(ROOT/'checks/component-layout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
if issues:raise SystemExit(1)
