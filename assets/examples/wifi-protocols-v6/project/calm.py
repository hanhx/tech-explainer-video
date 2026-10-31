"""Restrained V6 direction: no animated pointer arrows; data, fields and states carry motion."""
from drawing import *
TIMING=json.loads((ROOT/'timing-v6.json').read_text()) if (ROOT/'timing-v6.json').exists() else {}
PLAN=json.loads((ROOT/'project.json').read_text());CUES={c['id']:c for s in PLAN['scenes'] for c in s['cues']}
INDEX={s['id']:i for i,s in enumerate(SHOTS)}
def norm(s):return ''.join(x for x in s if x.isalnum())
def voice_s(cid):return TIMING[cid]['duration_s']
def budget(cid):return max(voice_s(cid),CUES[cid].get('action_s',0))
@lru_cache(maxsize=500)
def word(cid,term,tail=False):
    row=TIMING[cid];ws=row['words'];full=''.join(x['text'] for x in ws);term=norm(term);pos=full.find(term)
    if pos<0:raise ValueError(f'{cid}: timing anchor missing: {term}')
    if tail:pos+=len(term)-1
    w=next(w for w in ws if w['lo']<=pos<w['hi']);return w['end'] if tail else w['start']
def q(t,a,b):return phase(t,a,max(a+.25,b))
def blend(a,b,f):
    a=tuple(bytes.fromhex(a[1:]));b=tuple(bytes.fromhex(b[1:]));return '#'+''.join(f'{round(mix(x,y,clamp(f))):02x}' for x,y in zip(a,b))
def tint(c,box,co,opacity=1):
    x,y,w,h=box;tile=Image.new('RGBA',(max(1,round(w*c.s)),max(1,round(h*c.s))))
    d=ImageDraw.Draw(tile);rgb=tuple(bytes.fromhex(co[1:]));d.rounded_rectangle((0,0,tile.width-1,tile.height-1),round(7*c.s),fill=rgb+(round(25*clamp(opacity)),),outline=rgb+(round(145*clamp(opacity)),),width=max(1,round(1.5*c.s)))
    c.im.paste(tile,(round(x*c.s),round(y*c.s)),tile)
def card(c,x,y,w,h,label,value,co=GREEN,fade=1):
    c.rect(x,y,w,h,blend(PAPER,MINT if co==GREEN else LILAC,.4*fade),FAINT,1,8)
    needed=font(20).getlength(label)+font(23).getlength(value)+42
    if needed>w and h>=63:
        c.text(x+14,y+8,label,18,blend(PAPER,MUTED,fade))
        c.text(x+14,y+36,value,22,blend(PAPER,co,fade),mono=all(ord(z)<128 for z in value))
    else:
        vs=23
        while font(20).getlength(label)+font(vs).getlength(value)+42>w and vs>18:vs-=1
        c.text(x+14,y+11,label,20,blend(PAPER,MUTED,fade));c.text(x+w-14,y+10,value,vs,blend(PAPER,co,fade),'rt')
def screen(c,lines):
    c.rect(144,290,272,112,'#fffefa',BLUE,2,3)
    for j,(text,co) in enumerate(lines):c.text(280,310+j*39,text,23,co,'mt')
def caption(c,lines,co=INK,y=240,size=25):
    for j,line in enumerate(lines.split('\n')):c.text(620,y+j*39,line,size,co,'mt')
def at(pts,q0):
    ls=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(pts,pts[1:])];d=clamp(q0)*sum(ls);k=0
    while k<len(ls)-1 and d>ls[k]:d-=ls[k];k+=1
    f=d/ls[k] if ls[k] else 0;return mix(pts[k][0],pts[k+1][0],f),mix(pts[k][1],pts[k+1][1],f)
def packet(c,pts,t,a,b,label,co=PURPLE):
    if t<a or t>b+.35:return
    f=q(t,a,b);x,y=at(pts,f);fade=min(1,(t-a)/.22,max(0,(b+.35-t)/.35));w=max(88,min(230,len(label)*12+28))
    fi=blend(PAPER,LILAC if co==PURPLE else SKY if co==BLUE else MINT if co==GREEN else CREAM,.85*fade)
    c.rect(x-w/2,y-19,w,38,fi,blend(PAPER,co,fade),2,9);c.text(x,y,label,21,blend(PAPER,co,fade),'mm',True)
AIR=[(510,332),(750,332)];DNS=[(510,332),(790,332),(1010,490),(1150,438),(1240,320),(1340,320)];WEB=[(510,332),(790,332),(1010,490),(1150,438),(1280,490),(1340,490)]
def range_active(t,a,b):return a<=t<b

def rarp_times(cid='rarp'):
    a=word(cid,'向本地服务器');b=word(cid,'服务器查表');d=word(cid,'它不属于');end=voice_s(cid)
    request_end=max(a+1.8,b-.3);reply_end=max(request_end+2.4,d)
    return a,request_end,request_end+.3,reply_end

def state(i,p):
    cid=SHOTS[i]['id'];t=p*budget(cid)
    configured=i>INDEX['requestack'] or(cid=='requestack' and t>=4.95)
    connected=i>INDEX['link'] or(cid=='link' and t>=word(cid,'无线链路可以'))
    if i<INDEX['link']:connected=False
    if cid=='unplug':connected=t<word(cid,'关闭笔记本')+.8
    if cid=='effects':connected=False
    if cid=='replug':connected=t>=word(cid,'先恢复接入')
    history=cid=='rarp' or(cid=='rarp_bridge' and t>=word(cid,'下面换一台')+.9)
    if history:return dict(history=True,ip=cid=='rarp' and t>=rarp_times()[3],link=True)
    return dict(history=False,ip=configured,link=connected)

def field_grid(c,t,items,y=295):
    for j,(label,value,co,start) in enumerate(items):
        if t>=start:
            f=q(t,start,start+.6);card(c,468,y+j*52,315,43,label,value,co,f)

def make_world(i,p,g):
    cid=SHOTS[i]['id'];t=p*budget(cid);end=voice_s(cid);s=state(i,p);wide=g['WIDE'];cam=wide
    if cid in ['rarp_bridge','rarp']:
        if cid=='rarp_bridge' and not s['history']:
            w=g['clone'](g['world_base'](True,True,True,True));g['radio'](w,1)
            caption(w,'接入 访问 恢复\n现代主线已经完成',GREEN)
            tint(w,(145,300,265,95),GREEN,q(t,0,word(cid,'下面换一台')))
            return w,wide
        w=g['history_world'](0,True)
        # Keep both historical actors in a stable wide composition.
        w.rect(450,538,600,42,PAPER,PAPER,1,0)
        if cid=='rarp_bridge':
            a=word(cid,'知道自己的');b=word(cid,'向服务器')
            caption(w,'独立历史对照\n另一台设备 C',PURPLE)
            if t>=a:tint(w,(95,520,390,38),PURPLE,q(t,a,a+.6))
            if t>=b:tint(w,(145,325,230,110),GOLD,q(t,b,b+.6))
        else:
            a,b,d,e=rarp_times();caption(w,'RARP\n反向地址解析协议',PURPLE)
            if t<a:tint(w,(95,520,390,38),PURPLE,q(t,0,1))
            packet(w,[(425,422),(1040,450)],t,a,b,'RARP 请求',PURPLE)
            if t>=b:tint(w,(900,300,550,55),GOLD,q(t,b,d+.3))
            packet(w,[(1040,450),(425,422)],t,d,e,'RARP 回复',GREEN)
            if t>=e:w.text(260,400,'192.0.2.10',27,GREEN,'mt',True)
        return w,wide
    dns=i>=INDEX['why_dns'];web=i>=INDEX['web'];page=i>INDEX['web']
    w=g['clone'](g['world_base'](True,page,dns,web))
    if cid not in ['mac','effects'] and not (cid=='discover' and t<2.1):
        labels=cid not in ['configuration','why_dns','arp','web','effects']
        g['radio'](w,1 if s['link'] else 0,labels,labels)
    if cid=='hook':
        a=word(cid,'这次');b=word(cid,'没有网线')
        screen(w,[('选择 Home Wi-Fi',PURPLE),('尚未连接',GOLD)])
        caption(w,'没有网线\n谁先开始工作？',GOLD)
        if t<a:
            w.rect(1090,250,410,280,PAPER,FAINT,1,12);w.text(1295,270,'上一集：请求到达服务器',22,GREEN,'mt');g['smallserver'](w,1320,365,'服务器','',GREEN)
            packet(w,[(1145,425),(1290,425)],t,.2,max(2.3,a-.2),'请求',GREEN)
        elif t<b:tint(w,(130,460,125,76),PURPLE,q(t,a,a+.6))
        else:tint(w,(825,315,180,72),PURPLE,q(t,b,b+.7))
    elif cid=='interfaces':
        a=word(cid,'蓝色');b=word(cid,'两种');d=word(cid,'各有自己的')
        caption(w,'两种都可以是实体硬件',INK,size=24)
        if t<a:tint(w,(130,460,125,76),PURPLE,q(t,0,.7))
        elif t<b:
            tint(w,(285,460,125,76),BLUE,q(t,a,a+.7));w.text(620,355,'有线接口也可以外接',23,BLUE,'mt')
        else:
            field_grid(w,t,[('无线 B',g['FMAC'],PURPLE,b),('有线 A',g['WMAC'],BLUE,d)],335)
    elif cid=='access':
        a=word(cid,'无线网卡');b=word(cid,'这次选择无线')
        if t<a:
            caption(w,'有线接入对照\nIEEE 802.3',GOLD);w.line([(450,498),(805,498)],FAINT,4)
            packet(w,[(510,498),(750,498)],t,.2,max(2.6,a-.2),'有线帧',GOLD)
        elif t<b:
            caption(w,'无线接入对照\nIEEE 802.11',PURPLE);packet(w,AIR,t,a+.2,b-.3,'无线信号',PURPLE)
        else:
            caption(w,'本片选择无线 B',PURPLE);tint(w,(130,460,125,76),PURPLE,q(t,b,b+.7))
    elif cid=='link':
        a=word(cid,'完成认证');b=word(cid,'无线链路可以');d=word(cid,'但这不代表');e=word(cid,'本例还没有')
        if t<a:
            screen(w,[('扫描无线网络',PURPLE),('Home Wi-Fi',PURPLE)]);packet(w,list(reversed(AIR)),t,.3,max(2.7,a-.2),'网络通告',PURPLE)
        elif t<b:
            screen(w,[('连接 Home Wi-Fi',PURPLE),('接入与安全协商',GOLD)]);packet(w,AIR,t,a,a+2,'关联与协商',PURPLE);tint(w,(825,315,180,72),PURPLE,q(t,a,a+.6))
        else:
            screen(w,[('Wi-Fi 已连接',GREEN),('IP 尚未获取',GOLD)]);caption(w,'链路已通\n还不能推断网站可达',GREEN)
            field_grid(w,t,[('电脑 IP','尚未获取',GOLD,b),('网站访问','尚未验证',MUTED,d),('本例租约','不可用',GOLD,e)],350)
    elif cid=='needip':
        a=word(cid,'网络地址还没获取');b=word(cid,'接下来用')
        if t<b:
            screen(w,[('Wi-Fi 已连接',PURPLE),('IP 尚未获取',GOLD)]);caption(w,'MAC 已有\nIP 参数尚缺',GOLD)
            tint(w,(130,460,125,76),PURPLE,q(t,.2,.9))
            if t>=a:tint(w,(144,330,272,63),GOLD,q(t,a,a+.7))
        else:screen(w,[('DHCP 客户端',PURPLE),('自动获取上网参数',PURPLE)]);caption(w,'DHCP\n动态主机配置协议',PURPLE)
    elif cid=='mac':
        z=q(t,0,2.1);cam=tuple(mix(a,b,z) for a,b in zip(wide,g['NIC_CAM']))
        if t>=2.1:
            g['computer'](w,True,False,True);a=word(cid,'不必等');b=word(cid,'系统还可能')
            tint(w,(137,470,52,53),PURPLE,q(t,2.1,2.7))
            if a<=t<b:
                w.rect(470,503,285,80,PAPER,PAPER,1,0);w.rect(495,518,230,48,LILAC,PURPLE,1,6);w.text(610,530,'已有 MAC 可用于发送帧',14,PURPLE,'mt')
            elif t>=b:
                w.rect(470,503,285,80,PAPER,PAPER,1,0);w.text(490,520,'当前网络可使用私有地址',14,PURPLE);w.text(490,553,'MAC 可由软件配置',14,GOLD)
                tint(w,(480,474,230,24),GOLD,q(t,b,b+.6))
    elif cid in ['discover','offer','requestack']:
        screen(w,[('DHCP 客户端',PURPLE),('自动获取网络配置',PURPLE)])
        if cid=='discover':
            if t<2.1:
                z=q(t,0,2.1);cam=tuple(mix(b,a,z) for a,b in zip(wide,g['NIC_CAM']))
                g['computer'](w,True,False,True)
                w.rect(470,503,285,80,PAPER,PAPER,1,0);w.text(490,520,'当前网络可使用私有地址',14,PURPLE);w.text(490,553,'MAC 可由软件配置',14,GOLD)
                return w,cam
            caption(w,'DHCP Discover\n广播寻找配置服务器',PURPLE)
            packet(w,AIR,t,2.2,max(4.6,end-2),'DHCP Discover',PURPLE)
            if t>=2:field_grid(w,t,[('源 IP','0.0.0.0',PURPLE,2),('目的 IP','255.255.255.255',GOLD,4.2)],380)
        elif cid=='offer':
            caption(w,'DHCP Offer\n地址还只是提议',PURPLE)
            card(w,1080,305,340,60,'候选 IP','192.168.1.20',GREEN)
            packet(w,list(reversed(AIR)),t,2,max(4.5,end-2.2),'DHCP Offer',PURPLE)
        else:
            caption(w,'Request 申请\nACK 确认',PURPLE)
            packet(w,AIR,t,.1,2.3,'Request',PURPLE)
            packet(w,list(reversed(AIR)),t,2.55,4.95,'ACK',GREEN)
            if t>=4.95:tint(w,(144,290,272,112),GREEN,.8);screen(w,[('配置已确认',GREEN),('192.168.1.20',GREEN)])
    elif cid=='dhcp_recap':
        # A larger temporal close-up; no pointer arrows and no half-second cuts.
        w.rect(475,215,1035,360,PAPER,FAINT,1,12)
        w.text(990,230,'回放刚才的 DHCP 交换',27,INK,'mt')
        w.text(650,279,'电脑客户端',24,BLUE,'mt');w.text(1320,279,'DHCP 服务器',24,GREEN,'mt')
        steps=[('发现','Discover',False),('提供','Offer',True),('请求','Request',False),('确认','ACK',True)]
        starts=[word(cid,'第一步'),word(cid,'第二步'),word(cid,'第三步'),word(cid,'第四步')]
        for j,(zh,en,reverse) in enumerate(steps):
            a=starts[j];b=starts[j+1]-.35 if j<3 else end-.7;y=330+j*62
            w.line([(600,y),(1360,y)],FAINT,1)
            if t>=a:
                fade=q(t,a,a+.5);w.text(990,y-30,f'{j+1}  {en} / {zh}',21,blend(PAPER,PURPLE,fade),'mt')
                finish=max(a+2.25,b)
                pts=[(650,y+12),(1310,y+12)];packet(w,list(reversed(pts)) if reverse else pts,t,a+.25,finish,'DHCP',GREEN if j==3 else PURPLE)
                if t>=finish:w.ellipse((650 if reverse else 1310)-4,y+8,8,8,GREEN,GREEN,1)
    elif cid=='udp_ports':
        caption(w,'UDP\n用户数据报协议',BLUE)
        a=word(cid,'客户端');b=word(cid,'服务器')
        screen(w,[('DHCP 客户端',PURPLE),('UDP 68',BLUE)])
        w.rect(835,445,160,25,PAPER,PAPER,1,1);w.text(915,448,'UDP 67',21,GREEN,'mt',True)
        card(w,478,375,305,63,'DHCP 消息','装在 UDP 中',BLUE)
        packet(w,AIR,t,2.2,max(4.7,a-.5),'UDP / DHCP',BLUE)
        packet(w,list(reversed(AIR)),t,max(a+.3,b),max(b+2.6,end-1),'UDP / DHCP',BLUE)
        if t>=a:tint(w,(144,330,272,62),BLUE,q(t,a,a+.6))
        if t>=b:tint(w,(825,409,180,68),GREEN,q(t,b,b+.6))
    elif cid=='configuration':
        screen(w,[('DHCP 已确认',GREEN),('上网参数已齐',GREEN)]);caption(w,'自己的参数齐了',GREEN)
        terms=[('IP','192.168.1.20','电脑得到'),('掩码','255.255.255.0','子网掩码'),('网关','192.168.1.1','默认网关'),('DNS','192.0.2.53','DNS解析器'),('租期','3600 秒','租期')]
        field_grid(w,t,[(a,b,GREEN,word(cid,term)) for a,b,term in terms],300)
    elif cid=='why_dns':
        a=word(cid,'浏览器现在');b=word(cid,'别的网段');d=word(cid,'如果缓存')
        caption(w,'DNS 域名系统\n网站名字还需要解析',PURPLE)
        host='www.example.com';typing=q(t,a,a+2.2);screen(w,[(host[:round(len(host)*typing)] if t>=a else '准备输入网站名字',BLUE),('网站 IP：?',GOLD)])
        if t>=b:field_grid(w,t,[('DNS 位置','远端网段',PURPLE,b),('下一跳','192.168.1.1',GREEN,b+1.6)],365)
        if t>=d:card(w,478,489,305,55,'网关 MAC','缓存未命中',GOLD,q(t,d,d+.6))
    elif cid=='arp':
        a=word(cid,'在本地链路');b=word(cid,'网关回复');d=word(cid,'记入邻居缓存')
        caption(w,'ARP\n地址解析协议',GOLD)
        card(w,478,365,305,59,'下一跳 IP','192.168.1.1',GOLD)
        packet(w,AIR,t,a,max(a+2.6,b-.25),'ARP Request',GOLD)
        packet(w,list(reversed(AIR)),t,b,max(b+2.6,d),'ARP Reply',GREEN)
        if t>=max(b+2.6,d):card(w,478,443,305,67,'网关 MAC',g['GMAC'],GREEN)
    elif cid=='dns':
        a=word(cid,'DNS查询');b=word(cid,'解析器回传');d=word(cid,'DNS也能')
        caption(w,'DNS\n查询网站的 IP',PURPLE);screen(w,[('www.example.com',BLUE),('网站 IP：?',GOLD)])
        packet(w,DNS,t,a,max(a+3,b-.3),'DNS 查询',PURPLE)
        packet(w,list(reversed(DNS)),t,b,max(b+3,d-.3),'DNS 答复',PURPLE)
        if t>=max(b+3,d-.3):screen(w,[('www.example.com',BLUE),('198.51.100.80',GREEN)])
        if t>=d:
            w.rect(1090,230,415,125,PAPER,FAINT,1,10);w.text(1295,245,'传输选择对照',22,MUTED,'mt');card(w,1110,287,180,45,'本例','UDP 53',PURPLE);w.text(1405,299,'也可 TCP',23,BLUE,'mt')
    elif cid=='web':
        a=word(cid,'本例先用');b=word(cid,'再用TLS');d=word(cid,'然后发送');e=word(cid,'服务器返回');f=word(cid,'浏览器才')
        caption(w,'TCP 连接 · TLS 加密\nHTTP 请求与响应',BLUE,size=24)
        screen(w,[('www.example.com',BLUE),('正在访问',GOLD)])
        stages=[('TCP','建立连接',a,b,BLUE),('TLS','协商加密',b,d,GOLD),('HTTP','请求网页',d,e,PURPLE)]
        for j,(abbr,label,start,finish,co) in enumerate(stages):
            if t>=start:
                card(w,477,355+j*58,305,47,abbr,label,co,q(t,start,start+.5))
                if t<finish:packet(w,WEB,t,start+.5,max(start+2.6,finish-.4),abbr,co)
        arrived=max(e+2.6,f)
        packet(w,list(reversed(WEB)),t,e,arrived,'网页内容',GREEN)
        if t>=arrived:
            c=q(t,arrived,end-.6);w.rect(144,290,272,112,'#fffefa',BLUE,2,3);w.rect(155,308,max(3,235*min(1,c*2)),10,SKY,SKY,1,2)
            if c>.2:w.rect(155,335,65,max(3,50*clamp((c-.2)*3)),CREAM,GOLD,1,3)
            for j in range(3):
                z=clamp((c-.3-j*.15)/.2)
                if z>0:w.line([(240,340+j*20),(240+135*z,340+j*20)],MUTED,3)
    elif cid=='replay':
        caption(w,'暂停主线\n只回看刚才的 DNS 查询',GOLD)
        packet(w,DNS,t,2,max(5,end-1.8),'DNS 查询 Q1',PURPLE)
    elif cid=='frame':
        a=word(cid,'交给接入点');b=word(cid,'最终的链路目的地址');d=word(cid,'地址解析消息');e=word(cid,'网络数据包');is_arp=t<e
        w.rect(460,212,1040,368,PAPER,PAPER,1,0)
        w.rect(485,230,1010,240,PAPER,FAINT,1,12);w.text(990,245,'上行 802.11 无线数据帧（概念视图）',26,PURPLE,'mt')
        card(w,510,290,355,46,'无线接收者','AP',PURPLE);card(w,890,290,355,46,'发送者','无线 B',PURPLE)
        card(w,510,350,950,46,'载荷链路目的','广播' if is_arp else '网关 MAC',GOLD)
        card(w,510,410,950,46,'LLC / SNAP 类型','0x0806：ARP' if is_arp else '0x0800：IPv4',GREEN)
        if a<=t<b:tint(w,(510,290,355,46),PURPLE,q(t,a,a+.6))
        elif b<=t<d:tint(w,(510,350,950,46),GOLD,q(t,b,b+.6))
        elif t>=d:tint(w,(510,410,950,46),GREEN,q(t,d,d+.6))
    elif cid=='layers':
        terms=[('应用层','DNS',PURPLE),('传输层','UDP',BLUE),('网络层','IP',GREEN),('链路层','802.11',GOLD),('物理层','无线电',PURPLE)]
        w.rect(460,212,1040,368,PAPER,PAPER,1,0)
        w.text(990,229,'同一条 DNS 查询逐层封装',27,INK,'mt')
        # Each layer gets a full spoken sentence; the same query remains visible.
        x,y,ww,hh=1020,480,310,58
        for j in reversed(range(4)):
            term,abbr,co=terms[j];start=word(cid,term)
            if t<start:continue
            f=q(t,start,start+.85);bx=625-j*35;by=436-j*52;bw=730+j*70;bh=104+j*52
            w.rect(bx,by,bw,max(55,bh),blend(PAPER,co,.09*f),blend(PAPER,co,.65*f),2,10)
            w.text(bx+16,by+12,term+'  '+abbr,24,co)
            details=['主机名 www.example.com','源端口 53000 / 目的端口 53','源 192.168.1.20 / 目的 192.0.2.53','无线接收 AP / 载荷目的 网关 MAC']
            w.text(bx+bw-16,by+15,details[j],19,co,'rt')
        # The DNS payload is never replaced by another example.
        w.rect(720,480,560,48,LILAC,PURPLE,2,10);w.text(1000,504,'DNS：查询 www.example.com',23,PURPLE,'mm')
        a=word(cid,'物理层')
        if t>=a:
            points=[(650+j*13,553+7*math.sin(j*.9-(t-a)*2)) for j in range(55)];w.line(points,PURPLE,2)
            w.text(1410,553,'无线电',18,PURPLE,'lm')
    elif cid=='udp':
        a=word(cid,'UDP');b=word(cid,'TCP');d=word(cid,'它们是并列')
        w.rect(465,215,1040,360,PAPER,PAPER,1,0)
        w.text(985,230,'传输方式对比：并列选择',27,INK,'mt')
        card(w,500,300,430,60,'UDP','独立数据报',PURPLE)
        card(w,1020,300,430,60,'TCP','有序字节流',BLUE)
        # Messages keep boundaries; byte blocks assemble in order.
        if a<=t<b:
            for j in range(3):packet(w,[(545,415+j*45),(890,415+j*45)],t,a+j*1.4,a+j*1.4+2.6,'报文 '+str(j+1),PURPLE)
            tint(w,(500,300,430,60),PURPLE,q(t,a,a+.7))
        elif t>=b:
            tint(w,(1020,300,430,60),BLUE,q(t,b,b+.7))
            for j in range(5):
                z=q(t,b+j*.8,b+j*.8+2.3);xx=mix(1040+j*67,1080+j*67,z);yy=mix(510,415,z)
                w.rect(xx,yy,53,40,SKY,BLUE,1,5);w.text(xx+26,yy+20,str(j+1),23,BLUE,'mm')
        if t>=d:
            w.text(985,546,'不需要依次经过 UDP 和 TCP',23,MUTED,'mt')
            packet(w,[(545,475),(890,475)],t,d+.3,min(end-.5,d+3.6),'独立报文',PURPLE)
            w.text(1240,490,'确认 / 必要时重传',23,BLUE,'mt')
    elif cid=='unplug':
        a=word(cid,'关闭笔记本');b=word(cid,'这条无线链路');d=word(cid,'对比拔网线')
        screen(w,[('Wi-Fi 设置',PURPLE)])
        off=q(t,a,a+.8);w.rect(220,350,110,36,blend(MINT,RED,off),FAINT,1,18);w.ellipse(mix(294,224,off),354,28,28,PAPER,PAPER,1)
        caption(w,'接口已关闭' if t>=a+.8 else '准备关闭无线接口',RED)
        if b<=t<d:
            card(w,477,365,305,70,'本地状态','驱动通知系统',RED,q(t,b,b+.65));tint(w,(130,460,125,76),RED,q(t,b,b+.65))
        if t>=d:
            w.rect(1090,230,415,170,PAPER,FAINT,1,10);w.text(1295,245,'有线接入对照：拔网线',23,GOLD,'mt');w.rect(1130,310,28,38,'#293a40',INK,2,2);xx=mix(1158,1240,q(t,d+.4,d+2.8));w.rect(xx,314,70,30,CREAM,GOLD,1,4);w.line([(xx+70,329),(1460,329)],GOLD,4)
    elif cid=='effects':
        a=word(cid,'新请求');b=word(cid,'连接关闭');d=word(cid,'系统通知')
        caption(w,'页面仍在\n新请求可能等待或失败',RED)
        if t>=a:
            # This packet remains local: no transmission on the disconnected link.
            packet(w,[(280,355),(230,432)],t,a,a+2.6,'新请求',RED)
            w.text(620,385,'等待 '+str(max(0,int(t-a)))+' 秒',25,RED,'mt')
            theta=(t-a)*1.2;w.ellipse(592,434,46,46,None,RED,2);w.line([(615,457),(615+16*math.sin(theta),457-16*math.cos(theta))],RED,2)
        if t>=b:w.text(620,325,'断开接口不等于正常 FIN',22,RED,'mt')
        if t>=d:w.text(620,515,'通知、重传、超时由实现决定',21,MUTED,'mt')
    elif cid=='replug':
        a=word(cid,'先恢复接入');b=word(cid,'系统再检查');d=word(cid,'仍有效');e=word(cid,'失效时')
        caption(w,'恢复接入\n检查已有配置',GREEN)
        if t<a:screen(w,[('重新连接 Wi-Fi',PURPLE),('Home Wi-Fi',PURPLE)])
        packet(w,AIR,t,b,max(b+2,d),'检查旧配置',BLUE)
        if t>=d:screen(w,[('继续使用旧配置',GREEN),('192.168.1.20',GREEN)]);tint(w,(144,330,272,63),GREEN,q(t,d,d+.7))
        if t>=e:w.text(620,380,'失效时才重新获取',23,MUTED,'mt')
    elif cid=='ending':
        captions=[('无线接入','802.11 完成本地接入',PURPLE),('DHCP','DHCP 准备上网参数',PURPLE),('ARP','ARP 找到下一跳邻居',GOLD),('DNS','DNS 查询网站 IP',PURPLE),('UDP和TCP','UDP / TCP 传送数据',BLUE),('IP支持','IP 支持跨网转发',GREEN)]
        for j,(term,text,co) in enumerate(captions):
            a=word(cid,term);b=word(cid,captions[j+1][0]) if j+1<len(captions) else end
            if a<=t<b:caption(w,text,co);break
    return w,cam
