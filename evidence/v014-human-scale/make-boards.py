from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Medium.ttc',20)
small=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',15)
crop=(435,230,1120,695)
board=Image.new('RGB',(1370,2*(465+38)), '#172125');draw=ImageDraw.Draw(board)
for row,t in enumerate((.8,1.7)):
 for col,label in enumerate(('修改前','本次修改')):
  source=ROOT/'evidence/v014-grip-step'/f'before-{t:.2f}.png' if not col else HERE/f'after-{t:.2f}.png'
  im=Image.open(source).crop(crop);x=col*685;y=row*503
  draw.text((x+12,y+9),f'{label} · {t:.2f} 秒',font=font,fill='#f4eadc');board.paste(im,(x,y+38))
board.save(HERE/'comparison-grip-and-scale.jpg',quality=94)
for name in ('normal','slow','actual'):
 folder=HERE/name
 if not (folder/'times.json').exists():continue
 records=json.loads((folder/'times.json').read_text());count=min(12,len(records));duration=min(records[-1]['elapsedMs'],14000 if name=='slow' else 3400)
 chosen=[min(records,key=lambda r:abs(r['elapsedMs']-i*duration/(count-1))) for i in range(count)]
 sheet=Image.new('RGB',(1260,4*278),'#172125');d=ImageDraw.Draw(sheet)
 for i,item in enumerate(chosen):
  im=Image.open(folder/f"{item['frame']:03d}.png");im=im.crop((425,200,1145,695)) if name!='actual' else im;im.thumbnail((420,250));x=(i%3)*420;y=(i//3)*278
  sheet.paste(im,(x,y+27));d.text((x+10,y+5),f"{name} · 捕获经过 {item['elapsedMs']/1000:.2f} s",font=small,fill='white')
 sheet.save(HERE/f'{name}-sheet.jpg',quality=90)

sheet=Image.new('RGB',(1600,5*280),'#172125');d=ImageDraw.Draw(sheet)
for row in range(5):
 for col,t in enumerate((.8,1.3,1.7,2.15)):
  im=Image.open(HERE/f'slot-{row+1}-{t:.2f}.png').crop((430,215,1140,695));im.thumbnail((400,250));x=col*400;y=row*280
  sheet.paste(im,(x,y+28));d.text((x+10,y+5),f'书位 {row+1} · {t:.2f} s',font=small,fill='white')
sheet.save(HERE/'five-slots.jpg',quality=94)
