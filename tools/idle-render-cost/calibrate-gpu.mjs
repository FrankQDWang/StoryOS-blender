import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,url]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true}),context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));const page=await context.newPage();await page.goto(url);await page.locator('.room-caption').waitFor();await page.waitForTimeout(2500);
const result=await page.evaluate(async()=>{
 const p=window.__renderProbe,{gl,scene,camera,setFrameloop,advance,clock}=p.state,ctx=gl.getContext(),ext=ctx.getExtension('EXT_disjoint_timer_query_webgl2');setFrameloop('never');await new Promise(r=>setTimeout(r,100));const rows=[];
 async function measure(label,fn){ctx.finish();const q=ctx.createQuery();ctx.beginQuery(ext.TIME_ELAPSED_EXT,q);const start=performance.now();fn();ctx.endQuery(ext.TIME_ELAPSED_EXT);ctx.flush();ctx.finish();const wall=performance.now()-start;await new Promise(r=>setTimeout(r,25));const ms=ctx.getQueryParameter(q,ctx.QUERY_RESULT)/1e6;rows.push({label,ms,wall,disjoint:ctx.getParameter(ext.GPU_DISJOINT_EXT)});ctx.deleteQuery(q)}
 for(let i=0;i<5;i++){await measure('empty',()=>{});await measure('frame',()=>advance(clock.elapsedTime+1/60,true));await measure('clear',()=>gl.clear());}
 return {rows,renderer:p.renderer};
});await fs.writeFile(`${out}/calibration.json`,JSON.stringify(result,null,2));console.log(result);await browser.close();
