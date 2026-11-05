"""Original paper props and object-led camera moves for the industry opening."""
import math
from PIL import Image,ImageDraw
from opening import Paper as MachineFilm
from continuity import BG,WHITE,INK,MUTED,TEAL,MINT,GOLD,CORAL,LINE,PURPLE,ease,mix,rectmix

class Paper(MachineFilm):
    def caption_footer(self,c,t):
        from scene import caption_parts,caption_edges
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts);p=min(1,t/max(.1,c['duration_s']))
        i=next((j for j in range(len(parts)) if p<edges[j+1]),len(parts)-1)
        self.d.rectangle((0,804,1600,900),fill=BG)
        self.txt(800,852,parts[i],38,INK,anchor='mm')
    def headline(self,s,sub=''):
        self.d.rectangle((0,0,1600,220),fill=BG)
        self.txt(800,110,s,64,INK,anchor='mm')
        if sub:self.txt(800,185,sub,29,MUTED,anchor='mm')
    def gear(self,x,y,r,c=TEAL,angle=0):
        pts=[]
        for j in range(48):
            a=angle+math.tau*j/48;rr=r if j%4 in [0,1] else r*.78;pts.append((x+rr*math.cos(a),y+rr*math.sin(a)))
        self.d.polygon(pts,fill=c);self.d.line(pts+[pts[0]],fill=INK,width=3)
        self.d.ellipse((x-r*.34,y-r*.34,x+r*.34,y+r*.34),fill=WHITE,outline=INK,width=3)
    def paper(self,b,fill=WHITE,corner=True):
        x,y,X,Y=b;fold=min(30,(X-x)*.08)
        self.d.rounded_rectangle((x+8,y+10,X+8,Y+10),13,fill='#D2E7ED')
        self.d.rounded_rectangle(b,13,fill=fill,outline=INK,width=3)
        if corner:
            self.d.polygon([(X-fold,y),(X,y+fold),(X-fold,y+fold)],fill='#DFEFF4',outline=INK,width=2)
    def engine(self,b,angle=0):
        x,y,X,Y=b;w=X-x;h=Y-y;self.paper(b)
        self.d.rounded_rectangle((x+18,y+17,X-18,y+h*.32),10,fill=MINT)
        self.txt((x+X)/2,y+h*.19,'DeepInfer',w*.115,TEAL,anchor='mm')
        self.gear(x+w*.27,y+h*.61,min(w*.15,h*.25),TEAL,angle)
        self.txt(x+w*.70,y+h*.61,'{ }',w*.14,PURPLE,anchor='mm')
        self.txt((x+X)/2,Y-h*.10,'推理引擎',w*.073,INK,anchor='mm')
    def source_box(self,t):
        q=ease((t-.12)/.55);x,X=490,1110
        self.d.ellipse((470,715,1145,775),fill='#DAEDF0')
        self.d.polygon([(x,475),(800,420),(X,475),(X,735),(x,735)],fill='#A8D9C9',outline=INK,width=4)
        # Sheets come from the same source box after the main reveal.
        fan=ease((t-.65)/.45)
        if fan>0:
            for k,bb in enumerate([(mix(560,340,fan),mix(480,345,fan),mix(690,505,fan),mix(665,555,fan)),(mix(910,1100,fan),mix(480,320,fan),mix(1040,1265,fan),mix(665,530,fan))]):
                self.paper(bb);self.txt((bb[0]+bb[2])/2,bb[1]+70,'{ }',44,TEAL,anchor='mm')
                for j in range(3):self.d.line((bb[0]+22,bb[1]+115+j*19,bb[2]-22,bb[1]+115+j*19),fill=LINE,width=3)
        card=rectmix((590,490,1010,730),(590,250,1010,490),ease((t-.28)/.65));self.engine(card,angle=min(t,1.1)*.4)
        self.d.polygon([(x,500),(800,550),(X,500),(X,735),(x,735)],fill=MINT,outline=INK,width=4)
        self.d.line((800,550,800,735),fill=TEAL,width=3)
        # Two folded paper flaps open outwards.
        self.d.polygon([(x,500),(800,550),(mix(800,620,q),mix(450,385,q)),(mix(x,365,q),mix(450,430,q))],fill='#E8F7F0',outline=INK,width=3)
        self.d.polygon([(800,550),(X,500),(mix(X,1235,q),mix(450,430,q)),(mix(800,980,q),mix(450,385,q))],fill='#C2E9DC',outline=INK,width=3)
        self.txt(650,632,'DeepSeek',57,TEAL,anchor='mm')
        self.d.rounded_rectangle((875,595,1035,673),12,fill=WHITE,outline=TEAL,width=3)
        self.txt(955,634,'开源',39,TEAL,anchor='mm')
    def cloud(self,b,label):
        x,y,X,Y=b;h=Y-y
        self.d.rounded_rectangle((x,y+h*.28,X,Y),h*.28,fill='#E3F0FC',outline=INK,width=3)
        self.d.ellipse((x+25,y,x+h*.8,y+h*.75),fill='#E3F0FC',outline=INK,width=3)
        self.d.ellipse((x+h*.55,y-h*.13,x+h*1.25,y+h*.6),fill='#E3F0FC',outline=INK,width=3)
        self.d.rounded_rectangle((x+18,y+h*.35,X-18,Y-8),h*.13,fill='#E3F0FC')
        self.txt((x+X)/2,y+h*.65,label,36 if len(label)>7 else 42,INK,anchor='mm')
    def receipt(self,b,question=True):
        x,y,X,Y=b;w=X-x;h=Y-y;self.paper(b,corner=False)
        pts=[(x,Y)]
        for j in range(15):pts.append((x+j*w/14,Y+(8 if j%2 else 0)))
        self.d.line(pts,fill=INK,width=2)
        self.txt((x+X)/2,y+h*.12,'算力账单',min(w*.115,h*.105),INK,anchor='mm')
        self.d.line((x+25,y+h*.22,X-25,y+h*.22),fill=LINE,width=2)
        for i,s in enumerate(['计算','通信','缓存']):
            yy=y+h*(.35+i*.145);self.d.ellipse((x+28,yy-7,x+42,yy+7),fill=[TEAL,PURPLE,GOLD][i])
            self.txt(x+60,yy,s,min(w*.075,h*.070),INK,anchor='lm');self.d.line((x+w*.57,yy,X-30,yy),fill=LINE,width=3)
        if question:self.txt((x+X)/2,Y-h*.13,'能否更省？',min(w*.086,h*.080),CORAL,anchor='mm')
    def opening_industry(self,c,t):
        self.source_box(t)
        self.headline('DeepSeek 开源，谁的成本账可能变？','这次公开的是推理引擎 DeepInfer')
    def cost_question(self,c,t):
        p=min(1,t/c['duration_s']);q=ease(t/.5)
        self.engine(rectmix((590,250,1010,490),(90,355,510,615),q))
        if p>.07:self.cloud((1120,370,1480,490),'OpenAI')
        if p>.18:self.cloud((1120,590,1480,710),'Anthropic')
        if p>.07:self.txt(1300,300,'美国 AI 服务商',29,MUTED,anchor='mm')
        # Feed one receipt into view, rather than introducing a static comparison table.
        feed=ease((t-c['duration_s']*.52)/.6)
        if feed>0:
            saved=self.im.copy();b=(595,285,1015,745);self.receipt(b)
            cut=round(b[1]+(b[3]-b[1])*feed)
            if cut<b[3]:self.im.paste(saved.crop((b[0]-10,cut,b[2]+12,b[3]+20)),(b[0]-10,cut));self.d=ImageDraw.Draw(self.im)
        if q>.98:self.txt(800,255,'每次回答，都在消耗算力',30,TEAL,anchor='mm')
        self.headline('一个引擎，可能影响谁的生意？','从模型能力，看到运行成本')
        self.txt(1300,760,'潜在的成本竞争',27,MUTED,anchor='mm')
    def small_waiting_gpu(self,b,t):
        self.gpu(b,label=False)
        x,y,X,Y=b;w=X-x;h=Y-y;sx=w/510;sy=h/300
        core=(x+25*sx,y+24*sy,x+w*.71,Y-25*sy);cx=(core[0]+core[2])/2;cy=(core[1]+core[3])/2
        self.d.rounded_rectangle(core,max(3,12*sx),fill=MINT,outline=TEAL,width=max(1,round(4*sx)))
        for xx in [cx-52*sx,cx+52*sx]:
            self.d.ellipse((xx-22*sx,cy-47*sy,xx+22*sx,cy+11*sy),fill=WHITE,outline=INK,width=max(1,round(3*sx)))
            self.d.ellipse((xx-12*sx,cy-23*sy,xx+2*sx,cy-3*sy),fill=INK)
            self.d.line((xx-22*sx,cy-66*sy,xx+20*sx,cy-62*sy),fill=INK,width=max(1,round(4*sx)))
        self.d.line((cx-25*sx,cy+46*sy,cx+25*sx,cy+46*sy),fill=INK,width=max(1,round(4*sx)))
    def saving_promise(self,c,t):
        p=min(1,t/c['duration_s']);b=(170,255,1430,750)
        if t<.65:
            self.receipt(rectmix((595,285,1015,745),b,ease(t/.65)))
            self.headline('同一批显卡，浪费能少在哪里？')
            return
        self.paper(b)
        self.txt(790,300,'一次回答的算力账',47,INK,anchor='mm')
        for i,(a,sub) in enumerate([('等待','工作能不能及时接上？'),('重复计算','算过的状态能不能留下？')]):
            yy=425+i*170;self.txt(315,yy,a,46,INK,anchor='mm');self.txt(690,yy,sub,34,MUTED,anchor='mm')
            if p>[.14,.27][i]:
                self.d.ellipse((210,yy-50,420,yy+52),outline=CORAL if i==0 else GOLD,width=5)
                self.d.line((440,yy,490,yy),fill=TEAL,width=4)
        thumb=(1110,555,1365,705);self.small_waiting_gpu(thumb,t)
        self.txt(1235,505,'同一批显卡',28,TEAL,anchor='mm')
        self.headline('同一批显卡，浪费能少在哪里？')
        if p>.82:
            q=ease((t-c['duration_s']*.82)/.65);self.im=Image.blend(self.im,self.bg,q);self.d=ImageDraw.Draw(self.im)
            self.small_waiting_gpu(rectmix(thumb,(955,350,1465,650),q),t)
            if q>.8:
                for i,s in enumerate(['A','B']):self.capsule(110,345+i*105,'请求 '+s,w=270,h=66)
            self.headline('把机器拆开，看它怎样省算力')
    def industry_payoff(self,c,t):
        p=min(1,t/c['duration_s']);self.engine((100,340,520,600));self.receipt((635,270,1065,740),question=False)
        self.txt(850,682,'收益看部署',35,TEAL,anchor='mm')
        self.txt(315,675,'运行方法可以被学习与复用',27,TEAL,anchor='mm')
        self.txt(1300,330,'潜在成本竞争',34,CORAL,anchor='mm')
        self.cloud((1130,420,1480,540),'AI 服务')
        if p>.65:
            for i,s in enumerate(['模型','硬件','负载']):self.tag(1120+i*128,650,s,[TEAL,PURPLE,INK][i])
        self.headline('开源的分量，在运行方法','具体收益，取决于部署条件')
    def industry_share(self,c,t):
        self.engine((160,325,580,585));self.receipt((995,280,1405,740),question=False)
        self.txt(1200,680,'算清运行成本',33,TEAL,anchor='mm')
        self.gpu((650,370,900,520),active=.5,label=False)
        self.txt(775,590,'模型怎样高效运行',30,TEAL,anchor='mm')
        self.headline('把模型能力和运行成本连起来')
        self.txt(380,690,'开源方法',35,TEAL,anchor='mm')
    def frame(self,c,elapsed,width=1600,static=False,animatic=False):
        methods={'industry-opening':self.opening_industry,'cost-question':self.cost_question,'saving-promise':self.saving_promise,'industry-payoff':self.industry_payoff,'industry-share':self.industry_share}
        if c['id'] not in methods:return super().frame(c,elapsed,width,static,animatic)
        from scene import caption_parts,caption_edges
        d=c['duration_s'];p=min(1,elapsed/d);parts=caption_parts(c['spoken_text']);edges=caption_edges(parts)
        caption=next((j for j in range(len(parts)) if p<edges[j+1]),len(parts)-1)
        motion={
            'industry-opening':(min(elapsed,1.1),),
            'cost-question':(min(elapsed,.5),p>.07,p>.18,min(.6,max(0,elapsed-d*.52))),
            'saving-promise':(min(elapsed,.65),p>.14,p>.27,min(.65,max(0,elapsed-d*.82))),
            'industry-payoff':(p>.65,), 'industry-share':(0,)}[c['id']]
        key=(c['id'],d,caption,width,static,animatic,motion)
        if key==getattr(self,'_industry_key',None):return self._industry_frame
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im)
        t=c['duration_s']*.95 if static else c['duration_s']*.70 if animatic else elapsed
        methods[c['id']](c,t);self.caption_footer(c,elapsed)
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        self._industry_key=key;self._industry_frame=self.im
        return self.im
