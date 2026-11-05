"""Original flat-illustration art direction and continuous mechanism staging.
No creator artwork or generated realistic hardware is used.
"""
from pathlib import Path
from functools import lru_cache
import math,random
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import base

ROOT=Path(__file__).resolve().parent
BG='#F2F9FC'; WHITE='#FFFFFF'; INK='#173D50'; MUTED='#497187'; TEAL='#07977D'; MINT='#CFF3E7'; GOLD='#FFB13B'; PURPLE='#3984BF'; CORAL='#EF7459'; LINE='#B7D8DF'; BODY='#FFFFFF'; SHADOW='#D5EAE8'; AMBER='#AD6500'
base.BG=BG;base.PAPER=WHITE;base.INK=INK;base.MUTED=MUTED;base.BLUE=TEAL;base.GOLD=GOLD;base.RED=CORAL;base.LINE=LINE
import os
FONT=os.environ.get('EXPLAINER_FONT','/System/Library/Fonts/STHeiti Medium.ttc')
@lru_cache(None)
def font(size):return ImageFont.truetype(FONT,max(1,round(size)))
def ease(p):return base.ease(p)
def mix(a,b,p):return a+(b-a)*p
def rectmix(a,b,p):return tuple(mix(x,y,p) for x,y in zip(a,b))

class Paper(base.Paper):
    def __init__(self):
        self.bg=Image.new('RGB',(1600,900),BG);d=ImageDraw.Draw(self.bg)
        # A light perspective grid gives the flat illustrations a coherent stage.
        for x in range(-800,2401,160):d.line((800+(x-800)*.46,235,x,804),fill='#D9EBF0',width=1)
        for y in [255,289,330,380,441,515,605,714]:d.line((0,y,1600,y),fill='#D9EBF0',width=1)
        self.labels=[]
    def txt(self,x,y,s,size=30,c=INK,anchor=None):
        self.d.text((round(x),round(y)),s,font=font(size),fill=AMBER if c==GOLD else c,anchor=anchor)
    def box(self,b,fill=WHITE,line=LINE,r=14,shadow=True):
        x,y,X,Y=b
        if shadow:self.d.rounded_rectangle((x+5,y+7,X+5,Y+7),r,fill='#D8EBF0')
        self.d.rounded_rectangle(b,r,fill=fill,outline=line,width=2)
    def tag(self,x,y,s,c=TEAL):
        w=self.d.textbbox((0,0),s,font=font(24))[2]+28
        self.d.rounded_rectangle((x,y,x+w,y+43),10,fill=c)
        self.txt(x+14,y+21,s,24,INK if c==GOLD else WHITE,anchor='lm')
    def note(self,s,c=MUTED):self.txt(800,758,s,27,c,anchor='mm')
    def capsule(self,x,y,s='请求 A',c=TEAL,w=165,h=56):
        self.d.rounded_rectangle((x+4,y+5,x+w+4,y+h+5),h/2,fill='#D3E9EB')
        self.d.rounded_rectangle((x,y,x+w,y+h),h/2,fill=c,outline=INK,width=2)
        self.d.ellipse((x+12,y+15,x+38,y+41),fill=WHITE)
        self.txt(x+25,y+28,s[-1] if s.startswith('请求 ') else '•',22,c,anchor='mm')
        self.txt(x+49,y+h/2,s,25,WHITE,anchor='lm')
    def tile(self,b,label='',sub='',color=GOLD,selected=False):
        x,y,X,Y=b
        self.d.rounded_rectangle((x+4,y+8,X+4,Y+8),9,fill='#D6E9EC')
        self.d.rounded_rectangle(b,9,fill=WHITE,outline=INK if selected else LINE,width=3 if selected else 2)
        self.d.rounded_rectangle((x+1,y+1,X-1,y+12),7,fill=color)
        if label:self.txt((x+X)/2,(y+Y)/2-7 if sub else (y+Y)/2+3,label,26,INK,anchor='mm')
        if sub:self.txt((x+X)/2,Y-21,sub,22,color,anchor='mm')
        if selected:
            self.d.line((x-8,y+18,x-8,y-8,x+18,y-8),fill=TEAL,width=3)
            self.d.line((X-18,Y+8,X+8,Y+8,X+8,Y-18),fill=TEAL,width=3)
    def cpu(self,b,active=False,label=True):
        x,y,X,Y=b;w=X-x;h=Y-y
        for j in range(1,7):
            xx=x+j*w/7;self.d.rounded_rectangle((xx-5,y-14,xx+5,Y+14),3,fill=GOLD,outline=INK,width=2)
        for j in range(1,5):
            yy=y+j*h/5;self.d.rounded_rectangle((x-14,yy-5,X+14,yy+5),3,fill=GOLD,outline=INK,width=2)
        self.d.rounded_rectangle((x+8,y+10,X+8,Y+10),18,fill=SHADOW)
        self.d.rounded_rectangle(b,18,fill=TEAL,outline=INK,width=3)
        self.d.rounded_rectangle((x+18,y+17,X-18,Y-17),12,fill=WHITE,outline=INK,width=3)
        self.d.rounded_rectangle((x+35,y+36,X-35,Y-36),8,fill=MINT if active else '#E9F8F5',outline=TEAL,width=2)
        self.txt((x+X)/2,(y+Y)/2,'CPU',max(19,w*.16),INK,anchor='mm')
        if label:self.txt((x+X)/2,Y+40,'控制与调度',26,TEAL,anchor='mm')
    def gpu(self,b,active=0,label=True):
        x,y,X,Y=b;w=X-x;h=Y-y
        self.d.rounded_rectangle((x+9,y+11,X+9,Y+11),18,fill=SHADOW)
        self.d.rounded_rectangle(b,18,fill=BODY,outline=INK,width=3)
        self.d.line((x+18,y+10,X-20,y+10),fill=WHITE,width=3)
        for i in range(13):
            xx=x+35+i*(w-90)/13;self.d.rectangle((xx,Y,xx+12,Y+17),fill=GOLD,outline=INK,width=1)
        core=(x+25,y+24,x+w*.71,Y-25)
        self.d.rounded_rectangle(core,12,fill=WHITE,outline=TEAL,width=4)
        cx,cy,cX,cY=core
        for r in range(3):
            for c in range(4):
                xx=cx+14+c*(cX-cx-25)/4;yy=cy+14+r*(cY-cy-25)/3
                self.d.rounded_rectangle((xx,yy,xx+(cX-cx-40)/4,yy+(cY-cy-38)/3),4,fill=GOLD if r*4+c<int(active*12) else (MINT if (r+c)%2 else '#D9EEFB'),outline=TEAL,width=1)
        for j in range(3):
            yy=y+40+j*(h-65)/3;self.d.rounded_rectangle((X-w*.21,yy,X-w*.06,yy+h*.12),5,fill=WHITE,outline=INK,width=2)
        self.d.ellipse((X-20,y+10,X-10,y+20),fill=GOLD,outline=INK,width=1)
        if label:
            self.txt((x+X)/2,y-30,'GPU / NPU',30,INK,anchor='mm')
            self.txt((x+X)/2,Y+51,'主要张量计算',25,TEAL,anchor='mm')
    def ssd(self,b,label=True):
        x,y,X,Y=b;w=X-x;h=Y-y
        self.d.rounded_rectangle((x+5,y+8,X+5,Y+8),13,fill=SHADOW)
        self.d.rounded_rectangle(b,13,fill=BODY,outline=INK,width=3)
        for j in range(4):
            xx=x+30+j*(w-65)/4;self.d.rounded_rectangle((xx,y+23,xx+(w-95)/4,Y-23),5,fill=WHITE,outline=INK,width=2)
        for j in range(5):self.d.rectangle((x-8,y+12+j*(h-22)/5,x+4,y+19+j*(h-22)/5),fill=GOLD,outline=INK,width=1)
        if label:self.txt((x+X)/2,y-25,'SSD · 模型检查点',25,MUTED,anchor='mm')
    def mini_hbm(self,b,occupied=3,loaded=True,label=True):
        x,y,X,Y=b;w=X-x
        for off in [20,10,0]:self.d.rounded_rectangle((x+off*.35,y+off,X+off*.35,Y+off),12,fill='#E4F1F7' if off else WHITE,outline=INK,width=2)
        if label:self.txt((x+X)/2,y-27,'HBM / 显存',28,INK,anchor='mm')
        if loaded:
            self.d.rounded_rectangle((x+14,y+17,X-14,y+75),7,fill=PURPLE,outline=INK,width=2)
            self.txt((x+X)/2,y+46,'权重',25,WHITE,anchor='mm')
        self.txt(x+16,y+101,'KV 块池',23,GOLD)
        for j in range(8):
            xx=x+15+j%4*(w-26)/4;yy=y+139+j//4*58
            self.d.rounded_rectangle((xx,yy,xx+(w-42)/4,yy+44),5,fill=GOLD if j in [2,5,7][:occupied] else '#EAF5F7',outline=INK,width=1)
        self.txt((x+X)/2,Y-24,'工作区',23,MUTED,anchor='mm')
    def pipe(self,pts,c=TEAL,progress=None):
        self.d.line(pts,fill='#E0F0F4',width=10,joint='curve');self.d.line(pts,fill=c,width=2,joint='curve')
        if progress is not None:
            x,y=base.point(pts,progress);self.d.rounded_rectangle((x-13,y-11,x+13,y+11),5,fill=c,outline=WHITE,width=2)
    def board(self,p,mode='roles',t=0):
        cpu=(150,470,370,640);gpu=(655,370,1095,620);hbm=(1215,375,1485,690);ssd=(105,290,415,390)
        # Same anchors across the request's lifecycle. Only relevant objects change.
        self.pipe([(390,550),(630,550)],TEAL,ease((p-.15)*2) if mode=='schedule' else None)
        self.pipe([(1110,495),(1190,495)],GOLD,ease((t-1.5)/.6) if mode in ['prefill','decode'] else None)
        if mode not in ['hook','schedule']:self.ssd(ssd)
        self.cpu(cpu,active=mode in ['hook','schedule','prefill'])
        self.gpu(gpu,active=(min(1,t/.55) if mode=='prefill' else min(1,t*1.5/self._source_duration) if mode=='decode' else 0))
        if mode!='hook':self.mini_hbm(hbm,occupied=min(3,int(p*4)) if mode=='prefill' else 3 if mode in ['kv','decode','finish'] else 0,loaded=mode!='weights' or p>.47)
        if mode=='hook':
            self.capsule(120,350,'请求 A');self.tag(700,715,'等待下一批工作',CORAL)
            self.d.rounded_rectangle((150,710,370,726),8,fill='#E0F1F2');self.d.rounded_rectangle((150,710,150+190*ease(p),726),8,fill=TEAL)
            self.txt(260,755,'CPU 正在准备',26,MUTED,anchor='mm')
            self.txt(800,280,'请求在排队，算力却有空档',35,INK,anchor='mm')
        elif mode=='roles':
            self.capsule(450,710,'请求 A');self.txt(510,600,'执行信息',25,TEAL,anchor='mm')
        elif mode=='weights':
            path=[(415,335),(485,335),(485,265),(1170,265),(1170,425),(1320,425)]
            if p<.47:
                x,y=base.point(path,ease(p/.47));self.tile((x-53,y-26,x+53,y+26),'权重',color=PURPLE)
            self.note('启动准备：装入模型参数，供后续请求反复使用')
        elif mode=='request':
            x=mix(65,170,ease(p*2));self.capsule(x,400,'请求 A')
            if p>.35:
                for i,v in enumerate([42,17,83,6]):self.tile((500+i*130,285,605+i*130,340),str(v),color=TEAL)
                self.txt(760,253,'词元编号 · 示例',24,MUTED,anchor='mm')
        elif mode=='schedule':
            for i,s in enumerate(['A','B','C']):self.capsule(90+i*190,300,'请求 '+s,c=TEAL if i<2 else '#89B2BF',w=165)
            if p>.6:self.tag(715,680,'本轮批次：A + B',TEAL)
        elif mode in ['prefill','kv']:
            self.capsule(115,710,'请求 A')
            if mode=='prefill' and 0<p<.8:
                x,y=base.point([(1050,550),(1155,550),(1155,580),(1350,580)],ease(p/.8));self.tile((x-40,y-25,x+40,y+25),'KV')
            if mode=='kv':self.note('权重保留；A 的注意力中间状态进入 KV 块池')
        elif mode=='decode':
            for i in range(min(4,int(p*5))):self.tile((470+i*150,255,595+i*150,310),f'输出 {i+1}',color=TEAL)
            self.pipe([(1188,565),(1120,565)],GOLD,ease(t/(self._source_duration*.5)));self.note('读取已有状态 → 继续计算 → 留下新状态')
        elif mode=='finish':
            self.mini_hbm(hbm,occupied=max(0,3-int(p*4)),loaded=True)
            self.capsule(500+ease((t-1.0)/.65)*780,250,'A 的输出',w=190)
            self.note('输出离开，KV 块归还；模型权重继续留驻')
    def pool_rects(self,b):
        x,y,X,Y=b;gap=14;w=(X-x-gap)/2;h=(Y-y-gap*3)/4
        return [(x+(i%2)*(w+gap),y+(i//2)*(h+gap),x+(i%2)*(w+gap)+w,y+(i//2)*(h+gap)+h) for i in range(8)]
    def pool(self,b,selected=7,ghost=False):
        self.txt((b[0]+b[2])/2,b[1]-28,'显存 KV 块池',29,INK,anchor='mm')
        for i,r in enumerate(self.pool_rects(b)):
            owner={5:'A0',2:'A1',7:'A2'}.get(i)
            self.tile(r,'' if ghost and i==7 else ('块 0 · 保留' if i==0 else f'块 {i}'+(' · '+owner if owner else '')),color=GOLD if owner else '#B4D8E5',selected=i==selected)
    def capacity(self,t,p,expand=False,expand_start=3.7):
        start=expand_start if expand else 0;q=ease((t-start)/.6) if expand else 1
        if expand and t<start:self.board(p,'kv');return
        if expand and q<1:
            self.board(1,'kv');self.fade_world(q)
        b=rectmix((1215,375,1485,690),(130,330,1470,700),q)
        self.d.rounded_rectangle((b[0]+6,b[1]+12,b[2]+6,b[3]+12),18,fill='#DBEDF2')
        self.d.rounded_rectangle(b,18,fill=WHITE,outline=INK,width=3)
        self.txt((b[0]+b[2])/2,b[1]+32,'HBM · 工作内存',30,INK,anchor='mm')
        if q>.98:
            for x,X,c,s in [(160,505,PURPLE,'模型权重'),(525,790,'#699BC2','运行时开销')]:
                for off in [12,6,0]:self.d.rounded_rectangle((x+off*.2,425+off,X+off*.2,625+off),12,fill=c,outline=INK,width=2)
                self.txt((x+X)/2,515,s,33,WHITE,anchor='mm')
            for i in range(8):
                x=825+(i%4)*150;y=416+(i//4)*104;owner={5:'A0',2:'A1',7:'A2'}.get(i)
                self.tile((x,y,x+130,y+86),f'{i}',owner or '',GOLD if owner else '#B4D8E5')
            self.txt(1115,654,'KV 可分配区',27,GOLD,anchor='mm')
            self.note('按峰值占用计算可用块数；容量比例仅为示意' if not expand else '同一块显存展开，看看状态怎样占据空间')
    def fade_world(self,p):
        region=(60,235,1540,790);self.im.paste(Image.blend(self.im.crop(region),self.bg.crop(region),p),region);self.d=ImageDraw.Draw(self.im)
        if p>=1:self.labels=[]
    def mapped(self,t,p,mode,cue):
        pool_b=(1010,350,1490,705)
        if mode=='paged' and t<.9:
            self.capacity(99,1);self.fade_world(ease(t/.9));return
        self.pool(pool_b,selected=7,ghost=mode!='paged')
        self.capsule(110,290,'请求 A')
        for i,phys in enumerate([5,2,7]):
            yy=390+i*100;self.tile((110,yy,380,yy+65),f'逻辑块 {i}',color=GOLD,selected=i==2)
        self.txt(675,300,'A 的块表',29,INK,anchor='mm')
        self.d.line((490,335,490,710),fill=LINE,width=2)
        for i,phys in enumerate([5,2,7]):self.txt(675,422+i*100,f'{i} → {phys}',39,TEAL,anchor='mm')
        if mode=='paged':
            for i,v in enumerate([5,2,7]):
                if p>.18+i*.2:
                    r=self.pool_rects(pool_b)[v];yy=(r[1]+r[3])/2
                    self.arrow([(390,422+i*100),(455,422+i*100)],GOLD,ease((t-self._cue_duration*(.18+i*.2))/(self._source_duration/4)))
                    if i==2:self.arrow([(805,622),(935,622),(935,yy),(1000,yy)],GOLD,ease((t-self._cue_duration*.5)/(self._source_duration/3)))
            self.note('逻辑连续，存放分散；同一组编号始终保留')
            return
        # The A2 tile lifts from physical block 7, leaving a marked place behind.
        q=1 if mode=='index' else ease(t/.6);src=self.pool_rects(pool_b)[7];dest=(1010,425,1490,520)
        self.fade_world(q)
        if q<1:
            self.tile(rectmix(src,dest,q),'A2',color=GOLD,selected=True)
            return
        self.txt(1250,360,'索引特写 · 原地读取',24,TEAL,anchor='mm');self.txt(330,300,'逻辑位置 9',42,TEAL,anchor='mm');self.txt(330,350,'每块 4 个槽位 · 教学示例',25,MUTED,anchor='mm')
        self.tile((110,425,420,520),'块号 2 + 偏移 1',color=TEAL)
        self.txt(690,472,'A 的块表：2 → 7',31,INK,anchor='mm')
        self.arrow([(430,472),(535,472)],TEAL,ease((t-.6)/.5));self.arrow([(850,472),(995,472)],GOLD,ease((t-.6)/.5))
        self.tile(rectmix(src,dest,q),'A2 · 显存块 7',color=GOLD,selected=True)
        if t>.85:
            if mode=='index':self.txt(1250,557,'槽位 29 = 7 × 4 + 1',30,GOLD,anchor='mm')
            self.capsule(110,630,'请求 B')
            self.txt(690,657,'B 的块表：2 → 3',30,INK,anchor='mm')
            self.tile((1010,620,1490,690),'显存块 3'+(' · 槽位 13' if mode=='index' else ''),color=GOLD)
        self.note('软件管理的缓存索引；不是 CPU 物理地址' if mode=='index' else '同样的位置 9，分别找到各自的 KV 数据',CORAL if mode=='index' else MUTED)
        if mode=='index' and t>cue['duration_s']-1.2:
            # Return the highlighted block to its exact previous pool slot.
            u=ease((t-(cue['duration_s']-1.2))/.65)
            if u>0:
                self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.labels=[];self.pool(pool_b,selected=7,ghost=True)
                self.tile(rectmix(dest,src,u),'A2' if u>.6 else 'A2 · 显存块 7',color=GOLD,selected=True)
                self.txt(430,425,'A2 回到原来的块 7',39,TEAL,anchor='mm');self.txt(430,495,'位置被找到，数据没有凭空搬家',27,MUTED,anchor='mm')
                self.note('寻址特写结束，回到同一个 KV 块池')
    def clock_scene(self,t,p,mode):
        left=370;scale=82;cpu_y=590;gpu_y=415
        self.gpu((95,370,265,468),label=False);self.txt(180,505,'GPU',29,INK,anchor='mm')
        self.cpu((120,565,245,660),label=False);self.txt(182,705,'CPU',29,INK,anchor='mm')
        for yy in [gpu_y+29,cpu_y+29]:self.d.line((335,yy,1480,yy),fill=LINE,width=2)
        self.txt(370,290,'同一批任务 · 示意时间 →',28,MUTED)
        shift=ease(t/.65) if mode=='overlap' else 1 if mode=='payoff' else 0
        # Three quick reveals, each followed by a reading hold.
        reveal=min(1,t/.55)/3 if t<1.3 else (1+min(1,(t-1.3)/.55))/3 if t<2.6 else (2+min(1,(t-2.6)/.55))/3 if mode=='serial' else 1
        if mode!='serial':reveal=1
        for n in range(3):
            cpu_start=mix(n*4,n*3,shift);gpu_start=cpu_start+1
            for start,duration,yy,c,label in [(cpu_start,1,cpu_y,TEAL,f'准备 {n+1}'),(gpu_start,3,gpu_y,PURPLE,f'计算 {n+1}')]:
                end=min(start+duration,12*reveal)
                if end>start:
                    x=left+start*scale;X=left+end*scale
                    self.d.rounded_rectangle((x+3,yy+5,X+3,yy+63),9,fill='#D6EAF0')
                    self.d.rounded_rectangle((x,yy,X,yy+58),9,fill=c)
                    if end-start>.85:self.txt((x+X)/2,yy+29,label,25,WHITE,anchor='mm')
            if shift<1:
                x=left+(n*4)*scale;w=scale*(1-shift)
                if w>2:self.d.rounded_rectangle((x,gpu_y,x+w,gpu_y+58),7,outline=CORAL,width=3)
        if mode=='serial':
            self.tag(585,730,'空档：设备在等 CPU',CORAL)
        elif mode=='overlap':
            self.tag(580,730,'同一套时间块，直接重排',TEAL)
        else:
            for b in [(left+3*scale,cpu_y,left+4*scale,cpu_y+58),(left+scale,gpu_y,left+4*scale,gpu_y+58)]:
                x,y,X,Y=b;self.d.rounded_rectangle((x-6,y-6,X+6,Y+6),12,outline=GOLD,width=3)
            self.tag(585,730,'准备下一轮，同时计算当前轮',GOLD)
        self.txt(1475,330,'非性能实测',23,MUTED,anchor='ra')
    def pressure(self,p,recompute=False,full=False):
        self.txt(800,280,'空闲块已经用完' if full else '同一个块池：保留 A，抢占 B',34,INK,anchor='mm')
        freed=[]
        for i in range(8):
            x=125+i%4*350;y=355+i//4*155
            is_b=i in [1,3,6];gone=is_b and (recompute or p>.55+[1,3,6].index(i)*.13)
            if gone:freed.append(i)
            owner={2:'A1',5:'A0',7:'A2'}.get(i)
            label='保留' if i==0 else '空闲' if gone else owner if owner else 'B 的 KV' if is_b else '其他请求'
            color=GOLD if owner or is_b and not gone else '#B4D8E5'
            self.tile((x,y,x+300,y+108),f'块 {i}',label,color,selected=i==7)
        self.capsule(125,715,'请求 C 等待',w=220)
        if recompute:self.capsule(580-110*ease(p*2),715,'请求 B → 等待',w=265)
        elif not full:self.tag(560,718,'释放 B 的块',CORAL)
        self.txt(1200,744,f'可用空闲块：{len(freed)}',30,TEAL,anchor='mm')
    def scope(self,p):
        self.gpu((150,390,560,625),active=.45)
        self.txt(355,310,'开源引擎',39,TEAL,anchor='mm')
        self.txt(355,710,'计算 · 调度 · 显存块管理',28,INK,anchor='mm')
        self.dashed((850,320,1470,710),CORAL)
        self.txt(1160,370,'外围生产系统',38,INK,anchor='mm')
        for i,s in enumerate(['长期 KV 存储','跨实例负载均衡','完整分离式服务']):self.txt(1160,470+i*77,s,29,MUTED,anchor='mm')
        self.note('虚线区域来自官方文档，未随引擎完整开源',CORAL)
    def stored(self,t,p,reuse=False):
        self.ssd((100,440,430,555),label=False);self.txt(265,385,'3FS 存储集群',31,INK,anchor='mm')
        self.d.rounded_rectangle((630,435,985,590),15,fill=MINT,outline=INK,width=3)
        self.txt(808,397,'主机共享内存',30,INK,anchor='mm')
        for i in range(5):self.d.rounded_rectangle((655+i*61,465,698+i*61,535),5,fill=WHITE,outline=INK,width=2)
        self.mini_hbm((1200,390,1490,690),occupied=0)
        self.pipe([(445,510),(610,510)],GOLD);self.pipe([(1000,510),(1180,510)],GOLD)
        self.txt(526,565,'取回',25,GOLD,anchor='mm');self.txt(1090,565,'换入',25,GOLD,anchor='mm')
        if not reuse:
            # Two crisp transfers, held at the named memory level during explanation.
            duration=getattr(self,'_cue_duration',11)
            q=ease((t-duration*.55)/.65)
            x=mix(215,745,q) if t<duration*.82 else mix(745,1300,ease((t-duration*.82)/.65))
            y=512+40*ease((x-1180)/120)
            self.tile((x-55,y-30,x+55,y+30),'前缀 KV',color=GOLD)
        else:
            self.tag(540,285,'SWA：单独的主机内存路径',GOLD)
            self.tile((1260,600,1430,662),'块 KV',color=GOLD)
        self.note('生产 Decode 未开启 KV offload；写盘用于后续复用' if reuse else '历史前缀复用：存储 → 主机内存 → 设备显存',CORAL if reuse else MUTED)
    def summary(self,t,p,share=False):
        q=1 if share else ease(t/.85)
        self.cpu(rectmix((150,470,370,640),(100,405,235,505),q),label=False)
        self.gpu(rectmix((655,370,1095,620),(285,355,560,510),q),active=.45,label=False)
        self.mini_hbm(rectmix((1215,375,1485,690),(700,350,965,630),q),occupied=3,label=q>.98)
        # Route the SSD across the empty upper lane, then down into its final column.
        if q<.25:ssd=rectmix((105,290,415,390),(105,245,415,345),q/.25)
        elif q<.75:ssd=rectmix((105,245,415,345),(1150,245,1490,350),(q-.25)/.5)
        else:ssd=rectmix((1150,245,1490,350),(1150,430,1490,535),(q-.75)/.25)
        self.ssd(ssd,label=False)
        if q>.98:
            for x,a,b,c in [(330,'谁来算','CPU 调度 · GPU/NPU 计算',TEAL),(830,'放在哪里','权重、状态与工作区',GOLD),(1320,'怎样接力','存储复用、搬运与调度',INK)]:
                self.txt(x,675,a,38,c,anchor='mm');self.txt(x,728,b,25,MUTED,anchor='mm')
        self.pipe([(370,760),(1480,760)],TEAL)
        if share:self.txt(800,280,'沿着请求，看见整台机器',35,TEAL,anchor='mm')
    def erase(self,b):
        self.im.paste(self.bg.crop(b),(b[0],b[1]));self.d=ImageDraw.Draw(self.im)
        self.labels=[a for a in self.labels if not (b[0]<=a['box'][0] and b[1]<=a['box'][1] and a['box'][2]<=b[2] and a['box'][3]<=b[3])]
    def repeat_question(self,t,p):
        self.txt(800,285,'如果每轮都从头算……',36,INK,anchor='mm')
        self.gpu((1080,395,1465,620),active=min(1,p*2),label=False)
        self.txt(1270,350,'GPU / NPU',30,INK,anchor='mm')
        for row in range(2):
            yy=390+row*150
            self.txt(100,yy+35,f'第 {row+1} 轮',27,MUTED)
            for i in range(4):
                self.tile((300+i*165,yy,445+i*165,yy+74),f'前文 {i+1}',color=GOLD)
            self.arrow([(980,yy+37),(1050,yy+37)],CORAL,min(1,p*3))
        self.tag(1090,680,'同一段前文，反复计算？',CORAL)
        self.note('假设方案：先看浪费在哪里，再看缓存怎样解决')
    def fragment_question(self,t,p):
        self.capacity(99,1)
        for i in [1,3,4,6]:
            x=825+i%4*150;y=416+i//4*104
            if t>i*.2:self.d.rounded_rectangle((x-5,y-5,x+135,y+91),13,outline=TEAL,width=4)
        self.erase((70,730,1530,789))
        self.note('空闲块分散：同一请求，不必拿到连续的显存块',TEAL)
    def next_prefix(self,t,p):
        self.board(1,'roles')
        self.erase((430,700,650,790))
        self.capsule(mix(450,800,ease((t-self._cue_duration*.28)/.6)),250,'相同的长前缀',w=270)
        self.note('运行空间已经归还；长期保留与复用，需要外围系统')
    def frame(self,cue,elapsed,width=1600,static=False,animatic=False):
        # Freeze genuinely unchanged drawings between semantic events. Captions keep their own clock.
        from scene import caption_parts,caption_edges
        duration=cue['duration_s'];p=min(1,elapsed/max(.1,duration));mode=cue['visual']
        parts=caption_parts(cue['spoken_text']);edges=caption_edges(parts)
        caption=next((i for i in range(len(parts)) if p<edges[i+1]),len(parts)-1)
        stable={'idle':duration,'board':0,'serial':3.15,'overlap':.65,'weights':duration*.22+.7,'request':duration*.5,'schedule':duration*.65,'prefill':duration*.66+.7,'kv':0,'decode':max(duration*.8,cue.get('source_duration_s',duration)*2/3),'expand':duration*.74+.6,'budget':0,'fragment-question':1.3,'paged':max(duration*.86,duration*.5+cue.get('source_duration_s',duration)/3),'lookup':max(.86,duration*.25),'recompute':cue.get('source_duration_s',duration)*.5,'finish':duration*.75,'full-question':0,'repeat-question':cue.get('source_duration_s',duration)*.5,'next-prefix':duration*.28+.6,'scope':0,'store':duration*.82+.65,'reuse':0,'summary':.86,'share':0}
        motion=min(elapsed,stable.get(mode,duration))
        if mode=='pressure':motion=sum(p>x for x in [.55,.68,.81])
        if mode=='index' and elapsed<duration-1.2:motion=min(elapsed,max(.86,duration*.25))
        if static or animatic:motion='static'
        key=(cue['id'],duration,cue['title'],cue['spoken_text'],cue['chapter'],width,static,animatic,caption,motion)
        if key==getattr(self,'_last_frame_key',None):return self._last_frame
        im=self._draw_frame(cue,elapsed,width,static,animatic)
        self._last_frame_key=key;self._last_frame=im
        return im
    def _draw_frame(self,cue,elapsed,width=1600,static=False,animatic=False):
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im)
        voice_p=min(1,elapsed/max(.1,cue['duration_s']))
        t=cue['duration_s']*(.95 if static or cue['visual']=='expand' else .8) if static or animatic else elapsed;p=min(1,t/max(.1,cue['duration_s']));mode=cue['visual'];mode='roles' if mode=='board' else mode
        self._cue_duration=cue['duration_s'];self._source_duration=cue.get('source_duration_s',cue['duration_s'])
        if mode=='weights':p=.48*min(1,max(0,(t-cue['duration_s']*.22)/.7))
        if mode=='prefill':p=.81*min(1,max(0,(t-cue['duration_s']*.66)/.7))
        group=cue['chapter']
        if mode in ['idle','roles','weights','request','schedule','prefill','kv','decode','finish']:
            self.board(p,'hook' if mode=='idle' else mode,t)
            if mode=='decode' and cue.get('from_pool') and t<.85:
                q=ease(t/.85);self.fade_world(1-q)
                saved=self.im;self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.pool((1010,350,1490,705),selected=7)
                roi=self.im.crop((990,305,1510,735));b=rectmix((990,305,1510,735),(1215,425,1485,650),q)
                roi=roi.resize((max(1,round(b[2]-b[0])),max(1,round(b[3]-b[1]))),Image.Resampling.LANCZOS)
                self.im=saved;self.im.paste(roi,(round(b[0]),round(b[1])));self.d=ImageDraw.Draw(self.im)
        elif mode in ['expand','budget']:self.capacity(t,p,mode=='expand',cue['duration_s']*.74)
        elif mode in ['paged','lookup','index']:self.mapped(t,p,mode,cue)
        elif mode in ['serial','overlap','payoff']:self.clock_scene(t,p,mode)
        elif mode in ['pressure','recompute']:self.pressure(min(1,t/cue.get('source_duration_s',cue['duration_s'])) if mode=='recompute' else p,mode=='recompute')
        elif mode=='scope':self.scope(p)
        elif mode in ['store','reuse']:self.stored(t,p,mode=='reuse')
        elif mode in ['summary','share']:self.summary(t,p,mode=='share')
        elif mode=='repeat-question':self.repeat_question(t,min(1,t/cue.get('source_duration_s',cue['duration_s'])))
        elif mode=='fragment-question':self.fragment_question(t,p)
        elif mode=='full-question':self.pressure(0,full=True)
        elif mode=='next-prefix':self.next_prefix(t,p)
        # Editorial hierarchy is stable across cues: chapter title stays, local cue is a quiet subline.
        self.d.rectangle((0,0,1600,232),fill=BG)
        self.txt(85,45,'DEEPINFER / 一个请求的旅程',24,TEAL)
        self.txt(1515,45,f'0{group} / 06',25,MUTED,anchor='ra')
        titles=['','让整台机器，接力工作','把算过的，留在显存','让准备和计算重叠','空间，也要继续周转','保存结果，供后续复用','沿着请求，看见整台机器']
        self.txt(85,102,cue['chapter_title'],53,INK)
        self.txt(88,179,('教学回看：请求开始前 · ' if cue['id']=='weights' else '')+cue['title'],28,MUTED)
        if mode in ['scope','store','reuse']:self.tag(1100,170,'官方文档 · 未完整开源',CORAL)
        self.d.rectangle((0,804,1600,900),fill=BG);self.d.line((85,804,1515,804),fill=LINE,width=2)
        # Captions use the current rewritten script and actual cue audio duration.
        from scene import caption_parts,caption_edges
        parts=caption_parts(cue['spoken_text']);edges=caption_edges(parts);j=next((i for i in range(len(parts)) if voice_p<edges[i+1]),len(parts)-1)
        self.txt(800,850,parts[j],35,INK,anchor='mm')
        for i in range(6):self.d.rounded_rectangle((85+i*242,888,300+i*242,892),2,fill=TEAL if i<group else '#D8EAF0')
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        return self.im
