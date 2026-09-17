import React,{useEffect,useMemo,useRef} from 'react';
import {useFrame} from '@react-three/fiber';
import * as THREE from 'three';
import layout from './room-layout.json';
import {HearthBed} from './HearthBed';
import {RectAreaLightUniformsLib} from 'three/addons/lights/RectAreaLightUniformsLib.js';
RectAreaLightUniformsLib.init();
const HEARTH=layout.fixtures.find(f=>f.id==='hearth').center;
const SHIFT=HEARTH[0]+4.14;

// Closed, curved volumes keep the fire legible while walking around the hearth.
// Their light is separate from their glow, so the opening remains a real space.
function flameGeometry(){
 const positions=[],indices=[],rings=28,sides=16;
 for(let ring=0;ring<=rings;ring++){
  const t=ring/rings;
  const radius=.002+(.46+.32*Math.sin(t*Math.PI))*Math.pow(1-t,.72)*(1+.16*Math.sin(t*14));
  for(let side=0;side<sides;side++){
   const a=side/sides*Math.PI*2;
   positions.push(Math.cos(a)*radius,t,Math.sin(a)*radius);
  }
 }
 for(let ring=0;ring<rings;ring++)for(let side=0;side<sides;side++){
  const a=ring*sides+side,b=ring*sides+(side+1)%sides,c=a+sides,d=b+sides;
  indices.push(a,c,b,b,c,d);
 }
 const base=positions.length/3,tip=base+1;positions.push(0,0,0,0,1,0);
 for(let side=0;side<sides;side++){
  const next=(side+1)%sides;
  indices.push(base,side,next,tip,rings*sides+next,rings*sides+side);
 }
 const geometry=new THREE.BufferGeometry();
 geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));
 geometry.setIndex(indices);geometry.computeVertexNormals();
 return geometry;
}

const vertexShader=`
 uniform float uTime;
 uniform float uSeed;
 varying float vHeight;
 varying vec3 vLocal;
 varying vec3 vViewNormal;
 varying vec3 vViewPosition;
 void main(){
  vec3 p=position;
  vHeight=p.y;
  float bend=p.y*p.y;
  float flow=uTime*(2.1+.14*sin(uSeed))+uSeed;
  p.x+=bend*(.34*sin(p.y*9.0-flow)+.18*sin(flow*1.73+p.y*5.1));
  p.z+=bend*(.26*cos(p.y*8.0-flow*1.1)+.14*sin(flow*.79+p.y*6.3));
  p.xz*=.81+.14*sin(flow*1.37-p.y*11.0)+.06*sin(flow*2.31+p.y*7.0);
  p.y*=.88+.13*sin(flow*.71)+.08*sin(flow*1.29+2.0);
  vLocal=p;
  vec4 viewPosition=modelViewMatrix*vec4(p,1.0);
  vViewNormal=normalize(normalMatrix*normal);vViewPosition=-viewPosition.xyz;
  gl_Position=projectionMatrix*viewPosition;
 }`;

const fragmentShader=`
 uniform float uTime;
 uniform float uSeed;
 uniform float uCore;
 varying float vHeight;
 varying vec3 vLocal;
 varying vec3 vViewNormal;
 varying vec3 vViewPosition;
 float hash(vec3 p){p=fract(p*.3183099+vec3(.17,.31,.47));p*=17.0;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}
 float noise(vec3 p){vec3 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
  return mix(mix(mix(hash(i),hash(i+vec3(1,0,0)),f.x),mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),
   mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}
 void main(){
  float h=vHeight;
  vec3 q=vec3(vLocal.x*4.5,h*5.0-uTime*(1.7+.08*uSeed),vLocal.z*4.5+uSeed);
  float n=.68*noise(q)+.32*noise(q*2.1+3.7);
  vec3 amber=vec3(1.0,.115,.004);
  vec3 gold=vec3(1.0,.39,.026);
  vec3 core=vec3(1.0,.66,.15);
  vec3 flame=mix(gold,amber,smoothstep(.15,.95,h));
  flame=mix(flame,core,(.28+uCore*.6)*(1.0-smoothstep(.06,.60,h)));
  float ribbon=smoothstep(.18+h*.20,.52,n);
  float facing=abs(dot(normalize(vViewNormal),normalize(vViewPosition)));
  float opacity=(.68+.16*uCore)*mix(.32,1.0,ribbon)*(1.0-smoothstep(.62,1.0,h))*smoothstep(.0,.48,facing);
  gl_FragColor=vec4(flame*(1.10+uCore*.28),opacity);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`;

const tongues=[
 {position:[-.09,0,-.38],scale:[.18,.44,.18],seed:.4},
 {position:[.025,0,-.25],scale:[.19,.72,.19],seed:2.1},
 {position:[-.075,0,-.07],scale:[.20,.54,.20],seed:4.2},
 {position:[.02,0,.08],scale:[.18,.80,.18],seed:5.6},
 {position:[-.055,0,.25],scale:[.19,.52,.17],seed:7.8},
 {position:[-.01,0,.38],scale:[.16,.41,.15],seed:9.2},
 {position:[.09,.025,-.26],scale:[.11,.35,.12],seed:1.5,core:1},
 {position:[.09,.025,-.09],scale:[.12,.49,.13],seed:3.3,core:1},
 {position:[.09,.025,.12],scale:[.11,.41,.12],seed:6.2,core:1},
 {position:[.09,.025,.29],scale:[.10,.30,.10],seed:8.4,core:1},
];

export function HearthFire({reduced}){
 const geometry=useMemo(flameGeometry,[]),light=useRef();
 const materials=useMemo(()=>tongues.map(({seed,core=0})=>new THREE.ShaderMaterial({
  uniforms:{uTime:{value:0},uSeed:{value:seed},uCore:{value:core}},
  vertexShader,fragmentShader,transparent:true,depthWrite:false,
  blending:THREE.NormalBlending,side:THREE.FrontSide,
 })),[]);
 useEffect(()=>()=>{geometry.dispose();materials.forEach(m=>m.dispose())},[geometry,materials]);
 useFrame(({clock})=>{
  const t=reduced?0:clock.elapsedTime;
  materials.forEach(material=>{material.uniforms.uTime.value=t});
  if(light.current)light.current.intensity=12*(reduced?1:1+.025*Math.sin(t*2.1)+.015*Math.sin(t*3.7+.4));
 });
 return <group>
  <group position={[HEARTH[0],0,HEARTH[1]]}><HearthBed/></group>
  <group position={[HEARTH[0],.43,HEARTH[1]]}>
   {tongues.map(({position,scale},i)=><mesh key={i} geometry={geometry} material={materials[i]} position={position} scale={scale}/>) }
   <HearthSparks reduced={reduced}/>
  </group>
  <pointLight ref={light} position={[-3.86+SHIFT,.84,HEARTH[1]]} color="#ffad55" intensity={12} distance={10} decay={2} castShadow shadow-intensity={.62} shadow-mapSize={[1024,1024]} shadow-radius={3} shadow-bias={-.0008} shadow-normalBias={.025} shadow-camera-near={.08} shadow-camera-far={12}/>
  <pointLight position={[HEARTH[0]-.10,.70,HEARTH[1]]} color="#ffad56" intensity={1.1} distance={1.8} decay={2}/>
  <rectAreaLight position={[HEARTH[0]+.60,.72,HEARTH[1]]} rotation={[0,-Math.PI/2,0]} width={1.15} height={.70} color="#ffab53" intensity={5}/>
 </group>;
}

function HearthSparks({reduced}){
 const points=useRef();
 const geometry=useMemo(()=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.Float32BufferAttribute(new Float32Array(12*3),3));g.setAttribute('aHeat',new THREE.Float32BufferAttribute(new Float32Array(12),1));return g},[]);
 const material=useMemo(()=>new THREE.ShaderMaterial({transparent:true,depthWrite:false,
  vertexShader:`attribute float aHeat;varying float heat;void main(){heat=aHeat;vec4 p=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*p;gl_PointSize=clamp(15.0/-p.z,1.0,4.0)*heat;}`,
  fragmentShader:`varying float heat;void main(){float r=length(gl_PointCoord-.5);float a=(1.-smoothstep(.08,.5,r))*heat;gl_FragColor=vec4(1.,.35,.035,a*.8);#include <tonemapping_fragment>\n#include <colorspace_fragment>}`.replace(';#include',';\n#include'),
 }),[]);
 useEffect(()=>()=>{geometry.dispose();material.dispose()},[geometry,material]);
 useFrame(({clock})=>{
  const p=geometry.attributes.position,h=geometry.attributes.aHeat;
  for(let i=0;i<12;i++){
   const t=(clock.elapsedTime*(.14+(i%3)*.025)+i*.173)%1;
   p.setXYZ(i,.03+Math.sin(t*4+i*2)*.065,t*.70,Math.sin(i*2.31)*.29+Math.sin(t*6+i)*.025);
   h.setX(i,reduced?0:Math.sin(Math.PI*t)**2*(i%3===0?1:.48));
  }
  p.needsUpdate=h.needsUpdate=true;
 });
 return <points ref={points} geometry={geometry} material={material} raycast={()=>null} frustumCulled={false}/>;
}
