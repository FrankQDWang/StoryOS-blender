import sharp from '../book-check/node_modules/sharp/dist/index.mjs';
import fs from 'node:fs/promises';
const folder=process.argv[2];const names=(await fs.readdir(folder)).filter(n=>n.endsWith('.png')&&!n.includes('sheet')&&!n.includes('diff'));
const cols=3,w=504,h=232;const input=await Promise.all(names.map(async(n,i)=>({input:await sharp(`${folder}/${n}`).resize(w,h).png().toBuffer(),left:i%cols*w,top:Math.floor(i/cols)*(h+26)})));
const labels=Buffer.from(`<svg width="${w*cols}" height="${Math.ceil(names.length/cols)*(h+26)}">${names.map((n,i)=>`<text x="${i%cols*w+8}" y="${Math.floor(i/cols)*(h+26)+h+18}" fill="white" font-size="14">${n}</text>`).join('')}</svg>`);
await sharp({create:{width:w*cols,height:Math.ceil(names.length/cols)*(h+26),channels:3,background:'#222'}}).composite([...input,{input:labels,left:0,top:0}]).png().toFile(`${folder}/sheet.png`);
