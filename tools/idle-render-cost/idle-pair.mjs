import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,baseline,candidate]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});const context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});
await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));
const page=await context.newPage(),cdp=await context.newCDPSession(page),rows=[],errors=[];page.on('pageerror',e=>errors.push(String(e)));await cdp.send('Performance.enable');
const get=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(m=>[m.name,m.value]));
for(let round=0;round<3;round++)for(const version of round%2?['candidate','baseline']:['baseline','candidate']){
 await page.goto(version==='baseline'?baseline:candidate);await page.locator('.room-caption').waitFor();await page.waitForTimeout(3000);
 for(const instrument of [false,true]){
  await page.evaluate(enabled=>{const p=window.__renderProbe;p.enabled=enabled;p.frames=[];p.passes=[];p.gpu=[];p.disjoint=false;window.__rafFrames=[];window.__rafRun=true;let last=performance.now();function tick(t){window.__rafFrames.push(t-last);last=t;if(window.__rafRun)requestAnimationFrame(tick)}requestAnimationFrame(tick)},instrument);
  const a=await get();await page.waitForTimeout(instrument?5000:15000);const b=await get();
  const detail=await page.evaluate(()=>{const p=window.__renderProbe;p.enabled=false;window.__rafRun=false;return {frames:p.frames,passes:p.passes,gpu:p.gpu,disjoint:p.disjoint,gpuTimer:p.ext,renderer:p.renderer,raf:window.__rafFrames}});
  const row={name:`${version}-${round}`,round,version,instrument,before:a,after:b,cpu:100*(b.ProcessTime-a.ProcessTime)/(b.Timestamp-a.Timestamp),main:100*(b.TaskDuration-a.TaskDuration)/(b.Timestamp-a.Timestamp),...detail};rows.push(row);console.log(row.name,instrument,row.cpu.toFixed(3));await fs.writeFile(`${out}/raw.json`,JSON.stringify({rows,errors},null,2));
 }
}
await browser.close();
