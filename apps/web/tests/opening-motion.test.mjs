import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {AnimationMixer,Group,Matrix4,PropertyBinding,Quaternion,Vector3} from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {clone} from 'three/addons/utils/SkeletonUtils.js';
import {openingPose,pagePose,OPENING_SECONDS} from '../src/opening-motion.mjs';
import {fitHandsToBook} from '../src/opening-anatomy.mjs';
import anatomy from '../src/opening-anatomy.json' with {type:'json'};
import layout from '../src/room-layout.json' with {type:'json'};

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

test('shipped hands keep one human size across lecterns without moving the grip anchor or accumulating scale',async()=>{
 const bytes=readFileSync(new URL('../../../public/assets/models/makehuman-hands.glb',import.meta.url));
 const size=bytes.readUInt32LE(12),gltf=JSON.parse(bytes.subarray(20,20+size));
 // Exercise the real shipped geometry, skeleton and clip in Three. Materials are
 // omitted only because Node has no browser image decoder; binary offsets remain.
 for(const mesh of gltf.meshes)for(const p of mesh.primitives)delete p.material;
 delete gltf.materials;delete gltf.textures;delete gltf.images;
 const json=Buffer.from(JSON.stringify(gltf)),length=Math.ceil(json.length/4)*4;
 const buffer=Buffer.alloc(20+length+bytes.length-(20+size),32);
 bytes.copy(buffer,0,0,20);buffer.writeUInt32LE(buffer.length,8);buffer.writeUInt32LE(length,12);
 json.copy(buffer,20);bytes.copy(buffer,20+length,20+size);
 const loaded=await new GLTFLoader().parseAsync(buffer.buffer.slice(buffer.byteOffset,buffer.byteOffset+buffer.length),'');
 for(const slot of layout.slots){
  const root=new Group(),object=clone(loaded.scene);root.add(object);
  root.position.fromArray(slot.position);root.rotation.set(slot.pitch,slot.yaw,0,'YXZ');root.scale.setScalar(slot.scale);
  const mixer=new AnimationMixer(object);for(const clip of loaded.animations)mixer.clipAction(clip).play();mixer.setTime(1.3);
  const arms=['Right','Left'].map(side=>{
   const arm=object.getObjectByName(`${side}Hand`),contact=arm.getObjectByName(PropertyBinding.sanitizeNodeName(side==='Right'?'finger3-3.R':'finger1-3.L'));
   assert.ok(arm&&contact);return {arm,contact,point:new Vector3()};
  });
  root.updateMatrixWorld(true);const contacts=arms.map(a=>a.contact.getWorldPosition(new Vector3()));
  for(let frame=0;frame<3;frame++){
   fitHandsToBook(arms,slot.scale);
   arms.forEach(({arm,contact},i)=>{
    assert.ok(contact.getWorldPosition(new Vector3()).distanceTo(contacts[i])<1e-6,'contact moved while fitting anatomy');
    const skin=arm.getObjectByName(`${i===0?'Right':'Left'}Skin`);
    // The skin's bind coordinates point down glTF Z from the wrist to fingertips.
    skin.geometry.computeBoundingBox();
    const handLength=-skin.geometry.boundingBox.min.z*skin.getWorldScale(new Vector3()).z;
    assert.ok(Math.abs(handLength-anatomy.handLengthMetres)<.001,`hand length ${handLength} at book scale ${slot.scale}`);
   });
  }
 }
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
 // Layered lined robes and skin/cloth surface maps have a 4 MB combined
 // budget; keep a hard bound even though the former plain sleeves were 1.5 MB.
 assert.ok(bytes.length<4000000,'hands and layered robes exceed 4 MB budget');
 const skinMaterial=gltf.materials.find(m=>m.name==='Human skin');
 assert.ok(skinMaterial.normalTexture&&skinMaterial.pbrMetallicRoughness.metallicRoughnessTexture,'skin detail maps lost in export');
 const normalImage=gltf.images[gltf.textures[skinMaterial.normalTexture.index].source];
 assert.equal(normalImage.mimeType,'image/png','skin normal must remain lossless');
 const read=(index)=>{
  const a=gltf.accessors[index],view=gltf.bufferViews[a.bufferView],n={SCALAR:1,VEC3:3,VEC4:4}[a.type];
  const scalarBytes={5121:1,5123:2,5126:4}[a.componentType];
  assert.ok(n&&scalarBytes);
  return Array.from({length:a.count},(_,i)=>Array.from({length:n},(_,j)=>{
   const at=binStart+(view.byteOffset??0)+(a.byteOffset??0)+i*(view.byteStride??n*scalarBytes)+j*scalarBytes;
   return scalarBytes===4?bytes.readFloatLE(at):scalarBytes===2?bytes.readUInt16LE(at):bytes.readUInt8(at);
  }));
 };
 assert.ok(!gltf.nodes.some(n=>n.name?.includes('InnerSleeve')),'rejected fitted sleeve returned');
 // Exercise the exported changes, not only the presence of authoring controls.
 for(const side of ['R','L']){
  const clothNodes=new Set(gltf.nodes.map((n,i)=>n.name?.startsWith('robe_')&&n.name.endsWith('.'+side)?i:-1).filter(i=>i>=0));
  const motion=clip.channels.filter(c=>clothNodes.has(c.target.node)&&c.target.path==='translation');
  assert.ok(motion.some(c=>{
   const values=read(clip.samplers[c.sampler].output);
   return [0,1,2].some(axis=>Math.max(...values.map(v=>v[axis]))-Math.min(...values.map(v=>v[axis]))>.005);
  }),'sleeve exported as a rigid forearm tube');
  const node=gltf.nodes.findIndex(n=>n.name===(side==='R'?'RightSkin':'LeftSkin'));
  const channel=clip.channels.find(c=>c.target.node===node&&c.target.path==='weights');
  assert.ok(channel,'skin flexion correction lost in export');
  const values=read(clip.samplers[channel.sampler].output).flat();
  assert.ok(Math.max(...values)-Math.min(...values)>.025,'skin corrective is static');
  assert.ok(values.every(v=>v>=0&&v<=1),'skin corrective weight outside its safe range');
 }
 for(const node of gltf.nodes.filter(n=>n.mesh!==undefined)){
  assert.ok(node.skin!==undefined,'unskinned hand piece');
  const rig=gltf.skins[node.skin],names=rig.joints.map(i=>gltf.nodes[i].name);
  assert.equal(names.filter(n=>!n.startsWith('robe_')).length,21,'human anatomy changed unexpectedly');
  assert.ok(names.some(n=>n.startsWith('robe_')),'cloth deformation rig missing');
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

test('the raised-cover poses avoid the previous folded right-wrist silhouette',()=>{
 // Test the shipped animation, not a second implementation of the Blender pose formula.
 const bytes=readFileSync(new URL('../../../public/assets/models/makehuman-hands.glb',import.meta.url));
 const size=bytes.readUInt32LE(12),gltf=JSON.parse(bytes.subarray(20,20+size)),binStart=28+size;
 const read=index=>{
  const a=gltf.accessors[index],view=gltf.bufferViews[a.bufferView],width={SCALAR:1,VEC3:3,VEC4:4}[a.type];
  assert.equal(a.componentType,5126);
  return Array.from({length:a.count},(_,i)=>Array.from({length:width},(_,j)=>bytes.readFloatLE(binStart+(view.byteOffset??0)+(a.byteOffset??0)+i*(view.byteStride??width*4)+j*4)));
 };
 const parents=new Map();gltf.nodes.forEach((n,i)=>n.children?.forEach(child=>parents.set(child,i)));
 const index=name=>{const i=gltf.nodes.findIndex(n=>n.name===name);assert.ok(i>=0,`missing ${name}`);return i;};
 const fore=index('lowerarm02.R'),wrist=index('wrist.R'),middle=index('finger3-1.R');
 const tracks=gltf.animations[0].channels.map(c=>{
  const sampler=gltf.animations[0].samplers[c.sampler];
  assert.ok(['LINEAR','STEP'].includes(sampler.interpolation??'LINEAR'));
  return {node:c.target.node,path:c.target.path,interpolation:sampler.interpolation??'LINEAR',times:read(sampler.input).flat(),values:read(sampler.output)};
 });
 for(let frame=45;frame<=57;frame++){
  const time=frame/30,poses=gltf.nodes.map(n=>({translation:n.translation??[0,0,0],rotation:n.rotation??[0,0,0,1],scale:n.scale??[1,1,1]}));
  for(const track of tracks){
   let hi=track.times.findIndex(t=>t>=time);if(hi<0)hi=track.times.length-1;
   const lo=Math.max(0,hi-1),fraction=hi===lo?0:(time-track.times[lo])/(track.times[hi]-track.times[lo]);
   if(track.interpolation==='STEP'){poses[track.node][track.path]=track.values[Math.abs(time-track.times[hi])<1e-6?hi:lo];continue;}
   poses[track.node][track.path]=track.path==='rotation'
    ?new Quaternion().fromArray(track.values[lo]).slerp(new Quaternion().fromArray(track.values[hi]),fraction).toArray()
    :track.values[lo].map((v,j)=>v+(track.values[hi][j]-v)*fraction);
  }
  const worlds=new Map();
  const world=i=>{
   if(worlds.has(i))return worlds.get(i);
   const p=poses[i],m=new Matrix4().compose(new Vector3().fromArray(p.translation),new Quaternion().fromArray(p.rotation),new Vector3().fromArray(p.scale));
   if(parents.has(i))m.premultiply(world(parents.get(i)));worlds.set(i,m);return m;
  };
  const position=i=>new Vector3().setFromMatrixPosition(world(i));
  const joint=position(wrist),armDirection=joint.clone().sub(position(fore)),palmDirection=position(middle).sub(joint);
  const degrees=armDirection.angleTo(palmDirection)*180/Math.PI;
  // The new side pinch has a different low pose. Guard the reported high-pose
  // regression only; this axis angle is not a medical limit or visual acceptance.
  assert.ok(degrees<=45,`right wrist bends ${degrees.toFixed(1)} degrees at ${time.toFixed(2)}s`);
 }
});
