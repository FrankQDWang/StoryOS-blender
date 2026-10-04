import fs from 'node:fs/promises';
import sharp from '../book-check/node_modules/sharp/dist/index.mjs';
const dir=`${process.env.WINDOW_OUT??'evidence/moonlit-window/final'}/video-frames`;
const files=(await fs.readdir(dir)).filter(n=>n.endsWith('.png')).sort();
for(let start=0;start<files.length;start+=24){const batch=files.slice(start,start+24);const w=504,h=250;const layers=await Promise.all(batch.map(async(f,i)=>({input:await sharp(`${dir}/${f}`).resize(w,h).png().toBuffer(),left:i%3*w,top:Math.floor(i/3)*(h+24)})));await sharp({create:{width:w*3,height:Math.ceil(batch.length/3)*(h+24),channels:3,background:'#222'}}).composite(layers).png().toFile(`${dir}/../video-sheet-${start/24}.png`)}
