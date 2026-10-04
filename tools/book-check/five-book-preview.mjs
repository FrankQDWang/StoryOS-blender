import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const out='evidence/five-book-color-preview-20261004';
const {fixture}=JSON.parse(await fs.readFile('design/round-11-cover-readability/references/capture.json'));
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1512,height:751},deviceScaleFactor:1}),errors=[],views=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fixture);
 await page.goto('http://127.0.0.1:4173/?preview=five-books');await page.locator('.room-caption').waitFor();await page.mouse.move(1500,740);await page.waitForTimeout(1200);
 assert.match(await page.getByRole('button',{name:/全部作品/}).innerText(),/5/);
 const snapshot=()=>page.evaluate(async()=>{
  const {_roots}=await import('/node_modules/.vite/deps/@react-three_fiber.js');const state=_roots.get(document.querySelector('.scene canvas')).store.getState();const books=[],lights=[];
  state.scene.traverse(o=>{if(o.name==='FlexibleCover'){
   const p=state.camera.position.clone().set(.02,.12,0);o.localToWorld(p);p.project(state.camera);
   books.push({point:[(p.x+1)*innerWidth/2,(1-p.y)*innerHeight/2],color:o.material[0].color.getHexString(),size:o.geometry.attributes.position.count});
  }if(o.isPointLight)lights.push(o.id)});return {books,lights};
 });
 const initial=await snapshot();assert.equal(initial.books.length,5);assert.equal(initial.books[1].color,'b09b80');
 await page.screenshot({path:`${out}/all-five.png`});
 for(let i=0;i<5;i++){
  if(i){await page.getByRole('button',{name:'返回房间全景',exact:true}).click();await page.mouse.move(1500,740);await page.waitForTimeout(1600)}
  const scene=await snapshot();const [x,y]=scene.books[i].point;
  await page.mouse.click(x,y);await page.locator('.focus-card').waitFor({timeout:5000});await page.mouse.move(1500,740);await page.waitForTimeout(1700);
  const title=await page.locator('.focus-card h2').innerText();const focused=await snapshot();assert.equal(focused.lights.length,initial.lights.length);
  await page.screenshot({path:`${out}/book-${i+1}.png`});views.push({slot:i,title,point:[x,y],color:focused.books[i].color});
 }
 await page.getByRole('button',{name:'打开这本书',exact:true}).click();await page.locator('.workspace h1').waitFor();
 await page.getByRole('button',{name:'返回藏书室',exact:true}).click();await page.locator('.room-caption').waitFor();
 assert.equal(await page.evaluate(()=>localStorage.getItem('storyos.library.demo.v1')),JSON.stringify(fixture));
 assert.deepEqual(errors,[]);
 await fs.writeFile(`${out}/check.json`,JSON.stringify({url:'http://127.0.0.1:4173/?preview=five-books',viewport:[1512,751],views,initial,errors,storagePreserved:true,opening:'fifth book opens and returns'},null,2)+'\n');console.log(JSON.stringify({views,errors}));
}catch(error){console.error(error);throw error}finally{await browser.close()}
