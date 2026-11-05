"""Problem → execution work → bandwidth opportunity → dependency → draft.
Native original paper art. No reference creator assets or audio are used.
"""
from pathlib import Path
import json
from PIL import Image,ImageDraw
import director_v14 as prior
from director_v14 import Paper as Kit,TEAL,BLUE,AMBER,PALE
from director_v10 import ramp
from continuity import BG,WHITE,INK,MUTED,GOLD,CORAL,LINE,mix

ROOT=Path(__file__).resolve().parent
ANCHORS_BY_CUE=json.loads((ROOT/'visual-anchors.json').read_text())
prior.CHAPTERS=['模型为何花钱','一轮怎样计算','草稿带来什么','验证怎样安排','长输入怎样算','开源怎样复用']
prior.STARTS={'service-question','follow-one-answer','unknown-next'}

class Paper(Kit):
 def person(self,x,y,color=TEAL,label='员工',scale=1):
  s=scale
  self.d.ellipse((x-27*s,y-78*s,x+27*s,y-24*s),fill=WHITE,outline=color,width=max(3,round(5*s)))
  self.d.arc((x-64*s,y-18*s,x+64*s,y+95*s),180,360,fill=color,width=max(3,round(6*s)))
  self.d.line((x-64*s,y+37*s,x-64*s,y+70*s),fill=color,width=max(3,round(6*s)));self.d.line((x+64*s,y+37*s,x+64*s,y+70*s),fill=color,width=max(3,round(6*s)))
  self.txt(x,y+108*s,label,44,color,anchor='mm')
 def clock_icon(self,x,y):
  self.d.ellipse((x-24,y-24,x+24,y+24),fill=WHITE,outline=AMBER,width=4);self.d.line((x,y-15,x,y,x+12,y+7),fill=AMBER,width=4)
 def packet(self,path,q,color=GOLD):
  from base import point
  if 0<q<1:
   x,y=point(path,q);self.d.rounded_rectangle((x-22,y-18,x+22,y+18),6,fill=color,outline=INK,width=2)
 def machine(self,b=(850,325,1500,700)):
  x,y,X,Y=b;self.panel(b,'machine',line=BLUE)
  self.txt((x+X)/2,y+45,'模型执行设备',48,INK,anchor='mm')
  self.d.rounded_rectangle((x+35,y+90,X-35,y+164),12,fill=BLUE);self.txt((x+X)/2,y+127,'已有模型参数',44,WHITE,anchor='mm')
  self.panel((x+100,y+205,X-100,Y-35),'machine-compute',line=BLUE);self.txt((x+X)/2,y+245,'计算单元',48,INK,anchor='mm')
 def service(self,c,t,work=False):
  self.person(155,465)
  self.panel((280,300,710,665),'chat');self.txt(495,352,'公司内部助手',48,TEAL,anchor='mm')
  self.d.rounded_rectangle((310,405,680,490),12,fill='#FFF1D6');self.txt(495,447,'差旅怎么申请？',44,INK,anchor='mm')
  self.machine();path=[(730,470),(810,470),(810,610),(950,610)];self.arrow(path,LINE)
  if work:
   a=self.ev(c,'每问一句',.08);q=ramp(t,a,1.0);self.packet(path,q)
   r=self.ev(c,'读取参数',.24);read=ramp(t,r,.9)
   self.arrow_line((1175,490),(1175,510),BLUE);self.packet([(1175,490),(1175,510),(1175,565)],read,BLUE)
   calc=self.ev(c,'做运算',.4);p=ramp(t,calc,.85)
   if t>=calc:
    self.d.rounded_rectangle((1010,620,1340,644),8,fill=PALE)
    if p>0:self.d.rounded_rectangle((1010,620,1010+330*p,644),8,fill=TEAL)
   answer=self.ev(c,'生成回答',.55);a2=ramp(t,answer,.85)
   back=[(830,680),(750,680),(750,570),(710,570)]
   if t>=answer:self.arrow(back,TEAL);self.packet(back,a2,TEAL)
   if a2>=1:
    self.d.rounded_rectangle((310,545,680,610),12,fill='#DDF3EB');self.txt(495,578,'请先填写申请单',44,TEAL,anchor='mm')
   if t>=self.ev(c,'反复用',.75):
    self.clock_icon(365,739);self.txt(410,739,'设备工作时间',42,AMBER,anchor='lm');self.txt(1080,739,'用电与设备开销',42,AMBER,anchor='mm')
  else:
   q=ramp(t,.35,1.15);self.packet(path,q)
   if q>=1:self.clock_icon(1175,680)
   self.note('模型文件已有；一次回答还需要执行工作')
 def queue(self,c,t):
  many=t>=self.ev(c,'人一多',.02);waiting=t>=self.ev(c,'排队',.4)
  for i in range(3 if many else 1):
   y=315+i*135;self.person(160,y+28,TEAL if i==0 else BLUE,f'员工{["甲","乙","丙"][i]}',scale=.55)
   self.fragment(315,y-10,340,['差旅怎么申请','假期怎么申请','报销需要什么'][i],GOLD,INK,82)
   if i and waiting:self.clock_icon(700,y+30)
  self.gpu((900,420,1490,675),active=.85,label=False);self.txt(1195,350,'当前请求在执行',48,BLUE,anchor='mm')
  q=.1+.65*ramp(t,self.ev(c,'排队',.4),3.2)
  self.d.rounded_rectangle((950,385,1450,403),6,fill=PALE);self.d.rounded_rectangle((950,385,950+500*q,403),6,fill=BLUE)
  self.arrow_line((760,525),(865,525),BLUE)
  if t>=self.ev(c,'现有机器',.8):
   self.d.rounded_rectangle((875,390,1510,710),20,outline=TEAL,width=5);self.note('研究同一批设备上的工作安排',TEAL)
  elif t>=self.ev(c,'增加资源',.57):self.note('增加资源，或改善执行安排')
  else:self.note('请求增多时，服务可能开始排队 · 教学情景')
 def engine(self,c,t):
  self.person(160,470);self.arrow_line((265,500),(430,500),LINE)
  self.card((465,365,1015,650),'DeepInfer' if t>=self.ev(c,'DeepInfer',.49) else '推理引擎','组织模型执行',TEAL)
  if t>=self.ev(c,'DeepInfer',.49):self.txt(740,305,'同类的另一份实现',46,BLUE,anchor='mm')
  elif t>=self.ev(c,'vLLM',.29):self.txt(740,305,'例如 vLLM',48,BLUE,anchor='mm')
  self.arrow_line((1045,500),(1135,500),TEAL);self.gpu((1175,405,1500,640),active=.8,label=False)
  if t>=self.ev(c,'主要基于',.83):self.note('DeepInfer 最初主要基于 vLLM 开发')
  else:self.note('开源执行实现，供检查、复现与适配')
 def follow(self,c,t):
  self.pill(90,280,'同一条请求',320);self.card((100,430,600,650),'差旅怎么申请？',color=TEAL)
  self.arrow_line((630,535),(720,535),BLUE);self.gpu((760,420,1220,670),active=.8,label=False)
  self.txt(1410,535,'……',70,TEAL,anchor='mm');self.arrow_line((1250,535),(1320,535),TEAL)
  self.note('把接下来要生成的内容，一步一步展开')
 def serial(self,c,t):
  starts=[.3,self.ev(c,'前一段',.45),self.ev(c,'新一轮计算',.7)]
  starts[1]=max(starts[1],starts[0]+1.4);starts[2]=max(starts[2],starts[1]+1.4)
  r=max([i for i,a in enumerate(starts) if t>=a] or [0]);q=ramp(t,starts[r],.8)
  self.panel((95,365,520,620),'known');self.txt(307,410,'本轮已知',48,INK,anchor='mm')
  self.txt(307,480,'提问 + 已有前文',44,MUTED,anchor='mm')
  labels=['请先','填写','申请单']
  if r:
   for i in range(r):self.fragment(130+i*180,530,160,labels[i],TEAL,WHITE,64)
  self.arrow_line((550,500),(640,500),BLUE);self.card((670,365,1060,620),'主模型','本轮计算',BLUE)
  self.d.rounded_rectangle((710,565,1020,591),8,fill=PALE)
  if q>0:self.d.rounded_rectangle((710,565,710+310*q,591),8,fill=BLUE)
  self.arrow_line((1090,500),(1180,500),TEAL);self.panel((1210,365,1500,620),'new-fragment');self.txt(1355,410,'采样下一段',44,TEAL,anchor='mm')
  if q>=1:self.fragment(1250,485,210,labels[r],TEAL,WHITE)
  else:self.txt(1355,525,'待确定',48,MUTED,anchor='mm')
  for i in range(3):
   x=390+i*400;self.txt(x,685,f'第 {i+1} 轮',46,TEAL if i==r else MUTED,anchor='mm')
  self.note('前文状态可缓存；新词元仍需一轮主模型计算')
 def hardware(self,c,t,batch=False,unknown=False):
  self.panel((95,285,1500,705),'gpu-inside',line=BLUE);self.txt(800,330,'GPU 内部 · 简化示意',48,INK,anchor='mm')
  self.panel((145,395,585,660),'hbm',line=BLUE);self.txt(365,438,'显存 · 模型参数',44,BLUE,anchor='mm')
  for j in range(16):
   x=185+(j%4)*90;y=480+(j//4)*37;self.d.rounded_rectangle((x,y,x+65,y+25),4,fill=BLUE)
  self.panel((955,395,1460,660),'compute',line=TEAL);self.txt(1207,438,'计算单元',46,INK,anchor='mm')
  self.arrow_line((615,530),(925,530),BLUE);self.txt(770,475,'读取参数',44,BLUE,anchor='mm')
  read=self.ev(c,'复用这批权重',.4) if batch else self.ev(c,'读到这些参数',.32)
  q=ramp(t,read,1.0)
  if not unknown:self.packet([(615,530),(925,530)],q,BLUE)
  count=3 if batch else 1
  for i in range(count):
   x=980+i*155 if batch else 1120
   if not unknown:
    self.fragment(x,490,130,['请先','填写','表格'][i] if batch else '前文',GOLD,INK,70)
    if t>=read+1.0:self.txt(x+65,605,'已计算',42,TEAL,anchor='mm')
  self.txt(1207,370,'后续输入未知' if unknown else '已知输入位置' if batch else '本轮已知输入',44,MUTED,anchor='mm')
  if not unknown:self.note('同批已知位置复用权重，摊薄搬运开销' if batch else '参数留在显存；计算单元读取后执行运算')
 def unknown(self,c,t):
  self.hardware(c,t,True,True);a=self.ev(c,'先采样前一个',.5);q=ramp(t,a+.2,.85)
  self.fragment(980,490,130,'前文',GOLD,INK,70)
  self.fragment(1135,490,130,'请先' if q>=1 else '？',GOLD if q>=1 else PALE,INK if q>=1 else MUTED,70)
  self.fragment(1290,490,130,'？',PALE,MUTED,70)
  self.txt(1045,605,'请先' if t>=a else '待采样',42,TEAL if t>=a else MUTED,anchor='mm')
  self.txt(1200,605,'待计算' if q>=1 else '未知',42,MUTED,anchor='mm');self.txt(1355,605,'未知',42,MUTED,anchor='mm')
  if t>=a:
   path=[(1045,635),(1045,680),(1120,680),(1120,525),(1127,525)];self.arrow(path,TEAL);self.packet(path,q,TEAL)
  self.note('前一个采样落定，后一个位置的输入才随之确定')
 def draft(self,c,t,reject=False):
  self.card((90,290,390,455),'草稿模型','先提候选',AMBER)
  words=['请先','填写','申请单','再','提交']
  given=self.ev(c,'候选都已给定',.35);calc=self.ev(c,'计算概率',.6)
  for i,s in enumerate(words):
   x=450+i*205;visible=reject or t>=self.ev(c,'草稿模型',.08)+.35+i*.16
   fill=GOLD;ink=INK
   if reject:
    if i<2 and t>=self.ev(c,'前两个通过',.05):fill=TEAL;ink=WHITE
    if i>=2 and t>=self.ev(c,'第三个被拒绝',.2):fill=PALE;ink=MUTED
   if visible:
    self.fragment(x,300,180,s,fill,ink)
    if reject and i==2 and t>=self.ev(c,'第三个被拒绝',.2):self.d.line((x+12,310,x+168,372),fill=CORAL,width=4)
    if reject and i>2 and t>=self.ev(c,'失效',.35):self.d.line((x+14,341,x+166,341),fill=MUTED,width=4)
   if reject or t>=given:self.arrow_line((x+90,397),(x+90,438),BLUE)
  self.panel((445,450,1495,610),'main',line=BLUE);self.txt(970,490,'主模型 · 运行网络',48,BLUE,anchor='mm')
  if reject or t>=calc:
   for i in range(5):self.txt(540+i*205,558,f'概率 {i+1}',44,BLUE,anchor='mm')
  elif t>=given:
   p=ramp(t,given,.85);self.d.rounded_rectangle((480,540,1460,570),8,fill=PALE)
   if p>0:self.d.rounded_rectangle((480,540,480+980*p,570),8,fill=BLUE)
  if reject:
   self.txt(450,681,'正式输出',44,TEAL,anchor='lm')
   for i in range(2):
    if t>=self.ev(c,'前两个通过',.05):self.fragment(680+i*205,640,180,words[i],TEAL,WHITE)
   if t>=self.ev(c,'补出词元',.5):self.fragment(1090,640,180,'报销单',BLUE,WHITE)
   self.note('有效输出要和草稿、验证的总开销一起看')
  else:self.note('给定候选 → 主模型计算概率 → 按规则接纳')
 def dspark(self,c,t):
  self.pill(95,275,'下一轮 · 验证前',460)
  for i,s in enumerate(['请先','填写','申请单','再','提交']):self.fragment(120+i*282,410,245,s,GOLD,INK)
  self.card((125,585,650,705),'送去验证多少？',color=BLUE);self.card((935,585,1470,705),'留下多少有效输出？',color=TEAL)
  self.txt(800,645,'权衡',48,INK,anchor='mm');self.note('DSpark：结合接受预测与设备效率选择长度')
 def motion_signature(self,c,t):
  points=[0,.3,.8,1.2,2.0,3.0]
  points.extend(self.ev(c,s) for s in ANCHORS_BY_CUE[c['id']])
  return tuple(round(max(0,min(4,t-a)),6) for a in points)
 def frame(self,c,elapsed,width=1600,static=False,animatic=False):
  from scene import caption_ranges
  t=c['duration_s']*.98 if static or animatic else elapsed;ranges=caption_ranges(c);cap=next((i for i,(a,b) in enumerate(ranges) if elapsed<b),len(ranges)-1)
  key=(c['id'],self.motion_signature(c,t),round(self.nav_offset(c,t),6),width,cap,static,animatic)
  if key==getattr(self,'_mobile_key',None):return self._mobile_frame
  self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.geometry=[];self._parent=None
  actions={'service-question':lambda:self.service(c,t),'request-compute':lambda:self.service(c,t,True),'queue-pressure':lambda:self.queue(c,t),'engine-purpose':lambda:self.engine(c,t),'follow-one-answer':lambda:self.follow(c,t),'serial-calls':lambda:self.serial(c,t),'read-weights':lambda:self.hardware(c,t),'batch-reuse':lambda:self.hardware(c,t,True),'unknown-next':lambda:self.unknown(c,t),'draft-known':lambda:self.draft(c,t),'accepted-output':lambda:self.draft(c,t,True),'dspark-question':lambda:self.dspark(c,t)}
  actions[c['id']]();self.header(c,t);self.footer(c,elapsed)
  if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
  self._mobile_key=key;self._mobile_frame=self.im;return self.im
