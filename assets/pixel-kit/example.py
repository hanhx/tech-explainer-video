"""Run: python example.py --font PROJECT/fonts/font.ttf --out preview.png"""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw
from pixel_ui import PixelUI
ap=argparse.ArgumentParser();ap.add_argument('--font',required=True);ap.add_argument('--out',required=True);a=ap.parse_args()
p=dict(ink='#26374A',paper='#FFFBEA',shade='#91A5A3');ui=PixelUI(a.font,p)
im=Image.new('RGB',(240,135),'#E9F3F1');d=ImageDraw.Draw(im)
ui.panel(d,(8,8,231,36),p['paper'],'#5779A4');ui.text(d,(16,16),'像素组件 / PIXEL KIT')
for i in range(4):ui.block(d,(18+i*54,53,65+i*54,78),'#5779A4',str(i),True)
ui.panel(d,(8,94,231,126),p['paper'],'#5779A4');ui.text(d,(16,104),'字体按 12px 的整倍数使用')
# Non-design font sizes are rejected rather than silently degrading glyphs.
try:ui.font(13)
except ValueError:pass
else:raise AssertionError('non-design size accepted')
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True);im.resize((960,540),Image.Resampling.NEAREST).save(out)
