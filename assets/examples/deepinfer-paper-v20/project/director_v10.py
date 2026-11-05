"""Landscape director revision: full six-chapter navigation, modern type and focused mechanisms.

Original bright paper hardware is retained; dense tables and small labels are restaged.
"""
from pathlib import Path
import math
from functools import lru_cache
from PIL import Image,ImageDraw
from industry import Paper as IllustrationKit
from director_base import HEADERS
from continuity import BG,WHITE,INK,MUTED,GOLD,CORAL,LINE,PURPLE,TEAL as OLD_TEAL,ease,mix,rectmix
from typography import font

ROOT=Path(__file__).resolve().parent
TEAL='#087F6E';MINT='#DDF3EB';BLUE='#337DB4';AMBER='#99630B'
CHAPTERS=['开源与接力','留下计算状态','缓存分块存','显存再周转','让前缀复用','看懂算力账']
CHAPTER_STARTS={'industry-opening','repeat-question','capacity-question','full-question','next-prefix','closing'}
SUBS={
 'repeat-question':'假设方案：每轮从头算','weights':'回看请求开始前','cached-decode':'回到生成现场',
 'lookup':'每块4个槽位 · 教学示例','mapping-boundary':'软件缓存索引 ≠ CPU物理地址',
 'scope':'官方文档架构 · 未完整开源','store':'官方文档架构 · 未完整开源','reuse':'SWA另有主机路径 · 文档架构未完整开源',
 'closing':'具体收益取决于模型、硬件与负载','next-prefix':'A的运行KV已归还，长期复用另有系统'}

def ramp(t,start,length=.9):return ease((t-start)/length)
def clipped(t,start,length=.9):return min(length,max(0,t-start))
@lru_cache(None)
def icon(name):return Image.open(ROOT/'assets/native-icons'/f'{name}.png').convert('RGBA')

class Paper(IllustrationKit):
    def __init__(self):
        super().__init__();self.geometry=[];self._parent=None
    def txt(self,x,y,s,size=48,c=INK,anchor=None):
        size=max(42,round(size));c=TEAL if c==OLD_TEAL else AMBER if c==GOLD else c
        weight='bold' if size>=54 else 'medium';f=font(size,weight)
        self.d.text((round(x),round(y)),str(s),font=f,fill=c,anchor=anchor)
        b=self.d.textbbox((round(x),round(y)),str(s),font=f,anchor=anchor)
        item={'id':f'text-{len(self.geometry)}','box':[b[0],b[1],b[2]-b[0],b[3]-b[1]],'text':str(s),'font_size':size}
        if self._parent:item['parent']=self._parent
        self.geometry.append(item)
    def panel(self,b,key,padding=14,fill=WHITE,line=LINE):
        self.box(b,fill=fill,line=line,r=20);self.geometry.append({'id':key,'box':[b[0],b[1],b[2]-b[0],b[3]-b[1]],'padding':padding})
    def card(self,b,title,detail='',color=TEAL,selected=False):
        key=f'card-{len(self.geometry)}';self.panel(b,key,line=TEAL if selected else LINE);previous=self._parent;self._parent=key
        x,y,X,Y=b;self.d.rounded_rectangle((x+2,y+2,X-2,y+14),8,fill=color)
        self.txt((x+X)/2,(y+Y)/2-(27 if detail else 0),title,48,INK,anchor='mm')
        if detail:self.txt((x+X)/2,(y+Y)/2+35,detail,44,color,anchor='mm')
        self._parent=previous
    def tag(self,x,y,s,c=TEAL):
        w=self.d.textbbox((0,0),s,font=font(44))[2]+36;self.d.rounded_rectangle((x,y,x+w,y+66),16,fill=c)
        self.txt(x+18,y+33,s,44,INK if c==GOLD else WHITE,anchor='lm')
    def pill(self,x,y,s,w=300,c=TEAL):
        self.d.rounded_rectangle((x+4,y+7,x+w+4,y+81),38,fill='#D2E8E9')
        self.d.rounded_rectangle((x,y,x+w,y+74),37,fill=c)
        self.txt(x+w/2,y+37,s,46,WHITE,anchor='mm')
    def note(self,s,c=MUTED):self.txt(800,747,s,42,c,anchor='mm')
    def line_arrow(self,a,b,color=TEAL,progress=1):
        self.arrow([a,b],color,progress)
    def nav_offset(self,c,t):
        chapter=c['chapter'];target=max(0,min(3,chapter-2))*480
        previous=max(0,min(3,chapter-3))*480
        return mix(previous,target,ramp(t,0,.75)) if c['id'] in CHAPTER_STARTS else target
    def header(self,c,t,thanks=False):
        self.d.rectangle((0,0,1600,230),fill=BG)
        offset=self.nav_offset(c,t)
        strip=Image.new('RGB',(1600,90),BG);nav=ImageDraw.Draw(strip)
        for i,label in enumerate(CHAPTERS):
            x=320+i*480-offset;active=c['chapter']==i+1;text=f'0{i+1} {label}'
            f=font(34,'medium');nav.text((x,43),text,font=f,fill=TEAL if active else MUTED,anchor='mm')
            bb=nav.textbbox((x,43),text,font=f,anchor='mm');left=max(80,bb[0]);right=min(1520,bb[2])
            if right>left:self.geometry.append({'id':f'nav-{i}','box':[left,bb[1],right-left,bb[3]-bb[1]],'text':text,'font_size':34,'role':'chapter navigation','clipped':left!=bb[0] or right!=bb[2]})
            if active:nav.line((x-155,77,x+155,77),fill=GOLD,width=4)
        self.im.paste(strip.crop((80,0,1520,90)),(80,0));self.d=ImageDraw.Draw(self.im)
        if offset>0:self.d.line((57,35,49,43,57,51),fill=MUTED,width=2)
        if offset<1440:self.d.line((1543,35,1551,43,1543,51),fill=MUTED,width=2)
        title='感谢观看' if thanks else HEADERS.get(c['id'],('同一批显卡，怎样降低回答成本？',''))[0]
        if c['id']=='lookup':title='同样的位置9，怎样找到不同数据？'
        size=58
        while self.d.textbbox((0,0),title,font=font(size,'bold'))[2]>1280:size-=1
        self.txt(80,127,title,size,INK,anchor='lm')
        self.txt(1520,127,f'{c.get("shot_number",1):02}/{c.get("shot_total",27):02}',42,MUTED,anchor='rm')
        sub='如果这段动画让你有所收获' if thanks else SUBS.get(c['id'],['CPU准备，设备计算','留下状态，减少重算','逻辑连续，物理分散','容量有限，空间要周转','长期复用需要外围系统','让机器高效协作'][c['chapter']-1])
        self.txt(82,193,sub,42,CORAL if c['id'] in ['scope','store','reuse'] else MUTED,anchor='lm')
        self.d.line((80,230,1520,230),fill=LINE,width=2)
    def footer(self,c,t):
        from scene import caption_parts,caption_edges
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts);p=min(1,t/c['duration_s']);j=next((j for j in range(len(parts)) if p<edges[j+1]),len(parts)-1)
        self.d.rectangle((0,790,1600,900),fill=BG);self.d.line((80,790,1520,790),fill=LINE,width=2)
        self.txt(800,846,parts[j],50,INK,anchor='mm')
    def engine(self,b,angle=0):
        x,y,X,Y=b;w=X-x;h=Y-y;self.paper(b)
        self.d.rounded_rectangle((x+18,y+17,X-18,y+h*.32),12,fill=MINT)
        self.txt((x+X)/2,y+h*.18,'DeepInfer',w*.105,TEAL,anchor='mm')
        self.gear(x+w*.27,y+h*.56,min(w*.14,h*.18),TEAL,angle)
        self.txt(x+w*.70,y+h*.56,'{ }',w*.14,BLUE,anchor='mm')
        self.txt((x+X)/2,Y-33,'推理引擎',42,INK,anchor='mm')
    def memory(self,b,occupied=3,loaded=True,fresh=False,labels=None):
        x,y,X,Y=b;self.box(b,fill=WHITE,line=INK,r=20);self.txt((x+X)/2,y-36,'显存 HBM',46,INK,anchor='mm')
        if loaded:
            self.d.rounded_rectangle((x+20,y+28,X-20,y+112),12,fill=BLUE);self.txt((x+X)/2,y+70,'权重',46,WHITE,anchor='mm')
        self.txt((x+X)/2,y+156,'KV缓存',46,AMBER,anchor='mm')
        n=3;cw=(X-x-56)/n
        for i in range(n):
            xx=x+20+i*(cw+8);self.d.rounded_rectangle((xx,y+202,xx+cw,y+290),10,fill=GOLD if i<occupied else '#E7F1F4',outline=LINE,width=2)
            if i<occupied:self.txt(xx+cw/2,y+246,labels[i] if labels else str(i+1),48,INK,anchor='mm')
            if fresh and i==occupied-1:self.d.rounded_rectangle((xx+4,y+273,xx+cw-4,y+286),5,fill=AMBER)
    def hardware_wait(self,c,t):
        for i,s in enumerate(['A','B','C']):self.pill(mix(-320,100,ramp(t,.15,.85)) if i==2 else 100,315+i*125,'请求 '+s,320)
        self.txt(260,274,'等待结果',48,TEAL,anchor='mm');self.waiting_gpu((920,350,1480,670),t)
        self.txt(1200,292,'显卡',50,INK,anchor='mm');self.card((500,425,820,535),'等工作',color=CORAL)
        self.line_arrow((450,480),(880,480),LINE)
    def hardware_roles(self,c,t):
        d=c['duration_s'];start=d*.45;q=ramp(t,start,.9)
        self.cpu((150,390,430,635),True,False);self.txt(290,692,'准备与调度',46,TEAL,anchor='mm')
        gpu=rectmix((920,350,1480,670),(700,355,1220,655),ramp(t,0,.85))
        if q<1:self.waiting_gpu(gpu,t)
        else:self.gpu(gpu,active=ramp(t,start+.9,.4),label=False)
        self.txt((gpu[0]+gpu[2])/2,gpu[1]-52,'GPU / NPU',48,INK,anchor='mm');self.line_arrow((465,510),(665,510),TEAL)
        if t>=start:
            x=mix(480,630,q);self.d.rounded_rectangle((x-55,462,x+55,552),13,fill=MINT,outline=TEAL,width=3)
        if q>=1:self.tag(1260,480,'计算',TEAL)
        self.note('CPU把准备好的工作，交给设备执行')
    def clock(self,c,t):
        shift=ramp(t,0,.9) if c['id']=='overlap' else 0;reveal=min(1,t/3.2) if c['id']=='serial' else 1
        self.txt(95,410,'GPU计算',50,INK,anchor='lm');self.txt(95,605,'CPU准备',50,INK,anchor='lm')
        for yy in [370,565]:self.d.line((390,yy+47,1490,yy+47),fill=LINE,width=3)
        unit=90
        for n in range(3):
            start=mix(n*4,n*3,shift)
            for a,length,y,color,label in [(start,1,565,TEAL,str(n+1)),(start+1,3,370,BLUE,'第'+str(n+1)+'轮')]:
                end=min(a+length,12*reveal)
                if end>a:
                    x=400+a*unit;X=400+end*unit;self.d.rounded_rectangle((x,y,X,y+94),12,fill=color)
                    if end-a>.8:self.txt((x+X)/2,y+47,label,46,WHITE,anchor='mm')
            gap=unit*(1-shift)
            if gap>3:self.d.rounded_rectangle((400+n*4*unit,370,400+n*4*unit+gap,464),10,outline=CORAL,width=4)
        self.txt(1470,275,'时间比例仅为示意',42,MUTED,anchor='rm')
        self.note('准备下一轮，同时计算当前轮' if shift>.9 else '这些空档，设备在等CPU',TEAL if shift>.9 else CORAL)
    def repeat(self,c,t):
        d=c['duration_s'];p=t/max(.1,c.get('source_duration_s',d))
        self.tag(90,254,'假设：每轮都重算',CORAL)
        from scene import caption_parts,caption_edges
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts);rewind=edges[next(i for i,s in enumerate(parts) if '回到请求开始前' in s)]
        if t>=d*rewind:self.tag(1020,254,'回到请求起点',TEAL)
        for row in range(2):
            y=390+row*175;self.txt(90,y+40,'上一轮' if row==0 else '这一轮',48,INK,anchor='lm')
            for i in range(4):self.card((290+i*195,y,460+i*195,y+104),'前文',color=GOLD)
            self.line_arrow((1085,y+50),(1170,y+50),CORAL,min(1,p*3))
        self.gpu((1190,400,1510,650),active=min(1,p*2),label=False)
    def weights(self,c,t):
        d=c['duration_s'];q=ramp(t,d*.22,.9)
        self.ssd((100,390,420,550),False);self.txt(260,320,'模型检查点',48,INK,anchor='mm')
        self.gpu((610,370,1060,650),label=False);self.txt(835,310,'GPU / NPU',46,INK,anchor='mm')
        self.memory((1190,350,1510,680),0,q>=1)
        self.arrow([(450,465),(520,465),(520,270),(1135,270),(1135,420),(1170,420)],BLUE)
        if q<1:
            from base import point
            x,y=point([(440,465),(520,465),(520,270),(1135,270),(1135,420),(1260,420)],q);self.d.rounded_rectangle((x-40,y-30,x+40,y+30),12,fill=BLUE)
        self.note('启动时装入，后续请求反复使用')
    def cache_board(self,c,t):
        d=c['duration_s'];mode=c['id'];p=min(1,t/d)
        self.gpu((130,355,650,655),active=min(1,t/.6) if mode=='prefill' else min(1,t/(c.get('source_duration_s',d)*2/3)) if mode=='cached-decode' else 0,label=False)
        self.txt(390,300,'GPU / NPU',48,INK,anchor='mm')
        q=ramp(t,d*.66,.9);occupied=(3 if q>=1 else 0) if mode=='prefill' else 3
        fresh=(mode=='cached-decode' and t>=d*.45+.85) or c.get('post_decode',False)
        self.memory((980,350,1480,685),occupied,fresh=fresh)
        if mode!='cached-decode':self.pill(130,698,'请求 A',280)
        if mode=='prefill':
            self.line_arrow((690,520),(940,520),GOLD)
            self.txt(810,438,'留下状态',46,AMBER,anchor='mm')
            if 0<q<1:self.d.rounded_rectangle((mix(700,930,q)-35,485,mix(700,930,q)+35,555),10,fill=GOLD)
        elif mode=='cached-decode':
            self.line_arrow((940,445),(690,445),GOLD);self.txt(810,385,'读缓存',46,AMBER,anchor='mm')
            self.line_arrow((690,625),(940,625),GOLD);self.txt(810,690,'新状态',46,AMBER,anchor='mm')
            self.pill(130,698,'A · 输出 '+str(min(4,int(p*4)+1)),420)
            add=ramp(t,d*.45,.85)
            if 0<add<1:
                xx=mix(700,930,add);self.d.rounded_rectangle((xx-28,597,xx+28,653),10,fill=GOLD)
        else:self.note('请求相关的状态，留给后面继续生成')
    def capacity(self,c,t):
        d=c['duration_s'];q=ramp(t,d*.74,.9) if c['id']=='capacity-question' else 1
        if q<1:
            self.cache_board(dict(c,id='kv',post_decode=True),t)
            if q==0:return
            self.im.paste(self.bg.crop((970,285,1500,700)),(970,285));self.d=ImageDraw.Draw(self.im)
            region=(70,250,1530,775);self.im.paste(Image.blend(self.im.crop(region),self.bg.crop(region),q),region);self.d=ImageDraw.Draw(self.im)
        b=rectmix((980,350,1480,685),(100,310,1500,710),q)
        if q<1:
            self.memory(b,3,fresh=True);return
        self.box(b,WHITE,INK,r=22)
        self.card((135,370,540,655),'模型权重',color=BLUE)
        self.card((570,370,900,655),'运行开销',color='#6D9CBE')
        for i in range(8):
            x=950+i%4*130;y=380+i//4*135;occupied=i in [2,5,7]
            self.d.rounded_rectangle((x,y,x+114,y+110),10,fill=GOLD if occupied else '#EDF5F7',outline=TEAL if c['id']=='fragment-question' and i in [1,3,4,6] else LINE,width=4 if c['id']=='fragment-question' and i in [1,3,4,6] else 2)
            if i==0:self.txt(x+57,y+55,'保留',42,INK,anchor='mm')
            elif occupied:self.txt(x+57,y+55,'KV',44,INK,anchor='mm')
        self.txt(1200,688,'KV可分配区',44,AMBER,anchor='mm')
        self.note('空位可以零散分布' if c['id']=='fragment-question' else '按峰值占用，计算还能分配多少块')
    def pool(self,selected=7,states=None,box=(980,325,1500,725)):
        x,y,X,Y=box;w=(X-x-16)/2;h=(Y-y-42)/4
        for i in range(8):
            xx=x+i%2*(w+16);yy=y+i//2*(h+14);owner={5:'A0',2:'A1',7:'A2'}.get(i)
            label='0 · 保留' if i==0 else f'{i} · {owner}' if owner else f'块 {i}'
            self.card((xx,yy,xx+w,yy+h),label,color=GOLD if owner else '#98BFD3',selected=i==selected)
    def mapped(self,c,t):
        d=c['duration_s'];mode=c['id'];old=c.get('source_duration_s',d)
        if mode=='paged':
            self.pool();self.txt(1240,275,'显存块',48,INK,anchor='mm')
            for i,phys in enumerate([5,2,7]):
                y=355+i*130;self.card((80,y,385,y+94),'逻辑块 '+str(i),color=GOLD,selected=i==2)
                self.txt(685,y+47,f'{i} → {phys}',54,TEAL,anchor='mm')
                self.line_arrow((410,y+47),(490,y+47),GOLD,ramp(t,d*(.18+i*.2),old/4))
            self.txt(685,283,'A的块表',48,INK,anchor='mm');self.line_arrow((845,662),(950,662),GOLD,ramp(t,d*.5,old/3))
            return
        if mode=='mapping-boundary' and t>d-1.2:
            self.pool();self.txt(440,435,'A2仍在块7',58,TEAL,anchor='mm');self.txt(440,520,'找到位置，原地读取',44,MUTED,anchor='mm');return
        if mode=='lookup' and t<.55:
            self.pool();self.txt(440,435,'找到A2 · 准备特写',54,TEAL,anchor='mm');self.txt(440,520,'数据仍在原来的块7',44,MUTED,anchor='mm');return
        self.card((80,340,520,555),'逻辑位置 9','块号2 + 偏移1',TEAL)
        self.card((610,340,1010,555),'A的块表','2 → 7',TEAL)
        self.card((1110,340,1510,555),'显存块 7','槽位29' if mode=='mapping-boundary' else 'A 的KV',GOLD)
        self.line_arrow((540,446),(590,446),TEAL,ramp(t,.5,.7));self.line_arrow((1030,446),(1090,446),GOLD,ramp(t,.5,.7))
        if t>.9:
            self.card((80,625,520,735),'请求 B',color=TEAL);self.card((610,625,1010,735),'2 → 3',color=TEAL);self.card((1110,625,1510,735),'块3 · 槽13' if mode=='mapping-boundary' else '显存块 3',color=GOLD)
        if mode=='mapping-boundary':self.txt(800,590,'29 = 7 × 4 + 1',48,AMBER,anchor='mm')
    def pressure(self,c,t):
        d=c['duration_s'];p=t/d;mode=c['id'];free={1,3,6} if mode in ['recompute','release-finished'] else set()
        if mode=='pressure':free={v for v,a in zip([1,3,6],[.55,.68,.81]) if p>a}
        if mode=='release-finished':free|={v for v,a in zip([2,5,7],[.3,.5,.7]) if p>a}
        for i in range(8):
            x=80+i%4*365;y=315+i//4*177;owner={2:'A1',5:'A0',7:'A2'}.get(i)
            label='保留' if i==0 else '空闲' if i in free else owner or ('B的KV' if i in [1,3,6] else '其他')
            self.card((x,y,x+330,y+145),'块 '+str(i),label,GOLD if owner or i in [1,3,6] and i not in free else '#9EC2D5')
        self.pill(80,705,'请求 C 等待',370)
        if mode=='recompute':self.pill(500,705,'B 回到等待队列',500,c=BLUE)
        elif mode=='release-finished':self.pill(500,705,'A 完成，权重留驻',560,c=BLUE)
        self.txt(1480,741,'空闲 '+str(len(free))+' 块',46,TEAL,anchor='rm')
    def next_prefix(self,c,t):
        self.gpu((130,390,650,690),label=False);self.txt(390,350,'GPU / NPU',48,INK,anchor='mm');self.memory((1010,385,1480,700),1,labels=['其他'])
        x=mix(430,720,ramp(t,c['duration_s']*.28,.9));self.pill(x,245,'相同的长前缀',600)
        # The header and narration explain the remaining boundary; keep this view uncluttered.
    def scope(self):
        self.engine((100,355,650,655));self.txt(375,715,'开源引擎',48,TEAL,anchor='mm')
        self.dashed((840,305,1510,735),CORAL);self.txt(1175,355,'外围生产系统',52,INK,anchor='mm')
        self.txt(1175,465,'长期KV存储',48,INK,anchor='mm');self.txt(1175,560,'服务编排与负载均衡',44,INK,anchor='mm');self.tag(980,646,'未完整开源',CORAL)
    def stored(self,c,t):
        d=c['duration_s'];reuse=c['id']=='reuse'
        self.ssd((100,390,460,590),False);self.txt(280,308,'3FS存储',48,INK,anchor='mm')
        self.box((600,360,1000,650),fill=MINT,line=TEAL,r=22);self.txt(800,308,'主机共享内存',48,INK,anchor='mm')
        for i in range(4):self.d.rounded_rectangle((630+i*87,420,695+i*87,555),12,fill=WHITE,outline=TEAL,width=3)
        self.memory((1120,360,1520,685),0)
        self.line_arrow((485,500),(575,500),GOLD);self.line_arrow((1025,500),(1095,500),GOLD)
        if reuse:
            self.card((1205,575,1440,675),'KV',color=GOLD);self.note('生产Decode未开启缓存卸载',CORAL)
        else:
            from base import point
            q=ramp(t,d*.55,.85)
            x,y=(mix(280,800,q),510) if t<d*.82 else point([(800,510),(1040,510),(1040,606),(1320,606)],ramp(t,d*.82,.85))
            self.card((x-108,y-49,x+108,y+49),'前缀KV',color=GOLD);self.note('先取回主机内存，再换入设备显存')
    def industry_scene(self,c,t):
        d=c['duration_s'];p=t/d
        if c['id']=='industry-opening':self.source_box(t);return
        if c['id']=='cost-question':
            self.engine(rectmix((590,250,1010,490),(80,365,490,645),ramp(t,0,.75)))
            if p>.08:self.cloud((1190,360,1510,480),'OpenAI')
            if p>.2:self.cloud((1190,565,1510,685),'Anthropic')
            if p>.52:self.receipt((630,290,1080,745))
            return
        self.panel((90,290,1040,735),'promise')
        self.txt(565,375,'减少空等',60,TEAL,anchor='mm');self.txt(565,450,'让下一批工作及时接上',46,INK,anchor='mm')
        self.txt(565,570,'减少重算',60,AMBER,anchor='mm');self.txt(565,645,'把算过的状态留给下一轮',46,INK,anchor='mm')
        self.small_waiting_gpu((1130,420,1500,650),t);self.txt(1315,340,'同一批显卡',48,TEAL,anchor='mm')
        if p>.82:
            q=ramp(t,d*.82,.9);self.im=Image.blend(self.im,self.bg,q);self.d=ImageDraw.Draw(self.im);self.small_waiting_gpu(rectmix((1130,420,1500,650),(920,350,1480,670),q),t)
    def closing(self,c,t):
        from scene import caption_parts,caption_edges
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts);d=c['duration_s'];invite=edges[next(i for i,s in enumerate(parts) if s.startswith('欢迎'))]*d;thanks=edges[-2]*d
        if t<invite+.4:
            self.stored(dict(c,id='reuse'),0)
            self.im.paste(self.bg.crop((60,705,1540,780)),(60,705));self.d=ImageDraw.Draw(self.im)
            if t>invite:
                roi=(60,235,1540,780);self.im.paste(Image.blend(self.im.crop(roi),self.bg.crop(roi),ramp(t,invite,.4)),roi);self.d=ImageDraw.Draw(self.im)
        else:
            for i,(name,label,fill) in enumerate([('like','点赞','#E3F3EB'),('save','收藏','#FFF2D5'),('follow','关注','#E6F0FB')]):
                if t<invite+.4+i*.14:continue
                cx=400+i*400;self.d.ellipse((cx-128,325,cx+128,581),fill='#D6E7EB');self.d.ellipse((cx-126,315,cx+126,567),fill=fill)
                img=icon(name).resize((220,220),Image.Resampling.LANCZOS);self.im.paste(img,(cx-110,325),img);self.d=ImageDraw.Draw(self.im)
                self.txt(cx,635,label,54,INK,anchor='mm')
            if t>=thanks:self.txt(800,735,'谢谢大家',64,TEAL,anchor='mm')
        return t>=invite
    def signature(self,c,t):
        d=c['duration_s'];p=min(1,t/d);id=c['id'];old=c.get('source_duration_s',d)
        if id=='industry-opening':return (min(t,1.5),)
        if id=='cost-question':return (min(t,.75),p>.08,p>.2,p>.52)
        if id=='saving-promise':return (clipped(t,d*.82),)
        if id=='opening':return (min(t,1.2),)
        if id=='roles':return (min(t,1.2),clipped(t,d*.45,1.3))
        if id=='serial':return (min(t,3.2),)
        if id=='overlap':return (min(t,.9),)
        if id=='weights':return (clipped(t,d*.22),)
        if id=='prefill':return (min(t,.6),clipped(t,d*.66))
        if id=='cached-decode':return (min(t,old*2/3),int(p*4),clipped(t,d*.45,.85))
        if id=='capacity-question':return (clipped(t,d*.74),)
        if id=='paged':return tuple(clipped(t,d*(.18+i*.2),old/4) for i in range(3))+(clipped(t,d*.5,old/3),)
        if id in ['lookup','mapping-boundary']:return (t>=.55,clipped(t,.5,.7),t>.9,t>d-1.2 if id=='mapping-boundary' else False)
        if id=='pressure':return tuple(p>x for x in [.55,.68,.81])
        if id=='release-finished':return tuple(p>x for x in [.3,.5,.7])
        if id=='next-prefix':return (clipped(t,d*.28),)
        if id=='store':return (clipped(t,d*.55,.85),clipped(t,d*.82,.85))
        if id=='repeat-question':return (min(t,old*.5),p>.606557377)
        if id=='closing':
            from scene import caption_parts,caption_edges
            parts=caption_parts(c['spoken_text']);ed=caption_edges(parts);a=ed[next(i for i,s in enumerate(parts) if s.startswith('欢迎'))]*d;b=ed[-2]*d
            return (t>=a,clipped(t,a,.9),tuple(t>=a+.4+i*.14 for i in range(3)),t>=b)
        return (0,)
    def frame(self,c,elapsed,width=1600,static=False,animatic=False):
        from scene import caption_parts,caption_edges
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts);p=min(1,elapsed/c['duration_s']);caption=next((j for j in range(len(parts)) if p<edges[j+1]),len(parts)-1)
        t=c['duration_s']*.99 if static or animatic else elapsed
        key=(c['id'],c['duration_s'],width,caption,self.signature(c,t),self.nav_offset(c,t),static,animatic)
        if key==getattr(self,'_mobile_key',None):return self._mobile_frame
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.geometry=[];self._parent=None;id=c['id'];thanks=False
        if id in ['industry-opening','cost-question','saving-promise']:self.industry_scene(c,t)
        elif id=='opening':self.hardware_wait(c,t)
        elif id=='roles':self.hardware_roles(c,t)
        elif id in ['serial','overlap']:self.clock(c,t)
        elif id=='repeat-question':self.repeat(c,t)
        elif id=='weights':self.weights(c,t)
        elif id in ['prefill','kv','cached-decode']:self.cache_board(c,t)
        elif id in ['capacity-question','budget','fragment-question']:self.capacity(c,t)
        elif id in ['paged','lookup','mapping-boundary']:self.mapped(c,t)
        elif id in ['full-question','pressure','recompute','release-finished']:self.pressure(c,t)
        elif id=='next-prefix':self.next_prefix(c,t)
        elif id=='scope':self.scope()
        elif id in ['store','reuse']:self.stored(c,t)
        elif id=='closing':thanks=self.closing(c,t)
        self.header(c,t,thanks);self.footer(c,elapsed)
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        self._mobile_key=key;self._mobile_frame=self.im;return self.im
