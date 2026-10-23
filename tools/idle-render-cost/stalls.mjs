// Production interaction probe: no GPU queries, isolated data, real Chrome input.
import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,url,candidate]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:process.env.HEADED!=='1'});
const results=[];
try{
 for(let round=0;round<Number(process.env.ROUNDS??3);round++){
 for(const version of (candidate?(round%2?['candidate','baseline']:['baseline','candidate']):['candidate'])){
 const context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});
 await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(candidate&&version==='candidate'?candidate:url);await page.locator('.room-caption').waitFor();await page.waitForTimeout(2500);
 for(const flow of ['opening','creating']){
 if(flow==='opening'){
 const pos=await page.evaluate(()=>{const {camera,gl}=window.__renderProbe.state,r=gl.domElement.getBoundingClientRect(),v=camera.position.clone().set(-3.93,1.25,.883).project(camera);return {x:(v.x+1)*r.width/2,y:(1-v.y)*r.height/2}});
 await page.mouse.click(pos.x,pos.y);await page.locator('.focus-card').waitFor();await page.mouse.move(1500,680);await page.waitForTimeout(2000);
 }else{
 await page.getByRole('button',{name:/全部作品/}).click();await page.getByRole('button',{name:'删除《无题手稿·乙》',exact:true}).click();await page.getByRole('button',{name:'删除这本书',exact:true}).click();await page.getByRole('button',{name:'关闭',exact:true}).click();
 await page.getByRole('button',{name:'新建作品',exact:true}).click();await page.getByRole('textbox',{name:'书名',exact:true}).fill('验证新世界');
 }
 await page.evaluate(()=>{
 const {gl,scene}=window.__renderProbe.state,original=gl.render;const data=window.__stalls={renders:[],frames:[],longtasks:[],started:performance.now()};
 let last;const tick=t=>{if(last)data.frames.push(t-last);last=t;data.raf=requestAnimationFrame(tick)};data.raf=requestAnimationFrame(tick);
 const observer=new PerformanceObserver(list=>data.longtasks.push(...list.getEntries().map(e=>({start:e.startTime,duration:e.duration}))));observer.observe({type:'longtask'});
 gl.render=function(s,...args){const start=performance.now();const result=original.call(this,s,...args);data.renders.push({start,duration:performance.now()-start,kind:s===scene?'main':'post'});return result};
 data.stop=()=>{gl.render=original;observer.disconnect();cancelAnimationFrame(data.raf)};
 });
 const cdp=await context.newCDPSession(page);if(process.env.PROFILE==='1'){await cdp.send('Profiler.enable');await cdp.send('Profiler.start')}
 await page.getByRole('button',{name:flow==='opening'?'打开这本书':'创造这本书',exact:true}).click();
 await page.waitForTimeout(4000);
 if(process.env.PROFILE==='1'){const {profile}=await cdp.send('Profiler.stop');await fs.writeFile(`${out}/${version}-${round}-${flow}-profile.json`,JSON.stringify(profile))}
 const raw=await page.evaluate(()=>{window.__stalls.stop();const {renders,frames,longtasks,started}=window.__stalls;return {renders,frames,longtasks,started}});
 const row={version,round,flow,maxFrame:Math.max(...raw.frames),maxRender:Math.max(...raw.renders.map(r=>r.duration)),longtasks:raw.longtasks,errors};results.push(row);console.log(row);
 await fs.writeFile(`${out}/${version}-${round}-${flow}.json`,JSON.stringify(raw));await page.screenshot({path:`${out}/${version}-${round}-${flow}.png`});
 if(flow==='opening'){await page.locator('.workspace h1').waitFor();await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();await page.waitForTimeout(2000)}
 await cdp.detach();
 }
 await context.close();
 }
 }
}finally{await browser.close();await fs.writeFile(`${out}/summary.json`,JSON.stringify(results,null,2))}
if(results.some(r=>(!candidate||r.version==='candidate')&&(r.maxFrame>50||r.errors.length)))process.exitCode=1;
