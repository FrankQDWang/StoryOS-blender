import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const out=process.argv[2]??'evidence/idle-render-cost/baseline-a',url=process.argv[3]??'http://127.0.0.1:4190';
await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-first-run']});
const context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});
await context.addInitScript(()=>{let seed=123456789;Math.random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296}});
const cases=[{name:'overview',frames:180},{name:'window',view:'window',frames:180},{name:'book',view:'book',frames:180},{name:'shadow',view:'shadow',frames:180},{name:'opening-early',opening:true,time:.7,frames:42},{name:'hands',opening:true,time:1.7,frames:102},{name:'opening-late',opening:true,time:2.8,frames:168},{name:'forming',crafting:true,frames:45},{name:'flying',crafting:true,frames:130},{name:'created',frames:210},{name:'deleted',deleted:true,frames:180}];
const errors=[];
for(const spec of cases){
 const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(url+'/tools/idle-render-cost/deterministic.html');
 await page.waitForFunction(()=>window.__caseReady&&window.__renderProbe);
 await page.evaluate(spec=>window.renderCase(spec),spec);
 await page.waitForFunction(()=>window.__caseReady&&window.__renderProbe);
 await page.evaluate(()=>document.fonts.ready);
 await page.waitForTimeout(500);
 await page.evaluate(n=>window.__renderProbe.step(n),spec.frames);
 await page.screenshot({path:`${out}/${spec.name}.png`});
 if(spec.name==='overview')await fs.writeFile(`${out}/inventory.json`,JSON.stringify(await page.evaluate(()=>({renderer:window.__renderProbe.renderer,gpuTimer:window.__renderProbe.ext,...window.__renderProbe.inventory()})),null,2));
 await page.close();console.log(spec.name);
}
await fs.writeFile(`${out}/capture.json`,JSON.stringify({cases,errors,browser:browser.version(),viewport:[1512,695],dpr:2},null,2));await browser.close();
if(errors.length)throw new Error(errors.join('\n'));
