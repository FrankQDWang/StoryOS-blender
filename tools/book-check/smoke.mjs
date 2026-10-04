import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
const browser=await chromium.connectOverCDP('http://127.0.0.1:9484');
const context=await browser.newContext({viewport:{width:1512,height:751},deviceScaleFactor:1});
const page=await context.newPage(),errors=[],steps=[];
page.on('pageerror',e=>errors.push(String(e)));
const root=process.argv[2]??'http://127.0.0.1:4173';
const out='evidence/five-books-20261003';
const state=()=>page.evaluate(()=>JSON.parse(localStorage.getItem('storyos.library.demo.v1')));
const screenshot=async name=>{await page.waitForTimeout(300);await page.screenshot({path:`${out}/${name}.png`})};
async function create(title,description=''){
 await page.getByRole('button',{name:'新建作品',exact:true}).click();
 await page.getByRole('textbox',{name:'书名',exact:true}).fill(title);
 if(description)await page.getByRole('textbox',{name:'一句话介绍 选填',exact:true}).fill(description);
 await page.getByRole('button',{name:'创造这本书',exact:true}).click();
 await page.locator('.cinema-caption').waitFor({state:'hidden'});
}
async function list(){await page.getByRole('button',{name:/全部作品/}).click()}
async function remove(title){
 await page.getByRole('button',{name:`删除《${title}》`,exact:true}).click();
 await page.getByRole('button',{name:'删除这本书',exact:true}).click();
}
await page.goto(root);await page.locator('.room-caption').waitFor();
assert.equal((await state()).books.length,0);await screenshot('01-empty');steps.push('fresh empty library');
const titles=['星海余烬','守月人','寄往风中的信','无题手稿·甲','无题手稿·乙'];
for(const [i,title] of titles.entries())await create(title,i===0?'群星熄灭之后，故事才刚刚开始。':'');
let full=await state();assert.deepEqual(full.books.map(b=>b.slot),[0,1,2,3,4]);
assert.deepEqual(full.books.map(b=>b.materialId),['warm-umber','muted-pine','slate-blue','smoky-plum','warm-ochre']);
await screenshot('02-five-books');steps.push('five UI creations in approved order');
await create('第六本');assert.equal((await state()).books.at(-1).slot,null);steps.push('sixth book kept in list');
await list();await remove('守月人');await page.getByRole('button',{name:'关闭',exact:true}).click();
let deleted=await state();assert.deepEqual(deleted.books, [...full.books.filter(b=>b.title!=='守月人'),deleted.books.at(-1)]);
await screenshot('03-deleted-gap');steps.push('deletion leaves others unchanged');
await create('新手稿');const replacement=(await state()).books.at(-1);
assert.equal(replacement.slot,1);assert.equal(replacement.materialId,'muted-pine');
await page.reload();await page.locator('.room-caption').waitFor();assert.deepEqual((await state()).books.at(-1),replacement);steps.push('replacement and reload preserve identity');
await list();await page.getByRole('textbox',{name:'搜索书名'}).fill('第六');
await page.locator('.book-row').click();await page.locator('.workspace h1').waitFor();
assert.equal(await page.locator('.workspace h1').innerText(),'第六本');await page.getByRole('button',{name:'返回藏书室',exact:true}).click();steps.push('overflow searchable via Quick Access');
await list();
await page.getByRole('button',{name:'删除《星海余烬》',exact:true}).click();await page.getByRole('button',{name:'保留作品',exact:true}).click();
assert.equal((await state()).books.length,6);steps.push('delete cancellation keeps book');
for(const book of (await state()).books)await remove(book.title);
await page.getByRole('button',{name:'关闭',exact:true}).click();await page.reload();await page.locator('.room-caption').waitFor();
assert.equal((await state()).books.length,0);assert.equal((await state()).lastBookId,null);await screenshot('04-empty-after-delete-reload');steps.push('delete all and refresh stays empty');
await create('重生手稿');assert.equal((await state()).books[0].materialId,'warm-umber');steps.push('new cycle begins with warm umber');
await screenshot('05-one-book');
assert.deepEqual(errors,[]);
await fs.writeFile(`${out}/smoke.json`,JSON.stringify({root,chrome:browser.version(),steps,errors,finalLibrary:await state()},null,2)+'\n');
console.log(JSON.stringify({steps,errors}));
await context.close();process.exit(0);
