// Compare actual scene renders, not display RAF frequency. No GPU timer queries.
import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,baseline,candidate]=process.argv.slice(2),rows=[];
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 for(let round=0;round<3;round++)for(const version of round%2?['candidate','baseline']:['baseline','candidate']){
  const context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});
  await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(version==='baseline'?baseline:candidate);await page.locator('.room-caption').waitFor();await page.waitForTimeout(3000);
  const cdp=await context.newCDPSession(page);await cdp.send('Performance.enable');
  const metrics=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(m=>[m.name,m.value]));
  async function sample(name,ms,action){
   await page.evaluate(()=>{
    const p=window.__renderProbe;p.enabled=false;const {gl,scene,clock,camera}=p.state,original=gl.render;
    const data=window.__cadence={renders:[],invalid:0};
    gl.render=function(s,...args){const start=performance.now(),elapsed=clock.elapsedTime,result=original.call(this,s,...args);
     if(s===scene){data.renders.push({start,elapsed,duration:performance.now()-start});if(!camera.position.toArray().every(Number.isFinite))data.invalid++}return result};
    data.stop=()=>{gl.render=original;return {renders:data.renders,invalid:data.invalid}};
   });
   const before=await metrics();const start=Date.now();if(action)await action();await page.waitForTimeout(ms);const after=await metrics();
   const raw=await page.evaluate(()=>window.__cadence.stop()),seconds=after.Timestamp-before.Timestamp;
   const gaps=raw.renders.slice(1).map((r,i)=>r.start-raw.renders[i].start).sort((a,b)=>a-b);
   const row={version,round,name,seconds,actionWaitMs:Date.now()-start,frames:raw.renders.length,fps:raw.renders.length/seconds,cpuPercent:100*(after.ProcessTime-before.ProcessTime)/seconds,cpuMsPerFrame:1000*(after.ProcessTime-before.ProcessTime)/raw.renders.length,maxGap:Math.max(0,...gaps),p95Gap:gaps[Math.floor(gaps.length*.95)]??0,maxRender:Math.max(0,...raw.renders.map(r=>r.duration)),backwardClock:raw.renders.some((r,i)=>i&&r.elapsed<raw.renders[i-1].elapsed),invalid:raw.invalid,errors:[...errors]};
   rows.push(row);await fs.writeFile(`${out}/${version}-${round}-${name}.json`,JSON.stringify(raw));await fs.writeFile(`${out}/summary.json`,JSON.stringify({browser:browser.version(),viewport:[1512,695],dpr:2,rows},null,2));console.log(row);
  }
  await sample('idle',6000);
  await page.getByRole('button',{name:'自由漫游',exact:true}).click();await page.keyboard.down('KeyW');await sample('roam',2000);await page.keyboard.up('KeyW');await page.keyboard.press('Escape');await page.waitForTimeout(2000);
  const pos=await page.evaluate(()=>{const {camera,gl}=window.__renderProbe.state,r=gl.domElement.getBoundingClientRect(),v=camera.position.clone().set(-3.93,1.25,.883).project(camera);return {x:(v.x+1)*r.width/2,y:(1-v.y)*r.height/2}});
  await page.mouse.click(pos.x,pos.y);await page.locator('.focus-card').waitFor();await page.waitForTimeout(1800);
  const openStart=Date.now();await sample('opening',0,async()=>{await page.getByRole('button',{name:'打开这本书',exact:true}).click();await page.locator('.workspace h1').waitFor()});rows.at(-1).transitionMs=Date.now()-openStart;
  await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();await page.waitForTimeout(2000);
  await page.getByRole('button',{name:/全部作品/}).click();await page.waitForTimeout(500);await sample('list',2000);
  await page.getByRole('button',{name:'删除《无题手稿·乙》',exact:true}).click();await page.getByRole('button',{name:'删除这本书',exact:true}).click();await page.getByRole('button',{name:'关闭',exact:true}).click();
  await page.getByRole('button',{name:'新建作品',exact:true}).click();await page.getByRole('textbox',{name:'书名',exact:true}).fill('帧率复核');
  await sample('creating',3500,()=>page.getByRole('button',{name:'创造这本书',exact:true}).click());await sample('resumed',3000);
  await context.close();
 }
}finally{const version=browser.version();await browser.close();await fs.writeFile(`${out}/summary.json`,JSON.stringify({browser:version,viewport:[1512,695],dpr:2,rows},null,2))}
// elapsedTime may reset when the baseline switches demand -> always. Retain
// backwardClock as a diagnostic; it does not itself establish a negative dt.
if(rows.some(r=>r.errors.length||r.invalid))process.exitCode=1;
