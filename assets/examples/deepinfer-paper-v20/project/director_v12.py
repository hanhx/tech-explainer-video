"""V12: demonstrate the missing causal links rather than append exclusions."""
from PIL import Image,ImageDraw
from director_v11 import Paper as V11,event
from director_v10 import ramp
from typography import font
from continuity import BG,WHITE,INK,MUTED,GOLD,CORAL,LINE,ease,mix
TEAL='#087F6E';BLUE='#337DB4';AMBER='#99630B'
CHAPTERS=['回答的成本','验证要划算','长输入少算','公开执行方案','部署与成本','带走什么']
STARTS={'baseline-hook','decode-rounds','input-bridge','open-value','production-boundary','conclusion'}
SUBS={
 'baseline-hook':'沿一次回答，找出计算开销与优化机会',
 'cost-loop':'参数保留；每次请求仍要执行推理',
 'engine-choice':'vLLM：通用底座 · DeepInfer：官方执行方案',
 'decode-rounds':'生成阶段 · 轮次与数量为教学示意',
 'draft-start':'候选 → 主模型验证 → 正式输出',
 'rejected-chain':'聚焦请求A · 候选按前缀依赖',
 'hardware-budget':'教学示意曲线 · 具体形状须在硬件上测量',
 'confidence':'回到验证前 · 概率与数量为教学示意',
 'verification-proof':'官方局部策略估算 · 比较条件固定',
 'input-bridge':'回看请求A的输入阶段 · 预填充',
 'replay-structure':'V4.1-Flash结构简化示意',
 'replay-exact':'精确恢复视角 · 层数与范围示意',
 'replay-bounded':'近似恢复视角 · 共享全局缓存保留',
 'quality-and-reuse':'计算量与回答质量，一起评估',
 'open-value':'把前面的机制，接回官方执行代码',
 'private-stack':'公开权重 + 兼容引擎 + 适配硬件',
 'production-boundary':'公开引擎核心；外围服务由部署者接入',
 'cost-proof':'同条件比较 · 单位输出设备开销',
 'training-boundary':'预训练学参数；后训练可能需要生成回答',
 'conclusion':'公开执行经验，让细节可检查、可复用',
 'closing':'开源价值：执行方案可以被研究和复用'}

class Paper(V11):
 def nav_offset(self,c,t):
  ch=c['chapter'];target=max(0,min(3,ch-2))*480;previous=max(0,min(3,ch-3))*480
  return mix(previous,target,ramp(t,0,.75)) if c['id'] in STARTS else target
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
  self.txt(82,193,'如果这段动画让你有所收获' if thanks else SUBS[c['id']],42,MUTED,anchor='lm');self.d.line((80,230,1520,230),fill=LINE,width=2)
 def cost_loop(self,c,t):
  self.card((90,310,475,470),'训练得到','模型参数',BLUE)
  self.gpu((590,460,1040,695),active=.75 if t>=event(c,'每来一个请求',.45) else 0,label=False)
  self.txt(815,410,'GPU / NPU',48,INK,anchor='mm')
  loaded=t>=event(c,'服务启动后',.22)+.9
  self.memory((1120,355,1510,690),0,loaded)
  q=ramp(t,event(c,'服务启动后',.22),.9)
  self.arrow_line((495,380),(1095,380),BLUE)
  self.txt(790,300,'启动时装入',44,BLUE,anchor='mm')
  if 0<q<1:
   x=mix(500,1090,q);self.d.rounded_rectangle((x-23,357,x+23,403),7,fill=BLUE)
  a=event(c,'每来一个请求',.45);phase=max(0,min(2.999,(t-a)/.8));n=max(0,min(3,int(phase)+1)) if t>=a else 0
  self.pill(100,570,'请求 '+('ABC'[max(0,n-1)]),310)
  self.arrow_line((440,608),(560,608),TEAL)
  if a<=t<a+2.4:
   x=mix(445,555,ease(phase%1));self.d.ellipse((x-17,591,x+17,625),fill=TEAL)
  self.note('参数保持不变；请求逐次使用设备执行' if n<3 else '回答越多，执行开销越值得优化')
 def engine_choice(self,c,t):
  self.pill(90,435,'请求 A',300)
  self.engine_card((525,300,1090,640),'推理引擎','调度 · 缓存 · 执行')
  self.gpu((1200,405,1500,620),active=.7,label=False)
  self.arrow_line((415,475),(500,475),TEAL);self.arrow_line((1110,475),(1175,475),TEAL)
  self.txt(1350,345,'GPU / NPU',44,INK,anchor='mm')
  self.pill(190,675,'vLLM',370,c=BLUE);self.arrow_line((590,712),(965,712),LINE);self.pill(990,675,'DeepInfer',420)
  self.txt(778,660,'最初主要基于',42,MUTED,anchor='mm')
 def decode_rounds(self,c,t):
  self.txt(100,325,'逐轮生成',48,INK,anchor='lm')
  for i,token in enumerate(['我','们','先']):
   x=440+i*350;self.card((x,285,x+265,445),'第'+str(i+1)+'轮',token,BLUE)
   if i<2:self.arrow_line((x+280,365),(x+330,365),LINE)
  a=event(c,'如果一轮',.55);q=ramp(t,a,.8)
  if t>=a:
   self.txt(100,585,'多词元验证',48,TEAL,anchor='lm');self.panel((440,510,1405,680),'batch',fill=WHITE,line=TEAL)
   for i,token in enumerate(['我','们','先']):
    x=560+i*310;self.d.rounded_rectangle((x-60,540,x+60,625),12,fill=TEAL if q>=1 else GOLD);self.txt(x,583,token,50,WHITE if q>=1 else INK,anchor='mm')
   self.note('一次执行，尝试确认多个候选；数量示意')
  else:self.note('每轮推进回答，都需要设备执行')
 def rejected_chain(self,c,t):
  self.pill(95,290,'请求 A',285);self.txt(980,325,'同一串候选',48,INK,anchor='mm')
  a=event(c,'前两个通过',.18);b=event(c,'第三个被拒绝',.35);z=event(c,'后面',.5)
  for i,token in enumerate(['我','们','先','看','看']):
   x=110+i*298;state='通过' if i<2 and t>=a else '拒绝' if i==2 and t>=b else '失效' if i>2 and t>=z+(i-3)*.3 else '候选'
   col=TEAL if state=='通过' else CORAL if state=='拒绝' else '#DCE8ED' if state=='失效' else GOLD
   self.panel((x,430,x+230,550),f'token-{i}',fill=col)
   self.txt(x+115,490,token,60,WHITE if state=='通过' else INK,anchor='mm');self.txt(x+115,605,state,46,TEAL if state=='通过' else CORAL if state=='拒绝' else MUTED,anchor='mm')
   if state=='失效':self.d.line((x+25,445,x+205,535),fill=MUTED,width=3)
   if i<4:self.arrow_line((x+245,490),(x+283,490),LINE)
  if t>=b:self.pill(490,680,'正式留下：我们…',660)
  else:self.note('后一个候选，基于前一个候选续写')
 def confidence_v12(self,c,t):
  c=dict(c,speech_events=dict(c.get('speech_events',{}),决定每条请求=event(c,'为每条请求',.5)))
  self.candidates(c,t,'confidence')
 def hardware_budget(self,c,t):
  self.card((90,370,560,650),'减少验证','单轮工作量下降',TEAL)
  self.panel((720,300,1500,700),'hardware-curve');self.txt(1110,345,'设备吞吐也随批次变化',46,INK,anchor='mm')
  self.d.line((825,600,1430,600),fill=MUTED,width=3);self.d.line((825,600,825,410),fill=MUTED,width=3)
  pts=[(825,582),(885,565),(945,530),(1005,480),(1065,440),(1125,418),(1185,410),(1245,408),(1305,408),(1375,408)]
  self.d.line(pts,fill=BLUE,width=5);self.txt(1130,655,'验证批次：小 → 大',42,MUTED,anchor='mm')
  a=event(c,'批次太小',.4)
  if t>=a:
   self.d.ellipse((871,551,899,579),fill=CORAL);self.txt(325,700,'小批次可能降低吞吐',42,CORAL,anchor='mm')
  self.note('计算量与吞吐曲线，共同决定验证安排')
 def strategy_result(self,c,t):
  self.pill(100,265,'EP64/DP64 · 每rank 60条序列',1280,c=BLUE)
  for x,s in [(280,'验证策略'),(670,'验证长度'),(1000,'接受长度'),(1380,'估算吞吐')]:self.txt(x,390,s,46,INK,anchor='mm')
  for y,name,values in [(495,'固定5候选',['5.00','3.30','13,730']),(625,'动态长度',['3.58','3.21','14,466'])]:
   self.panel((90,y-55,1510,y+55),f'result-{y}',fill=WHITE,line=TEAL if y==625 else LINE);self.txt(280,y,name,46,TEAL if y==625 else BLUE,anchor='mm')
   for i,x in enumerate([670,1000,1380]):
    threshold=[event(c,'减少验证计算',.2),event(c,'相近数量',.1),event(c,'估算吞吐',.55)][i]
    self.txt(x,y,values[i] if y==495 or t>=threshold else '…',52,TEAL if y==625 else BLUE,anchor='mm')
  if t>=event(c,'百分之五点四',.65):self.txt(1350,719,'约 +5.4%',48,TEAL,anchor='rm')
  self.txt(100,719,'长度：词元 · 吞吐：词元/秒/rank',42,MUTED,anchor='lm')
 def input_bridge(self,c,t):
  self.panel((90,360,450,650),'document');self.txt(270,300,'长文档',50,INK,anchor='mm')
  for i in range(5):self.d.rounded_rectangle((130,405+i*42,405-(i%2)*50,423+i*42),6,fill='#B7D8DF')
  self.gpu((650,405,1030,645),active=.8,label=False);self.txt(840,330,'GPU / NPU',48,INK,anchor='mm')
  a=event(c,'算成缓存',.55);q=ramp(t,a,.9);self.memory((1190,360,1510,690),3 if q>=1 else 0,True)
  self.arrow_line((475,520),(620,520),TEAL);self.arrow_line((1060,520),(1160,520),GOLD)
  if 0<q<1:
   x=mix(1070,1150,q);self.d.rounded_rectangle((x-20,500,x+20,540),6,fill=GOLD)
  self.note('输入先计算，留下状态供生成阶段使用')
 def replay_structure(self,c,t):
  self.pill(90,270,'请求 A',250)
  ready=t>=event(c,'全局缓存',.3)
  self.d.rounded_rectangle((410,270,1495,355),14,fill=BLUE if ready else '#E2EDF1');self.txt(952,312,'全局共享缓存',48,WHITE if ready else INK,anchor='mm')
  self.card((100,450,580,650),'前段','处理完整输入',BLUE)
  self.arrow_line((620,535),(755,535),BLUE)
  self.panel((800,420,1490,660),'decoder');self.txt(1145,470,'后段',50,INK,anchor='mm');self.txt(1145,540,'恢复近期窗口',44,TEAL,anchor='mm')
  if t>=event(c,'后段',.45):
   for i in range(6):self.d.rounded_rectangle((860+i*90,595,930+i*90,635),5,fill=TEAL if i>=4 else '#E2EDF1')
  self.note('全局信息跨层共享；近期窗口状态另行恢复')
 def replay_v12(self,c,t):
  events=dict(c.get('speech_events',{}))
  events['精确恢复']=event(c,'按完整依赖恢复',.55)
  events['只重放']=event(c,'恢复范围截在',.1)
  self.replay(dict(c,speech_events=events),t)
 def quality_and_reuse(self,c,t):
  self.card((95,405,510,640),'近似状态','有界重放',TEAL)
  self.arrow_line((535,520),(625,520),LINE)
  self.card((650,330,1110,475),'回答质量',color=BLUE);self.card((650,545,1110,690),'执行效率',color=TEAL)
  self.txt(880,510,'一起评估',44,MUTED,anchor='mm')
  if t>=event(c,'vLLM',.55):
   self.card((1205,345,1510,490),'vLLM',color=BLUE);self.card((1205,545,1510,690),'DeepInfer',color=TEAL)
  self.note('已有两套实现；实际任务上比较质量与效率')
 def implementation_path(self,c,t):
  self.card((90,400,430,620),'模型结构','实际依赖',BLUE)
  self.arrow([(450,510),(485,510),(485,385),(510,385)],LINE);self.arrow([(450,510),(485,510),(485,615),(510,615)],LINE)
  self.card((535,315,985,455),'验证预算',color=TEAL);self.card((535,545,985,685),'缓存恢复',color=AMBER)
  self.arrow([(1005,385),(1040,385),(1040,510),(1080,510)],LINE);self.arrow([(1005,615),(1040,615),(1040,510)],LINE)
  self.panel((1100,370,1510,655),'code');self.txt(1305,435,'{ }',80,TEAL,anchor='mm');self.txt(1305,555,'设备执行代码',46,INK,anchor='mm')
  a=event(c,'开发者能看到',.65)
  if t>=a:self.note('同一份源码，把机制与执行过程连起来',TEAL)
  else:self.note('从模型特点，追到具体执行选择')
 def private_v12(self,c,t):
  events=dict(c.get('speech_events',{}));events['加上适配']=event(c,'再配支持',.3);events['搭建自己的服务']=event(c,'引擎负责执行',.65)
  self.private(dict(c,speech_events=events),t)
  self.geometry=[e for e in self.geometry if e['box'][1]<720]
  self.d.rectangle((70,720,1530,780),fill=BG)
  self.note('DeepInfer公开支持：V4.1-Flash · SM100 / 昇腾950')
 def boundary_v12(self,c,t):
  self.box((80,300,730,700),fill=WHITE,line=TEAL,r=20);self.dashed((850,300,1520,700),CORAL)
  self.txt(405,345,'公开引擎核心',50,TEAL,anchor='mm');self.engine_card((155,400,655,670),'DeepInfer','本次仓库提供')
  self.txt(1185,345,'外围服务需接入',50,INK,anchor='mm')
  for i,s in enumerate(['长期缓存','分离部署','负载均衡']):
   if t>=event(c,s,.15+i*.1):self.card((920,405+i*95,1450,485+i*95),s,color=CORAL)
  self.note('围绕引擎接入组件，形成自己的线上服务')
 def unit_cost(self,c,t):
  self.pill(100,270,'回答质量与响应要求相当 · 同一批设备',1360)
  self.panel((100,390,650,690),'fixed');self.txt(375,445,'设备投入保持',50,INK,anchor='mm');self.gpu((180,500,570,650),active=.75,label=False)
  self.txt(1110,450,'每小时固定设备开销',48,BLUE,anchor='mm');self.d.line((760,520,1480,520),fill=INK,width=3)
  self.txt(1110,573,'每小时有效输出',48,TEAL,anchor='mm')
  n=5 if t>=event(c,'更多有效词元',.4) else 3
  for i in range(n):self.d.rounded_rectangle((860+i*105,630,940+i*105,690),8,fill=TEAL)
  self.note('输出增加 → 固定设备开销分摊到更多词元',TEAL)
 def training_v12(self,c,t):
  self.panel((90,310,650,700),'pretrain');self.txt(370,365,'预训练',54,BLUE,anchor='mm');self.card((165,445,575,620),'学习参数','单独一笔账',BLUE)
  self.dashed((800,310,1510,700),TEAL);self.txt(1155,365,'后训练',54,TEAL,anchor='mm');self.txt(1155,430,'训练系统接入',46,MUTED,anchor='mm')
  self.card((840,490,1100,625),'推理生成',color=TEAL);self.arrow_line((1120,555),(1170,555),LINE);self.card((1190,490,1470,625),'候选回答',color=BLUE)
  self.note('高效推理可能帮助训练中的回答生成环节')
 def conclusion(self,c,t):
  events=dict(c.get('speech_events',{}));events['修改和复用']=-3 if c['id']=='closing' else event(c,'合适的部分',.68)
  # The same inspected fragment is first adapted/validated, then reused.
  self.open_value(dict(c,speech_events=events),t)
  self.geometry=[e for e in self.geometry if e['box'][1]<720]
  self.d.rectangle((70,720,1530,780),fill=BG);self.note('源码经适配与验证，接入自己的系统')
 def frame(self,c,elapsed,width=1600,static=False,animatic=False):
  from scene import caption_ranges
  t=c['duration_s']*.98 if static or animatic else elapsed
  ranges=caption_ranges(c);cap=next((i for i,(a,b) in enumerate(ranges) if elapsed<b),len(ranges)-1)
  key=(c['id'],self.motion_signature(c,t),round(self.nav_offset(c,t),6),width,cap,static,animatic)
  if key==getattr(self,'_mobile_key',None):return self._mobile_frame
  self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.geometry=[];self._parent=None;id=c['id'];thanks=False
  actions={'baseline-hook':lambda:self.two_engines(c,t,True),'cost-loop':lambda:self.cost_loop(c,t),'engine-choice':lambda:self.engine_choice(c,t),'decode-rounds':lambda:self.decode_rounds(c,t),'draft-start':lambda:self.candidates(c,t,'draft-start'),'rejected-chain':lambda:self.rejected_chain(c,t),'hardware-budget':lambda:self.hardware_budget(c,t),'confidence':lambda:self.confidence_v12(c,t),'verification-proof':lambda:self.strategy_result(c,t),'input-bridge':lambda:self.input_bridge(c,t),'replay-structure':lambda:self.replay_structure(c,t),'replay-exact':lambda:self.replay_v12(c,t),'replay-bounded':lambda:self.replay_v12(c,t),'quality-and-reuse':lambda:self.quality_and_reuse(c,t),'open-value':lambda:self.implementation_path(c,t),'private-stack':lambda:self.private_v12(c,t),'production-boundary':lambda:self.boundary_v12(c,t),'cost-proof':lambda:self.unit_cost(c,t),'training-boundary':lambda:self.training_v12(c,t),'conclusion':lambda:self.conclusion(c,t)}
  if id=='closing':thanks=self.closing(c,t)
  else:actions[id]()
  self.header(c,t,thanks);self.footer(c,elapsed)
  if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
  self._mobile_key=key;self._mobile_frame=self.im;return self.im
 def motion_signature(self,c,t):
  # Full-time keys only for moving intervals; stable comparisons remain frozen.
  id=c['id'];clip=lambda a,n:round(max(0,min(n,t-a)),6)
  if id=='cost-loop':return (clip(event(c,'服务启动后',.22),.9),clip(event(c,'每来一个请求',.45),2.4))
  if id=='decode-rounds':return (clip(event(c,'如果一轮',.55),.8),t>=event(c,'如果一轮',.55))
  if id=='rejected-chain':return (t>=event(c,'前两个通过',.18),t>=event(c,'第三个被拒绝',.35),t>=event(c,'后面',.5),t>=event(c,'后面',.5)+.3)
  if id=='hardware-budget':return (t>=event(c,'批次太小',.4),)
  if id=='confidence':return (clip(event(c,'为每条请求',.5),1.1),)
  if id=='verification-proof':return tuple(t>=event(c,s,p) for s,p in [('减少验证计算',.2),('相近数量',.1),('估算吞吐',.55),('百分之五点四',.65)])
  if id=='input-bridge':return (clip(event(c,'算成缓存',.55),.9),)
  if id=='replay-structure':return (t>=event(c,'全局缓存',.3),t>=event(c,'后段',.45))
  if id=='replay-exact':return tuple(t>=event(c,'按完整依赖恢复',.55)+i*.5 for i in range(3))
  if id=='replay-bounded':return (clip(event(c,'恢复范围截在',.1),1.25),)
  if id=='quality-and-reuse':return (t>=event(c,'vLLM',.55),)
  if id=='open-value':return (t>=event(c,'开发者能看到',.65),)
  if id=='private-stack':return (clip(event(c,'再配支持',.3),.9),t>=event(c,'引擎负责执行',.65))
  if id=='production-boundary':return tuple(t>=event(c,s,.15+i*.1) for i,s in enumerate(['长期缓存','分离部署','负载均衡']))
  if id=='cost-proof':return (t>=event(c,'更多有效词元',.4),)
  if id=='conclusion':
   a=event(c,'合适的部分',.68);return (clip(a,.65),t>=a+.65,clip(a+1.1,.65))
  return super().motion_signature(c,t)
