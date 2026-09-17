import React,{useMemo,useEffect} from 'react';
import {useFrame,useThree} from '@react-three/fiber';
import {useGLTF} from '@react-three/drei';
import {clone} from 'three/addons/utils/SkeletonUtils.js';
import * as THREE from 'three';
import {OPENING_SECONDS} from './opening-motion.mjs';
import {fitHandsToBook} from './opening-anatomy.mjs';
import layout from './room-layout.json';

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
   arm.traverse(node=>{if(node.isBone&&node.name===THREE.PropertyBinding.sanitizeNodeName(`finger1-3.${side[0]}`))contact=node;});
   if(!contact)throw new Error(`Missing ${side} hand contact bone`);
   return {arm,contact,point:new THREE.Vector3()};
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
  rig.mixer.setTime(Math.max(0,Math.min(OPENING_SECONDS,clock.current)));
  if(bookIndex!=null)fitHandsToBook(rig.arms,layout.slots[bookIndex].scale??1);
  rig.object.visible=clock.current>0&&clock.current<OPENING_SECONDS;
 });
 if(bookIndex==null)return null;
 const slot=layout.slots[bookIndex];
 return <group position={slot.position} rotation={[slot.pitch??layout.lectern.pitch,slot.yaw,0,'YXZ']} scale={slot.scale??1}>
  <primitive object={rig.object}/>
 </group>;
}
useGLTF.preload('/assets/models/makehuman-hands.glb');
