import React,{useMemo,useRef} from 'react';
import {useFrame} from '@react-three/fiber';
import * as THREE from 'three';

// Closed, curved volumes keep the fire legible while walking around the hearth.
// Their light is separate from their glow, so the opening remains a real space.
function flameGeometry(){
 const positions=[],indices=[],rings=18,sides=12;
 for(let ring=0;ring<=rings;ring++){
  const t=ring/rings;
  const radius=.002+.74*Math.pow(1-t,.85)*(1+.12*Math.sin(t*9));
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
 void main(){
  vec3 p=position;
  vHeight=p.y;
  float bend=p.y*p.y;
  p.x+=bend*(.36*sin(p.y*5.0+uSeed)+.20*sin(uTime*1.8+uSeed+p.y*3.1));
  p.z+=bend*(.16*cos(p.y*4.0+uSeed)+.10*sin(uTime*1.3+uSeed+p.y*4.3));
  p.xz*=1.0+.035*sin(uTime*2.1+uSeed+p.y*7.0);
  vLocal=p;
  gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);
 }`;

const fragmentShader=`
 uniform float uTime;
 uniform float uSeed;
 uniform float uCore;
 varying float vHeight;
 varying vec3 vLocal;
 void main(){
  float h=vHeight;
  vec3 amber=vec3(1.0,.21,.018);
  vec3 gold=vec3(1.0,.57,.095);
  vec3 cream=vec3(1.0,.86,.43);
  vec3 flame=mix(gold,amber,smoothstep(.22,.95,h));
  flame=mix(flame,cream,uCore*(1.0-.35*h));
  float ribbon=.92+.08*sin(h*12.0-vLocal.x*3.0-uTime*2.0+uSeed);
  float opacity=(.64+.20*uCore)*ribbon*(1.0-smoothstep(.76,1.0,h));
  gl_FragColor=vec4(flame*(1.4+uCore*.8),opacity);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
 }`;

const tongues=[
 {position:[-.09,0,-.29],scale:[.08,.62,.10],seed:.4},
 {position:[.025,0,-.15],scale:[.09,.82,.10],seed:2.1},
 {position:[-.075,0,.015],scale:[.105,.70,.11],seed:4.2},
 {position:[.02,0,.16],scale:[.085,.90,.10],seed:5.6},
 {position:[-.055,0,.29],scale:[.075,.53,.08],seed:7.8},
 {position:[.09,.025,-.17],scale:[.05,.4,.055],seed:1.5,core:1},
 {position:[.09,.025,.01],scale:[.06,.46,.063],seed:3.3,core:1},
 {position:[.09,.025,.20],scale:[.05,.42,.06],seed:6.2,core:1},
];

export function HearthFire({reduced}){
 const geometry=useMemo(flameGeometry,[]),light=useRef();
 const materials=useMemo(()=>tongues.map(({seed,core=0})=>new THREE.ShaderMaterial({
  uniforms:{uTime:{value:0},uSeed:{value:seed},uCore:{value:core}},
  vertexShader,fragmentShader,transparent:true,depthWrite:false,
  blending:THREE.AdditiveBlending,side:THREE.FrontSide,
 })),[]);
 useFrame(({clock})=>{
  const t=reduced?0:clock.elapsedTime;
  materials.forEach(material=>{material.uniforms.uTime.value=t});
  if(light.current)light.current.intensity=19*(reduced?1:1+.025*Math.sin(t*2.1)+.015*Math.sin(t*3.7+.4));
 });
 return <group>
  <group position={[-4.14,.43,-.9]}>
   {tongues.map(({position,scale},i)=><mesh key={i} geometry={geometry} material={materials[i]} position={position} scale={scale}/>) }
  </group>
  <pointLight ref={light} position={[-3.86,.83,-.9]} color="#ffab62" intensity={19} distance={10} decay={2} castShadow shadow-mapSize={[1024,1024]} shadow-bias={-.0008} shadow-normalBias={.025} shadow-camera-near={.08} shadow-camera-far={12}/>
  <pointLight position={[-3.28,.36,-.82]} color="#e68a40" intensity={1.45} distance={4.5} decay={2}/>
 </group>;
}
