// Check real exported geometry, not screen coordinates. Browser QA covers the moving sheets.
import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import * as THREE from '../apps/web/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../apps/web/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {openingPose,OPENING_SECONDS,HAND_CONTACTS} from '../apps/web/src/book-animation.mjs';
const root=new URL('../',import.meta.url);
async function asset(path){const b=await readFile(new URL(path,root));return (await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'' )).scene}
const [book,hands]=await Promise.all([asset('public/assets/models/story-book.glb'),asset('public/assets/models/opening-hands.glb')]);
const cover=book.getObjectByName('CoverPivot'),right=hands.getObjectByName('RightHand'),left=hands.getObjectByName('LeftHand');
assert(cover&&right&&left,'Required hierarchy is missing');
cover.add(right);right.position.fromArray(HAND_CONTACTS.right);
book.add(left);left.position.fromArray(HAND_CONTACTS.left);
function penetrations(hand,target){
 book.updateMatrixWorld(true);const box=new THREE.Box3().setFromObject(target);let count=0,minGap=Infinity;
 hand.traverse(o=>{if(!o.isMesh||o.material.name!=='HandSkin')return;
  const p=o.geometry.attributes.position;
  for(let i=0;i<p.count;i++){
   const point=new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);
   if(box.containsPoint(point))count++;
   minGap=Math.min(minGap,box.distanceToPoint(point));
  }
 });return {verticesInside:count,minGapMetres:minGap};
}
const rightCover=penetrations(right,book.getObjectByName('Cover_BookLeather')||book.getObjectByName('FrontCover'));
function surfaceGap(hand,target){
 book.updateMatrixWorld(true);const bounds=new THREE.Box3().setFromObject(target).expandByScalar(.035),points=[];
 hand.traverse(o=>{if(!o.isMesh||o.material.name!=='HandSkin')return;const p=o.geometry.attributes.position;
  for(let i=0;i<p.count;i++){const v=new THREE.Vector3().fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);if(bounds.containsPoint(v))points.push(v)}
 });
 let gap=Infinity;const geo=target.geometry,p=geo.attributes.position,index=geo.index,closest=new THREE.Vector3();
 for(let i=0;i<(index?.count??p.count);i+=3){
  const tri=new THREE.Triangle(...[0,1,2].map(k=>new THREE.Vector3().fromBufferAttribute(p,index?index.getX(i+k):i+k).applyMatrix4(target.matrixWorld)));
  for(const v of points){tri.closestPointToPoint(v,closest);gap=Math.min(gap,v.distanceTo(closest))}
 }return gap;
}
const rightGoldGap=surfaceGap(right,book.getObjectByName('Cover_BookGold'));
const leftTopSheetGap=surfaceGap(left,book.getObjectByName('TurnPage2'));
assert(rightGoldGap<.01,'Right fingertips float away from the cover decoration');
assert(leftTopSheetGap<.01,'Left fingertips float above the top sheet');
const leftBlock=penetrations(left,book.getObjectByName('BookBlock'));
assert.equal(rightCover.verticesInside,0,'Right hand penetrates the closed cover');
assert.equal(leftBlock.verticesInside,0,'Left hand penetrates the page block');
for(let i=0;i<=380;i++){
 const p=openingPose(i/100);
 assert(p.pages[2]>=p.pages[1]&&p.pages[1]>=p.pages[0],'A lower sheet overtakes the sheet above');
 if(p.cover>0)assert.equal(p.hands,1,'Cover opens before the grip is established');
 if(p.travel>0)assert.equal(p.withdraw,1,'Lateral travel starts inside the row of books');
}
assert(openingPose(OPENING_SECONDS).pages.every(p=>p===1),'Transition ends before the pages settle');
console.log(JSON.stringify({rightCover,leftBlock,rightGoldGap,leftTopSheetGap,timelineSamples:381,status:'passed'},null,2));
