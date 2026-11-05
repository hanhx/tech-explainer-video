"""V19: equal work, visible forward dependencies, then explicit local-read truncation."""
from PIL import ImageDraw
from director_v18 import Paper as V18,ANCHORS_BY_CUE
from director_v14 import TEAL,BLUE,AMBER,PALE
from director_v10 import ramp
from continuity import WHITE,INK,MUTED,GOLD,CORAL,LINE

AFFECTED_VISUAL={'batch-reuse','hardware-choice','model-layers','model-structure','grid-reading','one-dependency','window-expands','bounded-replay','quality-boundary'}
class Paper(V18):
 def hardware(self,c,t,batch=False,unknown=False):
  if c['id']!='batch-reuse':return super().hardware(c,t,batch,unknown)
  self.panel((95,290,765,715),'separate-runs');self.panel((885,290,1505,715),'one-batch')
  self.txt(430,345,'分 3 轮完成',50,BLUE,anchor='mm');self.txt(1195,345,'合成 1 批完成',50,TEAL,anchor='mm')
  a=self.ev(c,'分三轮',.15)
  for i,s in enumerate(['请先','填写','表格']):
   y=415+i*96;active=t>=a+i*.6
   self.fragment(125,y,135,s,GOLD,INK,65)
   self.arrow_line((275,y+32),(295,y+32),LINE)
   self.d.rounded_rectangle((305,y,505,y+65),10,fill=BLUE if active else PALE);self.txt(405,y+32,'读取权重',42,WHITE if active else MUTED,anchor='mm')
   self.arrow_line((520,y+32),(545,y+32),BLUE if active else LINE)
   self.d.rounded_rectangle((560,y,730,y+65),10,fill='#DDF3EB' if active else WHITE,outline=LINE,width=2);self.txt(645,y+32,'算 1 个',42,TEAL if active else MUTED,anchor='mm')
  joined=t>=self.ev(c,'合成一批',.42)
  for i,s in enumerate(['请先','填写','表格']):
   x=920+i*185;self.fragment(x,500,140,s,GOLD,INK,65)
   self.d.rounded_rectangle((x,635,x+140,700),10,fill='#DDF3EB' if joined else WHITE,outline=LINE,width=2);self.txt(x+70,667,'计算',42,TEAL if joined else MUTED,anchor='mm')
   self.arrow_line((x+45,578),(x+45,620),TEAL if joined else LINE)
  self.d.rounded_rectangle((930,395,1460,460),12,fill=BLUE if joined else PALE);self.txt(1195,427,'权重读取：可共用一部分',42,WHITE if joined else MUTED,anchor='mm')
  if joined:
   self.d.line((930,427,900,427,900,600,1395,600),fill=BLUE,width=4)
   for i in range(3):self.arrow_line((1025+i*185,600),(1025+i*185,620),BLUE)
  self.note('两边都计算 3 个位置；蓝色标出读取权重的工作')
 def hardware_choice(self,c,t):
  self.candidate_row(300,words=['并','附上','车票','等','凭证'])
  self.panel((100,440,875,710),'cost-components');self.txt(487,482,'一轮执行的工作 · 示意',48,BLUE,anchor='mm')
  for i,(label,extra) in enumerate([('验3个',150),('验5个',245)]):
   y=552+i*86;self.txt(270,y,label,44,INK,anchor='rm')
   self.d.rounded_rectangle((300,y-26,550,y+26),8,fill=BLUE);self.txt(425,y,'共用读取',42,WHITE,anchor='mm')
   self.d.rounded_rectangle((560,y-26,560+extra,y+26),8,fill=TEAL);self.txt(560+extra/2,y,'计算',42,WHITE,anchor='mm')
  self.card((990,440,1500,710),'先测用时','再结合接受预测',TEAL);self.arrow_line((900,575),(960,575),TEAL)
  self.note('分解和长度均为教学示意；不同验证量的用时须由设备实测')
 def layer_model(self,c,t):
  super().layer_model(c,t)
  done=[self.ev(c,'前层形成的中间表示',.5)+i*.9 for i in range(3)]
  for i in range(2):
   y=320+i*150;roi=(812,y+97,868,y+149);self.im.paste(self.bg.crop(roi),roi);self.d=ImageDraw.Draw(self.im)
   if t>=done[i]:
    path=[(1330,y+94),(1330,y+118),(840,y+118),(840,y+138)]
    self.arrow(path,TEAL);self.packet(path,ramp(t,done[i],.7),TEAL)
 def shared_card(self):
  self.card((100,500,365,650),'共享状态','前部已算好',BLUE)
 def operator(self,title='当前层计算',approx=False,write=False,target_label=None):
  self.card((465,500,1115,650),title,'使用本层参数更新表示',TEAL)
  self.card((1180,500,1500,650),'近似结果 ≈' if approx and write else '新结果' if write else '待算出',target_label or ('第3层位置9' if approx else '第3层位置10'),TEAL if write else BLUE)
  self.arrow_line((390,575),(435,575),BLUE);self.arrow_line((1135,575),(1165,575),TEAL if write else LINE)
 def architecture(self,c,t):
  self.card((550,280,1050,430),'上一层的中间结果','要传给当前层',TEAL)
  self.shared_card();self.operator('当前层计算',target_label='传给下一层')
  self.arrow_line((800,450),(800,480),TEAL)
  self.txt(790,695,'本层近期窗口：还待准备',46,AMBER,anchor='mm')
  self.note('绿色是前层结果这一条主链；蓝色是共享状态这一条旁路')
 def grid_reading(self,c,t):
  super().grid_reading(c,t)
  x=1403
  for i,phrase in enumerate(['第二层','第三层']):
   start=self.ev(c,phrase,.6+i*.1)
   if t>=start:
    y=395+i*106;self.arrow_line((x,y+70),(x,y+94),TEAL)
    self.packet([(x,y+70),(x,y+94)],ramp(t,start,.7),TEAL)
 def parent_cards(self,positions=(8,9,10),omit=False):
  for i,p in enumerate(positions):
   x=150+i*480;kept=not omit or p>=9
   self.d.rounded_rectangle((x,340,x+350,440),14,fill='#DDF3EB' if kept else PALE,outline=TEAL if kept else LINE,width=3)
   self.txt(x+175,378,f'第2层 · 位置{p}',44,TEAL if kept else MUTED,anchor='mm')
   for j,w in enumerate([245-i*30,180+i*20]):self.d.rounded_rectangle((x+35,412+j*10,x+35+w,418+j*10),2,fill=TEAL if kept else LINE)
 def parent_paths(self,c,t,positions=(8,9,10),omit=False,start=0):
  for i,p in enumerate(positions):
   if omit and p<9:continue
   path=[(325+i*480,455),(600+i*200,480),(600+i*200,485)]
   self.arrow(path,TEAL);self.packet(path,ramp(t,start+i*.08,.8),TEAL)
 def local_dependencies(self,c,t,widen=False,bounded=False):
  if widen:return super().local_dependencies(c,t,True,False)
  if bounded:
   self.txt(800,289,'放大重放边界：算位置9时，局部读哪些输入？',46,INK,anchor='mm')
   omitted=t>=self.ev(c,'片段内的输入',.38)
   self.parent_cards((7,8,9),omitted);self.shared_card()
   a=self.ev(c,'片段内的输入',.38);write=t>=a+1.55
   self.operator('这一层的局部计算',True,write)
   self.parent_paths(c,t,(7,8,9),omitted,a)
   if omitted:
    self.d.line((1070,320,1070,465),fill=CORAL,width=5)
    for i in [0,1]:
     x=150+i*480;self.txt(x+175,465,'省略局部读取',42,CORAL,anchor='mm')
   self.note('省略的是片段外的局部读取；蓝色共享状态仍参与计算')
  else:
   self.txt(800,289,'本例窗口规则：结合上层最近3个位置，再计算当前位置',46,INK,anchor='mm')
   self.parent_cards();self.shared_card()
   start=self.ev(c,'三份结果读进来',.45);write=t>=max(start+1.55,self.ev(c,'才写出',.7))
   self.operator('第3层 · 本位置计算',False,write)
   if t>=start:self.parent_paths(c,t,start=start)
   if write:self.d.rounded_rectangle((1190,508,1490,642),16,outline=TEAL,width=5)
   self.note('先读取第2层的结果，再算出第3层的新结果：这就是依赖')
 def quality_check(self,c,t):
  self.card((100,430,555,680),'近似窗口状态 ≈','局部输入有所省略',AMBER)
  self.card((100,255,1500,340),'前部已算好的共享状态继续保留',color=BLUE)
  self.arrow_line((900,360),(900,410),BLUE);self.arrow_line((580,555),(655,555),TEAL);self.card((685,430,1115,680),'用于继续生成','得到实际回答',TEAL)
  if t>=self.ev(c,'相同的输入任务',.68):
   self.card((1190,380,1500,500),'准备时间',color=BLUE);self.card((1190,555,1500,675),'回答质量',color=TEAL)
  self.note('用同一输入任务比较：是否少等了，以及回答是否受到影响')
