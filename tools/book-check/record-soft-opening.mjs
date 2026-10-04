process.env.PLAYWRIGHT_BROWSERS_PATH??='.cache/book-check-browsers';
const {chromium}=await import('playwright');
import fs from 'node:fs/promises';
const out='evidence/book-mechanics-20261004/final';
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-first-run','--disable-background-networking']});
try{
 const context=await browser.newContext({viewport:{width:1512,height:751},deviceScaleFactor:1,recordVideo:{dir:`${out}/recording`,size:{width:1512,height:752}}});
 const started=Date.now(),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.addInitScript(()=>{const p=WebGL2RenderingContext.prototype,draw=p.drawElements;p.drawElements=function(...args){const value=draw.apply(this,args);window.__drawnCanvas=this.canvas;return value;}});
 await page.goto('http://127.0.0.1:4173/review.html?slot=0&time=0&view=hands-side');
 await page.locator('[data-scene-ready="true"]').waitFor();
 await page.waitForFunction(()=>window.__drawnCanvas===document.querySelector('.scene canvas'));
 await page.waitForTimeout(500);
 const replayAt=(Date.now()-started)/1000;
 await page.getByRole('button',{name:'重播',exact:true}).click();
 await page.waitForTimeout(4500);
 const finalTime=Number(await page.getByRole('spinbutton',{name:'时间',exact:true}).inputValue());
 const video=page.video();await context.close();await video.saveAs(`${out}/recording/raw.webm`);
 await fs.writeFile(`${out}/recording/metadata.json`,JSON.stringify({chrome:browser.version(),headless:true,viewport:[1512,751],replayAt,finalTime,errors,source:'Chrome video capture at normal playback speed; not assembled from still screenshots'},null,2)+'\n');
 console.log(JSON.stringify({replayAt,finalTime,errors}));
}finally{await browser.close()}
