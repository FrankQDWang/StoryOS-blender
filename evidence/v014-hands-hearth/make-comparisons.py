from PIL import Image, ImageDraw
from pathlib import Path
HERE=Path(__file__).resolve().parent

def pair(a,b,name,labels):
    images=[Image.open(a).convert('RGB'),Image.open(b).convert('RGB')]
    output=Image.new('RGB',(sum(i.width for i in images),max(i.height for i in images)+38),'#192027')
    draw=ImageDraw.Draw(output);x=0
    for im,label in zip(images,labels):
        output.paste(im,(x,38));draw.text((x+16,12),label,fill='white');x+=im.width
    output.save(HERE/name,quality=94)

pair(HERE/'baseline-fire-side.png',HERE/'14-fire-side.png','comparison-fire.jpg',[
    'APPROVED BASELINE / matching camera','REFINEMENT / volumetric flow, charred wood, softened light'])
pair(HERE/'baseline-hands-turn.png',HERE/'08-hands-turn.png','comparison-hands.jpg',[
    'APPROVED BASELINE / 1.30 seconds / matching camera','REFINEMENT / 1.30 seconds / new authored timing'])
if (HERE/'19-overview-final.png').exists():
    pair(HERE.parent/'design-discussion-20260917/01-overview.png',HERE/'19-overview-final.png','comparison-overview.jpg',[
        'APPROVED BASELINE / Chrome 1512 x 751','REFINEMENT / Chrome 1512 x 751'])
