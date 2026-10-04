import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
const out='design/round-11-cover-readability/references';
// Preserve the original three-book fixture and its darker custom cover colors.
const source=execFileSync('git',['show','eedd745:apps/web/src/library-model.mjs'],{encoding:'utf8'});
const prior=await import(`data:text/javascript;base64,${Buffer.from(source).toString('base64')}`);
const fixture=prior.initialLibrary();
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-first-run','--disable-background-networking']});
try{
const page=await browser.newPage({viewport:{width:1512,height:751},deviceScaleFactor:1});
await page.addInitScript(fixture=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(fixture)),fixture);
const errors=[];page.on('pageerror',e=>errors.push(String(e)));
await page.goto('http://127.0.0.1:4173/');await page.locator('.room-caption').waitFor();await page.mouse.move(1500,740);await page.waitForTimeout(1800);
await page.screenshot({path:`${out}/home-unselected.png`});
// A screenshot clip from the same overview; no zoom, focus, relight, or exposure edits.
await page.screenshot({path:`${out}/book-overview-clip.png`,clip:{x:0,y:250,width:300,height:285}});
await fs.writeFile(`${out}/capture.json`,JSON.stringify({url:page.url(),chrome:browser.version(),headless:true,viewport:[1512,751],state:'Actual home route, overview, no selected/hovered book; unchanged runtime renderer and lights',fixtureSource:'eedd745 initialLibrary, three original books/colors; isolated context, not a read of user browser storage',fixture,errors},null,2)+'\n');
console.log(JSON.stringify({url:page.url(),errors,paths:[`${out}/home-unselected.png`,`${out}/book-overview-clip.png`]}));
}finally{await browser.close()}
