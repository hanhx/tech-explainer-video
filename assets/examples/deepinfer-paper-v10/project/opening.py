"""Event-led opening: a visible queue and an idle GPU, followed by a work handoff.
Original flat illustrations; no reference creator assets.
"""
import math
from PIL import Image,ImageDraw
from continuity import Paper as Base, BG,WHITE,INK,MUTED,TEAL,MINT,GOLD,CORAL,LINE,ease,mix,rectmix

class Paper(Base):
    def footer(self,cue,t):
        from scene import caption_parts,caption_edges
        parts=caption_parts(cue['spoken_text']);edges=caption_edges(parts);p=min(1,t/max(.1,cue['duration_s']))
        j=next((i for i in range(len(parts)) if p<edges[i+1]),len(parts)-1)
        self.d.rectangle((0,804,1600,900),fill=BG);self.d.line((85,804,1515,804),fill=LINE,width=2)
        self.txt(800,851,parts[j],38,INK,anchor='mm')
    def waiting_gpu(self,b,t=0):
        self.gpu(b,label=False)
        x,y,X,Y=b;w=X-x;cx=(x+25+x+w*.71)/2;cy=(y+24+Y-25)/2
        self.d.rounded_rectangle((x+25,y+24,x+w*.71,Y-25),12,fill=MINT,outline=TEAL,width=4)
        # A simple expressive face makes the idle state readable without a hardware diagram.
        look=-5*ease(min(1,t/1.2))
        for xx in [cx-52,cx+52]:
            self.d.ellipse((xx-22,cy-47,xx+22,cy+11),fill=WHITE,outline=INK,width=3)
            self.d.ellipse((xx-7+look,cy-23,xx+7+look,cy-3),fill=INK)
            self.d.line((xx-22,cy-66,xx+20,cy-62),fill=INK,width=4)
        self.d.line((cx-25,cy+46,cx+25,cy+46),fill=INK,width=4)
    def hook(self,cue,t):
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im)
        self.d.rectangle((0,0,1600,232),fill=BG)
        self.txt(85,45,'推理中的一次等待 · 示意',24,MUTED)
        self.txt(800,135,'请求排队，显卡却在等活',70,INK,anchor='mm')
        self.txt(245,280,'排队等结果',35,TEAL,anchor='mm')
        for i,s in enumerate(['A','B','C']):
            x=110 if i<2 else mix(-310,110,ease((t-.15)/.8))
            self.capsule(x,345+i*105,'请求 '+s,w=270,h=66)
        self.pipe([(410,480),(910,480)],LINE)
        self.box((580,435,805,530),fill=WHITE,line=CORAL,r=16)
        self.txt(692,482,'等工作',39,CORAL,anchor='mm')
        self.waiting_gpu((955,350,1465,650),t)
        self.txt(1210,295,'显卡',42,INK,anchor='mm')
        self.tag(1070,710,'还没开工',CORAL)
        # A clock provides a state cue, without implying a measured benchmark.
        x,y=842,480;self.d.ellipse((x-25,y-25,x+25,y+25),fill=WHITE,outline=CORAL,width=3)
        ang=-math.pi/2+min(t,2.2)*1.1
        self.d.line((x,y,x+18*math.cos(ang),y+18*math.sin(ang)),fill=CORAL,width=3)
        self.footer(cue,t)
    def handoff(self,cue,t):
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);p=min(1,t/max(.1,cue['duration_s']))
        q=ease(t/.55);gpu=rectmix((955,350,1465,650),(655,370,1095,620),q)
        self.cpu((150,470,370,640),active=True)
        a=ease((t-.2)/.5);b=(100,430,445,715)
        self.im.paste(Image.blend(self.bg.crop(b),self.im.crop(b),a),b);self.d=ImageDraw.Draw(self.im)
        self.pipe([(390,550),(630,550)],TEAL)
        progress=ease((t-cue['duration_s']*.45)/.65)
        if p>.45:
            x=mix(390,630,progress);self.tile((x-46,520,x+46,580),'执行',color=TEAL)
        arrived=t>=cue['duration_s']*.45+.65
        if not arrived:self.waiting_gpu(gpu,t)
        else:self.gpu(gpu,active=min(1,(t-cue['duration_s']*.45-.65)/.4),label=False)
        self.txt((gpu[0]+gpu[2])/2,gpu[1]-35,'显卡 · GPU / NPU',29,INK,anchor='mm')
        self.txt(510,620,'准备好的执行信息',25,TEAL,anchor='mm')
        if arrived:
            self.tag(1155,485,'开始计算',TEAL)
            self.tile((1200,585,1450,650),'产生结果',color=GOLD)
        if p>.72:self.tag(140,735,'DeepInfer：组织调度与接力',TEAL)
        self.d.rectangle((0,0,1600,232),fill=BG)
        self.txt(85,45,'从等待，到开始计算',24,TEAL)
        self.txt(85,102,'下一批工作，谁来及时送到？',53,INK)
        self.txt(88,179,'准备好执行信息，把工作及时送到',28,MUTED)
        self.footer(cue,t)
    def frame(self,cue,elapsed,width=1600,static=False,animatic=False):
        if cue['id'] not in ['opening','roles']:return super().frame(cue,elapsed,width,static,animatic)
        from scene import caption_parts,caption_edges
        duration=cue['duration_s'];p=min(1,elapsed/duration);parts=caption_parts(cue['spoken_text']);edges=caption_edges(parts)
        caption=next((j for j in range(len(parts)) if p<edges[j+1]),len(parts)-1)
        motion=(min(elapsed,2.2),) if cue['id']=='opening' else (min(elapsed,1.2),min(1.05,max(0,elapsed-duration*.45)),p>.72)
        key=(cue['id'],duration,width,static,animatic,caption,motion)
        if key==getattr(self,'_opening_key',None):return self._opening_frame
        t=cue['duration_s']*.95 if static else elapsed
        if cue['id']=='opening':self.hook(cue,t)
        else:self.handoff(cue,t)
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        self._opening_key=key;self._opening_frame=self.im
        return self.im
