import {chromium} from '../book-check/node_modules/playwright/index.mjs';
import fs from 'node:fs/promises';
const dir='evidence/moonlit-window/trials';await fs.mkdir(dir,{recursive:true});
const b=await chromium.connectOverCDP('http://127.0.0.1:9486'),c=b.contexts()[0];let p=c.pages().find(p=>p.url().includes('127.0.0.1'))||await c.newPage();
await p.setViewportSize({width:1512,height:751});
const [action,arg,name]=process.argv.slice(2);
if(action==='goto'){await p.close();p=await c.newPage();await p.setViewportSize({width:1512,height:751});await p.goto(arg);await p.locator('.room-caption').waitFor();await p.mouse.move(1500,740);await p.waitForTimeout(1300);}
if(action==='click'){await p.getByRole('button',{name:arg,exact:true}).click();await p.waitForTimeout(1200);}
if(action==='hold'){const [key,ms]=arg.split(',');await p.keyboard.down(key);await p.waitForTimeout(Number(ms));await p.keyboard.up(key);await p.waitForTimeout(300);}
if(action==='look'){const [x,y]=arg.split(',').map(Number);await p.evaluate(([x,y])=>document.dispatchEvent(new MouseEvent('mousemove',{movementX:x,movementY:y,bubbles:true})),[x,y]);await p.waitForTimeout(300);}
if(action==='key'){await p.keyboard.press(arg);await p.waitForTimeout(500);}
if(name)await p.screenshot({path:`${dir}/${name}.png`});
console.log(await p.locator('body').ariaSnapshot());
console.log(await p.evaluate(()=>({locked:!!document.pointerLockElement,camera:window.__sceneState?.()?.camera.position.toArray()})));
process.exit(0);
