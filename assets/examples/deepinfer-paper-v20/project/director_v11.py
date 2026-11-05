"""Causal V11 recut. Reuse the approved paper kit, stage new mechanisms explicitly."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageColor
from director_v10 import Paper as PaperKit,icon,ramp
from typography import font
from continuity import BG,WHITE,INK,MUTED,GOLD,CORAL,LINE,ease,mix
TEAL='#087F6E';MINT='#DDF3EB';BLUE='#337DB4';AMBER='#99630B'
CHAPTERS=['先分两笔账','已有通用引擎','怎样安排验证','少重算哪一段','谁能自己部署','开源的价值']
STARTS={'baseline-hook','shared-engine','draft-start','replay-question','private-stack','open-value'}

def event(c,phrase,fallback):
    return c.get('speech_events',{}).get(phrase,c['duration_s']*fallback)

class Paper(PaperKit):
    def nav_offset(self,c,t):
        ch=c['chapter'];target=max(0,min(3,ch-2))*480;previous=max(0,min(3,ch-3))*480
        return mix(previous,target,ramp(t,0,.75)) if c['id'] in STARTS else target
    def header(self,c,t,thanks=False):
        self.d.rectangle((0,0,1600,230),fill=BG);offset=self.nav_offset(c,t)
        strip=Image.new('RGB',(1600,90),BG);d=ImageDraw.Draw(strip)
        for i,label in enumerate(CHAPTERS):
            x=320+i*480-offset;active=c['chapter']==i+1;s=f'0{i+1} {label}';f=font(34)
            d.text((x,43),s,font=f,fill=TEAL if active else MUTED,anchor='mm');b=d.textbbox((x,43),s,font=f,anchor='mm');left=max(80,b[0]);right=min(1520,b[2])
            if right>left:self.geometry.append(dict(id=f'nav-{i}',box=[left,b[1],right-left,b[3]-b[1]],text=s,font_size=34,role='navigation',clipped=left!=b[0] or right!=b[2]))
            if active:d.line((x-155,77,x+155,77),fill=GOLD,width=4)
        self.im.paste(strip.crop((80,0,1520,90)),(80,0));self.d=ImageDraw.Draw(self.im)
        if offset>0:self.d.line((57,35,49,43,57,51),fill=MUTED,width=2)
        if offset<1440:self.d.line((1543,35,1551,43,1543,51),fill=MUTED,width=2)
        title='感谢观看' if thanks else c['title'];size=58
        while self.d.textbbox((0,0),title,font=font(size,'bold'))[2]>1280:size-=1
        self.txt(80,127,title,size,INK,anchor='lm');self.txt(1520,127,f"{c['shot_number']:02}/{c['shot_total']:02}",42,MUTED,anchor='rm')
        subs={
          'baseline-hook':'看清共同基础、具体实现与开源价值','two-bills':'DeepInfer主要讨论推理执行','three-levers':'有效效率提升 ≠ 芯片峰值算力增加',
          'shared-engine':'回看请求A的执行过程 · 通用基础','overlap':'CPU/GPU重叠：共同基础，不是独有发明','prefill':'计算先发生，状态到达后再保留','kv':'请求相关状态；不是重新训练模型','source-map':'功能存在 ≠ 独占创新 ≠ 整体性能领先',
          'draft-start':'候选、验收与输出均为教学示意','fixed-budget':'回到验证前 · 比较两种安排','confidence':'概率与硬件吞吐共同影响验证长度','verification-proof':'切换到官方估算值 · 不沿用前镜教学数值',
          'replay-question':'回看请求A的输入阶段 · 模型结构示意','replay-exact':'精确恢复有跨层依赖；层数与范围示意','replay-bounded':'保留共享缓存，近似恢复近期窗口','replay-shared':'需要质量验证；vLLM也已实现',
          'private-stack':'模型能力来自公开权重','weights':'回看启动阶段 · 权重、引擎与硬件要适配','compatibility':'有权重，不等于当前引擎直接支持','production-boundary':'官方生产架构不等于全部已开源',
          'open-value':'公开实现，让细节可检查、可复现、可复用','cost-proof':'同条件测量，才能判断实际收益','training-boundary':'生成回答可能接入后训练；不是预训练框架','conclusion':'公开能力，也公开一部分执行实现','closing':'是否采用，交给实际场景验证'}
        sub='如果这段动画让你有所收获' if thanks else subs[c['id']]
        self.txt(82,193,sub,42,MUTED,anchor='lm');self.d.line((80,230,1520,230),fill=LINE,width=2)
    def footer(self,c,t):
        from scene import caption_parts,caption_ranges
        parts=caption_parts(c['spoken_text']);ranges=caption_ranges(c);j=next((i for i,(a,b) in enumerate(ranges) if t<b),len(parts)-1)
        self.d.rectangle((0,790,1600,900),fill=BG);self.d.line((80,790,1520,790),fill=LINE,width=2);self.txt(800,846,parts[j],50,INK,anchor='mm')
    def engine_card(self,b,name,sub,color=TEAL):
        x,y,X,Y=b;self.panel(b,f'engine-{len(self.geometry)}');self.d.rounded_rectangle((x+18,y+18,X-18,y+100),14,fill=MINT if color==TEAL else '#E4EFF9')
        self.txt((x+X)/2,y+59,name,52,color,anchor='mm');self.gear(x+(X-x)*.28,y+(Y-y)*.57,43,color,0);self.txt(x+(X-x)*.7,y+(Y-y)*.57,'{ }',64,color,anchor='mm');self.txt((x+X)/2,Y-45,sub,44,INK,anchor='mm')
    def arrow_line(self,a,b,color=TEAL):self.arrow([a,b],color)
    def two_engines(self,c,t,opening=False):
        if opening:
            self.panel((80,280,760,780),'assistant');self.txt(420,320,'企业助手（示意）',50,INK,anchor='mm')
            self.d.rounded_rectangle((220,355,630,420),13,fill='#E4EFF9');self.txt(425,388,'vLLM',52,BLUE,anchor='mm')
            self.gpu((180,450,650,690),active=.8,label=False);self.pill(110,700,'请求 A',250)
            self.pill(400,700,'已经能回答',310)
            x=mix(1630,950,ramp(t,.2,.9));self.engine_card((x,350,x+540,665),'DeepInfer','官方公开部分实现')
            if t>=1.1:self.txt(1220,735,'还带来什么？',54,TEAL,anchor='mm')
            return
        self.engine_card((110,330,650,645),'vLLM','现成的通用引擎',BLUE)
        x=950
        self.engine_card((x,330,x+540,645),'DeepInfer','一份官方实现')
        if opening:
            self.pill(160,690,'已经能运行',440,c=BLUE)
            if t>=1.1:self.pill(990,690,'还带来什么？',440)
        else:
            self.txt(800,480,'对照',48,TEAL,anchor='mm');self.arrow_line((680,540),(920,540),LINE)
            self.note('检查细节  ·  复现结果  ·  修改复用')
    def bills(self,c,t):
        self.panel((90,335,665,650),'train');self.panel((935,335,1510,650),'infer')
        self.txt(380,385,'训练',54,BLUE,anchor='mm');self.txt(380,455,'从数据学出参数',44,INK,anchor='mm')
        self.txt(1220,385,'推理',54,TEAL,anchor='mm');self.txt(1220,455,'使用参数生成回答',44,INK,anchor='mm')
        q=ramp(t,event(c,'推理',.36),.9)
        if q>0:self.arrow_line((685,565),(915,565),BLUE)
        x=mix(380,1220,q);self.card((x-112,515,x+112,625),'权重',color=BLUE)
        if t>=event(c,'DeepInfer主要',.72):self.pill(1000,690,'本片沿这条路径',450)
    def levers(self,c,t):
        for i,(title,detail,col) in enumerate([('硬件更强','峰值与带宽',BLUE),('模型少算','计算工作量',AMBER),('系统少等','执行与协作',TEAL)]):
            x=100+i*505;self.card((x,340,x+390,600),title,detail,col,selected=i==2)
        self.txt(800,700,'DeepInfer：组织已有硬件，执行模型',50,TEAL,anchor='mm')
    def shared(self,c,t):
        self.pill(90,300,'企业助手 · 请求 A',480)
        for i,(s,col) in enumerate([('调度',TEAL),('计算',BLUE),('缓存',GOLD)]):
            x=100+i*510;self.card((x,425,x+380,620),s,color=col)
            if i<2:self.arrow_line((x+400,520),(x+485,520),col)
        self.note('vLLM已提供基础；DeepInfer基于既有积累开发')
    def source_map(self,c,t):
        for i,(s,detail,col) in enumerate([('模型','结构与状态',BLUE),('算子','计算与通信',AMBER),('运行时','调度与执行',TEAL)]):
            x=100+i*505;self.card((x,335,x+390,625),s,detail,col)
        self.pill(390,690,'看具体机制，也看适用条件',820)
    def candidates(self,c,t,mode):
        d=c['duration_s'];q=ramp(t,event(c,'决定每条请求',.32),1.1) if mode=='confidence' else 0
        if mode=='verification-proof':q=1
        start=420;pitch=188;w=150
        self.txt(800,287,'同一批候选词元',48,INK,anchor='mm')
        for row,name in enumerate(['请求 A','请求 B']):
            y=365+row*182;self.pill(100,y+3,name,255,c=TEAL if row==0 else BLUE)
            for i in range(5):
                x=start+i*pitch
                chosen=i<(3 if row==0 else 2)
                col=GOLD
                if mode in ['confidence','verification-proof']:col=BLUE if chosen else '#DCE8ED'
                if mode=='confidence' and q<1:col=tuple(round(mix(a,b,q)) for a,b in zip(ImageColor.getrgb(GOLD),ImageColor.getrgb(BLUE if chosen else '#DCE8ED')))
                if mode=='draft-start':
                    gen=ramp(t,event(c,'候选词元',.27),.8)
                    if gen<(i+1)/5:col='#E2EDF1'
                    if t>=event(c,'验证通过',.65) and i<(2 if row==0 else 1):col=TEAL
                token=[['我','们','先','看','看'],['接','着','往','下','看']][row][i]
                if mode=='draft-start' and gen<(i+1)/5:token='·'
                key=f'candidate-{len(self.geometry)}';self.panel((x,y,x+w,y+88),key,fill=col);prev=self._parent;self._parent=key
                light=col in [TEAL,BLUE] if isinstance(col,str) else (mode=='confidence' and chosen and q>.6)
                self.txt(x+w/2,y+44,token,50,WHITE if light else INK,anchor='mm');self._parent=prev
                if mode in ['fixed-budget','confidence','verification-proof']:
                    prob=[[.95,.86,.74,.35,.12],[.9,.71,.28,.12,.05]][row][i]
                    self.txt(x+w/2,y+122,f'{round(prob*100)}%',42,AMBER if prob<.5 else TEAL,anchor='mm')
        if mode=='draft-start':
            when=event(c,'验证通过',.65)
            if t>=event(c,'主模型验证',.4):
                self.card((650,460,1120,540),'主模型验证',color=BLUE)
            if t>=when:
                for row,n in [(0,2),(1,1)]:
                    for i in range(n):self.d.rounded_rectangle((start+i*pitch+5,365+row*182+69,start+i*pitch+w-5,365+row*182+82),5,fill=TEAL)
                self.pill(400,702,'输出：我们… / 接…',800)
            else:self.note('先提出候选，再由主模型验证')
        elif mode=='fixed-budget':self.note('固定方案：每条请求统一验证5个候选')
        elif mode=='confidence':self.note('蓝色选中连续前缀；灰色本轮不验证')
        else:self.note('只解释策略取舍；这里没有框架排名或实测跑分')
    def replay(self,c,t):
        mode=c['id'];d=c['duration_s'];bounded=mode in ['replay-bounded','replay-shared']
        self.d.rounded_rectangle((330,270,1490,350),14,fill=BLUE);self.txt(910,310,'全局共享缓存 · 保留',46,WHITE,anchor='mm')
        self.pill(90,270,'请求 A',205)
        phase=ramp(t,event(c,'只重放',.25),1.25) if mode=='replay-bounded' else 1 if bounded else 0
        exact_start=event(c,'精确恢复',.43);exact=t>=exact_start if mode=='replay-exact' else False
        for row in range(3):
            y=405+row*102;self.txt(100,y+33,'后段层 '+str(row+1),44,INK,anchor='lm')
            for j in range(10):
                x=355+j*112;active=(j>=8) if bounded else ((j>=8-row*2) and t>=exact_start+row*.5) if exact else True
                fill=TEAL if bounded and active else GOLD if active else '#E2EDF1'
                if bounded and phase<1 and j<8:fill=GOLD if phase<(j+1)/10 else '#E2EDF1'
                self.d.rounded_rectangle((x,y,x+93,y+62),8,fill=fill,outline=LINE,width=2)
            if row and exact and t>=exact_start+row*.5:self.arrow_line((390+(8-(row-1)*2)*112,y-40),(390+(8-row*2)*112,y-4),AMBER)
        if mode=='replay-question':self.note('长提示词在左，近期窗口在右；范围示意')
        elif mode=='replay-exact':self.note('精确恢复的依赖范围，会跨层向前延伸')
        elif phase<1:self.note('共享缓存保留，只收缩后段层参与计算的片段')
        else:self.note('近期片段 → 近似窗口状态；保留长度取决于配置',TEAL)
    def verification_proof(self,c,t):
        self.pill(100,275,'EP64/DP64 · 每rank 60条序列',1120,c=BLUE)
        q=ramp(t,event(c,'动态长度',.3),1.0)
        for y,name,value,col in [(410,'固定5候选',13730,BLUE),(535,'动态长度',14466,TEAL)]:
            self.txt(100,y+40,name,48,INK,anchor='lm');length=700*value/14466*q
            if length>1:self.d.rounded_rectangle((430,y,430+length,y+80),12,fill=col)
            if q>=.99:self.txt(430+700*value/14466+25,y+40,f'{value:,}',52,col,anchor='lm')
        self.txt(100,675,'估算吞吐：词元/秒/rank',42,MUTED,anchor='lm')
        if q>=.99:self.txt(1380,675,'约 +5.4%',54,TEAL,anchor='rm')
        self.note('局部策略对比，不是DeepInfer与vLLM整体对测')
    def private(self,c,t):
        self.card((100,370,500,650),'公开权重','模型能力',BLUE)
        self.d.rounded_rectangle((625,290,1050,365),14,fill=MINT);self.txt(837,327,'适配的推理引擎',44,TEAL,anchor='mm')
        q=ramp(t,event(c,'加上适配',.35),.9)
        self.gpu((600,445,1060,685),active=.8 if q>=1 else 0,label=False);self.txt(830,402,'GPU / NPU',46,INK,anchor='mm')
        self.arrow_line((515,520),(580,520),BLUE)
        if 0<q<1:
            x=mix(520,580,q);self.d.rounded_rectangle((x-20,500,x+20,540),6,fill=BLUE)
        self.panel((1160,365,1510,665),'app');self.txt(1335,310,'企业助手',48,INK,anchor='mm');self.txt(1335,435,'请求 A',46,TEAL,anchor='mm')
        self.arrow_line((1085,550),(1135,550),TEAL)
        if t>=event(c,'搭建自己的服务',.68):self.txt(1335,565,'生成回答',46,TEAL,anchor='mm')
        self.note('权重 + 适配的引擎与硬件 → 自己的服务')
    def compatibility(self,c,t):
        self.card((100,350,550,670),'模型权重','需要适配',BLUE)
        for i,(s,col) in enumerate([('模型结构',TEAL),('缓存布局',AMBER),('计算算子',BLUE)]):
            y=335+i*125;self.card((800,y,1490,y+95),s,color=col);self.arrow_line((585,510),(760,y+47),LINE)
        self.note('当前公开支持：V4.1-Flash · SM100 / 昇腾950')
    def open_value(self,c,t):
        self.panel((100,310,685,705),'source');self.txt(392,365,'DeepInfer 源码',54,TEAL,anchor='mm')
        for i,s in enumerate(['调度实现','缓存管理','执行流程']):
            y=420+i*85;self.d.rounded_rectangle((155,y,625,y+60),10,fill='#E7F1F4');self.txt(390,y+30,s,44,INK,anchor='mm')
        self.card((755,430,975,595),'适配','验证',TEAL)
        self.gpu((1050,440,1500,700),active=.75,label=False);self.txt(1275,345,'自己的部署',50,INK,anchor='mm')
        self.arrow_line((705,510),(735,510),LINE);self.arrow_line((995,510),(1030,510),LINE)
        start=event(c,'修改和复用',.68);q=ramp(t,start,.65);v=ramp(t,start+1.1,.65)
        if 0<q<1:
            x=mix(640,735,q);self.d.rounded_rectangle((x-20,515,x+20,555),7,fill=BLUE)
        if q>=1:
            self.d.ellipse((935,440,962,467),fill=TEAL);self.d.line((941,452,947,459,957,447),fill=WHITE,width=3)
        if 0<v<1:
            x=mix(995,1030,v);self.d.rounded_rectangle((x-18,492,x+18,528),6,fill=TEAL)
        self.note('复用部分实现，仍需适配与验证；过程示意')
    def boundary(self,c,t):
        self.box((80,285,740,740),fill=WHITE,line=TEAL,r=20);self.dashed((850,285,1520,740),CORAL)
        self.txt(410,320,'引擎核心',50,TEAL,anchor='mm');self.engine_card((150,375,665,660),'DeepInfer','本次公开范围')
        self.txt(1185,320,'外围生产组件',50,INK,anchor='mm')
        for i,s in enumerate(['长期KV系统','分离部署','负载均衡']):self.card((920,385+i*105,1450,470+i*105),s,color=CORAL)
    def proof(self,c,t):
        for i,s in enumerate(['同一模型','同一硬件','同类请求']):self.card((110+i*500,285,510+i*500,395),s,color=TEAL)
        self.gpu((120,450,620,700),active=.75,label=False)
        self.txt(820,475,'峰值算力',46,INK,anchor='lm');self.d.rounded_rectangle((1110,450,1470,502),8,fill=BLUE)
        self.txt(820,620,'有效工作',46,INK,anchor='lm')
        q=ramp(t,event(c,'更多有效工作',.55),1.1)
        for i in range(5 if q>.6 else 3):self.d.rounded_rectangle((1110+i*73,590,1170+i*73,652),8,fill=TEAL)
        self.note('图形只解释效率概念，不是性能测量')
    def training(self,c,t):
        self.panel((80,310,710,700),'training');self.txt(395,370,'训练系统',54,BLUE,anchor='mm');self.txt(395,480,'反向传播',48,INK,anchor='mm');self.txt(395,585,'更新参数',48,INK,anchor='mm')
        self.engine_card((940,340,1500,680),'推理生成','生成回答')
        for x in range(745,920,24):self.d.line((x,510,x+12,510),fill=LINE,width=4)
        self.d.polygon([(720,510),(740,500),(740,520)],fill=LINE);self.txt(825,620,'需接入',42,MUTED,anchor='mm');self.note('后训练的生成环节可能受益；不是现成训练集成')
    def conclusion(self,c,t):
        self.card((110,350,620,660),'模型权重','能力来自这里',BLUE)
        self.engine_card((970,350,1490,660),'DeepInfer','公开部分执行实现')
        self.arrow_line((665,510),(925,510),TEAL);self.note('已有通用引擎，也能对照官方实现')
    def closing(self,c,t):
        a=event(c,'欢迎',.72);b=event(c,'谢谢大家',.94)
        if t<a+.4:
            self.conclusion(c,t)
            if t>=a:
                roi=(60,235,1540,780);self.im.paste(Image.blend(self.im.crop(roi),self.bg.crop(roi),ramp(t,a,.4)),roi);self.d=ImageDraw.Draw(self.im)
        else:
            for i,(name,label,fill) in enumerate([('like','点赞','#E3F3EB'),('save','收藏','#FFF2D5'),('follow','关注','#E6F0FB')]):
                if t<a+.4+i*.14:continue
                x=400+i*400;self.d.ellipse((x-128,325,x+128,581),fill='#D6E7EB');self.d.ellipse((x-126,315,x+126,567),fill=fill);im=icon(name).resize((220,220),Image.Resampling.LANCZOS);self.im.paste(im,(x-110,325),im);self.d=ImageDraw.Draw(self.im);self.txt(x,635,label,54,INK,anchor='mm')
            if t>=b:self.txt(800,735,'谢谢大家',64,TEAL,anchor='mm')
        return t>=a
    def frame(self,c,elapsed,width=1600,static=False,animatic=False):
        from scene import caption_parts,caption_ranges
        t=c['duration_s']*.98 if static or animatic else elapsed
        ranges=caption_ranges(c);cap=next((i for i,(a,b) in enumerate(ranges) if elapsed<b),len(ranges)-1)
        key=(c['id'],self.motion_signature(c,t),round(self.nav_offset(c,t),6),width,cap,static,animatic)
        if key==getattr(self,'_mobile_key',None):return self._mobile_frame
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.geometry=[];self._parent=None;id=c['id'];thanks=False
        if id=='baseline-hook':self.two_engines(c,t,True)
        elif id=='two-bills':self.bills(c,t)
        elif id=='three-levers':self.levers(c,t)
        elif id=='shared-engine':self.shared(c,t)
        elif id=='overlap':self.clock(c,t)
        elif id in ['prefill','kv']:self.cache_board(c,t)
        elif id=='source-map':self.source_map(c,t)
        elif id in ['draft-start','fixed-budget','confidence']:self.candidates(c,t,id)
        elif id=='verification-proof':self.verification_proof(c,t)
        elif id.startswith('replay-'):self.replay(c,t)
        elif id=='private-stack':self.private(c,t)
        elif id=='weights':self.weights(c,t)
        elif id=='compatibility':self.compatibility(c,t)
        elif id=='production-boundary':self.boundary(c,t)
        elif id=='open-value':self.open_value(c,t)
        elif id=='cost-proof':self.proof(c,t)
        elif id=='training-boundary':self.training(c,t)
        elif id=='conclusion':self.conclusion(c,t)
        elif id=='closing':thanks=self.closing(c,t)
        self.header(c,t,thanks);self.footer(c,elapsed)
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        self._mobile_key=key;self._mobile_frame=self.im;return self.im
    def motion_signature(self,c,t):
        id=c['id'];d=c['duration_s'];clip=lambda a,n:round(max(0,min(n,t-a)),6)
        if id=='baseline-hook':return (clip(.2,.9),t>=1.1)
        if id=='two-bills':return (clip(event(c,'推理',.36),.9),t>=event(c,'DeepInfer主要',.72))
        if id=='overlap':return (clip(0,.9),)
        if id=='prefill':return (clip(0,.6),clip(d*.66,.9))
        if id=='draft-start':return (clip(event(c,'候选词元',.27),.8),t>=event(c,'主模型验证',.4),t>=event(c,'验证通过',.65))
        if id=='confidence':return (clip(event(c,'决定每条请求',.32),1.1),)
        if id=='verification-proof':return (clip(event(c,'动态长度',.3),1.0),)
        if id=='replay-exact':return tuple(t>=event(c,'精确恢复',.43)+i*.5 for i in range(3))
        if id=='replay-bounded':return (clip(event(c,'只重放',.25),1.25),)
        if id=='weights':return (clip(d*.22,.9),)
        if id=='private-stack':return (clip(event(c,'加上适配',.35),.9),t>=event(c,'搭建自己的服务',.68))
        if id=='open-value':
            a=event(c,'修改和复用',.68);return (clip(a,.65),t>=a+.65,clip(a+1.1,.65))
        if id=='cost-proof':return (ramp(t,event(c,'更多有效工作',.55),1.1)>.6,)
        if id=='closing':
            a=event(c,'欢迎',.72);return (t>=a,clip(a,.4),tuple(t>=a+.4+i*.14 for i in range(3)),t>=event(c,'谢谢大家',.94))
        return (0,)
