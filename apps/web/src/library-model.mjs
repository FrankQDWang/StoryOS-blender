import {BOOK_MATERIALS,nextBookMaterial} from './book-materials.mjs';
export const STORAGE_KEY = 'storyos.library.demo.v1';
export const MAX_SLOTS = 5;
export function initialLibrary() {
  return {version:1,books:[],lastBookId:null,reducedMotion:false,sound:false};
}
export function normalizeLibrary(value) {
  if (!value || value.version !== 1 || !Array.isArray(value.books)) return initialLibrary();
  const ids=new Set(), slots=new Set();
  const books=value.books.filter(b=>b && typeof b.id==='string' && b.id && typeof b.title==='string' && b.title.trim() && !ids.has(b.id) && ids.add(b.id)).map((b,i)=>{
    const slot=Number.isInteger(b.slot) && b.slot>=0 && b.slot<MAX_SLOTS && !slots.has(b.slot) ? b.slot : null;
    if(slot!==null)slots.add(slot);
    const material=BOOK_MATERIALS.find(m=>m.id===b.materialId)??BOOK_MATERIALS[slot??i%MAX_SLOTS];
    return {id:b.id,title:b.title.trim().slice(0,60),description:typeof b.description==='string'?b.description.slice(0,180):'',materialId:material.id,color:/^#[0-9a-f]{6}$/i.test(b.color)?b.color:material.color,slot,words:Number.isFinite(b.words)?Math.max(0,b.words):0,updatedAt:typeof b.updatedAt==='string'?b.updatedAt:new Date(0).toISOString()};
  });
  return {version:1,books,lastBookId:books.some(b=>b.id===value.lastBookId)?value.lastBookId:books[0]?.id??null,reducedMotion:value.reducedMotion===true,sound:value.sound===true};
}
export function createBook(state, {title,description=''}, id, now=new Date().toISOString()) {
  const clean=title.trim();if(!clean || clean.length>60)throw new Error('请填写 1–60 字的书名');
  if(state.books.some(b=>b.id===id))return state;
  const used=new Set(state.books.map(b=>b.slot));const slot=Array.from({length:MAX_SLOTS},(_,i)=>i).find(i=>!used.has(i))??null;
  const material=nextBookMaterial(state.books);
  return {...state,books:[...state.books,{id,title:clean,description:description.trim().slice(0,180),materialId:material.id,color:material.color,slot,words:0,updatedAt:now}],lastBookId:id};
}
export function deleteBook(state,id) {
  const books=state.books.filter(book=>book.id!==id);
  return {...state,books,lastBookId:state.lastBookId===id?recentBooks({books})[0]?.id??null:state.lastBookId};
}
export function visitBook(state,id,now=new Date().toISOString()) {
  return state.books.some(b=>b.id===id)?{...state,lastBookId:id,books:state.books.map(b=>b.id===id?{...b,updatedAt:now}:b)}:state;
}
export function recentBooks(state){return [...state.books].sort((a,b)=>Date.parse(b.updatedAt)-Date.parse(a.updatedAt));}
