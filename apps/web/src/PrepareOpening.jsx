import {useEffect} from 'react';
import {useThree} from '@react-three/fiber';
import {useGLTF} from '@react-three/drei';
import {WebGLRenderTarget,HalfFloatType,Scene} from 'three';

// The GLB is already loaded by Room; prepare its GPU resources between interactions.
export function PrepareOpening(){
 const {gl,scene,camera}=useThree();
 const {scene:source}=useGLTF('/assets/models/makehuman-hands.glb');
 useEffect(()=>{
  const actor=source.clone(true),textures=new Set();
  actor.traverse(node=>{
   if(!node.isMesh)return;
   node.receiveShadow=false;node.frustumCulled=false;
   for(const material of (Array.isArray(node.material)?node.material:[node.material])){
    for(const value of Object.values(material))if(value?.isTexture)textures.add(value);
   }
  });
  const queue=[...textures];let cancelled=false,timer;
  const prepare=()=>{
   if(cancelled)return;
   if(queue.length){gl.initTexture(queue.shift());timer=setTimeout(prepare,32)}
   else {
    const target=new WebGLRenderTarget(1,1,{type:HalfFloatType});
    const staging=new Scene();staging.fog=scene.fog;staging.environment=scene.environment;
    scene.traverseVisible(node=>{if(node.isLight)staging.add(node.clone())});
    staging.add(actor);
    const previous=gl.getRenderTarget();
    gl.setRenderTarget(target);
    const compiled=gl.compileAsync(actor,camera,scene);
    gl.setRenderTarget(previous);
    compiled.then(()=>{
     if(cancelled){target.dispose();return}
     const previous=gl.getRenderTarget(),auto=gl.shadowMap.autoUpdate,dirty=gl.shadowMap.needsUpdate;
     // One offscreen draw also prepares geometry and morph textures, which compileAsync does not upload.
     gl.shadowMap.autoUpdate=false;gl.shadowMap.needsUpdate=false;
     try{gl.setRenderTarget(target);gl.render(staging,camera)}
     finally{gl.setRenderTarget(previous);gl.shadowMap.autoUpdate=auto;gl.shadowMap.needsUpdate=dirty;target.dispose()}
    });
   }
  };
  // Let the first visible room frame finish before uploading actor textures.
  timer=setTimeout(prepare,250);
  return()=>{cancelled=true;clearTimeout(timer)};
 },[gl,scene,camera,source]);
 return null;
}
