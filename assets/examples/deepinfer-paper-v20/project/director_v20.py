"""Continue the same leave request; semantic teaching before layer-state dependencies.
Chinese annotations illustrate information, not measured internal feature decodings.
"""
from PIL import Image,ImageDraw
from director_v19 import Paper as V19,ANCHORS_BY_CUE
from director_v14 import TEAL,BLUE,AMBER,PALE
from director_v10 import ramp
from continuity import WHITE,INK,MUTED,GOLD,CORAL,LINE
WORDS=['小王','想','在','下','周','一','请假','一天','找谁','审批']
class Paper(V19):
 def txt(self,x,y,s,size=48,c=INK,anchor=None):
  s=s.replace('差旅','请假').replace('报销单','请假单')
  s={'附上':'注明','车票':'起止','等':'日期','凭证':'事由'}.get(s,s)
  return super().txt(x,y,s,size,c,anchor)
 def note(self,s,c=MUTED):
  s={'绿色是前层结果这一条主链；蓝色是共享状态这一条旁路':'同一份请假输入：前层信息向下传，共享状态从旁路进入','用同一输入任务比较：是否少等了，以及回答是否受到影响':'用同一份请假任务比较：准备是否更快，审批答复是否受影响'}.get(s,s)
  return super().note(s,c)
 def layer_model(self,c,t):
  self.card((95,265,1500,355),'小王下周一请假一天，找谁审批？',color=BLUE)
  events=['先提取','再组合','假设公司制度'];titles=['提取线索','组合请假事项','联系公司制度'];xs=[95,590,1085]
  for i,x in enumerate(xs):
   active=t>=self.ev(c,events[i],.15+i*.22);color=TEAL if active else LINE
   self.panel((x,395,x+420,705),'semantic-stage-'+str(i),line=color)
   previous=self._parent;self._parent='semantic-stage-'+str(i)
   self.txt(x+210,440,titles[i],46,color,anchor='mm')
   if active:
    if i==0:lines=['申请人：小王','日期：下周一','时长：1天']
    elif i==1:lines=['小王 · 下周一','要请假 1 天','一份完整申请']
    else:lines=['教学制度：≤1天','交给直属主管','答复：直属主管审批' if t>=self.ev(c,'才有依据回答',.7) else '匹配：本次请假1天' if t>=self.ev(c,'把申请中的一天',.6) else '等待对照申请']
    for j,s in enumerate(lines):
     if (i==1 and j==1) or (i==2 and j==0 and t>=self.ev(c,'把申请中的一天',.6)):
      self.d.rounded_rectangle((x+25,482+j*70,x+395,540+j*70),10,fill='#FFF1D6')
     self.txt(x+210,510+j*70,s,40 if i==2 and j==2 else 42,INK if j<2 else TEAL,anchor='mm')
   self._parent=previous
   if i<2:
    a=self.ev(c,events[i+1],.4+i*.2);path=[(x+435,550),(x+480,550)]
    self.arrow(path,TEAL if t>=a else LINE)
    if t>=a:self.packet(path,ramp(t,a,.8),TEAL)
  self.note('信息加工阶段示意 · 多层共同完成，后续利用前面提炼的信息')
 def architecture(self,c,t):
  super().architecture(c,t)

 def grid_base(self):
  self.d.rounded_rectangle((100,275,1490,342),12,fill=BLUE);self.txt(795,308,'完整请假输入已处理 · 共享状态持续参与',46,WHITE,anchor='mm')
  self.d.line((352,342,352,675),fill=BLUE,width=6)
  for row in range(3):
   y=395+row*106;self.txt(100,y+30,f'第 {row+1} 层',44,INK,anchor='lm');self.arrow_line((352,y+30),(398,y+30),BLUE)
   for j in range(10):self.cell(row,j,PALE)
  self.txt(100,704,'文字 →',42,MUTED,anchor='lm')
  for j,s in enumerate(WORDS):self.txt(467+j*104,704,s,42,MUTED,anchor='mm')
 def grid_reading(self,c,t):
  self.grid_base()
  for roi in [(100,275,1490,342),(330,342,410,675)]:self.im.paste(Image.blend(self.bg.crop(roi),self.im.crop(roi),.38),roi)
  self.d=ImageDraw.Draw(self.im);x=425+7*104;a=self.ev(c,'一天',.35)
  if t>=a:
   self.d.rounded_rectangle((x-8,386,x+92,678),12,outline=TEAL,width=5)
   base=self.ev(c,'经过不同层',.5)
   for row in range(3):
    if t>=base+row*.7:
     self.cell(row,7,['#CFF3E7','#A9E5D4','#7CD5BE'][row],TEAL)
     for k,w in enumerate([[46,27,38],[23,52,33],[41,32,53]][row]):
      y=407+row*106+k*13;self.d.rounded_rectangle((x+14,y,x+14+w,y+6),2,fill=TEAL)
     if row<2:self.arrow_line((x+42,465+row*106),(x+42,489+row*106),TEAL)
  self.note('同一个“一天”，各层加工后的状态不同；文字位置保持不变')
 def state_parents(self,positions,omit=False):
  labels={7:'申请类型：请假',8:'时长：1天',9:'询问办理人',10:'办理动作：审批'}
  for i,p in enumerate(positions):
   x=150+i*480;kept=not omit or p>=9;fill='#DDF3EB' if kept else PALE;color=TEAL if kept else MUTED
   self.panel((x,340,x+350,470),'parent-state-'+str(p),fill=fill,line=color if kept else LINE)
   previous=self._parent;self._parent='parent-state-'+str(p)
   self.txt(x+175,378,f'第2层 · {WORDS[p-1]}',44,color,anchor='mm');self.txt(x+175,434,labels[p],40,color,anchor='mm');self._parent=previous
 def state_paths(self,t,start,positions,omit=False):
  for i,p in enumerate(positions):
   if omit and p<9:continue
   path=[(325+i*480,485),(600+i*200,510),(600+i*200,515)];self.arrow(path,TEAL);self.packet(path,ramp(t,start+i*.08,.8),TEAL)
 def state_operator(self,write=False,approx=False):
  self.card((100,530,365,690),'共享状态','前部已算好',BLUE)
  self.card((465,530,1115,690),'第3层 · 继续加工','结合上层加工过的信息',TEAL)
  self.arrow_line((390,610),(435,610),BLUE);self.arrow_line((1135,610),(1165,610),TEAL if write else LINE)
  self.card((1180,530,1510,690),'近似状态 ≈' if approx and write else '新状态' if write else '待算出','审批相关信息' if write else '本层待计算',TEAL if write else BLUE)
 def local_dependencies(self,c,t,widen=False,bounded=False):
  if widen:return super().local_dependencies(c,t,True,False)
  if bounded:
   self.txt(800,289,'放大位置9“找谁”：局部读取限制在近期片段内',44,INK,anchor='mm')
   start=self.ev(c,'片段内的输入',.38);omit=t>=start
   self.state_parents((7,8,9),omit);self.state_operator(t>=start+1.55,True);self.state_paths(t,start,(7,8,9),omit)
   if omit:
    self.d.line((1070,320,1070,510),fill=CORAL,width=5)
    for x in [325,805]:self.txt(x,499,'省略局部读取',40,CORAL,anchor='mm')
   self.note('只省略片段外的局部读取；蓝色共享状态保留 · 状态文字为教学示意')
  else:
   self.txt(800,289,'放大同一句话的最后3个位置，看看信息怎样接着用',44,INK,anchor='mm')
   start=self.ev(c,'第三层读取',.4);write=max(start+1.55,self.ev(c,'形成与请假审批',.6))
   self.state_parents((8,9,10));self.state_operator(t>=write)
   if t>=start:self.state_paths(t,start,(8,9,10))
   self.note('中文说明状态可能携带的信息 · 层间传递的是数值表示，非内部文字')
 def quality_check(self,c,t):
  super().quality_check(c,t)

