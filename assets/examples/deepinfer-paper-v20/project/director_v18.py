"""Define network depth before using the layer × token-position grid."""
from PIL import Image,ImageDraw
from director_v17 import Paper as V17,ANCHORS_BY_CUE
from director_v14 import TEAL,BLUE,AMBER,PALE,blend
from director_v10 import ramp
from continuity import WHITE,INK,MUTED,GOLD,CORAL,LINE

class Paper(V17):
 def layer_model(self,c,t):
  self.txt(800,267,'同一份输入 → 多层共同处理 → 更新后的数值表示',44,BLUE,anchor='mm')
  self.panel((90,315,525,710),'example-input',line=BLUE);self.txt(307,359,'本次输入',48,BLUE,anchor='mm')
  first=self.ev(c,'小王属于研发部',.08);second=self.ev(c,'研发部可以报销打车费',.2);question=self.ev(c,'回答小王能否报销',.32)
  if t>=first:self.fragment(120,405,375,'小王属于研发部',GOLD,INK,70)
  if t>=second:
   self.d.rounded_rectangle((120,500,495,618),12,fill=GOLD,outline=LINE,width=2);self.txt(307,535,'研发部',44,INK,anchor='mm');self.txt(307,585,'可以报销打车费',44,INK,anchor='mm')
  if t>=question:self.txt(307,668,'小王能否报销？',44,TEAL,anchor='mm')
  begin=self.ev(c,'多层让后层',.4);done=[self.ev(c,'前层形成的中间表示',.5)+i*.9 for i in range(3)]
  path=[(550,510),(590,510),(590,368),(610,368)];self.arrow(path,BLUE)
  if t>=begin:self.packet(path,ramp(t,begin,.8),BLUE)
  for row in range(3):
   y=320+row*150;active=t>=done[row]
   self.panel((635,y,1045,y+96),f'network-layer-{row}',line=TEAL if active else LINE,fill='#DDF3EB' if active else WHITE)
   self.txt(840,y+48,f'层 {row+1} · 参数 {"ABC"[row]}',46,TEAL if active else INK,anchor='mm')
   if row<2:
    self.arrow_line((840,y+108),(840,y+138),BLUE if active else LINE)
    if active:self.packet([(840,y+108),(840,y+138)],ramp(t,done[row],.7),BLUE)
   if active:
    self.arrow_line((1070,y+48),(1130,y+48),TEAL);self.fragment(1160,y+12,340,f'中间表示 {row+1}',TEAL,WHITE,72)
  self.note('各层共同处理输入信息 · 本例不固定指定每层的语义分工')
 def grid_base(self):
  self.d.rounded_rectangle((100,275,1490,342),12,fill=BLUE);self.txt(795,308,'已有全局共享状态 · 持续参与后部计算',48,WHITE,anchor='mm')
  self.d.line((352,342,352,690),fill=BLUE,width=6)
  for row in range(3):
   y=395+row*106;self.txt(100,y+30,f'第 {row+1} 层',44,INK,anchor='lm');self.arrow_line((352,y+30),(398,y+30),BLUE)
   for j in range(10):self.cell(row,j,PALE)
  self.txt(100,694,'位置 →',42,MUTED,anchor='lm')
  for j in range(10):self.txt(467+j*104,694,str(j+1),42,MUTED,anchor='mm')
 def grid_reading(self,c,t):
  self.grid_base()
  # Keep known global state present but reduce its weight while teaching axes.
  for roi in [(100,275,1490,342),(330,342,410,690)]:self.im.paste(Image.blend(self.im.crop(roi),self.bg.crop(roi),.62),roi)
  self.d=ImageDraw.Draw(self.im);column=self.ev(c,'这一列',.4)
  if t>=self.ev(c,'每一行',.1) and t<column:
   self.d.rounded_rectangle((413,388,1475,462),12,outline=TEAL,width=5)
  if t>=column:
   j=9;x=425+j*104;self.d.rounded_rectangle((x-8,386,x+92,678),12,outline=TEAL,width=5);self.txt(x+42,369,'位置 10',42,TEAL,anchor='mm')
   for row,phrase in enumerate(['第一层','第二层','第三层']):
    if t>=self.ev(c,phrase,.5+row*.1):
     self.cell(row,j,['#CFF3E7','#A9E5D4','#7CD5BE'][row],TEAL)
     for k,w in enumerate([[46,27,38],[23,52,33],[41,32,53]][row]):
      y=407+row*106+k*13;self.d.rounded_rectangle((x+14,y,x+14+w,y+6),2,fill=TEAL)
  self.note('同一列是同一个词元位置；各行是不同计算层的中间状态')
 def local_dependencies(self,c,t,widen=False,bounded=False):
  self.grid_base()
  if not widen and not bounded:
   self.cell(2,9,GOLD)
   if t>=self.ev(c,'第二层最后三个位置',.3):
    for j in range(7,10):self.cell(1,j,GOLD);self.dep(2,9,j)
   if t>=self.ev(c,'第一层的邻近位置',.65):
    for j in range(5,10):self.cell(0,j,GOLD)
    self.dep(1,7,5);self.dep(1,9,9)
   self.note('黄箭头向上追依赖：第3层 → 第2层 → 第1层')
  elif widen:
   for row,start,phrase,p in [(2,8,'最后两个位置',.1),(1,6,'最后四个',.4),(0,4,'最后六个',.65)]:
    if t>=self.ev(c,phrase,p):
     for j in range(start,10):self.cell(row,j,GOLD)
   if t>=self.ev(c,'最后四个',.4):self.dep(2,8,6)
   if t>=self.ev(c,'最后六个',.65):self.dep(1,6,4)
   self.note('本图每个位置依赖上层相邻3个位置 · 数量为教学示意')
  else:
   a=self.ev(c,'近期片段',.18);q=ramp(t,a,1.2)
   for row,start in [(0,4),(1,6),(2,8)]:
    for j in range(start,10):self.cell(row,j,GOLD if j>=8 else blend(GOLD,PALE,q))
   if t>=a:
    self.d.line((1242,365,1242,677),fill=CORAL,width=5);self.txt(1222,376,'局部重放起点',42,CORAL,anchor='rm')
   self.note('局部依赖截在近期片段内；上方蓝色全局状态一直保留',TEAL)
 def frame(self,c,elapsed,width=1600,static=False,animatic=False):
  if c['id'] not in ['model-layers','grid-reading']:return super().frame(c,elapsed,width,static,animatic)
  from scene import caption_ranges
  t=c['duration_s']*.98 if static or animatic else elapsed;ranges=caption_ranges(c);cap=next((i for i,(a,b) in enumerate(ranges) if elapsed<b),len(ranges)-1)
  key=(c['id'],self.motion_signature(c,t),round(self.nav_offset(c,t),6),width,cap,static,animatic)
  if key==getattr(self,'_mobile_key',None):return self._mobile_frame
  self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.geometry=[];self._parent=None
  if c['id']=='model-layers':self.layer_model(c,t)
  else:self.grid_reading(c,t)
  self.header(c,t);self.footer(c,elapsed)
  if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
  self._mobile_key=key;self._mobile_frame=self.im;return self.im
