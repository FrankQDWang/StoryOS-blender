import React,{useEffect,useMemo} from 'react';
import * as THREE from 'three';

// A surface layer on the three existing logs, using their original centres.
// No new collision, room rebuild or light is needed for the charred grain.
export function HearthBed(){
 const materials=useMemo(()=>{
  const bark=new THREE.MeshStandardMaterial({color:'#302319',roughness:.98,emissive:'#ec4b08',emissiveIntensity:.22});
  bark.onBeforeCompile=shader=>{
   shader.vertexShader='varying vec3 vLog;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n vLog=position;');
   shader.fragmentShader='varying vec3 vLog;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
    float a=atan(vLog.x,vLog.z);float bands=sin(a*17.0+sin(vLog.y*23.0+a)*.6);
    float grain=.65+.35*sin(a*39.0+vLog.y*7.0);diffuseColor.rgb*=grain;
    float cracks=pow(max(0.0,bands),24.0)*(.4+.6*sin(vLog.y*32.0+a*4.0)*sin(vLog.y*32.0+a*4.0));`);
   shader.fragmentShader=shader.fragmentShader.replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n totalEmissiveRadiance*=cracks;');
  };
  const end=new THREE.MeshStandardMaterial({color:'#59412a',roughness:.99,emissive:'#b56b30',emissiveIntensity:.18});
  end.onBeforeCompile=shader=>{
   shader.vertexShader='varying vec2 vCut;\n'+shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n vCut=position.xy;');
   shader.fragmentShader='varying vec2 vCut;\n'+shader.fragmentShader;
   shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`#include <color_fragment>
    float r=length(vCut);float a=atan(vCut.y,vCut.x);
    float rings=sin(r*450.0+sin(a*3.0+r*37.0)*.7);
    float split=pow(max(0.0,cos(a*3.0+sin(r*35.0)*.16)),65.0)*smoothstep(.015,.055,r);
    float endGrain=mix(.32,1.10,smoothstep(-.55,.15,rings))*(1.0-split*.88)*(1.0-smoothstep(.072,.105,r)*.8);diffuseColor.rgb*=endGrain;`);
   shader.fragmentShader=shader.fragmentShader.replace('#include <emissivemap_fragment>','#include <emissivemap_fragment>\n totalEmissiveRadiance*=endGrain;');
  };
  const soot=new THREE.ShaderMaterial({transparent:true,depthWrite:false,
   vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
   fragmentShader:'varying vec2 vUv;void main(){float edge=sin(vUv.x*3.14159)*sin(vUv.y*3.14159);float streak=.75+.25*sin(vUv.x*61.+sin(vUv.y*9.));gl_FragColor=vec4(.06,.038,.018,pow(max(0.,edge),1.4)*streak*.34);}'
  });
  return {bark,end,soot};
 },[]);
 useEffect(()=>()=>Object.values(materials).forEach(m=>m.dispose()),[materials]);
 return <group>
  {[.55,.04,-.44].map((z,i)=><group key={z}>
   <mesh position={[-.05,.3885,z]} rotation={[0,0,Math.PI/2]} material={materials.bark} castShadow receiveShadow raycast={()=>null}><cylinderGeometry args={[.105,.103,.732,14,8]}/></mesh>
   <mesh position={[.318,.3885,z]} rotation={[0,Math.PI/2,0]} material={materials.end} receiveShadow raycast={()=>null}><circleGeometry args={[.102,20]}/></mesh>
  </group>)}
  {Array.from({length:9},(_,i)=><mesh key={i} position={[-.04+(i%3)*.07,.345, -.48+i*.115]} scale={[.07,.025,.052]} rotation={[0,i*.7,0]} raycast={()=>null}>
   <icosahedronGeometry args={[1,1]}/><meshStandardMaterial color="#241b15" emissive="#f05408" emissiveIntensity={.7+(i%3)*.3} roughness={1}/>
  </mesh>)}
  <mesh position={[-.303,1.06,0]} rotation={[0,Math.PI/2,0]} material={materials.soot} raycast={()=>null}><planeGeometry args={[1.06,.83]}/></mesh>
 </group>;
}
