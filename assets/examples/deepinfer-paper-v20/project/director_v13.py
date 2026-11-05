"""Local V13 repair: an execution-work question with a matching payoff."""
import director_v12 as kit
from director_v12 import Paper as V12
from director_v11 import event
from director_v10 import ramp
from continuity import WHITE,INK,MUTED,GOLD,LINE,ease,mix
from base import point
TEAL='#087F6E';BLUE='#337DB4'
kit.SUBS.update({
 'baseline-hook':'沿一次回答，看验证工作与缓存重算怎样安排',
 'engine-choice':'vLLM：同类引擎示例 · DeepInfer：官方执行方案',
 'conclusion':'回扣验证预算与缓存恢复，公开代码供适配复用'})

class Paper(V12):
 def two_engines(self,c,t,opening=False):
  if not opening:return super().two_engines(c,t,opening)
  self.pill(170,275,'请求 A',350)
  self.txt(460,380,'同一批 GPU / NPU',48,INK,anchor='mm')
  q=ramp(t,0,.95);self.gpu((150,420,780,680),active=.2+.5*q,label=False)
  path=[(545,312),(760,312),(760,397)];self.arrow(path,TEAL)
  if q<1:
   x,y=point(path,q);self.d.ellipse((x-14,y-14,x+14,y+14),fill=GOLD)
  self.panel((980,285,1490,700),'execution-plan')
  named=t>=event(c,'DeepInfer',.32)
  self.txt(1235,335,'DeepInfer' if named else '怎样安排工作？',52,TEAL if named else INK,anchor='mm')
  self.txt(1235,430,'{ }',80,TEAL if named else MUTED,anchor='mm')
  verify=t>=event(c,'分配验证工作',.76);replay=t>=event(c,'减少重复计算',.88)
  self.card((1010,495,1460,575),'验证预算' if verify else '验证多少？',color=TEAL if verify else GOLD)
  self.card((1010,600,1460,680),'缓存恢复' if replay else '哪些需要重算？',color=TEAL if replay else GOLD)
  self.arrow_line((950,535),(815,535),TEAL);self.txt(880,475,'安排执行',42,TEAL,anchor='mm')
 def open_value(self,c,t):
  self.panel((100,310,685,705),'source');self.txt(392,365,'DeepInfer 源码',54,TEAL,anchor='mm')
  for i,s in enumerate(['验证预算','缓存恢复','执行流程']):
   y=420+i*85;self.d.rounded_rectangle((155,y,625,y+60),10,fill='#E7F1F4');self.txt(390,y+30,s,44,INK,anchor='mm')
  self.card((755,430,975,595),'适配','验证',TEAL)
  self.gpu((1050,440,1500,700),active=.75,label=False);self.txt(1275,345,'自己的部署',50,INK,anchor='mm')
  self.arrow_line((705,510),(735,510),LINE);self.arrow_line((995,510),(1030,510),LINE)
  start=event(c,'修改和复用',.68);q=ramp(t,start,.65);v=ramp(t,start+1.1,.65)
  if 0<q<1:
   x=mix(640,735,q);self.d.rounded_rectangle((x-20,515,x+20,555),7,fill=BLUE)
  if q>=1:
   self.d.ellipse((935,440,962,467),fill=TEAL);self.d.line((941,452,947,459,957,447),fill=WHITE,width=3)
  if 0<v<1:
   x=mix(995,1030,v);self.d.rounded_rectangle((x-18,492,x+18,528),6,fill=TEAL)
 def motion_signature(self,c,t):
  if c['id']=='baseline-hook':
   return (round(max(0,min(.95,t)),6),t>=event(c,'DeepInfer',.32),t>=event(c,'分配验证工作',.76),t>=event(c,'减少重复计算',.88))
  return super().motion_signature(c,t)
