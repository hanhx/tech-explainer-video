"""V14: a tracked request and visible operations, using the approved paper kit."""
from PIL import Image,ImageDraw,ImageColor
from director_v12 import Paper as Kit
from director_v10 import ramp
from director_v11 import event
from typography import font
from continuity import BG,WHITE,INK,MUTED,GOLD,CORAL,LINE,mix
TEAL='#087F6E';BLUE='#337DB4';AMBER='#99630B';PALE='#E3EEF2'
CHAPTERS=['一次回答的工作','让验证更划算','长输入少重算','成本怎样降低','开源怎样复用','带走什么']
STARTS={'baseline-hook','token-flow','input-bridge','cost-proof','open-value','conclusion'}
ANCHORS_BY_CUE={
 'baseline-hook':['模型已经加载','这条企业助手','一轮轮工作'],
 'engine-context':['DeepInfer','vLLM','主要基于','先看生成','再回看'],
 'token-flow':['词元','文本小片段','前一个','下一个'],
 'draft-start':['草稿模型','先写几个候选','候选已经给定','一次计算'],
 'target-score':['运行网络','计算概率','接受规则','从头保留'],
 'rejected-chain':['前两个候选通过','第三个被拒绝','后面','撤掉','补出替代词元','继续生成'],
 'hardware-budget':['都花时间','验证得越多','不一定','成批执行','用时'],
 'confidence':['另一条请求','DSpark','接受概率预测','硬件效率','连续前缀','有效输出'],
 'verification-proof':['固定五候选','平均验证长度','三点五八','平均接纳长度','图示配置','百分之五点四'],
 'input-bridge':['生成时','倒回','读文档','另一类工作'],
 'replay-structure':['前部处理','全局状态','后部还要','近期窗口状态','怎样补'],
 'replay-exact':['后层的近期状态','更早层','更多历史位置','逐层扩大'],
 'replay-bounded':['截在近期片段内','全局共享状态','近似重建','缩短'],
 'quality-and-reuse':['近似结果','回答质量','vLLM','两套实现'],
 'cost-proof':['更多有效词元','固定设备开销','比较两套'],
 'open-value':['代码','复现测试','合适的部分','适配'],
 'private-stack':['模型','权重许可','硬件','运行环境','缓存','负载均衡'],
 'training-boundary':['生成候选回答','高效推理','训练系统接入','预训练'],
 'conclusion':['候选验证','长输入计算','开源','代码','验证它'],
 'closing':['欢迎','谢谢大家']}

def blend(a,b,q):
 a=ImageColor.getrgb(a);b=ImageColor.getrgb(b)
 return tuple(round(mix(x,y,q)) for x,y in zip(a,b))

class Paper(Kit):
 def ev(self,c,s,p=.5):return event(c,s,p)
 def nav_offset(self,c,t):
  ch=c['chapter'];target=max(0,min(3,ch-2))*480;prev=max(0,min(3,ch-3))*480
  return mix(prev,target,ramp(t,0,.75)) if c['id'] in STARTS else target
 def header(self,c,t,thanks=False):
  self.d.rectangle((0,0,1600,230),fill=BG);offset=self.nav_offset(c,t)
  strip=Image.new('RGB',(1600,90),BG);d=ImageDraw.Draw(strip)
  for i,label in enumerate(CHAPTERS):
   x=320+i*480-offset;active=c['chapter']==i+1;s=f'0{i+1} {label}';size=44 if active else 42;f=font(size,'bold' if active else 'medium')
   if active:d.rounded_rectangle((x-210,10,x+210,76),18,fill='#DDF3EB')
   d.text((x,43),s,font=f,fill=TEAL if active else MUTED,anchor='mm');b=d.textbbox((x,43),s,font=f,anchor='mm');left=max(80,b[0]);right=min(1520,b[2])
   if right>left:self.geometry.append(dict(id=f'nav-{i}',box=[left,b[1],right-left,b[3]-b[1]],text=s,font_size=size,role='navigation',clipped=left!=b[0] or right!=b[2]))
   if active:d.line((x-160,83,x+160,83),fill=GOLD,width=5)
  self.im.paste(strip.crop((80,0,1520,90)),(80,0));self.d=ImageDraw.Draw(self.im)
  if offset>0:self.d.line((57,35,49,43,57,51),fill=MUTED,width=2)
  if offset<1440:self.d.line((1543,35,1551,43,1543,51),fill=MUTED,width=2)
  title='感谢观看' if thanks else c['title'];size=54
  while self.d.textbbox((0,0),title,font=font(size,'bold'))[2]>1280:size-=1
  self.txt(80,130,title,size,INK,anchor='lm');self.txt(1520,130,f"{c['shot_number']:02}/{c['shot_total']:02}",42,MUTED,anchor='rm')
  self.txt(82,193,'如果这段动画让你有所收获' if thanks else c['visual_subtitle'],42,MUTED,anchor='lm');self.d.line((80,230,1520,230),fill=LINE,width=2)
 def fragment(self,x,y,w,label,fill=GOLD,ink=INK,h=82):
  self.d.rounded_rectangle((x+4,y+6,x+w+4,y+h+6),12,fill='#D8EBF0')
  self.d.rounded_rectangle((x,y,x+w,y+h),12,fill=fill,outline=LINE,width=2)
  self.txt(x+w/2,y+h/2,label,48,ink,anchor='mm')
 def request(self,x=100,y=280):self.pill(x,y,'请求 A',250)
 def hook(self,c,t):
  self.request();self.txt(425,385,'模型已加载',48,INK,anchor='mm')
  self.gpu((125,440,725,690),active=.7,label=False)
  self.panel((910,300,1500,690),'answer');self.txt(1205,355,'差旅申请怎么走？',46,INK,anchor='mm')
  self.arrow_line((760,555),(870,555),BLUE)
  for i,s in enumerate(['请先','查看','说明']):
   if t>=.8+i*1.15:self.fragment(965+i*165,490,145,s,TEAL,WHITE)
  self.note('一次回答，仍要让设备逐轮执行')
 def engine_context(self,c,t):
  self.request();self.card((100,410,580,640),'DeepInfer' if t>=self.ev(c,'DeepInfer',.17) else '推理引擎','安排执行',TEAL)
  self.arrow_line((610,525),(760,525),TEAL);self.gpu((800,420,1460,680),active=.7,label=False)
  self.txt(1130,330,'GPU / NPU',48,INK,anchor='mm')
  if t>=self.ev(c,'主要基于',.48):self.note('DeepInfer 最初主要基于 vLLM 开发')
  elif t>=self.ev(c,'vLLM',.3):self.note('vLLM：同类推理引擎',BLUE)
  else:self.note('跟着请求 A，观察执行安排')
 def tokens(self,c,t):
  self.request();self.card((100,405,550,650),'主模型','逐轮采样',BLUE)
  labels=['请先','查看','说明'];a=self.ev(c,'前一个',.6);b=self.ev(c,'下一个',.85)
  steps=[self.ev(c,'文本小片段',.24),a,b]
  for i,s in enumerate(labels):
   x=730+i*255
   self.txt(x+105,370,f'第 {i+1} 轮',44,MUTED,anchor='mm')
   if t>=steps[i]:self.fragment(x,450,210,s,TEAL,WHITE)
   else:self.fragment(x,450,210,'待生成',PALE,MUTED)
   if i<2:self.arrow_line((x+218,493),(x+244,493),BLUE if t>=steps[i+1] else LINE)
  self.note('文字卡片代指词元 · 不代表真实分词')
 def draft_board(self,c,t,phase):
  self.request(90,650);self.card((90,290,390,455),'草稿模型','提出候选',AMBER)
  self.panel((445,450,1495,610),'target-network',line=BLUE)
  self.txt(970,490,'主模型 · 网络计算',48,BLUE,anchor='mm')
  labels=['请先','查看','流程','再','提交'];given=self.ev(c,'候选已经给定',.55)
  emit=self.ev(c,'先写几个候选',.28)
  accepted=self.ev(c,'前两个候选通过',.08);rejected=self.ev(c,'第三个被拒绝',.3);withdraw=self.ev(c,'撤掉',.5);replace=self.ev(c,'补出替代词元',.72)
  for i,label in enumerate(labels):
   x=450+i*205
   visible=phase!='draft' or t>=emit+i*.18
   fill=GOLD;ink=INK
   if phase=='reject':
    if i<2 and t>=accepted:fill=TEAL;ink=WHITE
    if i>=2 and t>=rejected:fill=PALE;ink=MUTED
   if visible:
    self.fragment(x,300,180,label,fill,ink)
    if phase=='reject' and i==2 and t>=rejected:
     self.d.line((x+8,310,x+172,372),fill=CORAL,width=4);self.d.line((x+172,310,x+8,372),fill=CORAL,width=4)
    if phase=='reject' and i>2 and t>=withdraw:
     self.d.line((x+15,341,x+165,341),fill=MUTED,width=4)
   if phase!='draft' or t>=given:
    self.arrow_line((x+90,397),(x+90,438),BLUE)
  if phase=='draft':
   if t>=given:
    self.txt(970,558,'候选已知 · 准备批量评分',44,MUTED,anchor='mm')
   self.note('候选已给定 → 多个位置可以批量评分')
  else:
   a=self.ev(c,'运行网络',.18);p=self.ev(c,'计算概率',.4)
   if phase=='reject' or t>=p:
    for i in range(5):self.txt(540+i*205,558,f'p{i+1}',48,BLUE,anchor='mm')
   elif t>=a:
    q=ramp(t,a,.9);self.d.rounded_rectangle((480,542,1460,572),10,fill=PALE)
    self.d.rounded_rectangle((480,542,480+max(2,980*q),572),10,fill=BLUE)
   else:self.txt(970,558,'候选已知 · 准备批量评分',44,MUTED,anchor='mm')
   if phase=='score':
    if t>=self.ev(c,'接受规则',.65):self.txt(970,675,'概率计算 → 接受判定',48,TEAL,anchor='mm')
    self.note('验证仍在执行主模型；p 表示各位置概率计算')
   else:
    self.txt(450,681,'正式输出',44,TEAL,anchor='lm')
    if t>=accepted:
     for i,s in enumerate(labels[:2]):self.fragment(680+i*205,640,180,s,TEAL,WHITE)
    if t>=replace:self.fragment(1090,640,180,'说明',BLUE,WHITE)
    self.note('草稿前缀 + 拒绝处替代词元 → 继续生成',TEAL)
 def budget(self,c,t):
  self.txt(100,310,'回看验证前 · 同一条草稿',48,INK,anchor='lm')
  for row,(label,n) in enumerate([('送入 5 个候选',5),('送入较短前缀',3)]):
   y=405+row*190;self.txt(100,y+40,label,44,INK,anchor='lm')
   for i,s in enumerate(['请先','查看','流程','再','提交']):self.fragment(440+i*135,y,118,s,GOLD if i<n else PALE,INK if i<n else MUTED)
  self.panel((1190,350,1500,680),'tradeoff')
  self.txt(1345,405,'有效输出',48,TEAL,anchor='mm');self.d.line((1225,485,1465,485),fill=INK,width=3)
  self.txt(1345,548,'本轮用时',48,BLUE,anchor='mm')
  if t>=self.ev(c,'成批执行',.68):self.txt(1345,625,'受批次影响',42,MUTED,anchor='mm')
  self.note('候选接纳情况 + 设备批次效率 → 一起权衡')
 def confidence(self,c,t):
  ready=t>=self.ev(c,'接受概率预测',.29);choose=t>=self.ev(c,'连续前缀',.7)
  for row,(request,labels,probs,keep) in enumerate([('A',['请先','查看','流程','再','提交'],[95,86,74,35,12],3),('B',['完成','登记','即可','提交','申请'],[90,71,28,12,5],2)]):
   if row and t<self.ev(c,'另一条请求',.02)+.5:continue
   y=350+row*205;self.pill(90,y+5,f'请求 {request}',250,c=TEAL if row==0 else BLUE)
   for i,s in enumerate(labels):
    x=420+i*145;fill=BLUE if choose and i<keep else PALE if choose else GOLD
    self.fragment(x,y,125,s,fill,WHITE if choose and i<keep else INK)
    if ready:self.txt(x+62,y+115,str(probs[i])+'%',44,AMBER,anchor='mm')
  self.panel((1225,320,1510,690),'hardware',line=BLUE);self.txt(1367,370,'硬件效率',48,BLUE,anchor='mm')
  if t>=self.ev(c,'硬件效率',.43):
   self.d.line((1260,570,1475,570),fill=MUTED,width=2);self.d.line((1260,570,1260,435),fill=MUTED,width=2)
   self.d.line([(1260,550),(1315,480),(1370,455),(1430,443),(1470,440)],fill=BLUE,width=4)
   self.txt(1367,625,'曲线示意',42,MUTED,anchor='mm')
  self.note('蓝色：本轮送验证 · 灰色：本轮暂不验证' if choose else '接受概率是预测，稍后由主模型实际验证')
 def proof(self,c,t):
  thresholds=[self.ev(c,'三点五八',.35),self.ev(c,'平均接纳长度',.5),self.ev(c,'百分之五点四',.9)]
  for i,(title,before,after,col) in enumerate([('平均验证长度','5.00','3.58',BLUE),('平均接纳长度','3.30','3.21',TEAL),('估算吞吐','','+5.4%',TEAL)]):
   x=100+i*490;self.panel((x,330,x+440,690),f'proof-{i}',line=col);self.txt(x+220,390,title,48,INK,anchor='mm')
   if before:
    self.txt(x+220,473,before,64,MUTED,anchor='mm');self.arrow_line((x+220,520),(x+220,555),col)
   else:self.txt(x+220,458,'每秒有效词元数',42,MUTED,anchor='mm')
   if t>=thresholds[i]:self.txt(x+220,610 if before else 570,after,76,col,anchor='mm')
  self.note('EP64/DP64 · 60条序列/rank · 官方局部策略估算')
 def bridge(self,c,t):
  self.request();self.txt(540,317,'读输入',48,INK,anchor='mm');self.txt(1220,317,'生成回答',48,INK,anchor='mm')
  self.d.line((540,370,1220,370),fill=LINE,width=5)
  q=ramp(t,self.ev(c,'倒回',.5),1.15);x=mix(1220,540,q);self.d.ellipse((x-16,354,x+16,386),fill=GOLD)
  if q>0:self.arrow_line((1050,348),(760,348),AMBER)
  self.panel((100,455,540,685),'document');self.txt(320,425,'公司差旅制度',48,INK,anchor='mm')
  for i in range(4):self.d.rounded_rectangle((145,495+i*43,490-(i%2)*70,514+i*43),7,fill='#BADAE3')
  self.arrow_line((575,565),(720,565),BLUE);self.gpu((760,455,1430,685),active=.7,label=False)
  self.note('明确回看：读输入先发生，生成随后进行')
 def structure(self,c,t):
  self.request();self.card((100,455,600,675),'模型前部','处理完整输入',BLUE)
  ready=t>=self.ev(c,'全局状态',.32);self.panel((710,270,1460,355),'global',fill=BLUE if ready else PALE,line=BLUE)
  self.txt(1085,313,'跨层共用 · 全局 KV',48,WHITE if ready else INK,anchor='mm')
  self.arrow([(620,510),(660,510),(660,313),(690,313)],BLUE)
  self.txt(800,420,'模型后部',48,INK,anchor='mm')
  for i in range(3):
   y=465+i*79;self.d.rounded_rectangle((950,y,1450,y+62),10,fill=WHITE,outline=LINE,width=2)
   self.txt(1060,y+31,f'层 {i+1}',44,INK,anchor='mm')
   label='待准备' if t>=self.ev(c,'近期窗口状态',.7) else '近期窗口'
   self.txt(1300,y+31,label,44,AMBER,anchor='mm')
   if ready:self.arrow([(1488,355),(1488,y+31),(1465,y+31)],BLUE)
  self.note('全局 KV 已有；各层近期窗口状态仍需准备')
 def global_grid(self):
  self.request(90,270);self.d.rounded_rectangle((395,270,1450,345),14,fill=BLUE)
  self.txt(922,308,'全局共享状态 · 始终保留',48,WHITE,anchor='mm')
  for i in range(3):
   y=415+i*110
   self.arrow([(1495,345),(1495,y+32),(1465,y+32)],BLUE)
  self.txt(100,378,'正向层序 ↓',42,MUTED,anchor='lm')
 def replay(self,c,t,bounded=False):
  self.global_grid();q=ramp(t,self.ev(c,'截在近期片段内',.12),1.2) if bounded else 0
  stages=[self.ev(c,'更多历史位置',.6),self.ev(c,'更早层',.4),self.ev(c,'后层的近期状态',.12)]
  for row,(label,start) in enumerate([('较早层 1',4),('中间层 2',6),('较后层 3',8)]):
   y=415+row*110;self.txt(100,y+32,label,44,INK,anchor='lm')
   active=bounded or t>=stages[row]
   for j in range(10):
    x=355+j*112;fill=GOLD if active and j>=start else PALE
    if bounded and j>=8:fill=blend(GOLD,TEAL,q)
    elif bounded and j>=start:fill=blend(GOLD,PALE,q)
    self.d.rounded_rectangle((x,y,x+90,y+64),8,fill=fill,outline=LINE,width=2)
  if not bounded:
   for row in [2,1]:
    if t>=stages[row-1]:
     x=355+(8-(2-row)*2)*112+45;y=415+row*110
     self.arrow_line((x,y-10),(x-224,y-46),AMBER)
   self.txt(1110,378,'依赖追溯 ↖',42,AMBER,anchor='mm')
   self.note('从后层目标向更早层追溯，所需历史范围扩大')
  else:
   if q>0:
    x=mix(700,1237,q);self.d.line((x,394,x,713),fill=CORAL,width=4)
    self.txt(x-20,375,'重放起点',42,CORAL,anchor='rm')
   self.note('保留全局状态；限定近期片段，近似重建窗口',TEAL)
 def quality(self,c,t):
  self.d.rounded_rectangle((100,270,1500,345),14,fill=BLUE);self.txt(800,308,'全局共享状态继续参与',48,WHITE,anchor='mm')
  self.card((100,435,565,670),'窗口状态','近似重建',TEAL)
  self.arrow_line((590,550),(675,550),LINE)
  self.card((700,385,1100,510),'回答质量',color=BLUE);self.card((700,575,1100,700),'执行效率',color=TEAL)
  self.txt(900,547,'一起评估',44,MUTED,anchor='mm')
  if t>=self.ev(c,'vLLM',.55):
   self.card((1190,385,1500,510),'vLLM',color=BLUE);self.card((1190,575,1500,700),'DeepInfer',color=TEAL)
  self.note('同一任务上，检查质量与实际执行效果')
 def source(self,c,t):
  self.card((100,330,540,475),'候选验证','选择验证长度',TEAL)
  self.card((100,550,540,695),'长输入计算','近似重建窗口',AMBER)
  self.panel((665,375,1035,665),'source',line=TEAL);self.txt(850,445,'DeepInfer',52,TEAL,anchor='mm');self.txt(850,540,'{ }',90,TEAL,anchor='mm')
  self.arrow([(560,405),(615,405),(615,520),(645,520)],LINE);self.arrow([(560,620),(615,620),(615,520)],LINE)
  if t>=self.ev(c,'代码',.25):self.arrow_line((1055,520),(1130,520),TEAL)
  self.card((1150,330,1500,485),'复现测试','适配',TEAL)
  if t>=self.ev(c,'适配',.82):
   self.arrow_line((1325,505),(1325,545),TEAL);self.card((1150,565,1500,705),'企业助手','请求 A',BLUE)
  self.note('把可观察机制，接回可检查与可复现的代码')
 def deployment(self,c,t):
  self.panel((100,300,735,700),'compatibility');self.txt(417,355,'匹配支持条件',50,INK,anchor='mm')
  self.txt(150,440,'模型',44,MUTED,anchor='lm');self.txt(470,440,'V4.1-Flash',46,BLUE,anchor='mm')
  if t>=self.ev(c,'硬件',.48):
   self.txt(150,520,'硬件',44,MUTED,anchor='lm');self.txt(475,520,'SM100 / 昇腾950',42,BLUE,anchor='mm')
  if t>=self.ev(c,'权重许可',.3):self.txt(417,610,'许可与环境：逐项确认',44,MUTED,anchor='mm')
  self.panel((865,300,1500,700),'peripherals');self.txt(1182,355,'围绕引擎接入服务',50,TEAL,anchor='mm')
  for i,(s,trigger) in enumerate([('缓存系统','缓存'),('分离部署','运行环境'),('负载均衡','负载均衡')]):
   if t>=self.ev(c,trigger,.65+i*.1):self.card((930,400+i*96,1435,490+i*96),s,color=BLUE)
  self.note('当前版本支持范围 · 外围组件需部署者接入')
 def training(self,c,t):
  self.panel((100,320,1500,700),'training-system');self.txt(800,370,'训练系统中的两类工作',50,INK,anchor='mm')
  self.card((155,465,535,640),'推理生成','候选回答',TEAL)
  if t>=self.ev(c,'训练系统接入',.6):
   self.arrow_line((565,550),(730,550),LINE);self.txt(647,455,'需接入',42,MUTED,anchor='mm')
  self.card((765,465,1445,640),'学习 / 更新参数','由训练系统完成',BLUE)
  self.note('高效生成可能节省其中一环；参数学习单独核算')
 def conclusion(self,c,t):
  finished=c['id']=='closing';self.request()
  self.card((100,375,550,515),'候选验证','追求有效产出',TEAL)
  self.card((100,560,550,700),'长输入计算','利用状态结构',AMBER)
  self.gpu((665,450,1050,650),active=.85,label=False);self.txt(858,385,'同一批设备',48,INK,anchor='mm')
  self.arrow_line((580,535),(635,535),TEAL);self.arrow_line((1080,535),(1150,535),BLUE)
  self.panel((1180,345,1500,665),'answer-finished');self.txt(1340,402,'请求 A 完成',48,TEAL,anchor='mm')
  for i,s in enumerate(['请先','查看','说明']):
   self.d.rounded_rectangle((1235,455+i*59,1445,502+i*59),8,fill='#DDF3EB');self.txt(1340,478+i*59,s,42,TEAL,anchor='mm')
  if finished or t>=self.ev(c,'代码',.82):self.txt(858,700,'{ } 可检查代码',44,TEAL,anchor='mm')
  self.note('在自己的模型、设备与请求条件下验证收益')
 def motion_signature(self,c,t):
  times=[0,.8,1.95,3.1]
  times.extend(self.ev(c,s) for s in ANCHORS_BY_CUE[c['id']])
  # Every animated interval is <= 4s; outside them both scene and captions freeze.
  return tuple(round(max(0,min(4,t-a)),6) for a in times)
 def frame(self,c,elapsed,width=1600,static=False,animatic=False):
  from scene import caption_ranges
  t=c['duration_s']*.98 if static or animatic else elapsed
  ranges=caption_ranges(c);cap=next((i for i,(a,b) in enumerate(ranges) if elapsed<b),len(ranges)-1)
  key=(c['id'],self.motion_signature(c,t),round(self.nav_offset(c,t),6),width,cap,static,animatic)
  if key==getattr(self,'_mobile_key',None):return self._mobile_frame
  self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.geometry=[];self._parent=None;thanks=False
  actions={'baseline-hook':self.hook,'engine-context':self.engine_context,'token-flow':self.tokens,'draft-start':lambda c,t:self.draft_board(c,t,'draft'),'target-score':lambda c,t:self.draft_board(c,t,'score'),'rejected-chain':lambda c,t:self.draft_board(c,t,'reject'),'hardware-budget':self.budget,'confidence':self.confidence,'verification-proof':self.proof,'input-bridge':self.bridge,'replay-structure':self.structure,'replay-exact':lambda c,t:self.replay(c,t),'replay-bounded':lambda c,t:self.replay(c,t,True),'quality-and-reuse':self.quality,'cost-proof':self.unit_cost,'open-value':self.source,'private-stack':self.deployment,'training-boundary':self.training,'conclusion':self.conclusion}
  if c['id']=='closing':thanks=self.closing(c,t)
  else:actions[c['id']](c,t)
  self.header(c,t,thanks);self.footer(c,elapsed)
  if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
  self._mobile_key=key;self._mobile_frame=self.im;return self.im
