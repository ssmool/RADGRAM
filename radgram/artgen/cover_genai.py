from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap, random

def generate_cover(title, artist='RADGRAM Artist', prompt='', annex='', out='exports/cover.png'):
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    img=Image.new('RGB',(1400,1400),(10,14,28)); draw=ImageDraw.Draw(img)
    for i in range(80):
        x=random.randint(0,1400); y=random.randint(0,1400); r=random.randint(20,180)
        draw.ellipse((x-r,y-r,x+r,y+r), outline=(30+i%80,60,120+i%100), width=2)
    draw.rectangle((90,90,1310,1310), outline=(180,180,255), width=5)
    draw.text((140,180), title.upper(), fill=(235,235,255))
    draw.text((140,250), f'by {artist}', fill=(200,210,240))
    body='GEN-AI cover seed: '+(prompt or annex or 'web references and musical annex')
    draw.text((140,980), '\n'.join(textwrap.wrap(body,42)), fill=(220,220,230))
    img.save(out); return out
