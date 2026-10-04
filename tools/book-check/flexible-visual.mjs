import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import sharp from 'sharp';
const stage=process.argv[2]??'candidate';
const out=process.env.BOOK_EVIDENCE?`${process.env.BOOK_EVIDENCE}/${stage}`:`evidence/flexible-book-20261004/${stage}`;await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-first-run','--disable-background-networking']});
try{
 const page=await browser.newPage({viewport:{width:1512,height:751},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.addInitScript(()=>{const p=WebGL2RenderingContext.prototype,draw=p.drawElements;p.drawElements=function(...args){const result=draw.apply(this,args);window.__draws=(window.__draws??0)+1;return result}});
 const frames=[];
 for(const view of ['opening','hands-side']){
  await page.goto(`http://127.0.0.1:4173/review.html?slot=0&time=0&view=${view}`);
  await page.locator('[data-scene-ready="true"]').waitFor();await page.waitForFunction(()=>window.__draws>20);await page.waitForTimeout(250);
  for(const time of [0,.8,1.25,1.7,2.15,2.5,2.8,3.1,3.45]){
   await page.getByRole('spinbutton',{name:'时间',exact:true}).fill(String(time));await page.waitForTimeout(100);
   const file=`${out}/${view}-${time.toFixed(2)}.jpg`;await page.screenshot({path:file,quality:92});frames.push({file,view,time});
  }
 }
 await page.goto('http://127.0.0.1:4173/review.html?view=overview');await page.locator('[data-scene-ready="true"]').waitFor();await page.waitForFunction(()=>window.__draws>20);await page.waitForTimeout(200);await page.screenshot({path:`${out}/overview.jpg`,quality:92});
 const tiles=[];for(const [i,f] of frames.entries())tiles.push({input:await sharp(f.file).resize(504,250).toBuffer(),left:i%3*504,top:Math.floor(i/3)*250});
 await sharp({create:{width:1512,height:Math.ceil(frames.length/3)*250,channels:3,background:'#111'}}).composite(tiles).jpeg({quality:91}).toFile(`${out}/contact-sheet.jpg`);
 await fs.writeFile(`${out}/result.json`,JSON.stringify({chrome:browser.version(),headless:true,viewport:[1512,751],frames,errors},null,2)+'\n');
 console.log(JSON.stringify({stage,frames:frames.length,errors}));
}finally{await browser.close()}
