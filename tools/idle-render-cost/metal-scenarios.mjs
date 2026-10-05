import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import path from 'node:path';
import {spawn,execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,url]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:true}),context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));const page=await context.newPage(),cdp=await browser.newBrowserCDPSession();
for(const scene of (process.env.SCENES??'idle,roam,opening,creating,list').split(',')){
 const dir=`${out}/${scene}`;await fs.mkdir(dir,{recursive:true});const trace=path.resolve('.cache/idle-render-cost/native-traces',out.replaceAll('/','_'),scene+'.trace');await fs.mkdir(path.dirname(trace),{recursive:true});await fs.writeFile(`${dir}/trace-path.json`,JSON.stringify({trace},null,2));await page.goto(url);await page.locator('.room-caption').waitFor();await page.waitForTimeout(2500);
 if(scene==='opening'){
  const pos=await page.evaluate(()=>{const {camera,gl}=window.__renderProbe.state,r=gl.domElement.getBoundingClientRect(),v=camera.position.clone().set(-3.93,1.25,.883).project(camera);return {x:(v.x+1)*r.width/2,y:(1-v.y)*r.height/2}});await page.mouse.click(pos.x,pos.y);await page.locator('.focus-card').waitFor();await page.waitForTimeout(2000);
 }
 if(scene==='creating'){await page.getByRole('button',{name:/全部作品/}).click();await page.getByRole('button',{name:'删除《无题手稿·乙》',exact:true}).click();await page.getByRole('button',{name:'删除这本书',exact:true}).click();await page.getByRole('button',{name:'关闭',exact:true}).click();await page.getByRole('button',{name:'新建作品',exact:true}).click();await page.getByRole('textbox',{name:'书名',exact:true}).fill('原生测量新世界')}
 if(scene==='list')await page.getByRole('button',{name:/全部作品/}).click();
 const processes=await cdp.send('SystemInfo.getProcessInfo');await fs.writeFile(`${dir}/processes.json`,JSON.stringify(processes,null,2));const gpu=processes.processInfo.find(p=>p.type==='GPU');
 const notification=`storyos.idle-render-cost.${process.pid}.${scene}`;
 const notify=spawn('notifyutil',['-1',notification]);const started=new Promise(resolve=>notify.on('exit',resolve));
 const child=spawn('xcrun',['xctrace','record','--template','Metal System Trace','--attach',String(gpu.id),'--time-limit','7s','--output',trace,'--notify-tracing-started',notification,'--no-prompt']);let log='';child.stdout.on('data',v=>log+=v);child.stderr.on('data',v=>log+=v);const done=new Promise(resolve=>child.on('exit',resolve));
 await started;await page.waitForTimeout(1000);
 await page.evaluate(()=>{window.__metalFrames=[];const p=window.__renderProbe.state;const original=p.gl.render;p.gl.render=function(s,c,...args){if(s===p.scene)window.__metalFrames.push(Date.now());return original.call(this,s,c,...args)}});
 const start=Date.now();
 if(scene==='opening')await page.getByRole('button',{name:'打开这本书',exact:true}).click();
 if(scene==='creating')await page.getByRole('button',{name:'创造这本书',exact:true}).click();
 if(scene==='roam'){await page.getByRole('button',{name:'自由漫游',exact:true}).click();await page.keyboard.down('KeyW')}
 await page.waitForTimeout(scene==='opening'||scene==='creating'?2600:3500);const end=Date.now();await page.keyboard.up('KeyW');const frames=await page.evaluate(()=>window.__metalFrames);await fs.writeFile(`${dir}/window.json`,JSON.stringify({scene,start,end,frames:frames.filter(t=>t>=start&&t<=end)},null,2));
 await done;notify.kill();await fs.writeFile(`${dir}/record.log`,log);console.log(scene,'recorded');
 for(const [schema,name]of [['metal-gpu-intervals','gpu-intervals'],['metal-application-command-buffer-submissions','submissions']])await promisify(execFile)('xcrun',['xctrace','export','--input',trace,'--xpath',`/trace-toc/run[@number="1"]/data/table[@schema="${schema}"]`,'--output',`${dir}/${name}.xml`]);
 await promisify(execFile)('xcrun',['xctrace','export','--input',trace,'--toc','--output',`${dir}/toc.xml`]);
 await page.evaluate(()=>document.exitPointerLock());
}
await browser.close();
