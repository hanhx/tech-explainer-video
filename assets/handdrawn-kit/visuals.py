"""Deterministic handdrawn network explainer. No external assets or network access.

Logical canvas: 1600x900. Draw at delivery resolution, keeping text sharp.
Usage: python scene.py --stills | --animatic | --draft | --final
"""
from pathlib import Path
from functools import lru_cache
import argparse, hashlib, json, math, os, subprocess, wave
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT=Path(__file__).resolve().parent
PAPER='#fcf8ed'; INK='#263a40'; MUTED='#627476'; BLUE='#276eab'; GREEN='#347563'
GOLD='#b97522'; PURPLE='#785b99'; RED='#b94f46'; FAINT='#dcded4'
SKY='#e1edf5'; MINT='#e1eee2'; CREAM='#f9e7bd'; LILAC='#ede4f5'
FONT=os.environ.get('EXPLAINER_FONT','/System/Library/Fonts/Hiragino Sans GB.ttc')
MONO=os.environ.get('EXPLAINER_MONO_FONT','/System/Library/Fonts/Menlo.ttc')

def clamp(x):return min(1,max(0,x))
def ease(x):x=clamp(x);return x*x*(3-2*x)
def phase(p,a,b):return ease((p-a)/(b-a))
def mix(a,b,p):return a+(b-a)*p

@lru_cache(maxsize=200)
def font(size,mono=False):return ImageFont.truetype(MONO if mono else FONT,size)

@lru_cache(maxsize=1400)
def text_tile(t,size,color,anchor,mono):
    f=font(size,mono)
    scratch=Image.new('RGBA',(1,1));d=ImageDraw.Draw(scratch)
    b=d.textbbox((0,0),t,font=f,anchor=anchor)
    tile=Image.new('RGBA',(max(1,b[2]-b[0]),max(1,b[3]-b[1])))
    ImageDraw.Draw(tile).text((-b[0],-b[1]),t,font=f,fill=color,anchor=anchor)
    return tile,b

class Canvas:
    def __init__(self,width=1920,height=1080):
        self.s=width/1600;self.im=Image.new('RGB',(width,height),PAPER);self.d=ImageDraw.Draw(self.im)
        # Subtle notebook dots do not move between frames.
        for x in range(40,1600,32):
            for y in range(30,900,32):
                self.d.ellipse(self.box(x,y,x+1.1,y+1.1),fill='#e9e5d9')
    def box(self,*v):return tuple(round(a*self.s) for a in v)
    def text(self,x,y,t,size=28,color=INK,anchor='lt',mono=False):
        f=font(round(size*self.s),mono and all(ord(ch)<128 for ch in t))
        if '\n' in t:
            for i,line in enumerate(t.split('\n')):self.text(x,y+i*(size+10),line,size,color,anchor,mono)
            return
        tile,b=text_tile(t,round(size*self.s),color,anchor,mono and all(ord(ch)<128 for ch in t))
        self.im.paste(tile,(round(x*self.s)+b[0],round(y*self.s)+b[1]),tile)
    def line(self,pts,color=INK,width=3,rough=True):
        points=[(round(x*self.s),round(y*self.s)) for x,y in pts]
        self.d.line(points,fill=color,width=max(1,round(width*self.s)),joint='curve')
        if rough:
            # A stable second pen trace. No per-frame random jitter.
            ghost=[(round((x+1.3*math.sin(i*2.7+x*.02))*self.s),round((y+.9*math.cos(y*.017+i))*self.s)) for i,(x,y) in enumerate(pts)]
            self.d.line(ghost,fill=color,width=max(1,round(self.s)))
    def rect(self,x,y,w,h,fill=None,color=INK,width=2,r=15):
        self.d.rounded_rectangle(self.box(x,y,x+w,y+h),round(r*self.s),fill=fill,outline=color,width=max(1,round(width*self.s)))
        if color:
            self.line([(x+12,y-1),(x+w*.55,y+.8),(x+w-12,y-1)],color,1)
    def ellipse(self,x,y,w,h,fill=None,color=INK,width=2):
        self.d.ellipse(self.box(x,y,x+w,y+h),fill=fill,outline=color,width=max(1,round(width*self.s)))
    def arrow(self,a,b,color=INK,width=3,progress=1,label=None):
        if progress<=0:return
        end=(mix(a[0],b[0],progress),mix(a[1],b[1],progress));self.line([a,end],color,width)
        theta=math.atan2(end[1]-a[1],end[0]-a[0]);z=13
        self.line([(end[0]-z*math.cos(theta-.45),end[1]-z*math.sin(theta-.45)),end,
                   (end[0]-z*math.cos(theta+.45),end[1]-z*math.sin(theta+.45))],color,width)
        if label and progress>.95:self.text((a[0]+b[0])/2,(a[1]+b[1])/2-30,label,23,color,'mt')
    def note(self,x,y,t,color=GOLD,size=25):
        self.text(x,y,t,size,color)
        w=max(self.d.textlength(s,font=font(round(size*self.s))) for s in t.split('\n'))/self.s
        self.line([(x,y+size+8),(x+w*.5,y+size+12),(x+w,y+size+7)],color,3)
    def chip(self,x,y,t,color=BLUE,fill=SKY,w=None,size=25):
        w=w or self.d.textlength(t,font=font(round(size*self.s)))/self.s+32
        self.rect(x,y,w,46,fill,color,2,9);self.text(x+w/2,y+23,t,size,color,'mm')

def laptop(c,x,y,s=1,label='你的电脑'):
    c.rect(x,y,180*s,110*s,SKY,BLUE,3,8)
    c.rect(x+12*s,y+12*s,156*s,82*s,PAPER,BLUE,2,3)
    c.line([(x-12*s,y+122*s),(x+192*s,y+122*s),(x+180*s,y+110*s),(x,y+110*s),(x-12*s,y+122*s)],BLUE,3)
    c.text(x+90*s,y+142*s,label,27,BLUE,'mt')
    c.line([(x+40*s,y+40*s),(x+138*s,y+40*s)],BLUE,2)
    c.line([(x+40*s,y+60*s),(x+110*s,y+60*s)],BLUE,2)

def router(c,x,y,s=1,label='路由器',color=INK):
    c.rect(x,y+28*s,150*s,64*s,'#eeeade',color,3,12)
    c.line([(x+22*s,y+28*s),(x+14*s,y-18*s)],color,3)
    c.line([(x+128*s,y+28*s),(x+136*s,y-18*s)],color,3)
    for i in range(4):c.ellipse(x+(30+i*24)*s,y+51*s,7*s,7*s,MINT,GREEN,1)
    c.text(x+75*s,y+115*s,label,27,color,'mt')

def server(c,x,y,s=1,label='服务器'):
    c.rect(x,y,130*s,170*s,MINT,GREEN,3,9)
    for i in range(3):
        c.rect(x+12*s,y+(16+i*47)*s,106*s,34*s,PAPER,GREEN,2,5)
        c.ellipse(x+24*s,y+(29+i*47)*s,6*s,6*s,GREEN,GREEN,1)
        c.line([(x+46*s,y+(33+i*47)*s),(x+96*s,y+(33+i*47)*s)],GREEN,2)
    c.text(x+65*s,y+190*s,label,27,GREEN,'mt')

def cloud(c,x,y,w=210,h=110,label='互联网'):
    c.ellipse(x,y,w,h,'#f0eee5',MUTED,2)
    c.text(x+w/2,y+h/2,label,30,MUTED,'mm')

def lock(c,x,y,s=1,color=GOLD):
    c.d.arc(c.box(x+7*s,y-19*s,x+31*s,y+13*s),180,360,fill=color,width=round(3*c.s))
    c.rect(x,y,38*s,29*s,CREAM,color,2,5)
    c.ellipse(x+17*s,y+8*s,4*s,8*s,color,color,1)

def packet(c,x,y,label='SYN',kind='syn',s=1):
    co,fi=(PURPLE,LILAC) if kind=='dns' else (GOLD,CREAM) if kind=='tls' else (BLUE,SKY)
    w=100*s;h=48*s
    c.rect(x-w/2,y-h/2,w,h,fi,co,3,8)
    c.text(x,y,label,22*s,co,'mm',mono=True)
    if kind=='tls':lock(c,x+w/2-7*s,y-31*s,.55*s,co)

def moving(c,points,p,label='SYN',kind='syn'):
    p=clamp(p)
    lengths=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(points,points[1:])]
    distance=p*sum(lengths);k=0
    while k<len(lengths)-1 and distance>lengths[k]:distance-=lengths[k];k+=1
    f=distance/lengths[k] if lengths[k] else 0
    x=mix(points[k][0],points[k+1][0],f);y=mix(points[k][1],points[k+1][1],f)
    packet(c,x,y,label,kind)

def path(c,pts,color=MUTED,width=3):
    for a,b in zip(pts,pts[1:]):c.arrow(a,b,color,width)


# Topic-independent primitives taken from the approved film.
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

def at(pts,q0):
    ls=[math.hypot(b[0]-a[0],b[1]-a[1]) for a,b in zip(pts,pts[1:])];d=clamp(q0)*sum(ls);k=0
    while k<len(ls)-1 and d>ls[k]:d-=ls[k];k+=1
    f=d/ls[k] if ls[k] else 0;return mix(pts[k][0],pts[k+1][0],f),mix(pts[k][1],pts[k+1][1],f)

def packet(c,pts,t,a,b,label,co=PURPLE):
    if t<a or t>b+.35:return
    f=q(t,a,b);x,y=at(pts,f);fade=min(1,(t-a)/.22,max(0,(b+.35-t)/.35));w=max(88,min(230,len(label)*12+28))
    fi=blend(PAPER,LILAC if co==PURPLE else SKY if co==BLUE else MINT if co==GREEN else CREAM,.85*fade)
    c.rect(x-w/2,y-19,w,38,fi,blend(PAPER,co,fade),2,9);c.text(x,y,label,21,blend(PAPER,co,fade),'mm',True)
