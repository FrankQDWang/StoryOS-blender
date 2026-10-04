import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import os from 'node:os';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';

const out=process.env.BOOK_CHECK_OUT??'evidence/moonlit-window/performance';await fs.mkdir(out,{recursive:true});
const context=await chromium.launchPersistentContext('.cache/moonlit-window/benchmark-chrome',{
 channel:'chrome',headless:true,viewport:{width:1512,height:751},deviceScaleFactor:1,
 args:['--no-first-run','--disable-background-networking'],
});
const page=context.pages()[0],cdp=await context.newCDPSession(page),errors=[];
process.on('uncaughtException',async error=>{await page.screenshot({path:`${out}/benchmark-error.png`});console.error(error,errors,await page.locator('body').innerText());await context.close();process.exit(1)});
page.on('pageerror',e=>errors.push(String(e)));
const fixture=fiveBookPreview(initialLibrary());
await context.addInitScript(fixture=>{
 try{localStorage.setItem('storyos.library.demo.v1',JSON.stringify(fixture))}catch{}
 const sample=window.__bookBench={scenePaints:[],handDraw:null,clickStart:null,workspaceAt:null};
 const contexts=new Set(),shaders=new WeakMap(),programs=new WeakMap(),active=new WeakMap(),litDraws=new WeakMap(),skyDraws=new WeakMap();
 const proto=WebGL2RenderingContext.prototype;
 const shaderSource=proto.shaderSource,attachShader=proto.attachShader,useProgram=proto.useProgram;
 proto.shaderSource=function(shader,source){shaders.set(shader,{skin:source.includes('#define USE_SKINNING'),lit:source.includes('RE_Direct_Physical'),sky:source.includes('STORYOS_WINDOW_SKY')||source.includes('vNightAltitude')});return shaderSource.call(this,shader,source)};
 proto.attachShader=function(program,shader){const old=programs.get(program)??{},next=shaders.get(shader)??{};programs.set(program,{skin:old.skin||next.skin,lit:old.lit||next.lit,sky:old.sky||next.sky});return attachShader.call(this,program,shader)};
 proto.useProgram=function(program){contexts.add(this);active.set(this,program);return useProgram.call(this,program)};
 for(const method of ['drawElements','drawArrays']){
  const original=proto[method];proto[method]=function(...args){const result=original.apply(this,args);const p=programs.get(active.get(this));
   if(p?.sky)skyDraws.set(this,1);
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
    const gl=[...contexts].find(gl=>gl.canvas===canvas&&litDraws.get(gl)>0&&skyDraws.get(gl)>0);
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
const extendNetwork=process.env.BOOK_CHECK_EXTEND_NETWORK;
const onlyNetwork=process.env.BOOK_CHECK_NETWORK;
const rows=supplement||extendNetwork||process.env.BOOK_CHECK_APPEND==='1'?JSON.parse(await fs.readFile(`${out}/benchmark-raw.json`)).rows:[];
for(const network of (extendNetwork?[extendNetwork]:supplement?['20mbps-50ms']:onlyNetwork?[onlyNetwork]:['local','20mbps-50ms'])){
 await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:network==='local'?0:50,downloadThroughput:network==='local'?-1:20_000_000/8,uploadThroughput:network==='local'?-1:10_000_000/8});
 const rounds=network==='local'?Number(process.env.BOOK_CHECK_LOCAL_ROUNDS??3):3;
 for(let round=supplement||extendNetwork?3:0;round<(supplement||extendNetwork?5:rounds);round++)for(const version of (round%2?['candidate','current','baseline']:['baseline','current','candidate'])){
  const root=version==='baseline'?'http://127.0.0.1:4183':version==='current'?'http://127.0.0.1:4180':'http://127.0.0.1:4182';
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
   const resources=await page.evaluate(()=>performance.getEntriesByType('resource').map(r=>({name:new URL(r.name).pathname,transferSize:r.transferSize,encodedBodySize:r.encodedBodySize,startTime:r.startTime,duration:r.duration,responseEnd:r.responseEnd})));
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
for(const network of ['local','20mbps-50ms'])for(const cache of ['cold','warm'])for(const metric of ['firstPaint','firstHand','workspace'])for(const against of ['baseline','current']){
 const value=version=>median(rows.filter(r=>r.network===network&&r.cache===cache&&r.version===version).map(r=>r[metric]));
 const baseline=value(against),candidate=value('candidate');
 comparisons.push({against,network,cache,metric,samples:rows.filter(r=>r.network===network&&r.cache===cache&&r.version==='baseline').length,baseline,candidate,increasePercent:(candidate/baseline-1)*100,pass:candidate<=baseline*1.1});
}
await fs.writeFile(`${out}/benchmark-summary.json`,JSON.stringify({comparisons,errors,pass:comparisons.every(r=>r.pass)&&!errors.length},null,2)+'\n');
await context.close();
