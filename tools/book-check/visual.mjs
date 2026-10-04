import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
const browser=await chromium.connectOverCDP('http://127.0.0.1:9484');
const page=browser.contexts()[0].pages()[0];
await page.setViewportSize({width:1512,height:751});
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
const out='evidence/five-books-20261003';
for(let slot=0;slot<5;slot++)for(const [label,time] of [['cover',0],['open',3.2]]){
 await page.goto(`http://127.0.0.1:4173/review.html?slot=${slot}&time=${time}`);
 await page.getByRole('combobox',{name:'书位'}).waitFor();await page.waitForTimeout(800);
 await page.screenshot({path:`${out}/material-${slot+1}-${label}.png`});
}
await page.goto('http://127.0.0.1:4173/review.html?slot=0&time=1.7');await page.waitForTimeout(800);
await page.screenshot({path:`${out}/contact-1.7.png`});
await page.goto('http://127.0.0.1:4173/review.html?slot=0&time=1.7&view=hands-side');await page.waitForTimeout(800);
await page.screenshot({path:`${out}/contact-side-1.7.png`});
await page.goto('http://127.0.0.1:4173/review.html?view=overview');await page.waitForTimeout(800);
await page.screenshot({path:`${out}/five-materials-overview.png`});
assert.deepEqual(errors,[]);await fs.writeFile(`${out}/visual-errors.json`,JSON.stringify(errors)+'\n');
await page.goto('about:blank');console.log('13 Chrome screenshots, no page/console errors');process.exit(0);
