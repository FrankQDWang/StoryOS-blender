import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import sharp from 'sharp';
const out=process.env.BOOK_CHECK_OUT??'evidence/flexible-book-20261004/final';
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1512,height:751},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 for(const [label,query] of [['book-1-closed','slot=0&time=0'],['overview','view=overview']]){
  await page.goto(`http://127.0.0.1:4173/review.html?${query}`);
  await page.locator('[data-scene-ready="true"]').waitFor();await page.waitForTimeout(300);
  await page.screenshot({path:`${out}/${label}.jpg`,quality:92});
 }
 await fs.writeFile(`${out}/handoff-captures.json`,JSON.stringify({headless:true,errors,firstClosed:'Recaptured after actual scene-ready; original capture was too early.'},null,2));
}finally{await browser.close()}
const tiles=[];
for(let i=0;i<5;i++)for(const [row,label] of ['closed','open'].entries())tiles.push({input:await sharp(`${out}/book-${i+1}-${label}.jpg`).resize(605,300).toBuffer(),left:i%3*605,top:(Math.floor(i/3)*2+row)*300});
await sharp({create:{width:1815,height:1200,channels:3,background:'#111'}}).composite(tiles).jpeg({quality:91}).toFile(`${out}/five-books.jpg`);
const frames=JSON.parse(await fs.readFile(`${out}/normal/frames.json`));
const playlist=frames.map((f,i)=>`file '${f.file.split('/').at(-1)}'\nduration ${i<frames.length-1?(frames[i+1].elapsed-f.elapsed)/1000:1}`).join('\n')+`\nfile '${frames.at(-1).file.split('/').at(-1)}'\n`;
await fs.writeFile(`${out}/normal/frames.ffconcat`,playlist);
console.log('Corrected closed view and overview captured; five-book sheet and timestamp playlist ready.');
