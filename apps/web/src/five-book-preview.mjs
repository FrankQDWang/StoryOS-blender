import {BOOK_MATERIALS} from './book-materials.mjs';

// A dev-only review of the existing five stands, using the real home experience.
export function fiveBookPreview(library) {
  const books=library.books.map(book=>({...book}));
  const titles=['星海余烬','守月人','寄往风中的信','无题手稿·甲','无题手稿·乙'];
  const colors=['#325852','#b09b80','#384d6b',BOOK_MATERIALS[3].color,BOOK_MATERIALS[4].color];
  for(let slot=0;slot<5;slot++){
    if(!books.some(book=>book.slot===slot))books.push({
      id:`preview-book-${slot}`,slot,title:titles[slot],description:'',
      materialId:BOOK_MATERIALS[slot].id,color:colors[slot],words:0,updatedAt:'2026-10-04T00:00:00Z',
    });
  }
  const brown=books.find(book=>book.id==='moonkeeper'||book.title==='守月人');
  if(brown)brown.color='#b09b80';
  return {...library,books,lastBookId:library.lastBookId??books[0].id};
}
