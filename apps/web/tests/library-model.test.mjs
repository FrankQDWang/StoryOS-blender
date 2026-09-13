import test from 'node:test';import assert from 'node:assert/strict';
import {initialLibrary,createBook,normalizeLibrary,visitBook} from '../src/library-model.mjs';
test('creation retains all projects and leaves occupied positions stable at capacity',()=>{
 let s=initialLibrary();for(let i=0;i<5;i++)s=createBook(s,{title:`Book ${i}`},`new${i}`);
 assert.equal(s.books.length,8);assert.deepEqual(s.books.map(b=>b.slot),[0,1,2,3,4,null,null,null]);
 assert.equal(createBook(s,{title:'again'},'new0'),s);
});
test('invalid creation is atomic and whitespace is removed',()=>{
 const s=initialLibrary();assert.throws(()=>createBook(s,{title:'   '},'bad'));
 assert.equal(s.books.length,3);assert.equal(createBook(s,{title:'  风  '},'new').books.at(-1).title,'风');
});
test('persisted data repairs duplicate slots and ids without losing valid projects',()=>{
 const s=initialLibrary();s.books.push({...s.books[0]});s.books[1].slot=0;
 const restored=normalizeLibrary(JSON.parse(JSON.stringify(s)));assert.equal(restored.books.length,3);assert.equal(restored.books[1].slot,null);
 assert.deepEqual(normalizeLibrary(null),initialLibrary());
});
test('visiting changes recency without moving a displayed book',()=>{
 const s=initialLibrary();const next=visitBook(s,'letters','2026-09-13T12:00:00Z');assert.equal(next.lastBookId,'letters');
 assert.deepEqual(next.books.map(b=>b.slot),s.books.map(b=>b.slot));assert.equal(s.lastBookId,'embers');
});
