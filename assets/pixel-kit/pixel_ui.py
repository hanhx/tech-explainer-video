"""Small native-pixel primitives; supply a licensed font and project palette."""
from PIL import ImageFont
class PixelUI:
 def __init__(self,font_path,colors,base_px=12):
  self.font_path=str(font_path);self.colors=colors;self.base_px=base_px;self.fonts={}
 def font(self,size=None):
  size=size or self.base_px
  if size<=0 or size%self.base_px:raise ValueError('Use integer multiples of the font design size')
  if size not in self.fonts:self.fonts[size]=ImageFont.truetype(self.font_path,size)
  return self.fonts[size]
 def text(self,d,xy,s,color=None,size=None,anchor='la',shadow=False):
  d.fontmode='1';x,y=map(round,xy);f=self.font(size)
  if shadow:d.text((x+1,y+1),s,font=f,fill=self.colors['ink'],anchor=anchor)
  d.text((x,y),s,font=f,fill=color or self.colors['ink'],anchor=anchor)
 def panel(self,d,box,fill,edge):
  x,y,r,b=map(round,box);p=self.colors
  d.rectangle((x,y,r,b),fill=p['ink']);d.rectangle((x+1,y+1,r-1,b-1),fill=edge);d.rectangle((x+3,y+3,r-3,b-3),fill=fill)
  d.line([(x+3,b-3),(r-3,b-3),(r-3,y+3)],fill=p['shade'],width=1)
 def block(self,d,box,fill,label='',lit=False):
  x,y,r,b=map(round,box);p=self.colors;d.rectangle((x,y,r,b),fill=p['ink']);d.rectangle((x+1,y+1,r-1,b-1),fill=fill)
  d.line([(x+1,y+1),(r-1,y+1)],fill=p['paper']);d.line([(x+1,b-2),(r-1,b-2)],fill=p['shade'],width=2)
  if label:self.text(d,((x+r)/2,(y+b)/2),label,p['paper'] if lit else p['ink'],anchor='mm')
 def sprite(self,d,rows,xy,colors,scale=1):
  x,y=map(round,xy)
  for j,row in enumerate(rows):
   for i,ch in enumerate(row):
    if ch in colors:d.rectangle((x+i*scale,y+j*scale,x+(i+1)*scale-1,y+(j+1)*scale-1),fill=colors[ch])
