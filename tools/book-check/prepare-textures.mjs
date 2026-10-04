import sharp from 'sharp';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const source='assets/source/manuscript/atlas.png';
const {width,height}=await sharp(source).metadata();
const half=width/2;
const outputs=[
  ['public/assets/textures/manuscript-leather.webp', sharp(source).extract({left:0,top:0,width:half,height}).resize(768,768).grayscale().linear(1.3,75)],
  ['public/assets/textures/manuscript-page.webp', sharp(source).extract({left:half,top:0,width:half,height}).resize(768,768)],
];
for(const [path,pipeline] of outputs)await pipeline.webp({quality:86}).toFile(path);
const paths=[source,'assets/source/manuscript-texture-prompt.txt','design/round-10-five-book-materials/warm-umber.png',...outputs.map(([path])=>path)];
const files=await Promise.all(paths.map(async path=>{const data=await fs.readFile(path);return {path,bytes:data.length,sha256:crypto.createHash('sha256').update(data).digest('hex')}}));
await fs.writeFile('assets/source/manuscript/provenance.json',JSON.stringify({tool:'built-in ImageGen',date:'2026-10-04',referenceRole:'Approved material/style reference; not a baked room photograph',originalOutput:'/Users/frankqdwang/.codex/generated_images/01a10277-6227-7be3-8a41-42c814b07908/exec-04db59dc-37f6-43b3-969b-8fcd6cbb741c.png',processing:'Split two square atlas panels, resize to 768, neutralize leather for shared tinting, WebP quality 86; command: node tools/book-check/prepare-textures.mjs',files},null,2)+'\n');
console.log(files);
