import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,url]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true}),context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));const page=await context.newPage();
for(const flow of ['idle','roam','opening','creating','list']){
 const dir=`${out}/${flow}`;await fs.mkdir(dir,{recursive:true});await page.goto(url);await page.locator('.room-caption').waitFor();await page.waitForTimeout(2500);
 if(flow==='opening'){const pos=await page.evaluate(()=>{const {camera,gl}=window.__renderProbe.state,r=gl.domElement.getBoundingClientRect(),v=camera.position.clone().set(-3.93,1.25,.883).project(camera);return {x:(v.x+1)*r.width/2,y:(1-v.y)*r.height/2}});await page.mouse.click(pos.x,pos.y);await page.locator('.focus-card').waitFor();await page.waitForTimeout(1800)}
 if(flow==='creating'){await page.getByRole('button',{name:/全部作品/}).click();await page.getByRole('button',{name:'删除《无题手稿·乙》',exact:true}).click();await page.getByRole('button',{name:'删除这本书',exact:true}).click();await page.getByRole('button',{name:'关闭',exact:true}).click();await page.getByRole('button',{name:'新建作品',exact:true}).click();await page.getByRole('textbox',{name:'书名',exact:true}).fill('计数新世界')}
 if(flow==='list'){await page.getByRole('button',{name:/全部作品/}).click();await page.waitForTimeout(1000)}

await page.evaluate(()=>{const {gl,scene}=window.__renderProbe.state;const render=gl.render,shadow=gl.shadowMap.render;let shadowCalls=0,shadowCPU=0;window.__passes=[];
 gl.shadowMap.render=function(...args){const start=gl.info.render.calls,t=performance.now();const result=shadow.apply(this,args);shadowCalls=gl.info.render.calls-start;shadowCPU=performance.now()-t;return result};
 gl.render=function(s,c,...args){const start=gl.info.render.calls,t=performance.now();shadowCalls=shadowCPU=0;const result=render.call(this,s,c,...args);window.__passes.push({kind:s===scene?'main':'post',calls:gl.info.render.calls-start-shadowCalls,shadowCalls,cpu:performance.now()-t-shadowCPU,shadowCPU});return result};});
 if(flow==='opening')await page.getByRole('button',{name:'打开这本书',exact:true}).click();
 if(flow==='creating')await page.getByRole('button',{name:'创造这本书',exact:true}).click();
 if(flow==='roam'){await page.getByRole('button',{name:'自由漫游',exact:true}).click();await page.keyboard.down('KeyW')}
 await page.waitForTimeout(flow==='opening'||flow==='creating'?2600:3500);await page.keyboard.up('KeyW');const data=await page.evaluate(()=>window.__passes);await fs.writeFile(`${dir}/passes.json`,JSON.stringify(data));const frames=data.filter(p=>p.kind==='main').length;const result={frames,mainCalls:data.filter(p=>p.kind==='main').reduce((s,p)=>s+p.calls,0)/frames,shadowCalls:data.reduce((s,p)=>s+p.shadowCalls,0)/frames,postCalls:data.filter(p=>p.kind==='post').reduce((s,p)=>s+p.calls,0)/frames,mainCPU:data.filter(p=>p.kind==='main').reduce((s,p)=>s+p.cpu,0)/frames,shadowCPU:data.reduce((s,p)=>s+p.shadowCPU,0)/frames,postCPU:data.filter(p=>p.kind==='post').reduce((s,p)=>s+p.cpu,0)/frames};await fs.writeFile(`${dir}/summary.json`,JSON.stringify(result,null,2));console.log(flow,result);await page.evaluate(()=>document.exitPointerLock());
}
await browser.close();
