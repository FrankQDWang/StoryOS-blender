import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {openingPose,pagePose,OPENING_SECONDS} from '../src/opening-motion.mjs';

test('cover opens before pages; sheets stay ordered, never overtake the cover, and settle before entry',()=>{
 let previousCover=0;
 for(let t=0;t<=OPENING_SECONDS;t+=1/120){
  const cover=openingPose(t),pages=[0,1,2].map(i=>pagePose(t,i));
  assert.ok(cover.angle>=previousCover-1e-9,'cover reverses');previousCover=cover.angle;
  assert.ok(pages.every(p=>p.angle+p.curl<=cover.angle+.001),'a bent sheet crosses the cover');
  assert.ok(pages[0].angle<=pages[1].angle+.001&&pages[1].angle<=pages[2].angle+.001,'sheets overtake each other');
  if(cover.angle===0)assert.ok(pages.every(p=>p.angle===0),'pages move through a closed cover');
 }
 assert.equal(openingPose(OPENING_SECONDS).visible,false);
 assert.equal(openingPose(OPENING_SECONDS-.1).release,1);
 assert.ok([0,1,2].every(i=>Math.abs(pagePose(OPENING_SECONDS-.1,i).curl)<1e-9));
});

test('MakeHuman hands retain complete weighted anatomy and a synchronized baked clip',()=>{
 const bytes=readFileSync(new URL('../../../public/assets/models/makehuman-hands.glb',import.meta.url));
 const size=bytes.readUInt32LE(12),gltf=JSON.parse(bytes.subarray(20,20+size));
 const binStart=20+size+8;
 assert.equal(gltf.skins.length,2);
 assert.equal(gltf.animations.length,1);
 const clip=gltf.animations[0];
 const animated=new Set(clip.channels.map(c=>c.target.node));
 for(const skin of gltf.skins)for(const joint of skin.joints)assert.ok(animated.has(joint),'joint missing from the baked clip');
 for(const sampler of clip.samplers){const time=gltf.accessors[sampler.input];assert.deepEqual(time.min,[0]);assert.deepEqual(time.max,[OPENING_SECONDS]);}
 assert.ok(bytes.length<1500000,'hand asset exceeds 1.5 MB budget');
 const read=(index)=>{
  const a=gltf.accessors[index],view=gltf.bufferViews[a.bufferView],n={SCALAR:1,VEC4:4}[a.type];
  const scalarBytes={5121:1,5123:2,5126:4}[a.componentType];
  assert.ok(n&&scalarBytes);
  return Array.from({length:a.count},(_,i)=>Array.from({length:n},(_,j)=>{
   const at=binStart+(view.byteOffset??0)+(a.byteOffset??0)+i*(view.byteStride??n*scalarBytes)+j*scalarBytes;
   return scalarBytes===4?bytes.readFloatLE(at):scalarBytes===2?bytes.readUInt16LE(at):bytes.readUInt8(at);
  }));
 };
 for(const node of gltf.nodes.filter(n=>n.mesh!==undefined)){
  assert.ok(node.skin!==undefined,'unskinned hand piece');
  const rig=gltf.skins[node.skin],names=rig.joints.map(i=>gltf.nodes[i].name);
  assert.equal(names.length,21);
  assert.ok(names.some(n=>n.startsWith('wrist.')));
  assert.ok(names.some(n=>n.startsWith('lowerarm02.')));
  for(let digit=1;digit<=5;digit++)for(let i=1;i<=3;i++)assert.ok(names.some(n=>n.startsWith(`finger${digit}-${i}.`)));
  for(const p of gltf.meshes[node.mesh].primitives){
   const weights=read(p.attributes.WEIGHTS_0),joints=read(p.attributes.JOINTS_0);
   assert.equal(weights.length,joints.length);
   weights.forEach((w,i)=>{assert.ok(w.every(Number.isFinite));assert.ok(Math.abs(w.reduce((a,b)=>a+b,0)-1)<.002);assert.ok(joints[i].every(j=>j<rig.joints.length));});
  }
 }
});
