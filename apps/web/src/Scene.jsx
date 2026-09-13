import React,{Suspense,useEffect,useMemo,useRef,useState} from 'react';
import {Canvas,useFrame,useThree} from '@react-three/fiber';
import {useGLTF,Html,Sparkles} from '@react-three/drei';
import {EffectComposer,Bloom,Vignette} from '@react-three/postprocessing';
import * as THREE from 'three';

export const SLOTS=[[-2.85,1.25,-1.55],[-2.02,1.25,-3.52],[2.02,1.25,-3.52],[3.02,1.25,-1.22],[3.02,1.25,1.34]];
const YAWS=[0,-.15,.15,.22,.32];
const HOME=new THREE.Vector3(0,1.85,5.9),HOME_LOOK=new THREE.Vector3(0,1.52,-1.6);
const TINTS={Timber:'#705237',FloorWood:'#917250',WarmPlaster:'#a0947f',Stone:'#59606a'};
function prepare(scene,room=false){
 const s=scene.clone(true);s.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;o.material=o.material.clone();
 if(room && TINTS[o.material.name])o.material.color.set(TINTS[o.material.name]);
 if(o.material.map)o.material.map.anisotropy=8;
 }});return s;
}
function Room({onReady}){
 const {scene}=useGLTF('/assets/models/library-room.glb');const object=useMemo(()=>prepare(scene,true),[scene]);
 useEffect(()=>{onReady()},[onReady]);return <primitive object={object}/>;
}
function ProjectBook({book,index,onSelect,selected,opening,reduced,appearing}){
 const {scene}=useGLTF('/assets/models/story-book.glb');
 const object=useMemo(()=>{const s=prepare(scene);s.traverse(o=>{if(o.isMesh && o.material.name==='BookLeather')o.material.color.set(book.color)});return s},[scene,book.color]);
 const cover=useMemo(()=>object.getObjectByName('CoverPivot'),[object]);
 const pages=useMemo(()=>[0,1,2].map(i=>object.getObjectByName(`PagePivot${i}`)),[object]);
 const group=useRef();const [hover,setHover]=useState(false);const age=useRef(0);
 useFrame((state,dt)=>{
  age.current+=dt;
  if(cover)cover.rotation.z=THREE.MathUtils.damp(cover.rotation.z,opening?2.65:0,opening?3.5:6,dt);
  pages.forEach((p,i)=>{if(p)p.rotation.z=THREE.MathUtils.damp(p.rotation.z,opening?Math.max(0,2.4-i*.13):0,2-i*.15,dt)});
  if(group.current){group.current.position.y=SLOTS[index][1]+(appearing&&!reduced?Math.max(0,1.1-age.current*.6):0);group.current.scale.setScalar(appearing&&!reduced?Math.min(1,age.current*1.4):1)}
 });
 return <group ref={group} position={SLOTS[index]} rotation={[.28,YAWS[index],0]} onClick={e=>{e.stopPropagation();onSelect(book.id)}} onPointerOver={e=>{e.stopPropagation();setHover(true);document.body.style.cursor='pointer'}} onPointerOut={()=>{setHover(false);document.body.style.cursor=''}}>
  <primitive object={object}/>
  {hover&&!selected&&!opening&&<Html position={[0,.35,0]} center distanceFactor={4} zIndexRange={[8,0]}><div className="book-label">{book.title}<small>点击查看作品</small></div></Html>}
  {(selected||hover)&&<pointLight position={[0,.5,0]} intensity={.8} color="#ffcd8b" distance={1.8}/>}
 </group>;
}
function MagicTable({onCreate,crafting,reduced}){
 const ref=useRef();useFrame(({clock})=>{if(ref.current&&!reduced)ref.current.rotation.y=clock.elapsedTime*.2});
 return <group position={[0,1.1,.6]} onClick={e=>{e.stopPropagation();onCreate()}} onPointerOver={()=>document.body.style.cursor='pointer'} onPointerOut={()=>document.body.style.cursor=''}>
  <mesh rotation={[-Math.PI/2,0,0]}><circleGeometry args={[.76,48]}/><meshBasicMaterial transparent opacity={0} depthWrite={false}/></mesh>
  <group ref={ref} position={[0,.08,0]}>
   <mesh rotation={[-Math.PI/2,0,0]}><torusGeometry args={[.35,.006,6,80]}/><meshStandardMaterial color="#95c9af" emissive="#65b897" emissiveIntensity={crafting?5:1.3}/></mesh>
   <mesh rotation={[-Math.PI/2,0,.4]}><torusGeometry args={[.20,.005,6,64]}/><meshStandardMaterial color="#bdcfb8" emissive="#8dc6a9" emissiveIntensity={crafting?4:.6}/></mesh>
  </group>
  {!reduced&&<Sparkles count={crafting?100:18} scale={[1.15,crafting?2.8:.65,1.15]} size={crafting?4:2} speed={crafting?1.5:.18} color="#c6dfb2" opacity={.5}/>}
  <pointLight position={[0,.45,0]} color="#76b7a1" intensity={crafting?5:.45} distance={3}/>
 </group>;
}
function CreatingBook({book}) {
 const {scene}=useGLTF('/assets/models/story-book.glb');
 const object=useMemo(()=>{const s=prepare(scene);s.traverse(o=>{if(o.isMesh&&o.material.name==='BookLeather')o.material.color.set(book.color)});return s},[scene,book.color]);
 const pieces=useMemo(()=>object.children.map((o,i)=>({o,base:o.position.clone(),offset:new THREE.Vector3(Math.sin(i*2.4)*.35,.35+(i%4)*.16,Math.cos(i*2.4)*.3)})),[object]);
 const ref=useRef(),elapsed=useRef(0);const start=useMemo(()=>new THREE.Vector3(0,1.75,.6),[]);
 useFrame((_,dt)=>{
  elapsed.current+=dt;const t=elapsed.current;
  const assemble=1-THREE.MathUtils.smoothstep(t,0,1.2);
  pieces.forEach(({o,base,offset})=>o.position.copy(base).addScaledVector(offset,assemble));
  if(ref.current){
   const fly=THREE.MathUtils.smoothstep(t,1.45,3.0),dest=book.slot!==null?new THREE.Vector3(...SLOTS[book.slot]):new THREE.Vector3(0,3,.6);
   ref.current.position.copy(start).lerp(dest,fly);ref.current.position.y+=Math.sin(fly*Math.PI)*.7;
   const scale=THREE.MathUtils.smoothstep(t,0,.4)*(book.slot===null?1-fly:1);ref.current.scale.setScalar(scale);
   ref.current.rotation.set(.28,book.slot!==null?YAWS[book.slot]*fly:fly,0);
  }
 });
 return <group ref={ref} position={start.toArray()}><primitive object={object}/><pointLight color="#bbdebc" intensity={1.5} distance={3}/></group>;
}
function OpeningHands({active,bookIndex}){
 const {scene}=useGLTF('/assets/models/opening-hands.glb');const object=useMemo(()=>prepare(scene),[scene]);const ref=useRef();const progress=useRef(0);
 useFrame((_,dt)=>{progress.current=THREE.MathUtils.damp(progress.current,active?1:0,4,dt);if(ref.current){ref.current.visible=progress.current>.015;ref.current.position.y=-.12+(1-progress.current)*-.3;ref.current.position.z=.48+(1-progress.current)*.6;ref.current.rotation.x=progress.current*-.18}});
 if(bookIndex==null)return null;
 return <group position={SLOTS[bookIndex]} rotation={[0,YAWS[bookIndex],0]}><group ref={ref}><primitive object={object}/></group></group>;
}
function CameraRig({mode,selected,books,onMode,onNear,opening,resetToken,reduced,onLockChange}){
 const {camera,gl}=useThree();const keys=useRef(new Set());const target=useRef(HOME_LOOK.clone());const wasLocked=useRef(false);const nearestRef=useRef(null);
 useEffect(()=>{const down=e=>{if(['INPUT','TEXTAREA'].includes(document.activeElement?.tagName))return;keys.current.add(e.code)};const up=e=>keys.current.delete(e.code);const clear=()=>keys.current.clear();window.addEventListener('keydown',down);window.addEventListener('keyup',up);window.addEventListener('blur',clear);return()=>{window.removeEventListener('keydown',down);window.removeEventListener('keyup',up);window.removeEventListener('blur',clear)}},[]);
 useEffect(()=>{
  const button=document.getElementById('roam-button');
  let dragDistance=0;
  const lock=()=>{
   const fallback=()=>{onLockChange(false);onMode('roam')};
   if(!document.body.requestPointerLock){fallback();return}
   document.body.requestPointerLock().catch(fallback);
  };
  const change=()=>{
   const locked=document.pointerLockElement===document.body;
   onLockChange(locked);
   if(locked)onMode('roam');
   else if(wasLocked.current){keys.current.clear();onMode(previous=>previous==='roam'?'overview':previous)}
   wasLocked.current=locked;
  };
  const down=()=>{dragDistance=0};
  const move=e=>{
   const locked=document.pointerLockElement===document.body;
   if(!locked&&(mode!=='roam'||e.buttons!==1||e.target!==gl.domElement))return;
   if(!locked)dragDistance+=Math.abs(e.movementX)+Math.abs(e.movementY);
   const angles=new THREE.Euler().setFromQuaternion(camera.quaternion,'YXZ');
   angles.y-=e.movementX*.002;
   angles.x=THREE.MathUtils.clamp(angles.x-e.movementY*.002,-1.12,1.12);
   camera.quaternion.setFromEuler(angles);
  };
  const click=e=>{if(dragDistance>5){e.stopPropagation();dragDistance=0}};
  button?.addEventListener('click',lock);
  gl.domElement.addEventListener('pointerdown',down);
  gl.domElement.addEventListener('click',click,true);
  document.addEventListener('pointerlockchange',change);
  document.addEventListener('mousemove',move);
  return()=>{
   button?.removeEventListener('click',lock);
   gl.domElement.removeEventListener('pointerdown',down);
   gl.domElement.removeEventListener('click',click,true);
   document.removeEventListener('pointerlockchange',change);
   document.removeEventListener('mousemove',move);
  };
 },[gl,camera,onMode,mode,onLockChange]);
 useEffect(()=>{if(mode!=='roam'&&document.pointerLockElement===document.body)document.exitPointerLock()},[mode,gl]);
 useEffect(()=>{if(mode!=='roam'){camera.position.copy(HOME);target.current.copy(HOME_LOOK)}},[resetToken]);
 useFrame((_,delta)=>{
  const dt=Math.min(delta,.05);
  if(mode==='roam'){
   const f=new THREE.Vector3();camera.getWorldDirection(f);f.y=0;f.normalize();const right=new THREE.Vector3().crossVectors(f,camera.up).normalize();const move=new THREE.Vector3();
   if(keys.current.has('KeyW')||keys.current.has('ArrowUp'))move.add(f);if(keys.current.has('KeyS')||keys.current.has('ArrowDown'))move.sub(f);
   if(keys.current.has('KeyD')||keys.current.has('ArrowRight'))move.add(right);if(keys.current.has('KeyA')||keys.current.has('ArrowLeft'))move.sub(right);
   move.normalize().multiplyScalar(dt*2.0);const next=camera.position.clone().add(move);next.x=THREE.MathUtils.clamp(next.x,-4.0,4.0);next.z=THREE.MathUtils.clamp(next.z,-2.75,6.4);next.y=1.7;
   // Keep the eye out of the central table, lecterns and the fireplace.
   const obstacles=[[0,.6,1.15],[-4.1,-.9,.75],...SLOTS.map(p=>[p[0],p[2],.7])];
   if(!obstacles.some(([x,z,r])=>Math.hypot(next.x-x,next.z-z)<r))camera.position.copy(next);
   let closest=null,d=1.9;for(const b of books){if(b.slot===null)continue;const p=new THREE.Vector3(...SLOTS[b.slot]);const dist=p.distanceTo(camera.position);if(dist<d){d=dist;closest=b.id}}
   if(closest!==nearestRef.current){nearestRef.current=closest;onNear(closest)}
  }else{
   const b=books.find(b=>b.id===selected);let pos=HOME.clone(),look=HOME_LOOK.clone();
   if((mode==='focus'||opening)&&b?.slot!=null){const p=new THREE.Vector3(...SLOTS[b.slot]);pos=p.clone().add(new THREE.Vector3(.05,opening?.96:1.12,opening?1.05:1.9));look=p.clone().add(new THREE.Vector3(0,.12,0));}
   if(reduced){camera.position.copy(pos);target.current.copy(look)}else{camera.position.lerp(pos,1-Math.exp(-dt*(opening?2.8:2.2)));target.current.lerp(look,1-Math.exp(-dt*2.5))}camera.lookAt(target.current);
  }
 });
 return null;
}
function Performance({onMetrics}){const {gl}=useThree();const bucket=useRef({t:0,n:0});useFrame((_,dt)=>{if(dt>.2||document.hidden){bucket.current={t:0,n:0};return}bucket.current.t+=dt;bucket.current.n++;if(bucket.current.t>2){onMetrics({fps:Math.round(bucket.current.n/bucket.current.t),calls:gl.info.render.calls,triangles:gl.info.render.triangles});bucket.current={t:0,n:0}}});return null;}
export function LibraryScene({books,selected,mode,setMode,onSelect,onCreate,onReady,onNear,onMetrics,opening,crafting,appearing,reduced,resetToken,paused,onLockChange}){
 const [visible,setVisible]=useState(!document.hidden);
 useEffect(()=>{const changed=()=>setVisible(!document.hidden);document.addEventListener('visibilitychange',changed);return()=>document.removeEventListener('visibilitychange',changed)},[]);
 const selectedBook=books.find(b=>b.id===selected);
 return <Canvas frameloop={visible&&!paused?'always':'demand'} shadows="percentage" dpr={[1,1.5]} camera={{position:HOME.toArray(),fov:53,near:.06,far:60}} gl={{antialias:true,powerPreference:'high-performance'}} onCreated={({gl})=>{gl.toneMapping=THREE.ACESFilmicToneMapping;gl.toneMappingExposure=1.08;gl.shadowMap.type=THREE.PCFShadowMap}}>
  <color attach="background" args={['#141b22']}/><fog attach="fog" args={['#202329',11,28]}/>
  <ambientLight intensity={.12} color="#899bb8"/>
  <hemisphereLight args={['#758aa7','#3d2416',.38]}/>
  <directionalLight position={[-1,5,-6]} color="#749ecd" intensity={1.1}/>
  <pointLight position={[0,3.15,-3.8]} color="#729acd" intensity={14} distance={12} decay={2}/>
  <pointLight position={[-.94,1.5,-3.45]} color="#ffc57e" intensity={12} distance={6} castShadow shadow-mapSize={[1024,1024]} shadow-bias={-.001} shadow-normalBias={.035}/>
  <pointLight position={[-3.82,.70,-.9]} color="#ffa255" intensity={9} distance={8} castShadow shadow-mapSize={[512,512]} shadow-bias={-.001}/>
  <pointLight position={[-4.05,2.55,2.1]} color="#ffd295" intensity={7} distance={9} castShadow shadow-mapSize={[512,512]} shadow-bias={-.001}/>
  <pointLight position={[4.05,2.55,2.1]} color="#ffc68c" intensity={6} distance={9}/>
  <pointLight position={[4.05,2.55,-2.95]} color="#ffd09e" intensity={5} distance={8}/>
  <Suspense fallback={null}>
   <Room onReady={onReady}/>
   {books.filter(b=>b.slot!==null&&b.id!==crafting?.id).map(b=><ProjectBook key={b.id} book={b} index={b.slot} onSelect={onSelect} selected={selected===b.id} opening={opening&&selected===b.id} reduced={reduced} appearing={appearing===b.id}/>)}
   <MagicTable onCreate={onCreate} crafting={crafting} reduced={reduced}/>
   {crafting&&<CreatingBook key={crafting.id} book={crafting}/>}
   <OpeningHands active={opening&&!reduced} bookIndex={selectedBook?.slot}/>
  </Suspense>
  {!reduced&&<Sparkles count={35} scale={[8,3.2,8]} position={[0,1.7,0]} size={1.4} speed={.07} color="#d6cdb0" opacity={.20}/>}
  <CameraRig mode={mode} selected={selected} books={books} onMode={setMode} onNear={onNear} opening={opening} resetToken={resetToken} reduced={reduced} onLockChange={onLockChange}/>
  <Performance onMetrics={onMetrics}/>
  <EffectComposer multisampling={0}><Bloom luminanceThreshold={1.25} intensity={.32} mipmapBlur/><Vignette eskil={false} offset={.23} darkness={.44}/></EffectComposer>
 </Canvas>;
}
useGLTF.preload('/assets/models/library-room.glb');useGLTF.preload('/assets/models/story-book.glb');useGLTF.preload('/assets/models/opening-hands.glb');
