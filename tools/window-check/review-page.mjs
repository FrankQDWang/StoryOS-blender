import {chromium}from'../book-check/node_modules/playwright/index.mjs';
import fs from'node:fs/promises';
const b=await chromium.connectOverCDP('http://127.0.0.1:9486'),c=await b.newContext({viewport:{width:1512,height:1200},deviceScaleFactor:1}),p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(String(e)));
await p.goto('http://127.0.0.1:4186/revision.html');await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));await p.screenshot({path:'evidence/moonlit-window/revision-v2/review-page.png',fullPage:true});await fs.writeFile('evidence/moonlit-window/revision-v2/review-page.json',JSON.stringify({images:await p.locator('img').count(),errors}));await c.close();process.exit(0);
