"""Complete causal film. The accepted V15 operations are inherited unchanged.
New mechanisms keep persistent objects and attach each action to measured speech.
"""
from pathlib import Path
import json
from PIL import Image,ImageDraw
from director_v15 import Paper as Pilot,ANCHORS_BY_CUE
import director_v14 as prior
from director_v14 import TEAL,BLUE,AMBER,PALE,blend
from director_v10 import ramp,icon
from continuity import BG,WHITE,INK,MUTED,GOLD,CORAL,LINE,mix
prior.STARTS={'service-question','follow-one-answer','unknown-next','fixed-waste','return-input','service-payoff'}
OLD={'service-question','request-compute','queue-pressure','engine-purpose','follow-one-answer','serial-calls','read-weights','batch-reuse','unknown-next','draft-known','accepted-output','dspark-question'}
WORDS=['请先','填写','申请单','再','提交']
NEXT_WORDS=['并','附上','车票','等','凭证']

class Paper(Pilot):
 def dspark(self,c,t):
  self.pill(95,275,'下一轮 · 验证前',460)
  self.candidate_row(410,words=NEXT_WORDS)
  self.card((125,585,650,705),'送去验证多少？',color=BLUE);self.card((935,585,1470,705),'留下多少有效输出？',color=TEAL)
  self.txt(800,645,'权衡',48,INK,anchor='mm');self.note('DSpark：结合接受预测与设备效率选择长度')
 def candidate_row(self,y=410,reject=False,c=None,t=0,words=WORDS):
  for i,s in enumerate(words):
   fill=TEAL if reject and i<2 else PALE if reject else GOLD
   self.fragment(120+i*282,y,245,s,fill,WHITE if fill==TEAL else MUTED if reject else INK)
   if reject and i==2:self.d.line((700,y+8,905,y+72),fill=CORAL,width=5)
   if reject and i>2:self.d.line((120+i*282+22,y+41,120+i*282+223,y+41),fill=MUTED,width=4)
 def fixed_waste(self,c,t):
  self.pill(95,275,'回看 · 刚才这一轮',485)
  done=t>=self.ev(c,'前两个',.32)
  self.candidate_row(410,done)
  self.txt(800,365,'送验 5 个 → 主模型计算',48,BLUE,anchor='mm')
  if done:
   self.d.rounded_rectangle((110,519,656,636),16,outline=TEAL,width=4);self.txt(383,577,'接纳前 2 个',48,TEAL,anchor='mm')
  if t>=self.ev(c,'后两个',.45):
   self.txt(806,577,'拒绝点',44,CORAL,anchor='mm');self.d.rounded_rectangle((956,519,1490,636),16,outline=CORAL,width=4);self.txt(1223,577,'后两个：算过，未留下',44,CORAL,anchor='mm')
  self.note('先看已经发生的结果，再决定下一轮怎样分配')
 def predict(self,c,t):
  self.pill(95,275,'下一轮 · 验证前',485);self.candidate_row(410,words=NEXT_WORDS)
  self.txt(800,365,'候选都在；接纳结果还没出来',48,INK,anchor='mm')
  if t>=self.ev(c,'置信度预测模块',.28):
   self.txt(800,678,'预计接受可能性 · 教学示意',44,BLUE,anchor='mm')
   probs=[.92,.84,.58,.3,.15]
   for i,v in enumerate(probs):
    x=120+i*282;q=ramp(t,self.ev(c,'置信度预测模块',.28)+i*.12,.7)
    self.d.rounded_rectangle((x,535,x+245,556),6,fill=PALE)
    if q>0:self.d.rounded_rectangle((x,535,x+245*v*q,556),6,fill=BLUE)
    self.txt(x+122,615,['较高','较高','下降','较低','更低'][i],44,BLUE,anchor='mm')
  self.note('预测条长短为教学示意；实际结果仍由验证决定')
 def hardware_choice(self,c,t):
  self.candidate_row(305,words=NEXT_WORDS)
  self.panel((100,450,845,700),'profile-bars');self.txt(472,495,'设备用时 · 示意',48,BLUE,anchor='mm')
  for j,(label,w) in enumerate([('验 3 个',275),('验 5 个',375)]):
   y=560+j*80;self.txt(260,y,label,46,INK,anchor='rm');self.d.rounded_rectangle((295,y-18,295+w,y+18),8,fill=BLUE if j==0 else TEAL)
  self.card((985,450,1495,700),'预计有效输出','与设备用时一起权衡',TEAL)
  self.arrow_line((870,575),(952,575),TEAL)
  self.note('批量用时可能非线性；实际曲线须在设备上测量')
 def allocation(self,c,t):
  add=t>=self.ev(c,'另一条请求',.08);choose=t>=self.ev(c,'不同长度',.6);send=self.ev(c,'同一轮验证',.87)
  for row in range(2 if add else 1):
   y=340+row*174;self.txt(170,y+40,f'请求 {"AB"[row]}',46,TEAL if row==0 else BLUE,anchor='mm')
   for i,s in enumerate(NEXT_WORDS if row==0 else ['请','提交','请假单','给','主管']):
    x=350+i*225;selected=choose and i<(2 if row==0 else 4)
    self.fragment(x,y,195,s,GOLD if not choose or selected else PALE,INK if not choose or selected else MUTED)
    if selected:self.d.rounded_rectangle((x-5,y-5,x+200,y+87),16,outline=BLUE,width=4)
   self.txt(170,y+110,('送验 2 个' if row==0 else '送验 4 个') if choose else ('后段预期低' if row==0 else '后段预期高'),42,BLUE,anchor='mm')
  if t>=send:
   self.d.rounded_rectangle((460,664,1435,718),12,fill=BLUE);self.txt(948,691,'同一轮主模型验证 · 连续前缀',44,WHITE,anchor='mm')
   self.arrow([(660,435),(660,475),(1530,475),(1530,691),(1450,691)],BLUE)
   self.arrow([(900,605),(900,635),(1490,635),(1490,691),(1450,691)],BLUE)
  self.note('示例分配不是实测；预测与设备条件改变，长度也会改变')
 def payoff(self,c,t):
  self.pill(95,275,'同配置 · 两种验证策略',610)
  cols=[(610,'固定 5'),(1210,'动态长度')]
  for x,s in cols:self.txt(x,383,s,50,BLUE if x==610 else TEAL,anchor='mm')
  rows=[('平均送验', '5.00','3.58','少验了一些'),('平均接纳','3.30','3.21','平均接纳量略降')]
  for i,(label,a,b,phrase) in enumerate(rows):
   y=480+i*92;self.txt(125,y,label,46,INK,anchor='lm')
   if t>=self.ev(c,phrase,.4+i*.15):
    for x,v in [(610,a),(1210,b)]:self.txt(x,y,v,58,BLUE if x==610 else TEAL,anchor='mm')
  if t>=self.ev(c,'百分之五点四',.7):
   self.d.rounded_rectangle((380,645,1420,714),14,fill='#DDF3EB');self.txt(900,679,'估算吞吐：13,730 → 14,466（+5.4%）',46,TEAL,anchor='mm')
  self.note('官方 EP64/DP64 · 60 并发/rank · 吞吐单位：词元/秒/rank')
 def input_return(self,c,t):
  self.txt(350,295,'处理输入',48,TEAL,anchor='mm');self.txt(1230,295,'逐步生成回答',48,MUTED,anchor='mm')
  self.arrow_line((580,295),(1000,295),LINE)
  a=self.ev(c,'倒回',.25);q=ramp(t,a,1)
  self.d.ellipse((mix(1205,325,q),330,mix(1255,375,q),380),fill=TEAL)
  if t>=a:self.txt(800,365,'时间倒回 ←',44,TEAL,anchor='mm')
  self.panel((100,430,630,700),'policy-doc');self.txt(365,480,'公司差旅制度',50,BLUE,anchor='mm')
  for j in range(3):self.d.rounded_rectangle((155,530+j*35,565-j*24,541+j*35),5,fill=LINE)
  self.txt(365,660,'+ 差旅怎么申请？',44,INK,anchor='mm')
  self.arrow_line((660,555),(800,555),BLUE);self.card((835,430,1480,700),'模型处理输入','准备生成要用的状态',TEAL)
  self.note('先补回生成之前的工作，再研究长输入怎样少算')
 def kv(self,c,t):
  self.card((90,320,400,530),'长输入','差旅制度',BLUE)
  self.card((590,320,1000,530),'模型计算','逐层处理',BLUE)
  self.arrow_line((425,425),(560,425),BLUE);self.packet([(425,425),(560,425)],ramp(t,.4,1),BLUE)
  self.panel((1160,280,1500,705),'memory-kv',line=BLUE);self.txt(1330,330,'显存',50,BLUE,anchor='mm')
  self.d.rounded_rectangle((1190,380,1470,445),10,fill=BLUE);self.txt(1330,413,'模型参数',44,WHITE,anchor='mm')
  named=t>=self.ev(c,'KV状态',.28)
  if named:
   for j in range(3):self.fragment(1200,475+j*65,260,['KV 状态','KV 状态','KV 状态'][j],GOLD,INK,52)
  self.arrow_line((1030,485),(1130,485),AMBER);self.packet([(1030,485),(1130,485)],ramp(t,self.ev(c,'中间结果',.18),1),GOLD)
  if t>=self.ev(c,'下一个词元',.55):
   self.fragment(125,620,300,'新的词元',TEAL,WHITE,66)
   self.arrow([(450,653),(795,653),(795,560)],TEAL)
   self.arrow([(1140,610),(1050,610),(1050,575),(965,575),(965,555)],AMBER)
   self.txt(795,686,'新输入 + 已有中间状态 → 继续算',44,TEAL,anchor='mm')
  self.note('普通 KV 缓存是已有基础；这里存中间结果，不存完整答案')
 def architecture(self,c,t):
  self.card((95,350,545,660),'前部层','处理完整输入',BLUE)
  a=self.ev(c,'共享的全局状态',.35)
  if t>=a:
   self.arrow_line((575,435),(680,435),BLUE);self.d.rounded_rectangle((710,300,1450,365),12,fill=BLUE);self.txt(1080,332,'共享的全局状态',48,WHITE,anchor='mm')
   self.d.line((710,332,670,332,670,685),fill=BLUE,width=6)
  for i in range(3):
   y=410+i*95;self.panel((800,y,1460,y+72),f'back-layer-{i}',line=TEAL);self.txt(965,y+36,f'后部第 {i+1} 层',44,INK,anchor='mm')
   if t>=a:self.arrow_line((670,y+36),(775,y+36),BLUE)
   self.d.rounded_rectangle((1180,y+12,1438,y+60),8,fill='#FFF1D6');self.txt(1310,y+36,'窗口待补',42,AMBER,anchor='mm')
  self.note('蓝色：共享的全局状态；金色：每层各自的近期窗口')
 def grid_base(self):
  # This lane is invariant across exact and bounded local replay.
  self.d.rounded_rectangle((100,275,1490,342),12,fill=BLUE);self.txt(795,308,'已有全局共享状态 · 持续参与后部计算',48,WHITE,anchor='mm')
  self.d.line((352,342,352,690),fill=BLUE,width=6)
  for row,label in enumerate(['较早层','中间层','较后层']):
   y=395+row*106;self.txt(100,y+30,label,44,INK,anchor='lm');self.arrow_line((352,y+30),(398,y+30),BLUE)
   for j in range(10):self.cell(row,j,PALE)
  self.txt(685,695,'更早的历史 ←',42,MUTED,anchor='mm');self.txt(1365,695,'近期 →',42,AMBER,anchor='mm')
 def cell(self,row,j,color,outline=LINE):
  x=425+j*104;y=395+row*106;self.d.rounded_rectangle((x,y,x+84,y+60),8,fill=color,outline=outline,width=3)
 def dep(self,row,j,target_j):
  # Arrow goes from required state to dependencies when tracing BACKWARDS.
  self.arrow_line((467+j*104,385+row*106),(467+target_j*104,466+(row-1)*106),AMBER)
 def local_dependencies(self,c,t,widen=False,bounded=False):
  self.grid_base()
  if not widen and not bounded:
   self.cell(2,9,GOLD)
   if t>=self.ev(c,'上一层相邻位置',.25):
    for j in range(7,10):self.cell(1,j,GOLD);self.dep(2,9,j)
   if t>=self.ev(c,'更前面的状态',.65):
    for j in range(5,10):self.cell(0,j,GOLD)
    self.dep(1,7,5);self.dep(1,9,9)
   self.note('先追一个位置的局部依赖 · 金色箭头表示向前追溯')
  elif widen:
   for row,start,phrase,default in [(2,8,'最后两个位置',.08),(1,6,'同样的依赖',.25),(0,4,'越多历史',.5)]:
    if t>=self.ev(c,phrase,default):
     for j in range(start,10):self.cell(row,j,GOLD)
   if t>=self.ev(c,'同样的依赖',.25):self.dep(2,8,6)
   if t>=self.ev(c,'越多历史',.5):self.dep(1,6,4)
   self.note('后层目标虽小，精确准备时可能需要更多上游计算')
  else:
   a=self.ev(c,'近期片段',.18);q=ramp(t,a,1.2)
   for row,start in [(0,4),(1,6),(2,8)]:
    for j in range(start,10):self.cell(row,j,GOLD if j>=8 else blend(GOLD,PALE,q))
   if t>=a:
    x=1242;self.d.line((x,365,x,687),fill=CORAL,width=5);self.txt(x-20,376,'局部重放起点',42,CORAL,anchor='rm')
   self.note('局部依赖截在近期片段内；上方蓝色全局状态一直保留',TEAL)
 def quality_check(self,c,t):
  self.d.rounded_rectangle((100,275,1490,342),12,fill=BLUE);self.txt(795,308,'已有全局共享状态 · 继续参与生成',48,WHITE,anchor='mm')
  self.card((100,425,535,660),'近期窗口','近似重建',AMBER)
  self.arrow_line((560,540),(645,540),TEAL);self.card((675,425,1085,660),'继续生成','差旅申请回答',TEAL)
  if t>=self.ev(c,'速度和回答质量',.4):
   self.card((1170,400,1490,515),'回答质量',color=BLUE);self.card((1170,560,1490,675),'实际用时',color=TEAL)
  if t>=self.ev(c,'vLLM',.6):self.note('DeepInfer 与 vLLM 都有相关实现；比较具体任务上的结果')
  else:self.note('近似重建带来取舍；质量与效率要一起检查')
 def service_result(self,c,t):
  for i in range(3):
   y=325+i*120;self.person(145,y+32,TEAL if i==0 else BLUE,f'员工{["甲","乙","丙"][i]}',.5)
   self.fragment(285,y-10,400,['差旅怎么申请','假期怎么申请','报销需要什么'][i],GOLD,INK,70)
   a=self.ev(c,'更多有效输出',.68)+i*.55
   if t>=a:
    self.d.rounded_rectangle((700,y+4,775,y+48),12,fill=TEAL);self.txt(737,y+26,'好',42,WHITE,anchor='mm')
   else:self.clock_icon(737,y+26)
  self.gpu((890,430,1490,675),active=.8,label=False)
  self.card((880,280,1490,385),'少验低收益候选',color=TEAL)
  # Unit-output takeaway is retained in the note, clear of GPU pins.
  if t>=self.ev(c,'重复计算',.3):self.txt(1190,405,'减少后部重复计算',44,AMBER,anchor='mm')
  self.note('收益要落实到有效输出，不能只看算过多少位置')
 def open_code(self,c,t):
  self.panel((115,325,615,690),'code-sheet',line=TEAL);self.txt(365,382,'DeepInfer',56,TEAL,anchor='mm');self.txt(365,475,'{ }',110,TEAL,anchor='mm')
  for i in range(3):self.d.rounded_rectangle((190,570+i*30,540-i*30,580+i*30),4,fill=LINE)
  for i,(s,tr) in enumerate([('检查执行细节','检查'),('复现运行效果','复现'),('适配自己的服务','适配')]):
   y=315+i*135
   if t>=self.ev(c,tr,.2+i*.1):
    self.card((805,y,1485,y+105),s,color=TEAL if i<2 else BLUE);self.arrow_line((650,y+52),(775,y+52),TEAL)
  self.note('代码成为可以验证的实现；适用性仍取决于模型、硬件与任务')
 def deployment_full(self,c,t):
  self.panel((95,330,545,680),'support-range',line=BLUE);self.txt(320,390,'匹配支持范围',48,BLUE,anchor='mm')
  for j,label in enumerate(['模型与权重许可','兼容硬件','运行环境']):self.txt(320,475+j*72,label,44,INK,anchor='mm')
  self.arrow_line((575,500),(660,500),BLUE);self.card((690,395,1110,635),'DeepInfer','离线推理核心',TEAL)
  if t>=self.ev(c,'线上服务',.34):
   self.panel((1160,300,1500,700),'services',line=TEAL);self.txt(1330,345,'服务配套',46,TEAL,anchor='mm')
   for j,(s,phrase) in enumerate([('外部缓存','缓存'),('流量调度','流量调度')]):
    if t>=self.ev(c,phrase,.4+j*.1):self.card((1200,415+j*145,1460,520+j*145),s,color=BLUE)
  self.note('已有 vLLM 也可研究官方实现；选择依赖自己的任务评测')
 def training_steps(self,c,t):
  self.card((95,390,535,645),'推理执行','生成候选回答',TEAL)
  if t>=self.ev(c,'评分',.4):
   self.arrow_line((565,515),(665,515),TEAL);self.panel((700,300,1490,700),'training-other',line=AMBER);self.txt(1095,360,'训练系统',54,AMBER,anchor='mm')
   self.card((755,440,1060,640),'评分 / 学习',color=AMBER);self.arrow_line((1080,535),(1130,535),AMBER);self.card((1150,440,1450,640),'更新参数',color=AMBER)
  self.note('推理可能帮助训练里的生成环节；其余训练工作另行核算')
 def conclusion(self,c,t):
  self.person(150,465);self.panel((285,325,900,695),'finished-answer');self.txt(592,387,'差旅怎么申请？',50,INK,anchor='mm')
  self.fragment(335,470,515,'请先填写报销单',TEAL,WHITE,84);self.txt(592,625,'一次回答 · 执行完成',44,TEAL,anchor='mm')
  self.card((1045,310,1490,475),'候选验证','选择值得验证的前缀',TEAL);self.card((1045,545,1490,710),'状态复用','研究具体计算取舍',AMBER)
  self.arrow_line((930,515),(1015,515),BLUE)
  self.note('从代码里理解执行方式，再在自己的服务里验证')
 def motion_signature(self,c,t):
  points=[0,.3,.8,1.2,2,3]
  points.extend(self.ev(c,s) for s in ANCHORS_BY_CUE[c['id']])
  return tuple(round(max(0,min(4,t-a)),6) for a in points)
 def frame(self,c,elapsed,width=1600,static=False,animatic=False):
  if c['id'] in OLD:return super().frame(c,elapsed,width,static,animatic)
  from scene import caption_ranges
  t=c['duration_s']*.98 if static or animatic else elapsed;ranges=caption_ranges(c);cap=next((i for i,(a,b) in enumerate(ranges) if elapsed<b),len(ranges)-1)
  key=(c['id'],self.motion_signature(c,t),round(self.nav_offset(c,t),6),width,cap,static,animatic)
  if key==getattr(self,'_mobile_key',None):return self._mobile_frame
  self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.geometry=[];self._parent=None
  actions={'fixed-waste':self.fixed_waste,'predict-prefix':self.predict,'hardware-choice':self.hardware_choice,'allocate-prefix':self.allocation,'dspark-payoff':self.payoff,'return-input':self.input_return,'kv-foundation':self.kv,'model-structure':self.architecture,'one-dependency':lambda c,t:self.local_dependencies(c,t),'window-expands':lambda c,t:self.local_dependencies(c,t,True),'bounded-replay':lambda c,t:self.local_dependencies(c,t,bounded=True),'quality-boundary':self.quality_check,'service-payoff':self.service_result,'open-value':self.open_code,'deploy-boundary':self.deployment_full,'training-distinction':self.training_steps,'conclusion':self.conclusion}
  thanks=self.closing(c,t) if c['id']=='closing' else False
  if c['id']!='closing':actions[c['id']](c,t)
  self.header(c,t,thanks);self.footer(c,elapsed)
  if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
  self._mobile_key=key;self._mobile_frame=self.im;return self.im
