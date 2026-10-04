import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const out=process.env.WINDOW_OUT??'evidence/moonlit-window/final';const b=await chromium.connectOverCDP('http://127.0.0.1:9486'),c=await b.newContext({viewport:{width:1512,height:751},deviceScaleFactor:1});
await c.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));
const p=await c.newPage(),errors=[],checks=[];p.on('pageerror',e=>errors.push(String(e)));
await p.goto('http://127.0.0.1:4182');await p.locator('.room-caption').waitFor();await p.waitForTimeout(2000);
for(const [i,[x,y]]of [[100,380],[415,373],[1150,380],[1250,415],[1430,447]].entries()){
 await p.mouse.click(x,y);await p.locator('.focus-card').waitFor();await p.mouse.move(1500,740);await p.waitForTimeout(1500);
 await p.screenshot({path:`${out}/book-${i+1}.png`});checks.push({slot:i,title:await p.locator('.focus-card h2').innerText()});
 if(i===0){await p.getByRole('button',{name:'打开这本书',exact:true}).click();await p.waitForTimeout(1000);await p.screenshot({path:`${out}/opening.png`});await p.locator('.workspace h1').waitFor();await p.getByRole('button',{name:'返回藏书室',exact:true}).click();await p.locator('.room-caption').waitFor();await p.waitForTimeout(1500);await p.screenshot({path:`${out}/returned.png`})}
 else await p.getByRole('button',{name:'返回房间全景',exact:true}).click();
 await p.waitForTimeout(1600);
}
await p.getByRole('button',{name:/全部作品/}).click();await p.getByRole('textbox',{name:'搜索书名'}).fill('守月人');await p.locator('.book-row').click();assert.equal(await p.locator('.workspace h1').innerText(),'守月人');checks.push('Quick Access search and enter');await p.getByRole('button',{name:'返回藏书室',exact:true}).click();await p.locator('.room-caption').waitFor();await p.waitForTimeout(1500);
await p.getByRole('button',{name:'减少动态效果',exact:true}).click();await p.mouse.click(100,380);await p.locator('.focus-card').waitFor();await p.getByRole('button',{name:'打开这本书',exact:true}).click();await p.locator('.workspace h1').waitFor();await p.getByRole('button',{name:'返回藏书室',exact:true}).click();await p.locator('.room-caption').waitFor();checks.push('reduced motion open and return');
await p.getByRole('button',{name:'新建作品',exact:true}).click();await p.getByRole('dialog').waitFor();await p.getByRole('button',{name:'关闭',exact:true}).click();assert.equal(await p.getByRole('dialog').count(),0);checks.push('create cancel');
assert.deepEqual(errors,[]);await fs.writeFile(`${out}/smoke.json`,JSON.stringify({checks,errors},null,2));await c.close();console.log(checks);process.exit(0);
