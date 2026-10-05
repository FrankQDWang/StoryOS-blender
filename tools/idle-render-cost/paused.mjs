import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,baseline,candidate]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:process.env.HEADED!=='1',args:['--disable-backgrounding-occluded-windows','--disable-renderer-backgrounding']}),context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));const page=await context.newPage(),cdp=await context.newCDPSession(page),rows=[];await cdp.send('Performance.enable');const metrics=async()=>Object.fromEntries((await cdp.send('Performance.getMetrics')).metrics.map(x=>[x.name,x.value]));
for(let round=0;round<3;round++)for(const version of round%2?['candidate','baseline']:['baseline','candidate']){
 await page.goto(version==='baseline'?baseline:candidate);await page.bringToFront();await page.locator('.room-caption').waitFor();await page.waitForTimeout(2000);await page.getByRole('button',{name:/全部作品/}).click();await page.waitForTimeout(2000);
 await page.evaluate(()=>{const {gl,scene}=window.__renderProbe.state;const render=gl.render;window.__pausedRenders=0;gl.render=function(s,...args){if(s===scene)window.__pausedRenders++;return render.call(this,s,...args)}});
 const before=await metrics();await page.waitForTimeout(7000);const after=await metrics();const sceneRenders=await page.evaluate(()=>window.__pausedRenders);const seconds=after.Timestamp-before.Timestamp;const row={round,version,seconds,cpu:100*(after.ProcessTime-before.ProcessTime)/seconds,sceneRenders,before,after};rows.push(row);console.log(row.version,round,row.cpu,sceneRenders);await fs.writeFile(`${out}/raw.json`,JSON.stringify({method:'No measurement RAF while paused; CDP endpoint deltas only. Count actual scene.render calls without scheduling frames.',rows},null,2));
}
await browser.close();
