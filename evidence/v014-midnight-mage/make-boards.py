"""Unretouched actual Chrome screenshots, resized uniformly with time labels."""
from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import json
p=Path(__file__).resolve().parent
sets=[('five-slots-sheet.jpg',[(f'slot-{s}-{t:.2f}.png',f'Slot {s} | {t:.2f}s') for s in range(1,6) for t in [.8,1.3,1.7,2.15]],4),
      ('side-sheet.jpg',[(f'side-{t:.2f}.png',f'Side | {t:.2f}s') for t in [.8,1.3,1.7,2.15]],2),
      ('comparison-main.jpg',[(f'{v}-{t:.2f}.png',f'{v} | {t:.2f}s') for t in [.8,1.3,1.7,2.15] for v in ['before','after']],2)]
for kind in ['normal','slow','live']:
    data=p/kind/'times.json'
    if data.exists():
        rows=json.loads(data.read_text())
        if kind in ['normal','live'] and len(rows)>12:
            rows=[rows[round(i*(len(rows)-1)/11)] for i in range(12)]
        sets.append((kind+'-sheet.jpg',[(kind+'/'+r['file'],f'{kind} | {r["time"]:.2f}s') for r in rows],4))
for name,files,cols in sets:
    w,h=620,310
    sheet=Image.new('RGB',(w*cols,h*((len(files)+cols-1)//cols)),'#142027')
    for i,(file,label) in enumerate(files):
        im=ImageOps.contain(Image.open(p/file).convert('RGB'),(w,h-24));x=(i%cols)*w;y=(i//cols)*h
        sheet.paste(im,(x,y+24));ImageDraw.Draw(sheet).text((x+10,y+7),label,fill='white')
    sheet.save(p/name,quality=94)
print('Composed unretouched review sheets')
