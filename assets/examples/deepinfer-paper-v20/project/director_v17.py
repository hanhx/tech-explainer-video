"""V17: keep the first half; connect the input work, replay, cost, and uses.
Inter-cue narration holds are edited separately from the selected speech tempo.
"""
from PIL import ImageDraw
from director_v16 import Paper as V16,ANCHORS_BY_CUE
from director_v14 import TEAL,BLUE,AMBER,PALE
from director_v10 import ramp
from continuity import BG,WHITE,INK,MUTED,GOLD,CORAL,LINE

class Paper(V16):
 def input_return(self,c,t):
  focus=t>=self.ev(c,'生成之前',.5)
  self.card((100,285,690,450),'处理输入','公司制度 + 员工问题',BLUE,selected=focus)
  self.arrow_line((720,368),(865,368),LINE)
  self.card((900,285,1490,450),'逐步生成回答','DSpark 安排验证长度',TEAL,selected=not focus)
  if focus:
   self.panel((120,515,670,700),'company-policy',line=BLUE);self.txt(395,556,'长长的公司差旅制度',48,BLUE,anchor='mm')
   for j in range(3):self.d.rounded_rectangle((175,605+j*24,610-j*35,615+j*24),4,fill=LINE)
   self.arrow_line((720,605),(865,605),BLUE);self.card((900,515,1490,700),'接下来解释这一段','准备生成会用的状态',BLUE)
  else:self.txt(800,600,'刚才解释了生成；还有处理输入的工作',48,TEAL,anchor='mm')
  self.note('同一条请求：输入在前、生成在后；这里转去解释输入')
 def kv(self,c,t):
  self.card((90,355,410,615),'公司制度','+ 员工问题',BLUE)
  self.panel((560,280,1020,655),'model-layers',line=BLUE);self.txt(790,325,'模型逐层处理',48,BLUE,anchor='mm')
  run=self.ev(c,'逐层处理',.2);cache=self.ev(c,'中间结果',.4);named=self.ev(c,'KV状态',.6)
  self.arrow([(435,480),(520,480),(520,397),(595,397)],BLUE)
  for i in range(3):
   y=365+i*91;active=t>=run+i*.5
   self.d.rounded_rectangle((610,y,970,y+65),10,fill='#E5F2FA' if active else WHITE,outline=BLUE if active else LINE,width=3)
   self.txt(790,y+32,f'第 {i+1} 层',44,BLUE if active else MUTED,anchor='mm')
   if i<2:self.arrow_line((790,y+70),(790,y+86),BLUE if active else LINE)
  self.panel((1180,280,1500,705),'memory-kv',line=BLUE);self.txt(1340,325,'显存',50,BLUE,anchor='mm')
  self.d.rounded_rectangle((1210,365,1470,425),10,fill=BLUE);self.txt(1340,395,'模型参数',44,WHITE,anchor='mm')
  for i in range(3):
   if t>=cache+i*.45:
    y=465+i*66;self.fragment(1210,y,260,'KV 状态' if t>=named else '中间状态',GOLD,INK,52)
    lane=1090-i*25;self.arrow([(985,397+i*91),(lane,397+i*91),(lane,y+26),(1160,y+26)],AMBER)
    self.packet([(985,397+i*91),(lane,397+i*91),(lane,y+26),(1160,y+26)],ramp(t,cache+i*.45,.8),GOLD)
  new=self.ev(c,'后面写回答',.78)
  if t>=new:
   self.fragment(105,654,305,'新输入',TEAL,WHITE,62);self.arrow([(440,685),(790,685),(790,670)],TEAL)
   self.arrow([(1160,650),(1085,650),(1085,685),(900,685),(900,670)],AMBER)
  self.note('输入产生中间状态；后续生成利用这些结果继续算')
 def architecture(self,c,t):
  self.card((95,350,545,660),'前部层','处理完整输入',BLUE)
  a=self.ev(c,'共享的全局状态',.5)
  if t>=a:
   self.arrow([(575,440),(650,440),(650,332),(690,332)],BLUE);self.d.rounded_rectangle((710,300,1450,365),12,fill=BLUE);self.txt(1080,332,'共享的全局状态',48,WHITE,anchor='mm')
   self.d.line((710,332,670,332,670,685),fill=BLUE,width=6)
  for i in range(3):
   y=410+i*95;self.panel((800,y,1460,y+72),f'back-layer-{i}',line=TEAL);self.txt(965,y+36,f'后部第 {i+1} 层',44,INK,anchor='mm')
   if t>=a:self.arrow_line((670,y+36),(775,y+36),BLUE)
   self.d.rounded_rectangle((1180,y+12,1438,y+60),8,fill='#FFF1D6');self.txt(1310,y+36,'窗口待补',42,AMBER,anchor='mm')
  self.note('共享状态已有；接下来研究每层窗口还需准备多少计算')
 def quality_check(self,c,t):
  self.d.rounded_rectangle((100,275,1490,342),12,fill=BLUE);self.txt(795,308,'完整输入已处理 · 共享的全局状态保留',48,WHITE,anchor='mm')
  self.card((100,425,535,660),'后部窗口准备','少做局部重算',AMBER)
  self.arrow_line((565,540),(645,540),TEAL);self.card((675,425,1085,660),'窗口近似重建','继续生成',TEAL)
  if t>=self.ev(c,'近似重建',.65):
   self.card((1170,400,1490,515),'回答质量',color=BLUE);self.card((1170,560,1490,675),'实际用时',color=TEAL)
  self.note('省下哪部分计算已经明确；再一起检查质量与效率')
 def service_result(self,c,t):
  for i in range(3):
   y=325+i*120;self.person(145,y+32,TEAL if i==0 else BLUE,f'员工{["甲","乙","丙"][i]}',.5)
   self.fragment(285,y-10,400,['差旅怎么申请','假期怎么申请','报销需要什么'][i],GOLD,INK,70)
   a=self.ev(c,'更多有效输出',.82)+i*.4
   if t>=a:
    self.d.rounded_rectangle((700,y+4,775,y+48),12,fill=TEAL);self.txt(737,y+26,'好',42,WHITE,anchor='mm')
   else:self.clock_icon(737,y+26)
  self.gpu((890,430,1490,675),active=.8,label=False)
  if t>=self.ev(c,'生成时',.15):self.card((880,280,1490,385),'生成：选择送验候选',color=TEAL)
  if t>=self.ev(c,'重算',.4):self.txt(1190,405,'输入：减少后部局部重算',44,AMBER,anchor='mm')
  self.note('同样质量和响应要求下，比较单位设备的有效业务产出')
 def open_code(self,c,t):
  self.panel((115,325,615,690),'code-sheet',line=TEAL);self.txt(365,382,'DeepInfer',56,TEAL,anchor='mm');self.txt(365,475,'{ }',110,TEAL,anchor='mm')
  for i in range(3):self.d.rounded_rectangle((190,570+i*30,540-i*30,580+i*30),4,fill=LINE)
  labels=[('看方法怎样组合与调度','开源代码'),('复现自己的运行结果','复现测试'),('按任务选择适合部分','自己任务')]
  for i,(s,phrase) in enumerate(labels):
   y=315+i*135
   if t>=self.ev(c,phrase,.4+i*.2):self.card((805,y,1485,y+105),s,color=TEAL if i<2 else BLUE);self.arrow_line((650,y+52),(775,y+52),TEAL)
  self.note('同类方法也存在于 vLLM；这里研究官方的具体执行实现')
 def deployment_full(self,c,t):
  self.panel((95,330,545,680),'support-range',line=BLUE);self.txt(320,390,'匹配支持条件',48,BLUE,anchor='mm')
  for j,(label,phrase) in enumerate([('模型与权重许可','许可'),('兼容硬件','模型和硬件'),('运行环境','模型和硬件')]):
   if t>=self.ev(c,phrase,.2+j*.1):self.txt(320,475+j*72,label,44,INK,anchor='mm')
  self.arrow_line((575,500),(660,500),BLUE);self.card((690,395,1110,635),'DeepInfer','离线推理核心',TEAL)
  if t>=self.ev(c,'线上服务',.7):
   self.panel((1160,300,1500,700),'services',line=TEAL);self.txt(1330,345,'外围服务',46,TEAL,anchor='mm')
   for j,(s,phrase) in enumerate([('外部缓存','外部缓存'),('流量调度','流量调度')]):
    if t>=self.ev(c,phrase,.8+j*.1):self.card((1200,415+j*145,1460,520+j*145),s,color=BLUE)
  self.note('已有许可与兼容条件，再把离线核心接成线上服务')
 def training_steps(self,c,t):
  training=t>=self.ev(c,'训练流程',.22)
  self.card((95,390,535,645),'推理执行','生成候选回答' if training else '用已有模型回答',TEAL)
  if training:
   self.panel((700,300,1490,700),'training-other',line=AMBER);self.txt(1095,360,'训练系统中的后续工作',50,AMBER,anchor='mm')
  if t>=self.ev(c,'评分',.5):
   self.arrow_line((565,515),(665,515),TEAL);self.card((755,440,1060,640),'评分 / 学习',color=AMBER);self.arrow_line((1080,535),(1130,535),AMBER);self.card((1150,440,1450,640),'更新参数',color=AMBER)
  self.note('推理生成与学习更新是不同环节；收益分开核算')
