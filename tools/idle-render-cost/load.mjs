import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,base='http://127.0.0.1:4192',candidate=base]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true});const context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});
await context.addInitScript(f=>{
 localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f));
 window.__load={};const shaders=new WeakMap(),programs=new WeakMap(),active=new WeakMap(),proto=WebGL2RenderingContext.prototype;
 const source=proto.shaderSource,attach=proto.attachShader,use=proto.useProgram;
 proto.shaderSource=function(shader,s){shaders.set(shader,s.includes('#define USE_SKINNING'));return source.call(this,shader,s)};
 proto.attachShader=function(p,s){programs.set(p,programs.get(p)||shaders.get(s));return attach.call(this,p,s)};
 proto.useProgram=function(p){active.set(this,p);return use.call(this,p)};
 for(const k of ['drawElements','drawArrays']){const original=proto[k];proto[k]=function(...args){const result=original.apply(this,args);if(window.__load.click&&!window.__load.hand&&programs.get(active.get(this))){this.finish();window.__load.hand=performance.now()}return result}}
 document.addEventListener('click',e=>{if(e.target.closest('button')?.textContent.includes('打开这本书'))window.__load.click=performance.now()},true);
},fiveBookPreview(initialLibrary()));
const page=await context.newPage(),cdp=await context.newCDPSession(page),rows=[];await cdp.send('Network.enable');
for(let round=0;round<3;round++)for(const version of round%2?['candidate','baseline']:['baseline','candidate']){
 await cdp.send('Network.clearBrowserCache');
 for(const cache of ['cold','warm']){
  await page.goto(version==='baseline'?base:candidate,{waitUntil:'domcontentloaded'});await page.locator('.room-caption').waitFor();
  const firstPaint=await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>{window.__renderProbe.state.gl.getContext().finish();resolve(performance.now())}))));
  const pos=await page.evaluate(()=>{const {camera,gl}=window.__renderProbe.state,r=gl.domElement.getBoundingClientRect(),v=camera.position.clone().set(-3.93,1.25,.883).project(camera);return {x:(v.x+1)*r.width/2,y:(1-v.y)*r.height/2}});
  await page.mouse.click(pos.x,pos.y);await page.locator('.focus-card').waitFor();await page.waitForTimeout(350);await page.getByRole('button',{name:'打开这本书',exact:true}).click();await page.waitForFunction(()=>window.__load.hand);const timing=await page.evaluate(()=>window.__load);await page.locator('.workspace h1').waitFor();
  const row={round,version,cache,firstPaint,firstHand:timing.hand-timing.click};rows.push(row);console.log(row);await fs.writeFile(`${out}/raw.json`,JSON.stringify({rows},null,2));
 }
}
await browser.close();
