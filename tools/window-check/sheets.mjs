import sharp from '../book-check/node_modules/sharp/dist/index.mjs';
import fs from 'node:fs/promises';
const out=process.env.WINDOW_OUT??'evidence/moonlit-window/final';
const frames=JSON.parse(await fs.readFile(`${out}/motion-frames.json`));
async function sheet(names,file,w=504,cols=3){const h=Math.round(w*751/1512);const inputs=await Promise.all(names.map(async(n,i)=>({input:await sharp(`${out}/${n}.png`).resize(w,h).png().toBuffer(),left:(i%cols)*w,top:Math.floor(i/cols)*(h+22)})));await sharp({create:{width:w*cols,height:Math.ceil(names.length/cols)*(h+22),channels:3,background:'#252525'}}).composite(inputs).png().toFile(`${out}/${file}.png`)}
await sheet(frames.map(f=>f.name),'motion-sheet');
await sheet(['before','overview'],'before-after',756,2);
