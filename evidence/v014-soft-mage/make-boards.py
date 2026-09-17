from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',20)
small=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',16)
W,H=756,348

def tile(path):
 im=Image.open(path).convert('RGB');im.thumbnail((W,H));return im

def compare():
 times=['0.80','1.30','1.70','2.15']
 canvas=Image.new('RGB',(W*2,48+(H+28)*len(times)),(21,27,32));d=ImageDraw.Draw(canvas)
 d.text((14,12),'Before: preview.5',font=font,fill='white');d.text((W+14,12),'After: preview.6',font=font,fill='white')
 for row,t in enumerate(times):
  for col,p in enumerate([ROOT/'evidence/v014-midnight-mage'/f'after-{t}.png',OUT/f'after-{t}.png']):
   y=48+row*(H+28);d.text((col*W+14,y+3),t+' s',font=small,fill='#D5CBA9');canvas.paste(tile(p),(col*W,y+28))
 canvas.save(OUT/'comparison-four-poses.jpg',quality=91)

def sheet(group):
 paths=sorted((OUT/group).glob('*.png'));count=min(18,len(paths));indices=[round(i*(len(paths)-1)/max(1,count-1)) for i in range(count)]
 cols=3;w,h=504,232;rows=(len(indices)+cols-1)//cols
 canvas=Image.new('RGB',(cols*w,rows*(h+24)),(21,27,32));d=ImageDraw.Draw(canvas)
 data=json.loads((OUT/group/'times.json').read_text())
 for n,i in enumerate(indices):
  im=Image.open(paths[i]).convert('RGB');im.thumbnail((w,h));x=n%cols*w;y=n//cols*(h+24)
  tm=data[i]['time'] if isinstance(data[i],dict) else data[i]
  d.text((x+8,y+3),f'{group} {tm:.2f}s',font=small,fill='white');canvas.paste(im,(x,y+24))
 canvas.save(OUT/(group+'-contact-sheet.jpg'),quality=90)

def slots():
 times=['0.80','1.30','1.70','2.15'];w,h=378,174
 canvas=Image.new('RGB',(w*4,5*(h+26)),(21,27,32));d=ImageDraw.Draw(canvas)
 for row in range(5):
  for col,t in enumerate(times):
   im=Image.open(OUT/'slots'/f'{row+1}-{t}.png').convert('RGB');im.thumbnail((w,h));x,y=col*w,row*(h+26)
   d.text((x+8,y+3),f'Slot {row+1} / {t}s',font=small,fill='white');canvas.paste(im,(x,y+26))
 canvas.save(OUT/'five-slots.jpg',quality=93)
if (OUT/'after-0.80.png').exists():compare()
for group in ['normal','slow','live']:
 if (OUT/group/'times.json').exists():sheet(group)
if (OUT/'slots/5-2.15.png').exists():slots()
