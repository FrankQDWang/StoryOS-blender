"""Compose unretouched Chrome captures into labeled visual-review contact sheets."""
from PIL import Image, ImageDraw, ImageOps
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]/'evidence/v014-free-hands'
for kind,targets in [('normal',[.4,.8,1.15,1.55,1.9,2.2,2.6,3,3.5]),('slow',None)]:
 rows=json.loads((root/f'{kind}-frames.json').read_text())
 if targets:rows=[min(rows,key=lambda x:abs(x['time']-t)) for t in targets]
 columns=3 if kind=='normal' else 4;w,h=(500,275) if kind=='normal' else (400,295)
 sheet=Image.new('RGB',(columns*w,((len(rows)+columns-1)//columns)*h),'#172126')
 for i,row in enumerate(rows):
  im=Image.open(root/row['file']).convert('RGB')
  if kind=='slow':im=ImageOps.contain(im.crop((430,310,1050,min(730,im.height))),(400,271))
  else:im=ImageOps.contain(im,(500,248))
  x=(i%columns)*w;y=(i//columns)*h;sheet.paste(im,(x,y+24));ImageDraw.Draw(sheet).text((x+12,y+7),f"{kind} | t ~= {row['time']:.2f}s",fill='white')
 sheet.save(root/('02-normal-sequence.jpg' if kind=='normal' else '04-slow-contact-review.jpg'),quality=93)
