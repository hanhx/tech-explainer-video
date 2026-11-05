"""Reference-derived heading hierarchy and causal, object-led V8 staging.

Keep the approved bright palette and original drawings. No reference creator assets.
"""
from PIL import Image,ImageDraw
from industry import Paper as OriginalFilm
from continuity import BG,WHITE,INK,MUTED,TEAL,GOLD,CORAL,LINE,PURPLE,font,ease

NAV=['开源与接力','留下计算状态','缓存分块存','显存再周转','让前缀复用','看懂算力账']
HEADERS={
 'industry-opening':('DeepSeek 开源，谁的成本账可能变？','DeepInfer：跟着一次请求，看机器怎样协作'),
 'cost-question':('推理引擎，为什么会影响生意？','一次回答背后，也有一笔算力账'),
 'saving-promise':('同一批显卡，浪费能少在哪里？','从空等、重算，看到显存怎样周转'),
 'opening':('请求排队，显卡为什么还在等？','先看一次等待，再找工作交接的断点'),
 'roles':('下一批工作，谁来及时送到？','CPU 准备与调度，GPU / NPU 执行计算'),
 'serial':('每轮都等完再准备，会怎样？','沿着同一组 CPU / GPU 时间块看空档'),
 'overlap':('把准备和计算接起来','同一组时间块重排，观察重叠发生在哪里'),
 'repeat-question':('空等少了，重算前文怎么办？','先看浪费的假设，再回到请求开始前'),
 'weights':('启动前，先把模型装进显存','回看请求开始前 · 权重会被后续请求反复使用'),
 'prefill':('输入处理完，还能留下什么？','预填充：留下后面还能复用的注意力状态'),
 'kv':('把算过的状态，留给下一轮','KV Cache：请求相关的中间状态'),
 'cached-decode':('回到生成现场，只追加新的部分','读旧状态 → 继续计算 → 留下新状态'),
 'capacity-question':('重算少了，显存会不会被挤满？','沿着同一块 HBM 展开，看看空间分给了谁'),
 'budget':('显存这块地方，要同时放什么？','权重、运行时开销与可分配的 KV 块池'),
 'fragment-question':('有空位，却没连成一整片？','把请求状态分块，让零散空位也能利用'),
 'paged':('逻辑连续，存放可以分散','同一请求 A：逻辑块 → 块表 → 显存块'),
 'lookup':('同样的位置 9，怎样找到不同数据？','特写同一块表关系 · 数据仍在原来的块里'),
 'mapping-boundary':('像分页，但这里查的是缓存索引','软件管理的槽位，不是 CPU 物理地址'),
 'full-question':('分块用好了，为什么还是会满？','空间利用率提高了，容量上限仍然存在'),
 'pressure':('缓存不够，先让谁腾出空间？','同一块池：保留 A，抢占 B，新请求继续等待'),
 'recompute':('腾出空间之后，请求去哪里？','允许重算才回队列；部分配置会直接结束'),
 'release-finished':('请求完成，把运行空间还回来','KV 归还块池，模型权重继续留驻'),
 'next-prefix':('这次结束了，下次还想复用呢？','从运行空间的周转，走向长期结果的保留'),
 'scope':('长期复用，谁来负责？','区分开源引擎与官方文档中的外围生产系统'),
 'store':('要复用前缀，先把状态取回来','3FS → 主机共享内存 → HBM，分两步看'),
 'reuse':('写盘和解码卸载，是同一件事吗？','SWA 另有主机路径；生产 Decode 未开启 KV offload'),
 'industry-payoff':('回到开头：这笔算力账怎样变？','把一路看到的动作，收束成三个改进点'),
 'industry-impact':('方法可以扩散，收益取决于部署','潜在成本竞争 · 模型、硬件与负载共同决定收益'),
 'industry-share':('看大模型开源，也看怎样高效运行','从模型能力，看到机器协作与运行成本')}

class Paper(OriginalFilm):
    def header(self,c):
        self.d.rectangle((0,0,1600,234),fill=BG);self.header_geometry=[]
        for i,label in enumerate(NAV):
            x=80+i*240;active=c['chapter']==i+1;text=f'0{i+1} {label}'
            self.txt(x,43,text,23,TEAL if active else MUTED,anchor='lm')
            if active:self.d.line((x,76,x+215,76),fill=GOLD,width=4)
            b=self.d.textbbox((round(x),43),text,font=font(23),anchor='lm')
            self.header_geometry.append({'id':f'nav-{i}','box':[b[0],b[1],b[2]-b[0],b[3]-b[1]]})
        title,sub=HEADERS[c['id']];size=46
        while self.d.textbbox((0,0),title,font=font(size))[2]>1310:size-=1
        self.txt(80,128,title,size,INK,anchor='lm')
        self.txt(1520,128,f'{c.get("shot_number",1):02}/{c.get("shot_total",27):02}',24,MUTED,anchor='rm')
        self.txt(82,188,sub,26,MUTED,anchor='lm')
        for name,text,x,y,s,anchor in [('title',title,80,128,size,'lm'),('count',f'{c.get("shot_number",1):02}/{c.get("shot_total",27):02}',1520,128,24,'rm'),('sub',sub,82,188,26,'lm')]:
            b=self.d.textbbox((x,y),text,font=font(s),anchor=anchor);self.header_geometry.append({'id':name,'box':[b[0],b[1],b[2]-b[0],b[3]-b[1]]})
        self.d.line((80,220,1520,220),fill=LINE,width=2)
        if c['id'] in ['scope','store','reuse']:
            self.tag(1130,166,'文档架构 · 未完整开源',CORAL)
    def footer_v8(self,c,t):
        from scene import caption_parts,caption_edges
        parts=caption_parts(c['spoken_text']);edges=caption_edges(parts);p=min(1,t/c['duration_s'])
        j=next((i for i in range(len(parts)) if p<edges[i+1]),len(parts)-1)
        self.d.rectangle((0,804,1600,900),fill=BG);self.d.line((80,804,1520,804),fill=LINE,width=2)
        self.txt(800,851,parts[j],38,INK,anchor='mm')
    def receipt_result(self,checks):
        b=(555,270,1045,752);self.paper(b,corner=False)
        self.txt(800,322,'同一笔算力账',41,INK,anchor='mm')
        self.d.line((585,365,1015,365),fill=LINE,width=2)
        for i,(a,result) in enumerate([('等待','接上工作'),('重算','复用状态'),('空间','持续周转')]):
            y=420+i*105;self.txt(600,y,a,31,INK,anchor='lm')
            self.d.rounded_rectangle((705,y-18,741,y+18),6,fill=WHITE,outline=TEAL if i<checks else LINE,width=2)
            if i<checks:self.d.line([(713,y),(721,y+8),(734,y-9)],fill=TEAL,width=4)
            self.txt(766,y,result,29,TEAL if i<checks else MUTED,anchor='lm')
        self.txt(800,717,'方法示意，收益看部署',23,MUTED,anchor='mm')
    def closing_world(self,c,t):
        from scene import caption_parts,caption_edges
        mode=c['id'];p=min(1,t/c['duration_s']);checks=3
        if mode=='industry-payoff':
            parts=caption_parts(c['spoken_text']);edges=caption_edges(parts)
            thresholds=[edges[next(i for i,s in enumerate(parts) if word in s)] for word in ['减少空等','减少重算','显存']]
            checks=sum(p>=q for q in thresholds)
        self.engine((95,365,465,605));self.txt(280,666,'DeepInfer · 运行方法',27,TEAL,anchor='mm')
        self.receipt_result(checks)
        if mode=='industry-impact':
            self.txt(1295,304,'可学习、可复用',30,TEAL,anchor='mm')
            for i in range(3 if p>.25 else 1):
                x=1145+i*48;self.paper((x,365-i*12,x+165,470-i*12));self.txt(x+82,411-i*12,'方法',29,TEAL,anchor='mm')
            self.cloud((1125,515,1480,630),'更多服务？')
            if p>.58:
                for i,s in enumerate(['模型','硬件','负载']):self.tag(1120+i*128,687,s,[TEAL,PURPLE,INK][i])
        else:
            self.gpu((1120,405,1485,620),active=.75,label=False)
            self.txt(1300,340,'同一批显卡',33,TEAL,anchor='mm')
            if mode=='industry-share' and p>.43:
                self.paper((1100,661,1500,757),corner=False)
                self.txt(1300,691,'如果这趟旅程帮到了你',25,INK,anchor='mm')
                self.txt(1300,732,'转给关注 AI 开源的朋友',25,TEAL,anchor='mm')
            elif mode=='industry-payoff':self.txt(1300,685,'组织协作，提高利用效率',25,MUTED,anchor='mm')
    def frame(self,c,elapsed,width=1600,static=False,animatic=False):
        if c['id'].startswith('industry-') and c['id'] in ['industry-payoff','industry-impact','industry-share']:
            from scene import caption_parts,caption_edges
            p=min(1,elapsed/c['duration_s']);parts=caption_parts(c['spoken_text']);edges=caption_edges(parts)
            caption=next((i for i in range(len(parts)) if p<edges[i+1]),len(parts)-1)
            pose=tuple(p>=x for x in edges)+((p>.25),(p>.58),(p>.43))
            key=(c['id'],caption,pose,min(elapsed,.85) if c['id']=='industry-payoff' else 0,width,static,animatic)
            if key==getattr(self,'_closing_cache_key',None):return self._closing_cache_image
            self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.closing_world(c,elapsed)
            if c['id']=='industry-payoff' and elapsed<.85 and not static:
                result=self.im.copy();roi=(60,235,1540,790)
                if elapsed<.35:
                    self.im=self.bg.copy();self.d=ImageDraw.Draw(self.im);self.stored(0,1,True)
                    self.im.paste(Image.blend(self.im.crop(roi),self.bg.crop(roi),ease(elapsed/.35)),roi)
                else:
                    self.im=self.bg.copy();self.im.paste(Image.blend(self.bg.crop(roi),result.crop(roi),ease((elapsed-.35)/.5)),roi)
                self.d=ImageDraw.Draw(self.im)
            self.header(c);self.footer_v8(c,elapsed)
            if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
            self._closing_cache_key=key;self._closing_cache_image=self.im;return self.im
        base=super().frame(c,elapsed,1600,static,animatic)
        replay=False
        if c['id']=='repeat-question':
            from scene import caption_parts,caption_edges
            parts=caption_parts(c['spoken_text']);edges=caption_edges(parts)
            threshold=edges[next(i for i,s in enumerate(parts) if '回到请求开始前' in s)]
            replay=elapsed>=c['duration_s']*threshold
        key=(id(base),c['id'],width,static,animatic,replay)
        if key==getattr(self,'_director_cache_key',None):return self._director_cache_image
        self.im=base.copy();self.d=ImageDraw.Draw(self.im);self.header(c);self.footer_v8(c,elapsed)
        if c['id']=='repeat-question':
            self.tag(95,245,'假设：每轮从头算',CORAL)
            if replay:self.tag(1010,245,'回看：请求开始前',TEAL)
        if width!=1600:self.im=self.im.resize((width,round(width*9/16)),Image.Resampling.LANCZOS)
        self._director_source=base;self._director_cache_key=key;self._director_cache_image=self.im
        return self.im
