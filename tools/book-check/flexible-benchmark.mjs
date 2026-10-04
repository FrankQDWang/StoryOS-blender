import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import os from 'node:os';
import {BOOK_MATERIALS} from '../../apps/web/src/book-materials.mjs';

const out=process.env.BOOK_CHECK_OUT??'evidence/flexible-book-20261004/performance';await fs.mkdir(out,{recursive:true});
const context=await chromium.launchPersistentContext('.cache/flexible-book/benchmark-chrome',{
 channel:'chrome',headless:true,viewport:{width:1512,height:751},deviceScaleFactor:1,
 args:['--no-first-run','--disable-background-networking'],
});
const page=context.pages()[0],cdp=await context.newCDPSession(page),errors=[];
process.on('uncaughtException',async error=>{await page.screenshot({path:`${out}/benchmark-error.png`});console.error(error,errors,await page.locator('body').innerText());await context.close();process.exit(1)});
page.on('pageerror',e=>errors.push(String(e)));
const fixture={version:1,books:BOOK_MATERIALS.map((m,slot)=>({id:`bench-${slot}`,slot,materialId:m.id,color:m.color,title:['星海余烬','守月人','寄往风中的信','无题手稿·甲','无题手稿·乙'][slot],description:slot===0?'群星熄灭之后，故事才刚刚开始。':'',words:0,updatedAt:'2026-10-03T00:00:00Z'})),lastBookId:'bench-0',reducedMotion:false,sound:false};
await context.addInitScript(fixture=>{
 try{localStorage.setItem('storyos.library.demo.v1',JSON.stringify(fixture))}catch{}
 const sample=window.__bookBench={scenePaints:[],handDraw:null,clickStart:null,workspaceAt:null};
 const contexts=new Set(),shaders=new WeakMap(),programs=new WeakMap(),active=new WeakMap(),litDraws=new WeakMap();
 const proto=WebGL2RenderingContext.prototype;
 const shaderSource=proto.shaderSource,attachShader=proto.attachShader,useProgram=proto.useProgram;
 proto.shaderSource=function(shader,source){shaders.set(shader,{skin:source.includes('#define USE_SKINNING'),lit:source.includes('RE_Direct_Physical')});return shaderSource.call(this,shader,source)};
 proto.attachShader=function(program,shader){const old=programs.get(program)??{},next=shaders.get(shader)??{};programs.set(program,{skin:old.skin||next.skin,lit:old.lit||next.lit});return attachShader.call(this,program,shader)};
 proto.useProgram=function(program){contexts.add(this);active.set(this,program);return useProgram.call(this,program)};
 for(const method of ['drawElements','drawArrays']){
  const original=proto[method];proto[method]=function(...args){const result=original.apply(this,args);const p=programs.get(active.get(this));
   if(p?.lit)litDraws.set(this,(litDraws.get(this)??0)+1);
   if(sample.clickStart!==null&&sample.handDraw===null&&p?.skin&&p?.lit){this.finish();sample.handDraw=performance.now()}
   return result;
  };
 }
 let hasCaption=false;
 new MutationObserver(()=>{
  const caption=!!document.querySelector('.room-caption');
  if(caption&&!hasCaption){
   const painted=()=>{
    const canvas=document.querySelector('.scene canvas');
    const gl=[...contexts].find(gl=>gl.canvas===canvas&&litDraws.get(gl)>0);
    if(!gl){requestAnimationFrame(painted);return}
    requestAnimationFrame(()=>{gl.finish();sample.scenePaints.push(performance.now())});
   };
   requestAnimationFrame(painted);
  }
  hasCaption=caption;
  if(sample.clickStart!==null&&sample.workspaceAt===null&&document.querySelector('.workspace h1'))sample.workspaceAt=performance.now();
 }).observe(document,{childList:true,subtree:true});
 document.addEventListener('click',event=>{
  if(event.target.closest('button')?.textContent.includes('打开这本书')){sample.clickStart=performance.now();sample.handDraw=null;sample.workspaceAt=null}
 },true);
},fixture);
await cdp.send('Network.enable');
const supplement=process.env.BOOK_CHECK_SUPPLEMENT==='1';
const rows=supplement?JSON.parse(await fs.readFile(`${out}/benchmark-raw.json`)).rows:[];
for(const network of (supplement?['20mbps-50ms']:['local','20mbps-50ms'])){
 await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:network==='local'?0:50,downloadThroughput:network==='local'?-1:20_000_000/8,uploadThroughput:network==='local'?-1:10_000_000/8});
 for(let round=supplement?3:0;round<(supplement?5:3);round++)for(const version of (round%2?['candidate','baseline']:['baseline','candidate'])){
  const root=version==='baseline'?'http://127.0.0.1:4180':'http://127.0.0.1:4182';
  await page.goto('about:blank');
  if(!supplement)await cdp.send('Network.clearBrowserCache');
  for(const cache of ['cold','warm']){
   if(supplement&&cache==='cold'){
    await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:0,downloadThroughput:-1,uploadThroughput:-1});
    await page.goto(root);await page.waitForFunction(()=>window.__bookBench?.scenePaints.length>0);
    await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:50,downloadThroughput:20_000_000/8,uploadThroughput:10_000_000/8});
    continue;
   }
   await page.goto(root,{waitUntil:'domcontentloaded'});
   await page.waitForFunction(()=>window.__bookBench?.scenePaints.length>0,{},{timeout:90000});
   const firstPaint=await page.evaluate(()=>window.__bookBench.scenePaints[0]);
   const resources=await page.evaluate(()=>performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,transferSize:r.transferSize,encodedBodySize:r.encodedBodySize})));
   await page.mouse.click(101,376);await page.locator('.focus-card').waitFor();
   await page.waitForTimeout(350);
   await page.getByRole('button',{name:'打开这本书',exact:true}).click();
   await page.locator('.workspace h1').waitFor();
   const opening=await page.evaluate(()=>({...window.__bookBench}));
   if(opening.handDraw===null)throw new Error('No actual lit skinned-hand draw observed');
   const row={network,round,version,cache,firstPaint,firstHand:opening.handDraw-opening.clickStart,workspace:opening.workspaceAt-opening.clickStart,resources};
   rows.push(row);console.log(JSON.stringify({...row,resources:undefined}));
   await fs.writeFile(`${out}/benchmark-raw.json`,JSON.stringify({chrome:context.browser()?.version(),os:os.platform(),arch:os.arch(),viewport:[1512,751],dpr:1,fixture,rows,errors},null,2)+'\n');
  }
 }
}
const median=xs=>xs.sort((a,b)=>a-b)[Math.floor(xs.length/2)];
const comparisons=[];
for(const network of ['local','20mbps-50ms'])for(const cache of ['cold','warm'])for(const metric of ['firstPaint','firstHand','workspace']){
 const value=version=>median(rows.filter(r=>r.network===network&&r.cache===cache&&r.version===version).map(r=>r[metric]));
 const baseline=value('baseline'),candidate=value('candidate');
 comparisons.push({network,cache,metric,samples:rows.filter(r=>r.network===network&&r.cache===cache&&r.version==='baseline').length,baseline,candidate,increasePercent:(candidate/baseline-1)*100,pass:candidate<=baseline*1.1});
}
await fs.writeFile(`${out}/benchmark-summary.json`,JSON.stringify({comparisons,errors,pass:comparisons.every(r=>r.pass)&&!errors.length},null,2)+'\n');
await context.close();
