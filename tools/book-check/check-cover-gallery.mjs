import {chromium} from 'playwright';
import fs from 'node:fs/promises';
const out='design/round-11-cover-readability';
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1512,height:980},deviceScaleFactor:1}),errors=[];
 page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:4174/review.html');
 await page.waitForFunction(()=>document.querySelectorAll('.image-link img').length===2&&[...document.querySelectorAll('.image-link img')].every(i=>i.complete&&i.naturalWidth));
 const panels=page.locator('.panel');
 for(let i=0;i<7;i++){
  await panels.nth(0).locator('.choice').nth(i).click();
  await page.waitForFunction(()=>{const i=document.querySelector('.image-link img');return i.complete&&i.naturalWidth===1254});
 }
 await panels.nth(0).locator('.choice').nth(0).click();await panels.nth(1).locator('.choice').nth(3).click();
 await page.waitForFunction(()=>[...document.querySelectorAll('.image-link img')].every(i=>i.complete&&i.naturalWidth));
 await page.screenshot({path:`${out}/gallery-check.png`,fullPage:true});
 if(errors.length)throw new Error(errors.join('\n'));
 await fs.writeFile(`${out}/gallery-check.json`,JSON.stringify({url:page.url(),chrome:browser.version(),headless:true,images:7,choices:await page.locator('.choice').count(),errors},null,2)+'\n');
 console.log('Seven image choices loaded; two-panel gallery has no page errors.');
}finally{await browser.close()}
