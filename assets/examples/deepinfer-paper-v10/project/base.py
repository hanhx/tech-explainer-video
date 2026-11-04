"""DeepInfer request journey, editable paper cutaway film; uses prepared WAVs, Pillow and FFmpeg.
Run: python scene.py --mode stills|animatic|pilot|draft|final --skill SKILL_DIR
"""
from pathlib import Path
from functools import lru_cache
import argparse, json, math, hashlib, subprocess, sys, random, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
BG='#f4efe4'; PAPER='#fffaf0'; INK='#292e39'; MUTED='#686e76'; BLUE='#126782'; GOLD='#b26220'; RED='#ae493c'; LINE='#aaa89d'
import os
FONT=os.environ.get('EXPLAINER_FONT','/System/Library/Fonts/STHeiti Medium.ttc')
def ease(p):
    p=max(0,min(1,p));return p*p*(3-2*p)
def point(path,p):
    lengths=[math.dist(a,b) for a,b in zip(path,path[1:])];left=max(0,min(.999999,p))*sum(lengths)
    for a,b,n in zip(path,path[1:],lengths):
        if left<=n:return (a[0]+(b[0]-a[0])*left/n,a[1]+(b[1]-a[1])*left/n)
        left-=n
    return path[-1]
@lru_cache(None)
def font(size):return ImageFont.truetype(FONT,size)

class Paper:
    def __init__(self):
        self.bg=Image.new('RGB',(1600,900),BG);d=ImageDraw.Draw(self.bg);rng=random.Random(3)
        for _ in range(13000):d.point((rng.randrange(1600),rng.randrange(900)),fill='#e8e2d6')
    def txt(self,x,y,s,size=30,c=INK,anchor=None):
        self.d.text((x,y),s,font=font(size),fill=c,anchor=anchor)
    def box(self,b,fill=PAPER,line=LINE,r=15):
        x,y,X,Y=b
        self.d.rounded_rectangle((x+6,y+8,X+6,Y+8),r,fill='#d9d4c8')
        self.d.rounded_rectangle(b,r,fill=fill,outline=line,width=2)
    def arrow(self,path,c=BLUE,progress=1,token=False):
        p=point(path,progress);parts=[path[0]]
        total=sum(math.dist(a,b) for a,b in zip(path,path[1:]));acc=0
        for a,b in zip(path,path[1:]):
            acc+=math.dist(a,b)
            if acc<total*progress:parts.append(b)
            else:break
        parts.append(p);self.d.line(parts,fill=c,width=5,joint='curve')
        a=parts[-2];ang=math.atan2(p[1]-a[1],p[0]-a[0]);self.d.polygon([p,(p[0]-15*math.cos(ang-.5),p[1]-15*math.sin(ang-.5)),(p[0]-15*math.cos(ang+.5),p[1]-15*math.sin(ang+.5))],fill=c)
        if token:self.d.ellipse((p[0]-9,p[1]-9,p[0]+9,p[1]+9),fill=c,outline=PAPER,width=2)
    def tag(self,x,y,s,c=BLUE):
        n=self.d.textbbox((0,0),s,font=font(25))[2];self.box((x,y,x+n+30,y+48),fill=c,line=c,r=7);self.txt(x+15,y+11,s,25,'#fff')
    def note(self,s,c=MUTED):self.txt(800,735,s,29,c,anchor='mm')

    def chip(self,x,y,w=300,h=220,label='GPU',active=0):
        for j in range(1,8):
            xx=x+w*j/8;self.d.line((xx,y-13,xx,y+h+13),fill=LINE,width=5)
        for j in range(1,5):
            yy=y+h*j/5;self.d.line((x-13,yy,x+w+13,yy),fill=LINE,width=5)
        self.box((x,y,x+w,y+h),fill='#e8e4d8',line=INK,r=14)
        self.d.rectangle((x+15,y+15,x+w-15,y+h-15),fill=PAPER,outline=LINE,width=2)
        self.txt(x+w/2,y+48,label,39,INK,anchor='mm')
        for r in range(3):
            for c in range(6):
                on=r*6+c<int(active*18)
                xx=x+28+c*(w-50)/6;yy=y+85+r*(h-110)/3
                self.d.rectangle((xx,yy,xx+(w-65)/6,yy+(h-130)/3),fill=INK if on else '#dcd8cd')
    def ticket(self,x,y,label='请求 A',color=BLUE,w=180):
        self.box((x,y,x+w,y+70),fill=color,line=color,r=8);self.txt(x+w/2,y+35,label,29,'#fff',anchor='mm')
        self.d.ellipse((x+9,y+28,x+23,y+42),fill=PAPER)
    def kvcard(self,x,y,label='A · KV',w=110,h=65,color=GOLD):
        self.box((x,y,x+w,y+h),fill=color,line=color,r=5);self.txt(x+w/2,y+h/2,label,25,'#fff',anchor='mm')
    def disk(self,x,y,w=290,h=130,label='SSD / 检查点'):
        self.box((x,y,x+w,y+h),fill='#e7e0d4',line=INK,r=12)
        for j in range(2):
            self.d.rectangle((x+27,y+25+j*44,x+91,y+58+j*44),fill='#746585',outline=INK,width=1)
            for k in range(4):self.d.line((x+35+k*15,y+19+j*44,x+35+k*15,y+24+j*44),fill=INK,width=2)
        self.txt(x+115,y+48,label,26,INK);self.txt(x+115,y+88,'模型权重',23,'#736486')
    def hbm(self,x=1140,y=295,w=330,h=405,kv=3,loaded=True):
        self.box((x,y,x+w,y+h),line=INK,r=9);self.txt(x+w/2,y+32,'HBM / 显存',31,anchor='mm')
        if loaded:
            self.d.rectangle((x+20,y+67,x+w-20,y+155),fill='#746585');self.txt(x+w/2,y+110,'模型权重',29,'#fff',anchor='mm')
        self.txt(x+22,y+178,'KV / 请求状态',24,GOLD)
        for i in range(6):
            xx=x+20+(i%2)*(w-30)/2;yy=y+214+(i//2)*50
            self.d.rounded_rectangle((xx,yy,xx+(w-50)/2,yy+38),5,fill=GOLD if i<kv else '#ece5d8',outline=LINE,width=1)
        self.txt(x+w/2,y+h-25,'工作区 / 其他开销',23,MUTED,anchor='mm')
    def board(self,p,mode='roles'):
        if mode!='schedule':self.disk(100,270)
        self.chip(170,505,270,185,'CPU',.2 if mode not in ['roles','weights'] else 0)
        self.chip(765,420,290,245,'GPU / NPU',ease(p) if mode in ['prefill','decode','finish'] else .1)
        self.hbm(kv=min(4,int(p*5)) if mode=='prefill' else (4+min(2,int(p*3))) if mode=='decode' else 6 if mode=='finish' else 4 if mode=='kv' else 0,loaded=mode!='weights' or p>=1/2.2)
        # Control and data lanes have their own heights and text labels.
        self.d.line((450,590,745,590),fill=LINE,width=3);self.txt(600,630,'执行信息',25,BLUE,anchor='mm')
        self.d.line((1065,487,1123,487),fill=LINE,width=3)
        if mode=='roles':
            self.tag(155,440,'控制与调度',BLUE);self.tag(765,330,'主要张量计算',INK)
            self.ticket(100+ease(p)*380,700,'请求 A',BLUE)
        elif mode=='weights':
            self.d.line([(397,335),(595,335),(595,275),(1300,275),(1300,355)],fill=LINE,width=3)
            path=[(440,330),(595,330),(595,250),(1090,250),(1090,410),(1180,410)]
            if p<1/2.2:
                xx,yy=point(path,ease(p*2.2));self.kvcard(xx-50,yy-30,'权重',100,60,'#746585')
            self.note('启动时装载；后续请求复用同一份模型参数')
        elif mode=='request':
            q=ease(p*1.7);self.ticket(90+q*120,400,'请求 A',BLUE)
            if p>.4:
                for i,v in enumerate([42,17,83,6]):
                    xx=540+i*125;self.box((xx,280,xx+100,350),fill='#d9e9e8',r=6);self.txt(xx+50,315,str(v),33,BLUE,anchor='mm')
                self.txt(780,380,'词元编号 · 示例',25,MUTED,anchor='mm')
        elif mode=='schedule':
            for i,l in enumerate(['A','B','C']):self.ticket(90+i*220,275,f'请求 {l}',BLUE if i<2 else '#8b8b80')
            self.arrow([(440,590),(745,590)],BLUE,ease((p-.2)*1.6),True)
            if p>.65:self.tag(760,320,'本轮批次：A + B',BLUE)
        elif mode in ['prefill','kv']:
            self.ticket(150,395,'请求 A',BLUE)
            if mode=='prefill':
                path=[(1020,520),(1100,520),(1100,548),(1250,548)];xx,yy=point(path,ease((p-.15)*1.6));self.kvcard(xx-48,yy-26,'KV',96,52)
            else:
                self.tag(690,290,'KV = 注意力中间状态',GOLD)
                self.note('权重保持不变；请求状态逐步留下')
        elif mode=='decode':
            self.arrow([(1130,510),(1070,510)],GOLD,ease(p*2),True)
            self.arrow([(1070,580),(1130,580)],GOLD,ease((p-.35)*2),True)
            for i in range(min(4,int(p*5))):
                self.ticket(520+i*160,270,f'输出 {i+1}',BLUE,145)
            self.note('复用旧状态 → 计算下一步 → 留下新状态')
        elif mode=='finish':
            self.ticket(600+ease(p)*720,240,'A 的输出',BLUE)
            if p>.4:self.hbm(kv=max(0,6-int((p-.4)*12)),loaded=True)
            self.note('请求结束，KV块归还；模型权重继续留驻')
    def idle(self,p):
        self.chip(945,310,450,345,'GPU / NPU',0)
        self.box((100,340,665,575));self.txt(382,385,'CPU：下一批尚未就绪',33,anchor='mm')
        self.ticket(135,440,'请求 A',BLUE)
        self.d.rectangle((360,470,620,493),fill='#e3ddcf');self.d.rectangle((360,470,360+210*ease(p),493),fill=BLUE)
        self.txt(1170,715,'等待工作',46,RED,anchor='mm')
        self.d.line((685,470,900,470),fill=LINE,width=4)
        self.tag(180,670,'跟着请求 A，走进 DeepInfer',BLUE)
        self.txt(800,770,'情景示意 · 非性能测试',23,MUTED,anchor='mm')
    def memory(self,p,expand=False,elapsed=0):
        if expand and elapsed<=0:
            self.board(p,'kv');return
        b0=(1140,295,1470,700);b1=(125,320,1475,690)
        q=ease(elapsed/1.2) if expand else 1
        if expand and q<1:
            self.board(1,'kv');region=(60,235,1540,790);fade=Image.blend(self.im.crop(region),self.bg.crop(region),q*.85);self.im.paste(fade,region);self.d=ImageDraw.Draw(self.im)
        b=tuple(a+(z-a)*q for a,z in zip(b0,b1));self.box(b,line=INK,r=14)
        x,y,X,Y=b;self.txt((x+X)/2,y+35,'HBM / 显存',32,anchor='mm')
        if q>.98:
            self.txt(1460,285,'容量比例示意',23,MUTED,anchor='ra')
            widths=[405,270,580];labels=[('模型权重','#746585'),('运行时开销','#687180'),('KV 缓存池',GOLD)]
            xx=150
            for (label,c),w in zip(labels,widths):
                self.d.rectangle((xx,425,xx+w-15,630),fill=c);self.txt(xx+(w-15)/2,510,label,33,'#fff',anchor='mm')
                if label=='KV 缓存池':
                    for i in range(5):self.d.rectangle((xx+28+i*100,560,xx+100+i*100,601),outline='#fff',width=2)
                xx+=w
            if not expand:
                self.d.line((825,697,1430,697),fill=GOLD,width=4)
                self.txt(1120,738,'测量峰值占用后，计算可分配块数',27,GOLD,anchor='mm')
            else:self.note('展开示意 · 各分区宽度不代表实际占比')
    def blocks(self,p):
        self.ticket(100,270,'请求 A',BLUE)
        self.txt(350,300,'逻辑上连续',32,anchor='lm')
        for i in range(3):
            x=100+i*210;self.kvcard(x,405,f'逻辑块 {i}',180,95)
        self.box((800,270,1090,650));self.txt(945,310,'A 的块表',33,anchor='mm')
        for i,v in enumerate([5,2,7]):self.txt(945,405+i*90,f'{i} → {v}',37,BLUE,anchor='mm')
        self.txt(1320,265,'显存块池',32,anchor='mm')
        for i in range(8):
            y=310+i*48;on=i in [7,2,5];self.d.rounded_rectangle((1210,y,1440,y+38),6,fill=GOLD if on else '#e5dfd0',outline=LINE,width=1);self.txt(1325,y+19,f'块 {i}',25,'#fff' if on else MUTED,anchor='mm')
        for i,v in enumerate([5,2,7]):
            self.arrow([(1097,405+i*90),(1150+i*16,405+i*90),(1150+i*16,329+v*48),(1200,329+v*48)],GOLD,ease((p-i*.18)*2))
        self.note('逻辑连续，存放可以分散；块表负责连接')
    def lookup(self,p,index=False):
        self.txt(800,280,'逻辑位置 9',53,BLUE,anchor='mm')
        self.txt(800,345,'教学假设：每块 4 个槽位',27,MUTED,anchor='mm')
        self.box((570,400,1030,485),fill='#dfebe8');self.txt(800,442,'块号 2  +  偏移 1',36,BLUE,anchor='mm')
        rows=[(515,'A',7,29),(625,'B',3,13)]
        for y,label,phys,slot in rows:
            self.ticket(140,y,f'请求 {label}',BLUE)
            self.txt(600,y+35,f'块表：2 → {phys}',35,anchor='mm')
            if p>.3 or index:self.arrow([(760,y+35),(930,y+35)],GOLD,ease((p-.2)*2) if not index else 1)
            if p>.55 or index:self.kvcard(970,y,f'显存块 {phys}',240,70)
            if index:self.txt(1360,y+35,f'槽位 {slot}',36,GOLD,anchor='mm')
        self.note('软件管理的缓存索引；不是 CPU 物理地址' if index else '同一个逻辑位置，通过各自的块表找到不同落点',RED if index else MUTED)
    def timelines(self,p,mode):
        self.txt(100,265,'示意时间 →',26,MUTED)
        left=350;scale=83
        # Serial keeps CPU scheduling and device work separated.
        self.txt(90,340,'逐轮等待',31,RED);self.txt(290,375,'CPU',25,anchor='rm');self.txt(290,450,'GPU',25,anchor='rm')
        for y in [375,450]:self.d.line((320,y,1470,y),fill=LINE,width=2)
        for n in range(3):
            for start,dur,y,c,label in [(n*4,1,347,BLUE,f'准备 {n+1}'),(n*4+1,3,422,INK,f'计算 {n+1}')]:
                q=ease(p*2) if mode=='serial' else 1;end=min(start+dur,12*q)
                if end>start:
                    x=left+start*scale;X=left+end*scale;self.d.rounded_rectangle((x,y,X,y+55),7,fill=c)
                    if end-start>.8:self.txt((x+X)/2,y+27,label,25,'#fff',anchor='mm')
            if mode!='serial' or p>.4:self.d.rectangle((left+n*4*scale,422,left+(n*4+1)*scale,477),outline=RED,width=3)
        if mode in ['overlap','payoff']:
            self.txt(90,560,'异步接力',31,BLUE);self.txt(290,595,'CPU',25,anchor='rm');self.txt(290,670,'GPU',25,anchor='rm')
            for y in [595,670]:self.d.line((320,y,1470,y),fill=LINE,width=2)
            q=ease(p*1.5) if mode=='overlap' else 1
            for n in range(3):
                for start,dur,y,c,label in [(n*3,1,567,BLUE,f'准备 {n+1}'),(n*3+1,3,642,INK,f'计算 {n+1}')]:
                    end=min(start+dur,12*q)
                    if end>start:
                        x=left+start*scale;X=left+end*scale;self.d.rounded_rectangle((x,y,X,y+55),7,fill=c)
                        if end-start>.85:self.txt((x+X)/2,y+27,label,25,'#fff',anchor='mm')
            if mode=='payoff':
                x=left+3.5*scale
                for a,b in [(540,562),(624,638),(701,713)]:self.d.line((x,a,x,b),fill=GOLD,width=4)
                self.tag(1060,505,'同一时刻，双方在工作',GOLD)
        self.note('示意排程 · 不代表实际耗时或加速倍数')
    def pressure(self,p,recompute=False):
        self.txt(800,275,'显存 KV 块池',38,anchor='mm')
        for i in range(8):
            x=200+(i%4)*300;y=340+(i//4)*125;is_b=i in [1,4,7];freed=is_b and (recompute or p>.6+(i//3)*.1)
            self.box((x,y,x+245,y+88),fill='#e5dfd1' if freed else GOLD,r=8);self.txt(x+122,y+44,'空闲' if freed else ('B 的 KV' if is_b else 'A 的 KV'),30,MUTED if freed else '#fff',anchor='mm')
        self.ticket(130,660,'请求 C 等待',BLUE,230)
        if recompute:
            q=ease(p*2);self.ticket(750-250*q,660,'请求 B → 等待',BLUE,260)
            self.txt(1150,690,'允许时重算 / 按配置结束',26,RED,anchor='mm')
        else:
            self.ticket(630,660,'抢占请求 B',RED,240)
            self.txt(1200,700,'释放 B 占用的块',28,RED,anchor='mm')
    def scope(self,p):
        self.box((130,315,760,690),line=INK);self.txt(445,370,'开源引擎',44,anchor='mm')
        for j,s in enumerate(['计算与采样','调度与显存块管理','保存/传输扩展接口']):self.txt(445,465+j*64,s,31,BLUE,anchor='mm')
        self.dashed((890,315,1470,690),RED);self.txt(1180,370,'外围生产系统',42,anchor='mm')
        for j,s in enumerate(['长期 KV 存储','跨实例负载均衡','完整分离式服务部署']):self.txt(1180,465+j*64,s,31,MUTED,anchor='mm')
        self.note('右侧系统在官方文档中描述，未随引擎完整开源',RED)
    def dashed(self,b,c=LINE):
        x,y,X,Y=b
        for xx in range(int(x),int(X),26):
            self.d.line((xx,y,min(xx+14,X),y),fill=c,width=3);self.d.line((xx,Y,min(xx+14,X),Y),fill=c,width=3)
        for yy in range(int(y),int(Y),26):
            self.d.line((x,yy,x,min(yy+14,Y)),fill=c,width=3);self.d.line((X,yy,X,min(yy+14,Y)),fill=c,width=3)
    def store(self,p,reuse=False):
        nodes=[(85,420,'3FS 存储集群'),(610,420,'主机共享内存'),(1135,420,'设备 HBM')]
        for x,y,s in nodes:
            self.dashed((x,y,x+380,y+215),GOLD if x==85 else LINE);self.txt(x+190,y+45,s,33,anchor='mm')
        paths=[[(475,530),(595,530)],[(1000,530),(1120,530)]]
        for path in paths:self.arrow(path,GOLD,1)
        self.txt(535,380,'异步取回',25,GOLD,anchor='mm');self.txt(1060,380,'换入',25,GOLD,anchor='mm')
        if not reuse:
            q=ease(p);x=190+q*1100;self.kvcard(x,535,'前缀 KV',130,65)
            self.note('历史前缀复用：先取回共享内存，再进入设备显存')
        else:
            self.kvcard(1250,535,'块 KV',130,65)
            self.box((525,260,1070,330),fill='#eadbc8',r=7);self.txt(800,295,'SWA 窗口缓存：单独的主机内存路径',26,GOLD,anchor='mm')
            self.note('文档说明：生产 Decode 未开启 KV offload',RED)
    def summary(self,p,share=False):
        items=[('谁来算','CPU 调度 / GPU、NPU 计算',BLUE),('放在哪里','HBM：权重 + KV + 工作区',GOLD),('怎样接力','减少重复计算、搬运与空等',INK)]
        for i,(a,b,c) in enumerate(items):
            x=110+i*500;self.box((x,340,x+420,620),line=c);self.txt(x+210,420,a,47,c,anchor='mm');self.txt(x+210,525,b,26,MUTED,anchor='mm')
        self.d.line((150,710,1450,710),fill=LINE,width=3)
        xx=150+1300*ease(p) if not share else 1450;self.ticket(xx-85,675,'请求 A',BLUE,170)
        if share:self.txt(800,760,'把计算机组成，连接到真实推理框架',29,BLUE,anchor='mm')

    def frame(self,cue,elapsed,width=1600,static=False):
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);p=min(1,elapsed/max(.1,cue['duration_s']));p=.95 if static else p
        mode=cue['visual'];mode='roles' if mode=='board' else mode;self.txt(80,42,'DeepInfer / REQUEST A',25,BLUE)
        self.txt(1520,42,'官方文档描述 · 未完整开源' if mode in ['scope','store','reuse'] else '从计算机组成，看一次推理',24,RED if mode in ['scope','store','reuse'] else MUTED,anchor='ra')
        if mode in ['roles','weights','request','schedule','prefill','kv','decode']:
            self.txt(1520,245,'单设备视角 · 权重可跨设备分布',22,MUTED,anchor='ra')
        self.d.line((80,82,1520,82),fill=LINE,width=2);self.txt(80,112,cue['title'],51)
        chapter=1 if mode in ['idle','roles','weights','request','schedule'] else 2 if mode in ['prefill','kv','expand','budget','paged','lookup','index'] else 3 if mode in ['decode','serial','overlap','payoff'] else 4 if mode in ['pressure','recompute'] else 5 if mode in ['scope','store','reuse'] else 6
        self.txt(80,188,['','01 / 请求进入机器','02 / 状态留在显存','03 / 计算与调度接力','04 / 空间也要周转','05 / 生产存储的边界','06 / 回看整个旅程'][chapter],26,MUTED)
        if mode=='idle':self.idle(p)
        elif mode in ['roles','weights','request','schedule','prefill','kv','decode','finish']:self.board(p,mode)
        elif mode in ['expand','budget']:
            start=caption_edges(caption_parts(cue['spoken_text']))[2]*cue['duration_s'] if mode=='expand' else 0
            self.memory(p,mode=='expand',(elapsed-start) if not static else 99)
        elif mode=='paged':self.blocks(p)
        elif mode in ['lookup','index']:self.lookup(p,mode=='index')
        elif mode in ['serial','overlap','payoff']:self.timelines(p,mode)
        elif mode in ['pressure','recompute']:self.pressure(p,mode=='recompute')
        elif mode=='scope':self.scope(p)
        elif mode in ['store','reuse']:self.store(p,mode=='reuse')
        elif mode in ['summary','share']:self.summary(p,mode=='share')
        # Keep HUD and subtitles fixed while objects unfold or travel.
        self.d.rectangle((60,795,1540,899),fill=BG);self.d.line((80,795,1520,795),fill=LINE,width=2)
        parts=caption_parts(cue['spoken_text']);edges=caption_edges(parts);idx=next((i for i in range(len(parts)) if p<edges[i+1]),len(parts)-1)
        self.txt(800,838,parts[idx],35,INK,anchor='mm')
        for i in range(6):self.d.rectangle((80+i*242,883,300+i*242,887),fill=BLUE if i<chapter else '#dcd5c7')
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        return self.im

