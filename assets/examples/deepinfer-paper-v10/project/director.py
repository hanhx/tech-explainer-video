"""V9 continuous closing: finish on the technical diagram, then the user's invitation."""
import math
from PIL import Image,ImageDraw
from director_base import Paper as BodyFilm,HEADERS
from continuity import BG,WHITE,INK,MUTED,TEAL,GOLD,LINE,PURPLE,ease

class Paper(BodyFilm):
    def closing_events(self,c):
        from scene import caption_parts,caption_edges
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts)
        invitation=edges[next(i for i,s in enumerate(parts) if s.startswith('欢迎'))]*c['duration_s']
        thanks=edges[next(i for i,s in enumerate(parts) if '谢谢大家' in s)]*c['duration_s']
        return parts,edges,invitation,thanks
    def technical_close(self):
        # Keep the latest storage/memory illustration until the actual invitation.
        self.stored(0,1,True)
        self.im.paste(self.bg.crop((60,235,1540,350)),(60,235));self.d=ImageDraw.Draw(self.im)
        self.paper((160,260,1440,339),corner=False)
        self.txt(800,301,'减少空等与重算，让一次回答的成本有机会降低',35,TEAL,anchor='mm')
        self.im.paste(self.bg.crop((60,729,1540,790)),(60,729));self.d=ImageDraw.Draw(self.im)
        self.txt(800,759,'具体收益取决于模型、硬件与负载',27,MUTED,anchor='mm')
    def invitation_card(self,x,label,color):
        self.paper((x-150,340,x+150,625),corner=False)
        y=440
        if label=='点赞':
            # Original simple thumb outline; not a platform screenshot.
            pts=[(x-63,y+42),(x-63,y-24),(x-26,y-24),(x-6,y-71),(x+10,y-71),(x+17,y-58),(x+11,y-26),(x+62,y-26),(x+74,y-11),(x+58,y+48),(x-24,y+48),(x-24,y+42)]
            self.d.polygon(pts,fill='#D7F2E7',outline=color,width=5)
            self.d.rounded_rectangle((x-86,y-27,x-58,y+50),5,fill=WHITE,outline=color,width=5)
        elif label=='收藏':
            points=[]
            for k in range(10):
                a=-math.pi/2+k*math.pi/5;r=77 if k%2==0 else 33
                points.append((x+r*math.cos(a),y+r*math.sin(a)))
            self.d.polygon(points,fill='#FFF1CD',outline=color,width=5)
        else:
            self.d.ellipse((x-40,y-76,x+22,y-14),fill='#DCECF9',outline=color,width=5)
            self.d.arc((x-73,y-6,x+61,y+87),180,360,fill=color,width=6)
            self.d.line((x+62,y-5,x+62,y+47),fill=color,width=6)
            self.d.line((x+36,y+21,x+88,y+21),fill=color,width=6)
        self.txt(x,572,label,42,INK,anchor='mm')
    def frame(self,c,elapsed,width=1600,static=False,animatic=False):
        if c['id']!='closing':return super().frame(c,elapsed,width,static,animatic)
        parts,edges,invite,thanks=self.closing_events(c);p=min(1,elapsed/c['duration_s'])
        caption=next((i for i in range(len(parts)) if p<edges[i+1]),len(parts)-1)
        motion=min(.65,max(0,elapsed-invite));reveals=tuple(elapsed>=invite+.35+i*.15 for i in range(3));thank=elapsed>=thanks
        key=(c['id'],c['duration_s'],width,caption,motion,reveals,thank,elapsed>=invite,static,animatic)
        if key==getattr(self,'_v9_closing_key',None):return self._v9_closing_image
        self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im)
        if elapsed<invite+.35:
            self.technical_close()
            if elapsed>invite:
                roi=(60,235,1540,790);self.im.paste(Image.blend(self.im.crop(roi),self.bg.crop(roi),ease((elapsed-invite)/.35)),roi);self.d=ImageDraw.Draw(self.im)
        else:
            for i,(s,color) in enumerate([('点赞',TEAL),('收藏','#B97809'),('关注',PURPLE)]):
                if reveals[i]:self.invitation_card(400+i*400,s,color)
            if thank:self.txt(800,730,'谢谢大家',56,TEAL,anchor='mm')
        HEADERS['closing']=('感谢观看','如果这段动画让你有所收获') if elapsed>=invite else ('同一批显卡，怎样降低回答成本？','DeepInfer：把准备、计算与缓存配合起来')
        self.header(c);self.footer_v8(c,elapsed)
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        self._v9_closing_key=key;self._v9_closing_image=self.im;return self.im
