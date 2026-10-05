import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import os from 'node:os';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,baseline,candidate]=process.argv.slice(2);let url=baseline,version='baseline';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:process.env.HEADED!=='1',args:['--no-first-run','--disable-backgrounding-occluded-windows','--disable-renderer-backgrounding']});
const context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});
await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));
process.on('uncaughtException',async e=>{console.error(e);await browser.close();process.exit(1)});
const page=await context.newPage(),cdp=await context.newCDPSession(page),errors=[],rows=[];
page.on('pageerror',e=>errors.push(String(e)));await cdp.send('Performance.enable');
const metrics=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x=>[x.name,x.value]));
const home=async()=>{await page.goto(url);await page.bringToFront();await page.locator('.room-caption').waitFor();await page.waitForTimeout(2500)};
const sample=async(name,seconds,instrument=false,action)=>{
 await page.evaluate(enabled=>{const p=window.__renderProbe;p.frames=[];p.passes=[];p.gpu=[];p.enabled=enabled;p.disjoint=false;window.__rafFrames=[];window.__rafRun=true;const generation=window.__rafGeneration=(window.__rafGeneration??0)+1;let last=performance.now();function tick(t){if(window.__rafGeneration!==generation)return;window.__rafFrames.push(t-last);last=t;if(window.__rafRun)requestAnimationFrame(tick)}requestAnimationFrame(tick)},instrument);
 const before=await metrics();if(action)await action();await page.waitForTimeout(seconds*1000);const after=await metrics();
 const detail=await page.evaluate(()=>{window.__rafRun=false;const p=window.__renderProbe;p.enabled=false;return {frames:p.frames,passes:p.passes,gpu:p.gpu,disjoint:p.disjoint,raf:window.__rafFrames,renderer:p.renderer,gpuTimer:p.ext}});
 const elapsed=after.Timestamp-before.Timestamp;
 const row={name:`${version}-${name}`,version,scenario:name.split('-')[0],instrument,seconds:elapsed,before,after,cpu:100*(after.ProcessTime-before.ProcessTime)/elapsed,main:100*(after.TaskDuration-before.TaskDuration)/elapsed,...detail};rows.push(row);await fs.writeFile(`${out}/raw.json`,JSON.stringify({rows,errors,browser:browser.version(),platform:os.platform(),arch:os.arch(),viewport:[1512,695],dpr:2},null,2));console.log(version,name,instrument,row.cpu.toFixed(3));
};
for(let round=0;round<4;round++){
 const instrument=round===3;
 for(const v of (round%2?['candidate','baseline']:['baseline','candidate'])){version=v;url=v==='baseline'?baseline:candidate;
 await home();await sample('idle-'+round,instrument?5:12,instrument);
 await page.getByRole('button',{name:'自由漫游',exact:true}).click();await page.keyboard.down('KeyW');await sample('roam-'+round,3,instrument);await page.keyboard.up('KeyW');await page.keyboard.press('Escape');await page.evaluate(()=>document.exitPointerLock());
 await page.waitForTimeout(2500);
 // Pick the first real book through its projected world anchor (click remains UI).
 const pos=await page.evaluate(()=>{const {camera,gl}=window.__renderProbe.state;const r=gl.domElement.getBoundingClientRect();const v=camera.position.clone().set(-3.93,1.25,.883).project(camera);return {x:r.left+(v.x+1)*r.width/2,y:r.top+(1-v.y)*r.height/2}});
 // Baseline screen coordinate follows fixed viewport and known first stand.
 await page.mouse.click(pos.x,pos.y);await page.locator('.focus-card').waitFor({timeout:5000});await page.waitForTimeout(1800);
 await sample('opening-'+round,2.8,instrument,()=>page.getByRole('button',{name:'打开这本书',exact:true}).click());await page.locator('.workspace h1').waitFor();await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();await page.waitForTimeout(2000);
 await page.getByRole('button',{name:/全部作品/}).click();await page.waitForTimeout(500);await sample('list-'+round,5,instrument);await page.getByRole('button',{name:'删除《无题手稿·乙》',exact:true}).click();await page.getByRole('button',{name:'删除这本书',exact:true}).click();await page.getByRole('button',{name:'关闭',exact:true}).click();
 await page.getByRole('button',{name:'新建作品',exact:true}).click();await page.getByRole('textbox',{name:'书名',exact:true}).fill('测试新世界');await sample('creating-'+round,2.8,instrument,()=>page.getByRole('button',{name:'创造这本书',exact:true}).click());await page.waitForTimeout(1000);
}

}
await fs.writeFile(`${out}/errors.json`,JSON.stringify(errors));await browser.close();if(errors.length)throw new Error(errors.join('\n'));
