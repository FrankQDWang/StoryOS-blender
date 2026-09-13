import React,{useEffect,useMemo,useRef} from 'react';
import {useFrame} from '@react-three/fiber';
import {useGLTF} from '@react-three/drei';
import * as THREE from 'three';
import layout from './room-layout.json';
import {ease,openingPose,HAND_CONTACTS} from './book-animation.mjs';

export function cloneAsset(scene,bookColor){
 const copy=scene.clone(true);
 copy.traverse(o=>{if(!o.isMesh)return;o.castShadow=true;o.receiveShadow=true;o.material=o.material.clone();
  if(o.material.name==='BookLeather'&&bookColor)o.material.color.set(bookColor);
  if(o.name.startsWith('TurnPage')){o.geometry=o.geometry.clone();o.material.side=THREE.DoubleSide}
 });return copy;
}
export function slotRotation(index){
 return new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),layout.slots[index].yaw)
  .multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),Math.PI/2));
}
function makeSleeve(){
 const rows=20,columns=10,positions=new Float32Array((rows+1)*(columns+1)*3),indices=[];
 for(let i=0;i<rows;i++)for(let j=0;j<columns;j++){const a=i*(columns+1)+j;indices.push(a,a+1,a+columns+1,a+1,a+columns+2,a+columns+1)}
 const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setIndex(indices);
 const mesh=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:'#263d40',roughness:1,side:THREE.DoubleSide}));mesh.castShadow=true;
 return mesh;
}
function updateSleeve(mesh,hand,root,side){
 root.updateMatrixWorld(true);
 const start=root.worldToLocal(hand.localToWorld(new THREE.Vector3(0,0,.19)));
 const tangent=root.worldToLocal(hand.localToWorld(new THREE.Vector3(0,0,.32))).sub(start).normalize();
 const end=new THREE.Vector3(side*.65,-.12,1.60);
 const control=start.clone().addScaledVector(tangent,.25);control.z=Math.max(control.z,.80);
 const curve=new THREE.QuadraticBezierCurve3(start,control,end),positions=mesh.geometry.attributes.position;
 for(let i=0;i<=20;i++){
  const u=i/20,center=curve.getPoint(u),direction=curve.getTangent(u);
  const right=new THREE.Vector3().crossVectors(direction,new THREE.Vector3(0,1,0)).normalize(),up=new THREE.Vector3().crossVectors(right,direction).normalize();
  const radius=.067+.018*u;
  for(let j=0;j<=10;j++){const a=j/10*Math.PI*2,v=center.clone().addScaledVector(right,Math.cos(a)*radius).addScaledVector(up,Math.sin(a)*radius*.73);positions.setXYZ(i*11+j,v.x,v.y,v.z)}
 }
 positions.needsUpdate=true;mesh.geometry.computeVertexNormals();mesh.geometry.computeBoundingSphere();mesh.visible=hand.visible;
}
const deskRotation=new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0,1,0),layout.deskYaw);
export function OpeningBook({book,inspectTime=null}){
 const source=useGLTF('/assets/models/story-book.glb');
 const handSource=useGLTF('/assets/models/opening-hands.glb');
 const assembly=useMemo(()=>{
  const object=cloneAsset(source.scene,book.color);
  const cover=object.getObjectByName('CoverPivot');
  const hands=cloneAsset(handSource.scene);
  const left=hands.getObjectByName('LeftHand'),right=hands.getObjectByName('RightHand');
  object.add(left);cover.add(right);
  const leftSleeve=makeSleeve(),rightSleeve=makeSleeve();object.add(leftSleeve,rightSleeve);
  right.rotation.y=0;
  const pages=[0,1,2].map(i=>({pivot:object.getObjectByName(`PagePivot${i}`),mesh:object.getObjectByName(`TurnPage${i}`)}));
  for(const page of pages)page.original=page.mesh.geometry.attributes.position.array.slice();
  return {object,cover,left,right,pages,leftSleeve,rightSleeve};
 },[source.scene,handSource.scene,book.color]);
 useEffect(()=>()=>{
  assembly.object.traverse(o=>{if(o.isMesh)o.material.dispose()});
  assembly.pages.forEach(p=>p.mesh.geometry.dispose());
  assembly.leftSleeve.geometry.dispose();assembly.rightSleeve.geometry.dispose();
 },[assembly]);
 const ref=useRef(),elapsed=useRef(0);
 const from=useMemo(()=>new THREE.Vector3(...layout.slots[book.slot??0].position),[book.slot]);
 const fromRotation=useMemo(()=>slotRotation(book.slot??0),[book.slot]);
 useFrame((_,dt)=>{
  elapsed.current+=Math.min(dt,.05);
  const p=openingPose(inspectTime??elapsed.current);
  const exit=from.clone().add(new THREE.Vector3(0,0,1.10));
  ref.current.position.copy(from).lerp(exit,p.withdraw).lerp(new THREE.Vector3(...layout.deskBook),p.travel);
  ref.current.position.y+=.45*Math.sin(p.travel*Math.PI);
  ref.current.quaternion.copy(fromRotation).slerp(deskRotation,p.travel);
  assembly.cover.rotation.z=p.cover;
  // The right hand is a child of the actual cover hinge: its grip cannot drift.
  assembly.right.position.fromArray(HAND_CONTACTS.right).addScaledVector(new THREE.Vector3(.10,.10,.40),1-p.hands);
  assembly.left.position.fromArray(HAND_CONTACTS.left).addScaledVector(new THREE.Vector3(0,-.09,.48),1-p.leftHand);
  assembly.right.visible=p.hands>.001;assembly.left.visible=p.leftHand>.001;
  updateSleeve(assembly.leftSleeve,assembly.left,assembly.object,-1);
  updateSleeve(assembly.rightSleeve,assembly.right,assembly.object,1);
  assembly.pages.forEach(({pivot,mesh,original},i)=>{
   const turn=p.pages[i];pivot.rotation.z=2.80*turn;
   const positions=mesh.geometry.attributes.position;
   // Arch the sheet during the turn; endpoints flatten as it comes to rest.
   for(let j=0;j<positions.count;j++){
    const x=original[j*3];positions.setY(j,original[j*3+1]+.12*Math.sin(Math.PI*x/.70)*Math.sin(Math.PI*turn));
   }
   positions.needsUpdate=true;mesh.geometry.computeVertexNormals();
  });
 });
 return <group ref={ref} scale={layout.bookScale}><primitive object={assembly.object}/></group>;
}
export function CreatingBook({book}){
 const {scene}=useGLTF('/assets/models/story-book.glb');
 const object=useMemo(()=>cloneAsset(scene,book.color),[scene,book.color]);
 const pieces=useMemo(()=>object.children.map((o,i)=>({o,base:o.position.clone(),offset:new THREE.Vector3(Math.sin(i*2.4)*.28,.32+(i%4)*.12,Math.cos(i*2.4)*.26)})),[object]);
 const ref=useRef(),elapsed=useRef(0);
 const start=useMemo(()=>new THREE.Vector3(...layout.magic).add(new THREE.Vector3(0,.48,0)),[]);
 const dest=useMemo(()=>book.slot!==null?new THREE.Vector3(...layout.slots[book.slot].position):start.clone().add(new THREE.Vector3(0,1,0)),[book.slot,start]);
 const rotation=useMemo(()=>book.slot!==null?slotRotation(book.slot):deskRotation,[book.slot]);
 useFrame((_,dt)=>{
  elapsed.current+=Math.min(dt,.05);const t=elapsed.current,assemble=1-ease(t,0,1.2),fly=ease(t,1.45,3);
  pieces.forEach(({o,base,offset})=>o.position.copy(base).addScaledVector(offset,assemble));
  if(book.slot!==null){
   const approach=ease(t,1.45,2.55),insert=ease(t,2.55,3.0);
   const outside=dest.clone().add(new THREE.Vector3(0,0,1.10));
   ref.current.position.copy(start).lerp(outside,approach).lerp(dest,insert);
   ref.current.position.y+=Math.sin(approach*Math.PI)*.45;
   ref.current.quaternion.copy(deskRotation).slerp(rotation,approach);
  }else{
   ref.current.position.copy(start).lerp(dest,fly);
   ref.current.quaternion.copy(deskRotation);
  }
  ref.current.scale.setScalar(layout.bookScale*ease(t,0,.4)*(book.slot===null?1-fly:1));
 });
 return <group ref={ref} position={start.toArray()}><primitive object={object}/><pointLight color="#bbdebc" intensity={1} distance={2}/></group>;
}
