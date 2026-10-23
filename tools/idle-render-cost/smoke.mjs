import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,url]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({channel:'chrome',headless:process.env.HEADED!=='1'});const context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));
if(process.env.DENY_POINTER_LOCK==='1')await context.addInitScript(()=>{Element.prototype.requestPointerLock=()=>Promise.reject(new Error('smoke: denied pointer lock'))});
const page=await context.newPage(),errors=[],checks=[];page.on('pageerror',e=>errors.push(String(e)));
process.on('uncaughtException',async e=>{await fs.writeFile(`${out}/result.json`,JSON.stringify({checks,errors:[...errors,String(e)],pass:false},null,2));await page.screenshot({path:`${out}/error.png`}).catch(()=>{});await browser.close();console.error(e);process.exit(1)});
const shot=async name=>page.screenshot({path:`${out}/${name}.png`});
await page.goto(url);await page.locator('.room-caption').waitFor();await page.waitForTimeout(2500);await shot('home');
// A moving position does not prove the original mouse-look interaction works.
for(let attempt=0;attempt<2;attempt++){
 await page.getByRole('button',{name:'自由漫游',exact:true}).click();
 await page.waitForFunction(()=>document.pointerLockElement===document.body,null,{timeout:5000});
 await page.locator('.roam-help').waitFor();
 // pointerlockchange updates React after the browser property changes.
 await page.waitForFunction(()=>{const text=document.querySelector('.roam-help')?.textContent;return text?.includes('鼠标环顾')&&!text.includes('按住鼠标')},null,{timeout:5000});
 await page.evaluate(()=>{window.__lookEvents=[];window.__recordLook=e=>window.__lookEvents.push({buttons:e.buttons,x:e.movementX,y:e.movementY,trusted:e.isTrusted});document.addEventListener('mousemove',window.__recordLook)});
 const before=await page.evaluate(()=>({position:window.__renderProbe.state.camera.position.toArray(),rotation:window.__renderProbe.state.camera.quaternion.toArray()}));
 await page.mouse.move(700,350);await page.mouse.move(820,390,{steps:8});
 await page.keyboard.down('KeyW');await page.waitForTimeout(350);await page.keyboard.up('KeyW');
 const after=await page.evaluate(()=>({position:window.__renderProbe.state.camera.position.toArray(),rotation:window.__renderProbe.state.camera.quaternion.toArray(),events:window.__lookEvents}));
 assert.notDeepEqual(after.rotation,before.rotation,'Unlocked-button mouse movement must rotate the camera');
 assert(after.events.some(e=>e.trusted&&e.buttons===0&&(e.x||e.y)),'Real mouse movement without a pressed button required');
 assert.notDeepEqual(after.position,before.position);
 await shot(`roam-${attempt}`);await page.keyboard.press('Escape');
 await page.waitForFunction(()=>document.pointerLockElement===null,null,{timeout:5000});
 await page.locator('.roam-help').waitFor({state:'hidden'});
 await page.locator('.room-caption').waitFor();
 await page.evaluate(()=>document.removeEventListener('mousemove',window.__recordLook));
 await page.waitForTimeout(1500);checks.push({flow:'pointer lock, button-free look, movement, Escape',attempt,before,after});
}
const pos=await page.evaluate(()=>{const {camera,gl}=window.__renderProbe.state,r=gl.domElement.getBoundingClientRect(),v=camera.position.clone().set(-3.93,1.25,.883).project(camera);return {x:(v.x+1)*r.width/2,y:(1-v.y)*r.height/2}});await page.mouse.click(pos.x,pos.y);await page.locator('.focus-card').waitFor();await page.mouse.move(1500,680);await page.waitForTimeout(2000);await shot('focused');
await page.getByRole('button',{name:'打开这本书',exact:true}).click();for(let i=0;i<7;i++){await page.waitForTimeout(250);await shot(`opening-${i}`)}await page.locator('.workspace h1').waitFor();assert.equal(await page.locator('.workspace h1').innerText(),'星海余烬');await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();await page.waitForTimeout(2000);await shot('returned');checks.push('open and return');
await page.getByRole('button',{name:/全部作品/}).click();await page.getByRole('button',{name:'删除《无题手稿·乙》',exact:true}).click();await page.getByRole('button',{name:'删除这本书',exact:true}).click();await page.getByRole('button',{name:'关闭',exact:true}).click();await page.waitForTimeout(1000);await shot('deleted');checks.push('delete fifth slot');
await page.getByRole('button',{name:'新建作品',exact:true}).click();await page.getByRole('textbox',{name:'书名',exact:true}).fill('验证新世界');await page.getByRole('button',{name:'创造这本书',exact:true}).click();for(let i=0;i<6;i++){await page.waitForTimeout(300);await shot(`creating-${i}`)}await page.waitForTimeout(1500);await shot('created');const stored=await page.evaluate(()=>JSON.parse(localStorage.getItem('storyos.library.demo.v1')));assert.equal(stored.books.find(b=>b.title==='验证新世界').slot,4);checks.push('create, fly and place in freed fifth slot');
await page.getByRole('button',{name:/全部作品/}).click();await page.getByRole('textbox',{name:'搜索书名'}).fill('守月人');await page.locator('.book-row').click();assert.equal(await page.locator('.workspace h1').innerText(),'守月人');await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();checks.push('Quick Access search, enter and return');assert.deepEqual(errors,[]);await fs.writeFile(`${out}/result.json`,JSON.stringify({checks,errors,pass:true},null,2));await browser.close();console.log(checks);
