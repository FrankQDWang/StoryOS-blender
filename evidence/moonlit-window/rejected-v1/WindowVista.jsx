import React,{useMemo} from 'react';
import {useGLTF,useTexture} from '@react-three/drei';
import * as THREE from 'three';

const COLORS={VistaNear:'#0b1b27',VistaMiddle:'#10283a',VistaFar:'#17334b',VistaRidge:'#1c3852'};
const noPick=()=>{};

export function WindowVista(){
 const {scene}=useGLTF('/assets/models/window-vista.glb');
 const atlas=useTexture('/assets/textures/window-vista.webp');
 const object=useMemo(()=>{
  atlas.flipY=false;atlas.colorSpace=THREE.SRGBColorSpace;atlas.anisotropy=4;
  const root=scene.clone(true);root.name='MoonlitWindow';
  root.traverse(o=>{if(!o.isMesh)return;
   const name=o.material.name;
   if(name==='VistaWindowJoin')o.material=new THREE.MeshStandardMaterial({color:'#382218',roughness:1,fog:true});
   else if(name==='VistaGlass')o.material=new THREE.MeshBasicMaterial({color:'#829bb3',opacity:.018,transparent:true,depthWrite:false,side:THREE.DoubleSide,fog:false,toneMapped:false});
   else if(name==='VistaBark')o.material=new THREE.MeshStandardMaterial({color:'#4f6273',map:atlas,roughness:1,fog:false});
   else if(name==='VistaNear')o.material=new THREE.MeshStandardMaterial({color:'#172c3b',roughness:1,fog:false});
   else {
    o.material=new THREE.MeshBasicMaterial({color:COLORS[name]??'#ffffff',map:name==='VistaSky'||name==='VistaMoon'?atlas:null,side:THREE.DoubleSide,fog:false,toneMapped:false});
    if(name==='VistaMoon'){
     o.material.color.set('#acb8c4');o.material.alphaTest=.08;
     o.material.onBeforeCompile=shader=>{
      shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>','#include <map_fragment>\n diffuseColor.a *= smoothstep(0.018,0.085,max(diffuseColor.r,max(diffuseColor.g,diffuseColor.b)));');
     };
     o.material.customProgramCacheKey=()=> 'window-moon-cutout-1';
    }
   }
   o.material.defines={...o.material.defines,STORYOS_WINDOW_VISTA:1,...(name==='VistaSky'?{STORYOS_WINDOW_SKY:1}:{})};
   o.raycast=noPick;o.castShadow=false;o.receiveShadow=false;
  });
  return root;
 },[scene,atlas]);
 return <primitive object={object}/>;
}

useGLTF.preload('/assets/models/window-vista.glb');
useTexture.preload('/assets/textures/window-vista.webp');
