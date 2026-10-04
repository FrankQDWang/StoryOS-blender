import * as THREE from 'three';
import {BOOK,coverPoint,backPoint,blockPoint,leafPoint,gutterPoint,spinePoint} from './soft-book-shape.mjs';
import {applyCoverTitleMaterial} from './cover-title.mjs';

// Each closed ribbon has two surfaces and a sewn/thin edge, with shared UVs.
function ribbon(cols,rows){
 const params=[],uv=[],index=[];
 const vertex=(u,v,side)=>{const i=params.length/3;params.push(u,v,side);uv.push(u,1-v);return i};
 const quad=(a,b,c,d,flip=false)=>index.push(...(flip?[a,c,b,b,c,d]:[a,b,c,b,d,c]));
 const groups=[];
 for(const side of [1,-1]){
  const start=index.length,base=params.length/3;
  for(let row=0;row<=rows;row++)for(let col=0;col<=cols;col++)vertex(col/cols,row/rows,side);
  for(let row=0;row<rows;row++)for(let col=0;col<cols;col++){
   const a=base+row*(cols+1)+col;quad(a,a+cols+1,a+1,a+cols+2,side<0);
  }
  groups.push([start,index.length-start,side>0?0:1]);
 }
 const start=index.length;
 for(let edge=0;edge<4;edge++){
  const count=edge<2?rows:cols,base=params.length/3;
  for(let i=0;i<=count;i++){
   const u=edge===0?0:edge===1?1:i/count,v=edge===2?0:edge===3?1:i/count;
   vertex(u,v,1);uv[uv.length-2]=i/count;uv[uv.length-1]=1;
   vertex(u,v,-1);uv[uv.length-2]=i/count;uv[uv.length-1]=0;
  }
  for(let i=0;i<count;i++){const a=base+i*2;quad(a,a+1,a+2,a+3,edge===1||edge===2)}
 }
 groups.push([start,index.length-start,2]);
 const geometry=new THREE.BufferGeometry();geometry.setIndex(index);
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(params.length),3));
 geometry.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
 for(const group of groups)geometry.addGroup(...group);
 geometry.userData.params=params;
 return geometry;
}
function bendRibbon(geometry,surface,time,thickness){
 const params=geometry.userData.params,positions=geometry.attributes.position,p=[0,0,0,0];
 for(let i=0;i<positions.count;i++){
  surface(params[i*3],params[i*3+1],time,params[i*3+2]*thickness/2,p);
  positions.setXYZ(i,p[0],p[1],p[2]);
 }
 positions.needsUpdate=true;geometry.computeVertexNormals();
}
let edgeTexture;
function paperEdges(){
 if(edgeTexture)return edgeTexture;
 const canvas=document.createElement('canvas');canvas.width=64;canvas.height=512;
 const ctx=canvas.getContext('2d');ctx.fillStyle='#e7decc';ctx.fillRect(0,0,64,512);
 for(let row=0;row<512;row+=4){ctx.fillStyle=`rgba(93,72,46,${.12+.12*(.5+.5*Math.sin(row*12.8))})`;ctx.fillRect(0,row,64,1)}
 edgeTexture=new THREE.CanvasTexture(canvas);edgeTexture.colorSpace=THREE.SRGBColorSpace;edgeTexture.anisotropy=8;return edgeTexture;
}
const closedGeometries=new Map();
export function createSoftBook(appearance){
 const object=new THREE.Group();object.name='FlexibleBoundBook';
 const {style,leather}=appearance;
 const skin=new THREE.MeshStandardMaterial({map:leather,color:appearance.color,bumpMap:leather,bumpScale:style.grain,roughness:style.roughness});
 const title=skin.clone();title.map=appearance.title;applyCoverTitleMaterial(title);
 const paper=new THREE.MeshStandardMaterial({map:appearance.back,color:style.paper,roughness:.94});
 const content=paper.clone();content.map=appearance.page;
 const edges=new THREE.MeshStandardMaterial({map:paperEdges(),color:style.paper,roughness:1});
 const parts=[];
 function add(name,surface,thickness,materials,cols=32,rows=10,dynamic=true){
  let geometry=closedGeometries.get(name);
  if(!geometry){geometry=ribbon(cols,rows);bendRibbon(geometry,surface,0,thickness);geometry.computeBoundingSphere();closedGeometries.set(name,geometry)}
  const mesh=new THREE.Mesh(geometry,materials);mesh.name=name;mesh.castShadow=true;mesh.receiveShadow=true;mesh.frustumCulled=false;
  object.add(mesh);parts.push({mesh,surface,thickness,dynamic,owned:false});return mesh;
 }
 add('FlexibleBack',backPoint,BOOK.leather,[skin,skin,skin],32,10,false);
 add('LeatherSpine',spinePoint,BOOK.leather,[skin,skin,skin],14,10);
 add('BoundPaperBlock',(u,v,t,d,out)=>blockPoint(u,v,t,d-BOOK.blockThickness/2,out),BOOK.blockThickness,[content,paper,edges]);
 add('FlexibleCover',coverPoint,BOOK.leather,[title,skin,skin]);
 add('ContinuousEndpaper',gutterPoint,.0008,[paper,paper,paper],12,10);
 for(let i=0;i<3;i++)add(`BoundLeaf${i}`,(u,v,t,d,out)=>leafPoint(u,v,t,i,d,out),.00065,[paper,paper,paper],32,12);
 object.userData.softBook={parts,materials:[skin,title,paper,content,edges],time:0};
 return object;
}
export function updateSoftBook(object,time){
 const data=object.userData.softBook;if(data.time===time)return;
 for(const part of data.parts){
  if(!part.dynamic)continue;
  if(!part.owned){part.mesh.geometry=part.mesh.geometry.clone();part.mesh.geometry.attributes.position.setUsage(THREE.DynamicDrawUsage);part.owned=true}
  bendRibbon(part.mesh.geometry,part.surface,time,part.thickness);
 }
 data.time=time;
}
export function disposeSoftBook(object){
 for(const p of object.userData.softBook.parts)if(p.owned)p.mesh.geometry.dispose();
 for(const m of object.userData.softBook.materials)m.dispose();
}
