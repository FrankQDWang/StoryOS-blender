import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
const [out,url]=process.argv.slice(2);await fs.mkdir(out,{recursive:true});const browser=await chromium.launch({channel:'chrome',headless:true}),context=await browser.newContext({viewport:{width:1512,height:695},deviceScaleFactor:2});await context.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));const page=await context.newPage();await page.goto(url);await page.locator('.room-caption').waitFor();await page.waitForTimeout(3000);
const cdp=await browser.newBrowserCDPSession();const processes=await cdp.send('SystemInfo.getProcessInfo');await fs.writeFile(`${out}/processes.json`,JSON.stringify(processes,null,2));const gpu=processes.processInfo.find(p=>p.type==='GPU');
try {const result=await promisify(execFile)('xcrun',['xctrace','record','--template','Metal System Trace','--attach',String(gpu.id),'--time-limit','5s','--output',`${out}/gpu.trace`,'--no-prompt'],{timeout:60000});await fs.writeFile(`${out}/record.log`,result.stdout+'\n'+result.stderr);console.log(result)}catch(e){await fs.writeFile(`${out}/record.log`,String(e)+'\n'+e.stdout+'\n'+e.stderr);console.error(String(e));}finally{await browser.close()}
