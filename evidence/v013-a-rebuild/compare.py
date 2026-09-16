from PIL import Image,ImageDraw
from pathlib import Path
import sys
root=Path(__file__).resolve().parents[2]
current=sys.argv[1] if len(sys.argv)>1 else '11-global-light.jpg'
a=Image.open(root/'design/round-05/A-hearth-study/final.png').convert('RGB')
b=Image.open(root/'evidence/v013-a-rebuild'/current).convert('RGB')
assert a.size==b.size==(1849,851),(a.size,b.size)
canvas=Image.new('RGB',(1849*2,891),'#181818');draw=ImageDraw.Draw(canvas)
draw.text((16,13),'SELECTED A - concept',(230,230,230));draw.text((1865,13),'CHROME - actual 3D',(230,230,230));canvas.paste(a,(0,40));canvas.paste(b,(1849,40));canvas.save(root/'evidence/v013-a-rebuild/comparison-full.jpg',quality=95)
regions=[('HEARTH',(40,230,650,730)),('CENTRE',(695,400,1125,775)),('DESK / RIGHT',(1010,235,1830,785))]
rows=[]
for title,box in regions:
 pair=[]
 for im in [a,b]:
  crop=im.crop(box);crop.thumbnail((820,550));pair.append(crop)
 h=max(p.height for p in pair)+40
 row=Image.new('RGB',(1640,h),'#181818');d=ImageDraw.Draw(row);d.text((10,10),title+' / SELECTED A',(230,230,230));d.text((830,10),title+' / CHROME',(230,230,230))
 for i,p in enumerate(pair):row.paste(p,(i*820,40))
 rows.append(row)
canvas=Image.new('RGB',(1640,sum(r.height for r in rows)),'#181818');y=0
for r in rows:canvas.paste(r,(0,y));y+=r.height
canvas.save(root/'evidence/v013-a-rebuild/comparison-details.jpg',quality=95)
