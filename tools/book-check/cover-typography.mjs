import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';

const out=process.env.BOOK_CHECK_OUT??'evidence/cover-typography-20261004/visual';
const lightColor=process.env.BOOK_CHECK_LIGHT_COLOR??'#c8a16a';
await fs.mkdir(out,{recursive:true});
const capture=JSON.parse(await fs.readFile('design/round-11-cover-readability/references/capture.json'));
const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-first-run','--disable-background-networking']});
const errors=[],results=[],notFound=[];
try{
 const page=await browser.newPage({viewport:{width:1512,height:751},deviceScaleFactor:1});
 page.on('pageerror',e=>errors.push(String(e)));
 page.on('response',r=>{if(r.status()===404)notFound.push(r.url())});
 page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('404 (Not Found)'))errors.push(m.text())});
 await page.goto('http://127.0.0.1:4173/');
 const fixture=structuredClone(capture.fixture);
 for(const [label,title,color] of [
  ['dark-cn','星海余烬','#325852'],
  ['dark-en','A Catalogue of Forgotten Stars and the Roads Between Them','#325852'],
  ['light-cn','星海余烬',lightColor],
  ['light-en','A Catalogue of Forgotten Stars and the Roads Between Them',lightColor],
  ['long-cn','当最后一颗星辰熄灭之后我们仍在漫长旅途中寻找那些被世界遗忘的名字以及尚未寄出的信件与归途尽头等待我们的温柔灯火和永恒记忆','#325852'],
  ['mixed','星海余烬 The Last Light — Volume II','#ac8058'],
 ]){
  fixture.books[0].title=title;fixture.books[0].color=color;
  await page.evaluate(f=>localStorage.setItem('storyos.library.demo.v1',JSON.stringify(f)),fixture);
  await page.reload();await page.locator('.room-caption').waitFor();await page.mouse.move(1500,740);await page.waitForTimeout(1300);
  await page.screenshot({path:`${out}/${label}-home.png`});
  const details=await page.evaluate(async({title,color})=>{
   const {coverTitleStyle,layoutCoverTitle}=await import('/src/cover-title.mjs');
   const canvas=document.createElement('canvas');canvas.width=768;canvas.height=1024;
   const ctx=canvas.getContext('2d'),style=coverTitleStyle(color),layout=layoutCoverTitle(ctx,title,style);
   const widths=layout.lines.map(line=>ctx.measureText(line).width);
   const {_roots}=await import('/node_modules/.vite/deps/@react-three_fiber.js');
   const state=_roots.get(document.querySelector('.scene canvas')).store.getState();
   state.camera.setViewOffset(1512,751,0,240,500,500*751/1512);state.camera.updateProjectionMatrix();state.invalidate();
   return {title,color,...layout,style,widths,fontReady:document.fonts.check(`${style.weight} 24px ${style.font}`,title)};
  },{title,color});
  await page.waitForTimeout(250);
  await page.locator('.scene canvas').screenshot({path:`${out}/${label}-detail.png`});
  assert.ok(details.widths.every(width=>width<=details.maxWidth));
  assert.equal(details.lines.join('').replace(/\s/g,''),title.replace(/\s/g,''));
  assert.ok(details.y+details.lines.length*details.lineHeight<1024*.8);
  if(label.endsWith('-en'))for(const line of details.lines)for(const word of line.split(' '))assert.ok(title.split(' ').includes(word));
  results.push({label,...details});
 }
 // Real title creation, book opening and deletion are exercised by the existing smoke runner.
 const edgeCases=await page.evaluate(async()=>{
  const {coverTitleStyle,layoutCoverTitle}=await import('/src/cover-title.mjs');
  const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),rows=[];
  for(const color of ['#325852','#c8a16a'])for(const title of ['月','Moon', '星'.repeat(60),'W'.repeat(60),'a '.repeat(29)+'a','星海余烬 The Last Light — Volume II']){
   const style=coverTitleStyle(color),layout=layoutCoverTitle(ctx,title,style);
   rows.push({title,color,...layout,widths:layout.lines.map(line=>ctx.measureText(line).width)});
  }
  return rows;
 });
 for(const row of edgeCases){assert.ok(row.widths.every(w=>w<=row.maxWidth));assert.equal(row.lines.join('').replace(/\s/g,''),row.title.replace(/\s/g,''));assert.ok(row.y+row.lines.length*row.lineHeight<819)}
 await fs.writeFile(`${out}/results.json`,JSON.stringify({chrome:browser.version(),viewport:[1512,751],headless:true,state:'Actual home, unselected/unhovered; detail uses only projection crop, no lighting changes',baseline:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),results,edgeCases,errors,notFound},null,2)+'\n');
 assert.deepEqual(errors,[]);assert.ok(notFound.every(url=>url.endsWith('/favicon.ico')));
 console.log(JSON.stringify({results:results.map(({label,size,lines,style,fonts})=>({label,size,lines,dark:style.dark,fonts})),errors}));
}finally{await browser.close()}
