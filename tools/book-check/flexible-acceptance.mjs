import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import sharp from 'sharp';
import assert from 'node:assert/strict';
const out=process.env.BOOK_EVIDENCE?`${process.env.BOOK_EVIDENCE}/final`:'evidence/flexible-book-20261004/final';await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-first-run','--disable-background-networking']});
try{
 const context=await browser.newContext({viewport:{width:1512,height:751},deviceScaleFactor:1});
 const page=await context.newPage(),errors=[],captures=[],steps=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.addInitScript(()=>{const p=WebGL2RenderingContext.prototype,draw=p.drawElements;p.drawElements=function(...args){const result=draw.apply(this,args);window.__draws=(window.__draws??0)+1;window.__lastDrawnCanvas=this.canvas;return result}});
 const ready=async()=>{if(page.url().includes('review.html'))await page.locator('[data-scene-ready="true"]').waitFor();await page.waitForFunction(()=>window.__lastDrawnCanvas===document.querySelector('.scene canvas'));await page.waitForTimeout(180)};
 const shot=async(name,metadata={})=>{const file=`${out}/${name}.jpg`;await page.screenshot({path:file,quality:91});captures.push({file,...metadata})};
 if(!process.argv.includes('--smoke-only')){
 for(let slot=0;slot<5;slot++){
  await page.goto(`http://127.0.0.1:4173/review.html?slot=${slot}&time=0`);await ready();await shot(`book-${slot+1}-closed`,{slot,time:0});
  await page.getByRole('spinbutton',{name:'时间',exact:true}).fill('3.45');await page.waitForTimeout(120);await shot(`book-${slot+1}-open`,{slot,time:3.45});
  if([0,2,4].includes(slot)){
   await page.getByRole('spinbutton',{name:'时间',exact:true}).fill('1.7');await page.waitForTimeout(120);await shot(`book-${slot+1}-contact`,{slot,time:1.7});
  }
 }
 for(const speed of [1,.25]){
  await page.goto('http://127.0.0.1:4173/review.html?slot=0&time=0&view=hands-side');await ready();
  await page.getByRole('combobox',{name:'速度',exact:true}).selectOption(String(speed));await page.getByRole('button',{name:'重播',exact:true}).click();
  const start=Date.now(),frames=[];const folder=`${out}/${speed===1?'normal':'slow'}`;await fs.mkdir(folder,{recursive:true});
  while(true){
   const time=Number(await page.getByRole('spinbutton',{name:'时间',exact:true}).inputValue());
   const file=`${folder}/${String(frames.length).padStart(3,'0')}.jpg`;await page.screenshot({path:file,quality:86});frames.push({file,time,elapsed:Date.now()-start});
   if(time>=3.5)break;await page.waitForTimeout(speed===1?65:110);
  }
  const stride=speed===1?2:5,chosen=frames.filter((_,i)=>i%stride===0),tiles=[];
  for(const [i,f] of chosen.entries())tiles.push({input:await sharp(f.file).resize(504,250).toBuffer(),left:i%3*504,top:Math.floor(i/3)*250});
  await sharp({create:{width:1512,height:Math.ceil(chosen.length/3)*250,channels:3,background:'#111'}}).composite(tiles).jpeg({quality:89}).toFile(`${folder}/sheet.jpg`);
  await fs.writeFile(`${folder}/frames.json`,JSON.stringify(frames,null,2));steps.push(`${speed===1?'normal':'quarter-speed'} playback: ${frames.length} actual frames`);
 }
 await fs.writeFile(`${out}/visual.json`,JSON.stringify({chrome:browser.version(),headless:true,captures,steps,errors},null,2)+'\n');
 }
 await page.goto('http://127.0.0.1:4173/');await page.locator('.room-caption').waitFor();await ready();
 await page.getByRole('button',{name:'新建作品',exact:true}).click();await page.getByRole('textbox',{name:'书名',exact:true}).fill('软皮本验收');
 await page.getByRole('button',{name:'创造这本书',exact:true}).click();await page.locator('.cinema-caption').waitFor({state:'hidden'});await page.waitForTimeout(250);
 const state=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('storyos.library.demo.v1')));
 assert.equal((await state()).books[0].materialId,'warm-umber');await shot('created');steps.push('fresh empty library, create first soft book');
 await page.mouse.click(101,376);await page.locator('.focus-card').waitFor();await page.waitForTimeout(600);
 await page.getByRole('button',{name:'打开这本书',exact:true}).click();await page.locator('.workspace h1').waitFor();assert.equal(await page.locator('.workspace h1').innerText(),'软皮本验收');
 await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();await ready();steps.push('actual book opens and returns');
 await page.getByRole('button',{name:'减少动态效果',exact:true}).click();await ready();await page.mouse.click(101,376);await page.locator('.focus-card').waitFor();await page.getByRole('button',{name:'打开这本书',exact:true}).click();await page.locator('.workspace h1').waitFor();
 await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();steps.push('reduced-motion entry and return');
 await page.getByRole('button',{name:/全部作品/}).click();await page.getByRole('button',{name:'删除《软皮本验收》',exact:true}).click();await page.getByRole('button',{name:'删除这本书',exact:true}).click();await page.getByRole('button',{name:'关闭',exact:true}).click();await page.reload();await page.locator('.room-caption').waitFor();assert.equal((await state()).books.length,0);steps.push('delete removes geometry; refresh remains empty');
 assert.deepEqual(errors,[]);await fs.writeFile(`${out}/acceptance.json`,JSON.stringify({chrome:browser.version(),headless:true,captures,steps,errors},null,2)+'\n');console.log(JSON.stringify({steps,errors}));
}finally{await browser.close()}
