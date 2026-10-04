// Stable asset identities; display positions and recent ordering are independent.
export const BOOK_MATERIALS = [
  {id:'warm-umber', name:'暖棕', color:'#ac8058', paper:'#f4e9d4', ink:'#33251a', roughness:.58, grain:.001},
  {id:'muted-pine', name:'灰松绿', color:'#82927e', paper:'#efead8', ink:'#2e3127', roughness:.67, grain:.0008},
  {id:'slate-blue', name:'蓝灰', color:'#7e96b0', paper:'#f4eee0', ink:'#292e35', roughness:.53, grain:.0007},
  {id:'smoky-plum', name:'烟紫褐', color:'#a18490', paper:'#f0e5d4', ink:'#34272e', roughness:.62, grain:.0009},
  {id:'warm-ochre', name:'麦褐', color:'#c8a16a', paper:'#f7ebd2', ink:'#392c1d', roughness:.70, grain:.0012},
];

export function bookMaterial(book) {
  return BOOK_MATERIALS.find(material=>material.id===book.materialId) ?? BOOK_MATERIALS[book.slot??0];
}

export function nextBookMaterial(books) {
  const displayed=new Set(books.filter(book=>book.slot!==null).map(book=>book.materialId));
  const available=BOOK_MATERIALS.find(material=>!displayed.has(material.id));
  if(available)return available;
  // Full shelves never limit the collection. List-only books reuse the same family.
  return BOOK_MATERIALS[books.length % BOOK_MATERIALS.length];
}
