"""V6: Wi-Fi main story, one persistent laptop, visible state changes, explicit replay/history.

The world stays in fixed coordinates. Camera moves inspect the SAME wireless NIC.
"""
from drawing import *
import calm

WMAC='02:6A:10:20:30:40';FMAC='02:6A:10:20:30:41';GMAC='02:AA:BB:CC:DD:01'
BM='02:88:10:20:30:01'
WIDE=(80,210,1440,370);NIC_CAM=(95,430,670,172)
EVENTS={}
DIRECTED=set()
DHCP_RECAP={}

def clone(im):
    c=object.__new__(Canvas);c.s=im.width/1600;c.im=im.copy();c.d=ImageDraw.Draw(c.im);return c
def boxtext(c,x,y,w,h,t,co=INK,fi=PAPER,size=24):
    c.rect(x,y,w,h,fi,co,2,8);c.text(x+w/2,y+h/2,t,size,co,'mm')
def smallserver(c,x,y,name,ip,co=GREEN):
    c.rect(x,y,125,80,MINT if co==GREEN else LILAC,co,3)
    for j in range(2):
        c.rect(x+12,y+12+j*30,100,23,PAPER,co,2,3)
        c.ellipse(x+22,y+20+j*30,5,5,co,co,1)
    c.text(x+60,y-33,name,25,co,'mt');c.text(x+60,y+91,ip,21,co,'mt',True)

def screen(c,lines):
    c.rect(144,290,272,112,'#fffefa',BLUE,2,3)
    for j,(t,co) in enumerate(lines):c.text(280,310+j*39,t,23,co,'mt')

def focus(c,lines,co=GOLD,y=245,size=25):
    for j,t in enumerate(lines.split('\n')):c.text(620,y+j*39,t,size,co,'mt')

def computer(c,selected=True,page=False,details=False):
    c.text(285,225,'同一台笔记本 PC-A',29,BLUE,'mt')
    c.rect(130,275,300,145,SKY,BLUE,3)
    c.rect(144,290,272,112,'#fffefa',BLUE,2,3)
    c.line([(125,420),(110,438),(450,438),(435,420)],BLUE,4)
    c.rect(110,438,340,120,'#eeeade',BLUE,3,9)
    c.rect(130,460,125,76,LILAC,PURPLE,3)
    c.rect(285,460,125,76,SKY,MUTED,2)
    c.text(192,476,'无线网卡',21,PURPLE,'mt');c.text(192,506,'B',21,PURPLE,'mt',True)
    c.text(347,476,'有线接口',21,MUTED,'mt');c.text(347,506,'A',21,MUTED,'mt',True)
    c.rect(426,483,24,28,'#293a40',MUTED,2,2)
    if details:
        c.rect(130,460,125,76,LILAC,PURPLE,3)
        c.rect(137,470,52,53,PAPER,PURPLE,2,3);c.text(163,487,'MAC',15,PURPLE,'mt',True);c.text(163,507,'帧处理',12,PURPLE,'mt')
        c.rect(195,470,52,53,CREAM,GOLD,2,3);c.text(221,487,'PHY',15,GOLD,'mt',True);c.text(221,507,'无线收发',12,GOLD,'mt')
        c.text(485,442,'PC-A 的同一块无线网卡 B',15,PURPLE)
        c.text(485,478,'MAC '+FMAC,15,PURPLE,mono=True)
        c.text(485,513,'IP 待 DHCP 获取',15,GOLD)
    if page:
        c.rect(155,318,72,68,CREAM,GOLD,1,3)
        for j,z in enumerate([148,132,142]):c.line([(245,330+j*24),(245+z,330+j*24)],MUTED,4)
    else:c.text(280,340,'浏览器 / 系统程序',23,BLUE,'mm')

def gateway(c):
    c.text(913,245,'家用网关（含 AP）',25,GREEN,'mt')
    c.rect(805,295,220,250,MINT,GREEN,3,14)
    c.rect(825,315,180,72,LILAC,PURPLE,2)
    c.text(915,328,'无线接入点 AP',23,PURPLE,'mt');c.text(915,359,'Home Wi-Fi',21,PURPLE,'mt',True)
    c.rect(825,409,180,68,PAPER,GREEN,2)
    c.text(915,420,'DHCP 服务',23,GREEN,'mt');c.text(915,450,'192.168.1.1',18,GREEN,'mt',True)
    c.line([(850,295),(850,267)],PURPLE,3);c.line([(975,295),(975,267)],PURPLE,3)
    c.text(875,508,'LAN / 网关',18,GREEN,'mt');c.text(970,508,'WAN',18,GREEN,'mt',True)

@lru_cache(maxsize=8)
def world_base(selected=True,page=False,dns=False,web=False):
    c=Canvas(3200,1800);computer(c,selected,page);gateway(c)
    if dns or web:
        c.line([(1010,490),(1125,490)],FAINT,3)
        c.ellipse(1100,398,120,80,'#f0eee5',MUTED,2);c.text(1160,438,'互联网',22,MUTED,'mm')
    if dns:
        c.line([(1190,410),(1240,320),(1335,320)],FAINT,3)
        smallserver(c,1345,285,'DNS 解析器','192.0.2.53',PURPLE)
    if web:
        c.line([(1220,470),(1280,490),(1335,490)],FAINT,3)
        smallserver(c,1345,455,'网站服务器','198.51.100.80',GREEN)
    return c.im

def radio(c,connection=1,showstandard=True,showstatus=True):
    co=PURPLE if connection>.96 else MUTED
    # These arcs indicate an available radio link, never a drawn cable.
    for r in [35,65,95]:c.d.arc(c.box(450-r,365-r,450+r,365+r),320,350,fill=co,width=max(1,round(3*c.s)))
    if showstandard:c.text(600,541,'无线电 · IEEE 802.11',23,co,'mt')
    if showstatus:
        if connection>.96:c.text(600,501,'Wi-Fi 已连接',21,PURPLE,'mt')
        elif connection<=.02:c.text(600,501,'Wi-Fi 未连接',21,RED,'mt')
        else:c.text(600,501,'正在建立无线连接…',21,GOLD,'mt')

def token(c,pts,q,label,co=PURPLE,fi=LILAC,detail=None):
    lengths=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(pts,pts[1:])];d=clamp(q)*sum(lengths);k=0
    while k<len(lengths)-1 and d>lengths[k]:d-=lengths[k];k+=1
    f=d/lengths[k] if lengths[k] else 0;x=mix(pts[k][0],pts[k+1][0],f);y=mix(pts[k][1],pts[k+1][1],f)
    w=max(125,len(label)*14+28);c.rect(x-w/2,y-24,w,48,fi,co,3,6)
    c.line([(x-w/2+6,y-18),(x,y+3),(x+w/2-6,y-18)],co,1)
    c.text(x,y+5,label,22,co,'mm',True)
    if detail:c.text(620,443,detail,23,co,'mt')
    return x,y

SEND=[(280,355),(200,443),(435,420),(435,355),(815,355),(915,443)]
DNSPATH=SEND[:-1]+[(1005,490),(1150,438),(1240,320),(1340,320)]
WEBPATH=SEND[:-1]+[(1005,490),(1150,438),(1280,490),(1340,490)]

def phase_for(i):
    return SHOTS[i]['phase']
def state(i,p):return calm.state(i,p)

def hud(c,i,p):
    sh=SHOTS[i];phase_name=sh['phase']
    if sh['id']=='rarp_bridge' and not state(i,p)['history']:phase_name='ending'
    nav=['01 连接 Wi-Fi','02 DHCP 获取IP','03 ARP 找网关','04 DNS 查域名','05 HTTPS 访问','06 断开与恢复']
    active={'wifi':0,'dhcp':1,'arp':2,'dns':3,'web':4,'disconnect':5,'ending':5}.get(phase_name,-1)
    if phase_name in ['replay','history']:
        label='局部回放：刚才发生的通信，不是重新联网' if phase_name=='replay' else '历史对照：无盘工作站 C，与现代 DHCP 主线分开'
        c.text(80,40,label,26,GOLD if phase_name=='replay' else PURPLE)
    else:
        for j,t in enumerate(nav):
            x=80+j*243;c.text(x,40,t,21,INK if j==active else MUTED)
            if j==active:c.line([(x,75),(x+215,77)],GOLD,5)
    c.text(80,112,sh['title'],39,INK)
    c.text(1520,125,f'{i+1:02d}/{len(SHOTS):02d}',22,MUTED,'rt',True)
    c.line([(80,182),(1520,182)],FAINT,2,False)
    c.line([(80,754),(1520,754)],FAINT,2,False)
    for j,t in enumerate(sh['subtitle'].split('\n')):c.text(800,785+j*43,t,30,INK,'mt')
    c.text(80,873,'同一台笔记本 · Wi-Fi 主线',17,MUTED)
    c.text(1520,873,'Wi-Fi 连接到网页，再看断开与恢复',17,MUTED,'rt')
    s=state(i,p)
    c.rect(80,605,1440,130,'#fffefa',FAINT,2,12)
    if s['history']:
        c.text(105,619,'历史设备 C 的状态（这不是电脑 PC-A）',23,PURPLE)
        c.text(130,672,'已知 MAC：'+BM,27,PURPLE,mono=True)
        c.text(950,672,'自己的 IP：'+('192.0.2.10' if s['ip'] else '?'),27,GREEN if s['ip'] else GOLD)
        return
    status='Wi-Fi 已连接' if s['link'] else 'Wi-Fi 未连接'
    questions={'hook':'今天只跟同一台电脑走一遍','interfaces':'两块接口，各有自己的 MAC','access':'对照两种接入；本片使用无线 B','link':'选择网络，完成无线接入','needip':'首次接入，无有效租约 → 用 DHCP 获取','mac':'DHCP 先使用已有无线 MAC','discover':'DHCP Discover：找谁能给我分配 IP','offer':'DHCP Offer：IP 提议尚未确认','requestack':'DHCP Request / ACK：申请并确认','configuration':'DHCP 确认结果已写入这台电脑','why_dns':'电脑 IP 已有；网站 IP 还要查询','arp':'已有网关 IP，还缺下一跳 MAC','dns':'DNS 将网站主机名解析为地址','web':'目标 IP 已知，进行 HTTPS 访问','replay':'主线暂停：回放刚才的 DNS 查询','frame':'回放无线帧：先交给 AP，再交付载荷','layers':'剖开同一条 DNS Q1 查询','udp':'回看 DNS/UDP 与 HTTPS/TCP 两种传输','unplug':'回到现在：关闭无线接口','effects':'页面可保留；新请求可能等待或失败','replug':'先恢复链路，再检查旧配置','ending':'回到 PC-A：各协议完成不同工作'}
    if sh['id']=='arp' and p*calm.budget('arp')>=max(calm.word('arp','网关回复')+2.6,calm.word('arp','记入邻居缓存')):
        questions['arp']='已记录网关 MAC，可以继续 DNS 查询'
    c.text(105,617,'PC-A | '+status+' | '+questions.get(sh['id'],'局部解释：保持已确认的网络配置'),23,GREEN if s['link'] else RED)
    if sh['id'] in ['dhcp_recap','udp_ports']:

        c.rect(101,612,1410,34,PAPER,PAPER,1,0)
        c.text(105,617,'PC-A | Wi-Fi 已连接 | 局部回看刚才的 DHCP 交换  配置保持有效',23,GREEN)
    if sh['id'] in ['interfaces','access']:
        c.text(110,668,'有线 A：'+WMAC,26,BLUE,mono=True);c.text(825,668,'无线 B：'+FMAC,26,PURPLE,mono=True)
        c.text(110,704,'仅作对照：可内置，也可外接',20,BLUE);c.text(825,704,'后续通过 B 连接 Wi-Fi',20,MUTED)
        return
    fields=[('无线 B 的 MAC',FMAC,PURPLE),('电脑 IP','192.168.1.20' if s['ip'] else '尚未获取',GREEN if s['ip'] else GOLD),('默认网关','192.168.1.1' if s['ip'] else '尚未配置',GREEN if s['ip'] else MUTED),('DNS 解析器','192.0.2.53' if s['ip'] else '尚未配置',PURPLE if s['ip'] else MUTED)]
    for j,(label,value,co) in enumerate(fields):
        x=105+j*355;c.text(x,655,label,20,MUTED);c.text(x,688,value,25,co,mono=all(ord(a)<128 for a in value))
    if sh['id']=='configuration':c.text(470,714,'掩码 255.255.255.0 · 本例租期 3600 秒',17,GREEN)

def camera(c,w,cam):
    # Device world only; headings, subtitles and PC state remain fixed.
    x,y,cw,ch=cam;s=w.s
    src=w.im.crop((round(x*s),round(y*s),round((x+cw)*s),round((y+ch)*s)))
    dest=src.resize((round(1440*c.s),round(370*c.s)),Image.Resampling.LANCZOS)
    c.im.paste(dest,(round(80*c.s),round(210*c.s)));c.d=ImageDraw.Draw(c.im)
def lerpcam(t):return tuple(mix(a,b,t) for a,b in zip(WIDE,NIC_CAM))

def history_world(p,bridge=False):
    c=Canvas(3200,1800)
    c.text(260,242,'历史场景：无盘工作站 C',29,PURPLE,'mt')
    c.rect(130,305,260,155,'#ede4cf',PURPLE,3,7);c.rect(150,325,220,110,PAPER,PURPLE,2,3)
    c.text(260,360,'我的 IP 是多少？',25,PURPLE,'mt');c.line([(245,460),(245,500),(175,500),(330,500)],PURPLE,4)
    c.text(260,530,'已知 MAC：'+BM,20,PURPLE,'mt',True)
    smallserver(c,1090,405,'RARP 服务器','本地链路上的映射服务',GREEN)
    c.rect(880,245,590,130,MINT,GREEN,2,9)
    c.text(910,263,'服务器保存的 MAC → IP 映射',25,GREEN)
    co=GOLD if p>.42 and not bridge else GREEN
    boxtext(c,905,305,540,48,BM+' → 192.0.2.10',co,CREAM if co==GOLD else PAPER,23)
    c.line([(405,420),(1080,450)],FAINT,3)
    c.text(730,545,'独立历史对照：查询设备自己的 IP',24,PURPLE,'mt')
    return c

def world(i,p):return calm.make_world(i,p,globals())

def frame(index,p,width=1920,height=1080):
    p=clamp(p)
    c=Canvas(width,height);hud(c,index,p);w,cam=world(index,p);camera(c,w,cam);return c.im

def stills():
    out=ROOT/'out/stills';out.mkdir(parents=True,exist_ok=True)
    for i,sh in enumerate(SHOTS):frame(i,.88).save(out/f'{i+1:02d}-{sh["id"]}.png')
    sheet=Image.new('RGB',(1280,math.ceil(len(SHOTS)/3)*260),PAPER)
    for i in range(len(SHOTS)):sheet.paste(frame(i,.88,426,240),((i%3)*426,(i//3)*260))
    sheet.save(ROOT/'checks/contact-sheet.png')
    samples=Image.new('RGB',(1280,2160),PAPER)
    for j,i in enumerate([next(k for k,x in enumerate(SHOTS) if x['id']==name) for name in ['interfaces','dhcp_recap','rarp']]):samples.paste(frame(i,.88,1280,720),(0,j*720))
    samples.save(ROOT/'out/style-samples.png');print(f'{len(SHOTS)} stills saved',flush=True)

def audio_mix(timeline,out):
    cues=[q for s in timeline['scenes'] for q in s['cues']];rate=48000
    full=np.zeros(math.ceil(timeline['duration_s']*rate),np.float32)
    for q in cues:
        raw=subprocess.run(['ffmpeg','-v','error','-i',str(ROOT/q['audio']),'-ar',str(rate),'-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
        a=np.frombuffer(raw,dtype='<f4');start=round(q['absolute_start_s']*rate)
        full[start:start+len(a)]+=a
    if np.abs(full).max()>1:raise ValueError('Audio clipping before normalization')
    with wave.open(str(out),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes((full*32767).astype('<i2').tobytes())

def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

def render(mode,timeline_path=None,output_name=None):
    timeline=json.loads((timeline_path or ROOT/'timeline.json').read_text())
    out=ROOT/'out'/(output_name or mode);out.mkdir(parents=True,exist_ok=True)
    fps=24 if mode=='final' else 12;width,height=(1920,1080) if mode=='final' else (960,540)
    mixwav=ROOT/'.local'/f'narration-{output_name or mode}.wav'
    audio_mix(timeline,mixwav)
    silent=out/'picture.mp4'
    segmented=mode=='final'
    if segmented:
        from tools.segments import segment
        picture_files=[]
        proc=None
    else:
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{width}x{height}','-r',str(fps),'-i','-',
        '-an','-c:v','libx264','-preset','veryfast','-crf','19' if mode=='final' else '24','-pix_fmt','yuv420p',str(silent)],stdin=subprocess.PIPE)
    actual=[];srt=[];frame_cursor=0
    for s in timeline['scenes']:
        q=s['cues'][0];start_frame=round(s['start_s']*fps);end_frame=round((s['start_s']+s['duration_s'])*fps)
        i=next(k for k,shot in enumerate(SHOTS) if shot['id']==q['id'])
        still_bytes=frame(i,.87,width,height).tobytes() if mode=='animatic' else None
        if segmented:
            local_scene={k:v for k,v in s.items() if k!='start_s'}
            local_scene['cues']=[{k:v for k,v in q.items() if k!='absolute_start_s'}]
            picture_files.append(segment(local_scene,i,fps,width,height));frame_cursor+=end_frame-start_frame
        else:
            for n in range(start_frame,end_frame):
                t=n/fps;local=t-q['absolute_start_s'];p=clamp(local/max(.1,q['duration_s'],q['action_s']))
                pixels=still_bytes if mode=='animatic' else frame(i,p,width,height).tobytes()
                proc.stdin.write(pixels);frame_cursor+=1
        actual.append(dict(id=q['id'],subtitle=q['subtitle'],start_s=q['absolute_start_s'],duration_s=q['duration_s'],
            audio=q['audio'],audio_sha256=q['audio_sha256'],observation_s=q['slot_s']-q['duration_s'],minimum_observation_s=.85))
        srt.append(f'{i+1}\n{stamp(q["absolute_start_s"])} --> {stamp(q["absolute_start_s"]+q["duration_s"])}\n{q["subtitle"]}\n')
        print(f'{mode}: shot {i+1}/{len(SHOTS)} {q["id"]}',flush=True)
    if segmented:
        listing=ROOT/'.local/concat.txt'
        listing.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in picture_files)+'\n')
        subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(listing),'-c','copy',str(silent)],check=True)
    else:
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('Video encoder failed')
    video=out/'video.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(silent),'-i',str(mixwav),'-map','0:v:0','-map','1:a:0','-c:v','copy',
        '-af','loudnorm=I=-17:TP=-1.5:LRA=11','-c:a','aac','-b:a','192k','-t',str(frame_cursor/fps),'-movflags','+faststart',str(video)],check=True)
    (out/'actual-timeline.json').write_text(json.dumps(dict(project_root='../..',fps=fps,narration=True,cues=actual),ensure_ascii=False,indent=2)+'\n')
    (out/'subtitles.srt').write_text('\n'.join(srt)+'\n')
    silent.unlink()
    print(f'{video}: {frame_cursor/fps:.3f}s',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True)
    for m in ['stills','animatic','draft','final']:g.add_argument('--'+m,action='store_true')
    args=parser.parse_args()
    if args.stills:stills()
    else:render('final' if args.final else 'draft' if args.draft else 'animatic')
