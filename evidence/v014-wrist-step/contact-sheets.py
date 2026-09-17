"""Arrange unretouched Chrome screenshots for this one-point comparison."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import json
root=Path(__file__).resolve().parent
def sheet(name,rows,columns,width,height,crop=None):
 out=Image.new('RGB',(columns*width,((len(rows)+columns-1)//columns)*height),'#172126')
 draw=ImageDraw.Draw(out)
 for i,(file,label) in enumerate(rows):
  im=Image.open(root/file).convert('RGB')
  if crop:im=im.crop(crop)
  im=ImageOps.contain(im,(width,height-28))
  x=i%columns*width;y=i//columns*height
  out.paste(im,(x+(width-im.width)//2,y+28));draw.text((x+10,y+8),label,fill='white')
 out.save(root/name,quality=94)
sheet('comparison-wrist.jpg',[('before-1.70.png','Before | 1.70 s'),('after-1.70.png','After | 1.70 s')],2,640,565,(430,300,940,695))
sheet('comparison-four-poses.jpg',[(f'{kind}-{t:.2f}.png',f'{kind} | {t:.2f}s') for t in [.8,1.3,1.7,2.15] for kind in ['before','after']],2,550,415,(410,270,1000,695))
sheet('five-slots.jpg',[(f'slot-{slot}-{t:.2f}.png',f'Slot {slot} | {t:.2f}s') for slot in range(1,6) for t in [1.7,2.15]],2,550,415,(410,270,1000,695))
for kind,targets in [('normal',[.2,.5,.8,1.1,1.4,1.7,2,2.3,2.6,2.9,3.2,3.5]),('slow',[i*.7 for i in range(21)]),('live',[.2,.5,.8,1.1,1.4,1.7,2,2.3,2.6,2.9,3.2,3.5])]:
 index=root/f'{kind}-index.json'
 if not index.exists():continue
 frames=json.loads(index.read_text());selected=[min(frames,key=lambda r:abs(r['elapsedMs']/1000-t)) for t in targets]
 sheet(f'{kind}-contact-sheet.jpg',[(r['file'],f"{kind} | wall ~{r['elapsedMs']/1000:.2f}s") for r in selected],3,470,365,(380,220,1050,695))
