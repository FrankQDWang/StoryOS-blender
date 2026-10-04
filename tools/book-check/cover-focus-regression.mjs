import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const out=process.env.BOOK_CHECK_OUT??'evidence/cover-typography-focus-fix-20261004/before';
await fs.mkdir(out,{recursive:true});
const {fixture}=JSON.parse(await fs.readFile('design/round-11-cover-readability/references/capture.json'));
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1512,height:751},deviceScaleFactor:1}),errors=[],rows=[];
 await page.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fixture);
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:4173/');await page.locator('.room-caption').waitFor();await page.mouse.move(1500,1000);await page.waitForTimeout(1000);
 const inspect=()=>page.evaluate(async()=>{const {_roots}=await import('/node_modules/.vite/deps/@react-three_fiber.js');const state=_roots.get(document.querySelector('.scene canvas')).store.getState(),lights=[];state.scene.traverse(o=>{if(o.isPointLight)lights.push({id:o.id,intensity:o.intensity,position:o.position.toArray()});});return {lights}});
 const overview=await inspect();await page.screenshot({path:`${out}/overview.png`});
 for(const slot of [0,1]){
  if(slot){await page.setViewportSize({width:1512,height:751});await page.getByRole('button',{name:'返回房间全景',exact:true}).click();await page.mouse.move(1500,740);await page.waitForTimeout(1800)}
  const position=[{x:101,y:376},{x:408,y:366}][slot];await page.mouse.move(position.x,position.y);await page.waitForTimeout(200);
  const hovered=await inspect();await page.mouse.move(1500,740);await page.waitForTimeout(100);await page.mouse.click(position.x,position.y);await page.locator('.focus-card').waitFor();await page.mouse.move(1500,740);await page.waitForTimeout(2000);
  const focused=await inspect();await page.setViewportSize({width:1512,height:1049});await page.waitForTimeout(400);await page.screenshot({path:`${out}/slot-${slot}-focus.png`});
  const style=await page.evaluate(async color=>(await import('/src/cover-title.mjs')).coverTitleStyle(color),fixture.books[slot].color);
  rows.push({slot,color:fixture.books[slot].color,style,extraHoverLights:hovered.lights.filter(l=>!overview.lights.some(b=>b.id===l.id)),extraFocusLights:focused.lights.filter(l=>!overview.lights.some(b=>b.id===l.id))});
 }
 const result={rows,errors,pass:rows.every(r=>!r.extraHoverLights.length&&!r.extraFocusLights.length)&&rows[0].style.dark&&!rows[1].style.dark};
 await fs.writeFile(`${out}/result.json`,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));assert.equal(result.pass,true);
}finally{await browser.close()}
