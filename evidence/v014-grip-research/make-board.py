"""Arrange real reference frames and untouched Chrome captures; no retouching."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
r=Path(__file__).resolve().parent
font='/System/Library/Fonts/STHeiti Medium.ttc'
f=ImageFont.truetype(font,20);small=ImageFont.truetype(font,16);title=ImageFont.truetype(font,27)
out=Image.new('RGB',(1320,900),'#172126');d=ImageDraw.Draw(out)
d.text((24,18),'开书动作：真人参考与当前实现',font=title,fill='white')
d.text((24,58),'比较抓取方式和接触变化；视角、书尺寸与时间不同，不是修改前后对照。',font=small,fill='#c3cccb')
rows=[
 [(r/'reference-5-grip-0.90.png','真人 0.90s｜从外侧夹入',(300,150,1370,1080)),(r/'reference-5-lift-1.42.png','真人 1.42s｜手指转到内页侧',(300,60,1320,1080)),(r/'reference-5-release-1.75.png','真人 1.75s｜转为扶页',(280,120,1310,1080))],
 [(r.parent/'v014-grip-step/before-0.80.png','当前 0.80s｜从底角探入',(430,290,960,695)),(r.parent/'v014-grip-step/before-1.70.png','当前 1.70s｜仍维持张开的钩形',(430,290,960,695)),(r.parent/'v014-grip-step/before-2.15.png','当前 2.15s｜离开后手形仍僵硬',(430,290,960,695))]
]
for j,row in enumerate(rows):
 y=96+j*374
 for i,(p,label,crop) in enumerate(row):
  x=16+i*440
  d.text((x,y),label,font=f,fill='#efcb8e' if j==0 else '#b5d3d0')
  im=Image.open(p).convert('RGB').crop(crop);im=ImageOps.contain(im,(424,328))
  out.paste(im,(x+(424-im.width)//2,y+34+(328-im.height)//2))
d.text((24,856),'真人：Luis Quintero / Pexels 4203478；当前：Chrome，0.1.4-preview.3。仅裁切、等比缩放、加标签。',font=small,fill='#c3cccb')
out.save(r/'reference-vs-current.jpg',quality=95)
