// A continuous ten-second input path, without synchronous screenshots slowing input timing.
import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import {fiveBookPreview} from '../../apps/web/src/five-book-preview.mjs';
import {initialLibrary} from '../../apps/web/src/library-model.mjs';
import fs from 'node:fs/promises';
const root=process.env.WINDOW_ROOT??'http://127.0.0.1:4182',label=process.env.WINDOW_LABEL??'candidate',out=process.env.WINDOW_OUT??'evidence/moonlit-window/final';
const browser=await chromium.connectOverCDP('http://127.0.0.1:9486');const c=await browser.newContext({viewport:{width:1512,height:751},deviceScaleFactor:1,recordVideo:{dir:`${out}/roam-${label}`,size:{width:1512,height:751}}});
await c.addInitScript(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fiveBookPreview(initialLibrary()));
const p=await c.newPage();await p.goto(root);await p.locator('.room-caption').waitFor();await p.waitForTimeout(2000);await p.getByRole('button',{name:'自由漫游',exact:true}).click();
const hold=async(k,t)=>{await p.keyboard.down(k);await p.waitForTimeout(t);await p.keyboard.up(k)};
await hold('a',650);await hold('w',3600);await hold('d',650);
await p.evaluate(()=>document.dispatchEvent(new MouseEvent('mousemove',{movementX:0,movementY:-145,bubbles:true})));
await p.waitForTimeout(300);
await p.evaluate(()=>{window.__roamFrames=[];window.__roamRunning=true;let prev=performance.now();function frame(now){window.__roamFrames.push(now-prev);prev=now;if(window.__roamRunning)requestAnimationFrame(frame)}requestAnimationFrame(frame)});
await hold('w',450);await p.waitForTimeout(1000);await hold('a',400);await p.waitForTimeout(1400);await hold('d',800);await p.waitForTimeout(1400);await hold('a',400);await p.waitForTimeout(1400);await hold('s',650);await p.waitForTimeout(2100);
const times=await p.evaluate(()=>{window.__roamRunning=false;return window.__roamFrames});await p.keyboard.press('Escape');await p.waitForTimeout(500);await c.close();
const sorted=[...times].sort((a,b)=>a-b);await fs.writeFile(`${out}/roam-${label}.json`,JSON.stringify({root,frames:times.length,duration:times.reduce((a,b)=>a+b,0),median:sorted[Math.floor(sorted.length/2)],p95:sorted[Math.floor(sorted.length*.95)],max:Math.max(...times),over50:times.filter(t=>t>50).length,times},null,2));console.log({label,frames:times.length,p95:sorted[Math.floor(sorted.length*.95)]});process.exit(0);
