import React,{useMemo,useEffect} from 'react';
import {useFrame,useThree} from '@react-three/fiber';
import {useGLTF} from '@react-three/drei';
import {clone} from 'three/addons/utils/SkeletonUtils.js';
import * as THREE from 'three';
import {OPENING_SECONDS} from './opening-motion.mjs';
import {fitHandsToBook} from './opening-anatomy.mjs';
import layout from './room-layout.json';
import {handSupportTransform} from './soft-book-shape.mjs';
import {handClipTime} from './book-support.mjs';
import {smoothRange} from './opening-motion.mjs';

export function OpeningHands({clock,bookIndex}) {
 const invalidate=useThree(state=>state.invalidate);
 const {scene,animations}=useGLTF('/assets/models/makehuman-hands.glb');
 const rig=useMemo(()=>{
  const object=clone(scene);
  object.traverse(node=>{if(node.isMesh){node.castShadow=true;node.receiveShadow=false;node.frustumCulled=false;}});
  const mixer=new THREE.AnimationMixer(object);
  const actions=[];
  for(const clip of animations){const action=mixer.clipAction(clip);action.setLoop(THREE.LoopOnce,1);action.clampWhenFinished=true;actions.push(action);}
  const arms=['Right','Left'].map(side=>{
   const arm=object.getObjectByName(`${side}Hand`);
   let contact;
   // The right hand now supports the large cover on its middle finger pad.
   // Fit anatomy around that support, so smaller lecterns do not move it
   // around the formerly used, now relaxed thumb.
   const anchor=side==='Right'?'finger3-3.R':'finger1-3.L';
   arm.traverse(node=>{if(node.isBone&&node.name===THREE.PropertyBinding.sanitizeNodeName(anchor))contact=node;});
   if(!contact)throw new Error(`Missing ${side} hand contact bone`);
   return {side,arm,contact,point:new THREE.Vector3(),offset:[0,0,0]};
  });
  return {object,mixer,actions,arms};
 },[scene,animations]);
 useEffect(()=>{
  // React StrictMode replays effects; each setup must restart actions stopped by cleanup.
  for(const action of rig.actions)action.reset().play();
  invalidate();
  return ()=>rig.mixer.stopAllAction();
 },[rig,invalidate]);
 useFrame(()=>{
  for(const action of rig.actions)action.paused=false;
  rig.mixer.setTime(Math.max(0,Math.min(OPENING_SECONDS,handClipTime(clock.current))));
  if(bookIndex!=null){
   for(const {arm} of rig.arms)arm.rotation.set(0,0,0);
   fitHandsToBook(rig.arms,layout.slots[bookIndex].scale??1);
   for(const {side,arm} of rig.arms){
    const time=clock.current;
    if(side==='Left'){arm.position.y-=.068*smoothRange(time,.1,.72)*(1-smoothRange(time,2,3.15));continue;}
    const {angle,old,target,weight}=handSupportTransform(time),c=Math.cos(angle),s=Math.sin(angle);
    const x=arm.position.x-old[0],y=arm.position.y-old[1];
    arm.position.x=old[0]+x*c-y*s+(target[0]-old[0])*weight;
    arm.position.y=old[1]+x*s+y*c+(target[1]-old[1])*weight;
    arm.position.z+=(target[2]-old[2])*weight;arm.rotation.z=angle;
   }
  }
  rig.object.visible=clock.current>0&&clock.current<OPENING_SECONDS;
 });
 if(bookIndex==null)return null;
 const slot=layout.slots[bookIndex];
 return <group position={slot.position} rotation={[slot.pitch??layout.lectern.pitch,slot.yaw,0,'YXZ']} scale={slot.scale??1}>
  <primitive object={rig.object}/>
 </group>;
}
useGLTF.preload('/assets/models/makehuman-hands.glb');
