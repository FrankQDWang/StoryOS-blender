import React,{useMemo,useRef} from 'react';
import {useFrame} from '@react-three/fiber';
import * as THREE from 'three';
import layout from './room-layout.json';
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
  p.x+=bend*(.72*sin(p.y*8.0+uSeed-uTime*1.4)+.28*sin(uTime*2.1+uSeed+p.y*4.1));
  p.z+=bend*(.52*cos(p.y*7.0+uSeed-uTime*1.2)+.22*sin(uTime*1.6+uSeed+p.y*5.3));
  p.xz*=1.0+.10*sin(uTime*2.4+uSeed+p.y*9.0);
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
 void main(){
  float h=vHeight;
  vec3 amber=vec3(1.0,.21,.018);
  vec3 gold=vec3(1.0,.57,.095);
  vec3 cream=vec3(1.0,.86,.43);
  vec3 flame=mix(gold,amber,smoothstep(.22,.95,h));
  flame=mix(flame,cream,uCore*(1.0-.35*h));
  float ribbon=.92+.08*sin(h*12.0-vLocal.x*3.0-uTime*2.0+uSeed);
  float facing=abs(dot(normalize(vViewNormal),normalize(vViewPosition)));
  float opacity=(.56+.26*uCore)*ribbon*(1.0-smoothstep(.68,1.0,h))*smoothstep(.0,.60,facing);
  gl_FragColor=vec4(flame*(1.5+uCore*.7),opacity);
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
 useFrame(({clock})=>{
  const t=reduced?0:clock.elapsedTime;
  materials.forEach(material=>{material.uniforms.uTime.value=t});
  if(light.current)light.current.intensity=12*(reduced?1:1+.025*Math.sin(t*2.1)+.015*Math.sin(t*3.7+.4));
 });
 return <group>
  <group position={[HEARTH[0],.43,HEARTH[1]]}>
   {tongues.map(({position,scale},i)=><mesh key={i} geometry={geometry} material={materials[i]} position={position} scale={scale}/>) }
  </group>
  <pointLight ref={light} position={[-3.86+SHIFT,.84,HEARTH[1]]} color="#ffad55" intensity={12} distance={10} decay={2} castShadow shadow-intensity={.62} shadow-mapSize={[1024,1024]} shadow-radius={3} shadow-bias={-.0008} shadow-normalBias={.025} shadow-camera-near={.08} shadow-camera-far={12}/>
  <pointLight position={[HEARTH[0]-.18,.97,HEARTH[1]]} color="#ffad56" intensity={3.6} distance={1.8} decay={2}/>
  <rectAreaLight position={[HEARTH[0]+.60,.72,HEARTH[1]]} rotation={[0,-Math.PI/2,0]} width={1.15} height={.70} color="#ffab53" intensity={5}/>
 </group>;
}
