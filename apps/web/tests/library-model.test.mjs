import test from 'node:test';
import assert from 'node:assert/strict';
import {initialLibrary,createBook,deleteBook,normalizeLibrary,visitBook,recentBooks} from '../src/library-model.mjs';
import {BOOK_MATERIALS} from '../src/book-materials.mjs';
const threeBooks=()=>['embers','moonkeeper','letters'].reduce((state,id)=>createBook(state,{title:id},id,'2026-09-12T00:00:00Z'),initialLibrary());

test('new library is empty and five creations allocate the approved family in order',()=>{
 let state=initialLibrary();assert.equal(state.books.length,0);
 for(let i=0;i<5;i++)state=createBook(state,{title:`Book ${i}`},`new${i}`);
 assert.deepEqual(state.books.map(b=>b.slot),[0,1,2,3,4]);
 assert.deepEqual(state.books.map(b=>b.materialId),BOOK_MATERIALS.map(m=>m.id));
 const full=createBook(state,{title:'List only'},'overflow');
 assert.equal(full.books.at(-1).slot,null);assert.deepEqual(full.books.slice(0,5),state.books);
 assert.equal(createBook(full,{title:'again'},'new0'),full);
});
test('deletion leaves other books stable, refills the first hole and persists an empty shelf',()=>{
 let state=threeBooks();const remaining=state.books.filter(b=>b.id!=='moonkeeper');
 state=deleteBook(state,'moonkeeper');assert.deepEqual(state.books,remaining);
 state=createBook(state,{title:'Replacement'},'replacement');
 assert.equal(state.books.at(-1).slot,1);assert.equal(state.books.at(-1).materialId,'muted-pine');
 state=normalizeLibrary(JSON.parse(JSON.stringify({...state,books:recentBooks(state)})));
 assert.equal(state.books.find(b=>b.id==='replacement').materialId,'muted-pine');
 for(const book of state.books)state=deleteBook(state,book.id);
 assert.deepEqual(normalizeLibrary(JSON.parse(JSON.stringify(state))),initialLibrary());
});
test('invalid creation is atomic and whitespace is removed',()=>{
 const state=threeBooks();assert.throws(()=>createBook(state,{title:'   '},'bad'));
 assert.equal(state.books.length,3);assert.equal(createBook(state,{title:'  风  '},'new').books.at(-1).title,'风');
});
test('existing libraries retain works, custom colors and slots while gaining persistent material identities',()=>{
 const legacy=threeBooks();for(const b of legacy.books)delete b.materialId;
 legacy.books[0].color='#123456';legacy.books.push({...legacy.books[0]});legacy.books[1].slot=0;
 const restored=normalizeLibrary(JSON.parse(JSON.stringify(legacy)));
 assert.equal(restored.books.length,3);assert.equal(restored.books[1].slot,null);
 assert.equal(restored.books[0].color,'#123456');assert.equal(restored.books[0].materialId,'warm-umber');
 assert.deepEqual(normalizeLibrary(restored),restored);
 assert.deepEqual(normalizeLibrary(null),initialLibrary());
});
test('visiting and recent sorting do not change a displayed book identity or position',()=>{
 const state=threeBooks();const next=visitBook(state,'letters','2026-10-03T12:00:00Z');
 assert.equal(next.lastBookId,'letters');
 assert.deepEqual(recentBooks(next).map(b=>b.id),['letters','embers','moonkeeper']);
 assert.deepEqual(next.books.map(b=>[b.slot,b.materialId]),state.books.map(b=>[b.slot,b.materialId]));
});
