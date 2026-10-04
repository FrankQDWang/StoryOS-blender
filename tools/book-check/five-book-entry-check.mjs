import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const out='evidence/five-book-entry-fix-20261004';
const {fixture}=JSON.parse(await fs.readFile('design/round-11-cover-readability/references/capture.json'));
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1512,height:751}}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.addInitScript(f=>{if(!localStorage.getItem('storyos.library.demo.v1'))localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f))},fixture);
 await page.goto('http://127.0.0.1:4173/');await page.locator('.room-caption').waitFor();
 const before={count:await page.locator('.top-books span').innerText(),badge:await page.locator('.demo-tag').innerText()};
 const stored=await page.evaluate(()=>localStorage.getItem('storyos.library.demo.v1'));
 console.log(JSON.stringify({before,expectedCount:5,verdict:before.count==='5'?'PASS':'FAIL: root still shows three books'}));
 await fs.writeFile(`${out}/root-before.json`,JSON.stringify(before));
 await page.waitForFunction(()=>document.querySelector('.top-books span')?.textContent==='5',{},{timeout:60000});
 await page.waitForFunction(async()=>{
  const {_roots}=await import('/node_modules/.vite/deps/@react-three_fiber.js');
  const state=_roots.get(document.querySelector('.scene canvas'))?.store.getState();let count=0;
  state?.scene.traverse(o=>{if(o.name==='FlexibleCover')count++});return count===5;
 },{},{timeout:20000});
 await page.mouse.move(1500,740);await page.waitForTimeout(1500);
 const after=await page.evaluate(async()=>{
  const {_roots}=await import('/node_modules/.vite/deps/@react-three_fiber.js');const state=_roots.get(document.querySelector('.scene canvas')).store.getState();const colors=[];
  state.scene.traverse(o=>{if(o.name==='FlexibleCover')colors.push(o.material[0].color.getHexString())});
  return {url:location.href,count:document.querySelector('.top-books span').textContent,badge:document.querySelector('.demo-tag').textContent,colors};
 });
 assert.equal(after.colors.length,5);assert.ok(after.colors.includes('b09b80'));
 await page.screenshot({path:`${out}/root-after.png`});
 await page.reload();await page.locator('.room-caption').waitFor();assert.equal(await page.locator('.top-books span').innerText(),'5');
 assert.equal(await page.evaluate(()=>localStorage.getItem('storyos.library.demo.v1')),stored);assert.deepEqual(errors,[]);
 await fs.writeFile(`${out}/check.json`,JSON.stringify({before,after,refreshCount:5,storagePreserved:true,errors},null,2)+'\n');
 console.log(JSON.stringify({after,refreshCount:5,storagePreserved:true,errors}));
}finally{await browser.close()}
