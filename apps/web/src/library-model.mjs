export const STORAGE_KEY = 'storyos.library.demo.v1';
export const MAX_SLOTS = 5;
export const COLORS = ['#325852', '#78503b', '#384d6b', '#695077', '#736137'];
export function initialLibrary() {
  return { version: 1, books: [
    {id:'embers', title:'星海余烬', description:'群星熄灭之后，故事才刚刚开始。', color:COLORS[0], slot:0, words:12840, updatedAt:'2026-09-12T20:30:00.000Z'},
    {id:'moonkeeper', title:'守月人', description:'一座小镇，和一个不肯结束的长夜。', color:COLORS[1], slot:1, words:3680, updatedAt:'2026-09-11T18:10:00.000Z'},
    {id:'letters', title:'寄往风中的信', description:'写给那些尚未抵达的远方。', color:COLORS[2], slot:2, words:920, updatedAt:'2026-09-10T09:00:00.000Z'},
  ], lastBookId:'embers', reducedMotion:false, sound:false };
}
export function normalizeLibrary(value) {
  if (!value || value.version !== 1 || !Array.isArray(value.books)) return initialLibrary();
  const ids=new Set(), slots=new Set();
  const books=value.books.filter(b=>b && typeof b.id==='string' && b.id && typeof b.title==='string' && b.title.trim() && !ids.has(b.id) && ids.add(b.id)).map((b,i)=>{
    const slot=Number.isInteger(b.slot) && b.slot>=0 && b.slot<MAX_SLOTS && !slots.has(b.slot) ? b.slot : null;
    if(slot!==null)slots.add(slot);
    return {id:b.id,title:b.title.trim().slice(0,60),description:typeof b.description==='string'?b.description.slice(0,180):'',color:/^#[0-9a-f]{6}$/i.test(b.color)?b.color:COLORS[i%5],slot,words:Number.isFinite(b.words)?Math.max(0,b.words):0,updatedAt:typeof b.updatedAt==='string'?b.updatedAt:new Date(0).toISOString()};
  });
  return {version:1,books,lastBookId:books.some(b=>b.id===value.lastBookId)?value.lastBookId:books[0]?.id??null,reducedMotion:value.reducedMotion===true,sound:value.sound===true};
}
export function createBook(state, {title,description='',color=COLORS[0]}, id, now=new Date().toISOString()) {
  const clean=title.trim();if(!clean || clean.length>60)throw new Error('请填写 1–60 字的书名');
  if(state.books.some(b=>b.id===id))return state;
  const used=new Set(state.books.map(b=>b.slot));const slot=Array.from({length:MAX_SLOTS},(_,i)=>i).find(i=>!used.has(i))??null;
  return {...state,books:[...state.books,{id,title:clean,description:description.trim().slice(0,180),color,slot,words:0,updatedAt:now}],lastBookId:id};
}
export function visitBook(state,id,now=new Date().toISOString()) {
  return state.books.some(b=>b.id===id)?{...state,lastBookId:id,books:state.books.map(b=>b.id===id?{...b,updatedAt:now}:b)}:state;
}
export function recentBooks(state){return [...state.books].sort((a,b)=>Date.parse(b.updatedAt)-Date.parse(a.updatedAt));}
