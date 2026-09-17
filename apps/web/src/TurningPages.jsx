import React,{useEffect,useMemo,useRef} from 'react';
import {useFrame} from '@react-three/fiber';
import * as THREE from 'three';
import {pagePose} from './opening-motion.mjs';

function Page({index,clock}) {
 const mesh=useRef();
 const geometry=useMemo(()=>{
  const g=new THREE.PlaneGeometry(.70,.925,28,12);
  g.attributes.position.setUsage(THREE.DynamicDrawUsage);
  return g;
 },[]);
 useEffect(()=>()=>geometry.dispose(),[geometry]);
 useFrame(()=>{
  const p=pagePose(clock.current,index),positions=geometry.attributes.position;
  // Integrate the tangent along the sheet: it bends without stretching like rubber.
  let x=0,y=0;
  for(let col=0;col<=28;col++){
   const u=col/28;
   if(col){const a=p.angle+p.curl*Math.sin((u-.5/28)*Math.PI*1.35);
    x+=.70/28*Math.cos(a);y+=.70/28*Math.sin(a);}
   for(let row=0;row<=12;row++){
    const z=(row/12-.5)*.925;
    positions.setXYZ(row*29+col,-.345+x,.185+index*.0025+y+p.lift*Math.sin(u*Math.PI)*Math.cos(z*2),z);
   }
  }
  positions.needsUpdate=true;geometry.computeVertexNormals();
 });
 return <mesh ref={mesh} geometry={geometry} castShadow receiveShadow frustumCulled={false} raycast={()=>null}>
  <meshStandardMaterial color={['#d8c4a0','#d2bd97','#decca9'][index]} emissive="#b8a17e" emissiveIntensity={.13} roughness={.91} side={THREE.DoubleSide}/>
 </mesh>;
}
export function TurningPages({clock}) {return <group>{[0,1,2].map(i=><Page key={i} index={i} clock={clock}/>)}</group>}
