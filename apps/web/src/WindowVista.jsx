import React,{useMemo} from 'react';
import {useGLTF,useTexture} from '@react-three/drei';
import * as THREE from 'three';

const COLORS={VistaNear:'#0b1b27',VistaMiddle:'#0a1d2c',VistaFar:'#122b41',VistaRidge:'#1c3852'};
const noPick=()=>{};
const TEXTURES=['/assets/textures/window-bark-v2.webp','/assets/textures/window-sky-v2.webp','/assets/textures/window-needles-v2.webp'];

export function WindowVista(){
 const {scene}=useGLTF('/assets/models/window-vista.glb');
 const [atlas,sky,needles]=useTexture(TEXTURES);
 const object=useMemo(()=>{
  for(const texture of [atlas,sky,needles]){texture.flipY=false;texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;}
  const root=scene.clone(true);root.name='MoonlitWindow';
  root.updateMatrixWorld(true);
  const aperture=new THREE.Sphere(new THREE.Vector3(0,2.45,-4.2),1.65);
  root.traverse(o=>{if(!o.isMesh)return;
   const name=o.material.name;
   if(name.endsWith('Needles')){
    o.material=new THREE.MeshBasicMaterial({color:name==='VistaNeedles'?'#b5c4ce':name==='VistaMiddleNeedles'?'#0a1d2c':'#122b41',map:needles,alphaTest:.12,side:THREE.DoubleSide,fog:false,toneMapped:false});
    o.material.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`vec4 needleSample=texture2D(map,vMapUv); diffuseColor.a *= min(1.0,needleSample.a*2.5); ${name==='VistaNeedles'?'diffuseColor.rgb *= needleSample.rgb;':''}`);};
    o.material.customProgramCacheKey=()=> `window-needles-alpha-2-${name}`;
   }
   else if(name==='VistaWindowJoin')o.material=new THREE.MeshStandardMaterial({color:'#382218',roughness:1,fog:true});
   else if(name==='VistaGlass')o.material=new THREE.MeshBasicMaterial({color:'#829bb3',opacity:.018,transparent:true,depthWrite:false,side:THREE.DoubleSide,fog:false,toneMapped:false});
   else if(name==='VistaBark')o.material=new THREE.MeshStandardMaterial({color:'#4f6273',map:atlas,roughness:1,fog:false});
   else if(name==='VistaNear')o.material=new THREE.MeshBasicMaterial({color:'#0c1e2d',fog:false,toneMapped:false});
   else {
    o.material=new THREE.MeshBasicMaterial({color:COLORS[name]??'#ffffff',map:name==='VistaSky'?sky:null,side:THREE.DoubleSide,fog:false,toneMapped:false});
    if(name==='VistaSky'){
     o.material.color.setRGB(1.10,1.12,1.06);
     // Blend inside the image boundary: clamping outside stretched edge clouds into a rectangle.
     o.material.onBeforeCompile=shader=>{shader.fragmentShader=shader.fragmentShader.replace('#include <map_fragment>',`vec2 skyUV=vMapUv; vec4 skySample=texture2D(map,skyUV); vec4 edgeColor=texture2D(map,vec2(0.5,clamp(skyUV.y,0.0,1.0))); float insideX=smoothstep(0.0,0.28,skyUV.x)*smoothstep(0.0,0.28,1.0-skyUV.x); float insideY=smoothstep(0.0,0.16,skyUV.y)*smoothstep(0.0,0.16,1.0-skyUV.y); diffuseColor *= mix(edgeColor,skySample,insideX*insideY);`);};
     o.material.customProgramCacheKey=()=> 'window-sky-extended-2';
    }

   }
   o.material.defines={...o.material.defines,STORYOS_WINDOW_VISTA:1,...(name==='VistaSky'?{STORYOS_WINDOW_SKY:1}:{})};
   // Exterior scenery can only be seen through this window. Use its conservative
   // bounds for native frustum culling, including after camera movement this frame.
   o.boundingSphere=aperture.clone().applyMatrix4(o.matrixWorld.clone().invert());
   o.raycast=noPick;o.castShadow=false;o.receiveShadow=false;
  });
  return root;
 },[scene,atlas,sky,needles]);
 return <primitive object={object}/>;
}

useGLTF.preload('/assets/models/window-vista.glb');
// Preload the same grouped cache key consumed by useTexture above.
useTexture.preload(TEXTURES);
