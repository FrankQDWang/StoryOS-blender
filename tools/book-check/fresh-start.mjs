import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import {randomUUID} from 'node:crypto';
const {fixture}=JSON.parse(await fs.readFile('evidence/five-books-20261003/benchmark-raw.json'));
const rows=[];
for(let round=0;round<3;round++)for(const version of round%2?['candidate','baseline']:['baseline','candidate']){
 const context=await chromium.launchPersistentContext(`.cache/five-books/fresh-${randomUUID()}`,{channel:'chrome',headless:true,viewport:{width:1512,height:751},deviceScaleFactor:1});
 await context.addInitScript(fixture=>{
  localStorage.setItem('storyos.library.demo.v1',JSON.stringify(fixture));
  let gl,scheduled=false;const getContext=HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext=function(type,...args){const result=getContext.call(this,type,...args);if(type==='webgl2')gl=result;return result};
  new MutationObserver(()=>{if(!scheduled&&document.querySelector('.room-caption')){scheduled=true;requestAnimationFrame(()=>requestAnimationFrame(()=>{gl.finish();window.__freshPaint=performance.now()}))}}).observe(document,{childList:true,subtree:true});
 },fixture);
 const page=context.pages()[0];await page.goto(`http://127.0.0.1:${version==='baseline'?4180:4182}`);
 await page.waitForFunction(()=>window.__freshPaint>0);
 const firstPaint=await page.evaluate(()=>window.__freshPaint);rows.push({round,version,firstPaint});console.log(rows.at(-1));
 await context.close();
}
const median=version=>rows.filter(r=>r.version===version).map(r=>r.firstPaint).sort((a,b)=>a-b)[1];
const baseline=median('baseline'),candidate=median('candidate');
await fs.writeFile('evidence/five-books-20261003/fresh-browser-start.json',JSON.stringify({scope:'New Chrome process and empty project-local profile for every sample; local network, identical five-book fixture and production builds',rows,baseline,candidate,increasePercent:(candidate/baseline-1)*100,pass:candidate<=baseline*1.1},null,2)+'\n');
