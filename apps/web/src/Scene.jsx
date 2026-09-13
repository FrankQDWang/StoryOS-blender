import React,{Suspense,useEffect,useMemo,useRef,useState} from 'react';
import {Canvas,useFrame,useThree} from '@react-three/fiber';
import {useGLTF,Html,Sparkles} from '@react-three/drei';
import {EffectComposer,Bloom,Vignette} from '@react-three/postprocessing';
import * as THREE from 'three';
import layout from './room-layout.json';
import {OpeningBook,CreatingBook,cloneAsset,slotRotation} from './BookInteraction';

export const SLOTS=layout.slots.map(s=>s.position);
const HOME=new THREE.Vector3(...layout.home),HOME_LOOK=new THREE.Vector3(...layout.homeLook);
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
function ProjectBook({book,index,onSelect,selected}){
 const {scene}=useGLTF('/assets/models/story-book.glb');
 const object=useMemo(()=>cloneAsset(scene,book.color),[scene,book.color]);
 const rotation=useMemo(()=>slotRotation(index),[index]);const [hover,setHover]=useState(false);
 return <group position={SLOTS[index]} onClick={e=>{e.stopPropagation();onSelect(book.id)}} onPointerOver={e=>{e.stopPropagation();setHover(true);document.body.style.cursor='pointer'}} onPointerOut={()=>{setHover(false);document.body.style.cursor=''}}>
  <group quaternion={rotation} scale={layout.bookScale}><primitive object={object}/></group>
  {hover&&!selected&&<Html position={[0,.52,.32]} center distanceFactor={3} zIndexRange={[8,0]}><div className="book-label">{book.title}<small>点击查看作品</small></div></Html>}
  {(selected||hover)&&<pointLight position={[.08,.18,.5]} intensity={.55} color="#ffcd8b" distance={1.5}/>}
 </group>;
}
function MagicTable({onCreate,crafting,reduced,showHint}){
 const ref=useRef();useFrame(({clock})=>{if(ref.current&&!reduced)ref.current.rotation.y=clock.elapsedTime*.2});
 return <group position={layout.magic} onClick={e=>{e.stopPropagation();onCreate()}} onPointerOver={()=>document.body.style.cursor='pointer'} onPointerOut={()=>document.body.style.cursor=''}>
  <mesh rotation={[-Math.PI/2,0,0]}><circleGeometry args={[.45,48]}/><meshBasicMaterial transparent opacity={0} depthWrite={false}/></mesh>
  <group ref={ref} position={[0,.018,0]}>
   <mesh rotation={[-Math.PI/2,0,0]}><torusGeometry args={[.27,.004,6,80]}/><meshStandardMaterial color="#95c9af" emissive="#65b897" emissiveIntensity={crafting?5:1.3}/></mesh>
   <mesh rotation={[-Math.PI/2,0,.4]}><torusGeometry args={[.15,.003,6,64]}/><meshStandardMaterial color="#bdcfb8" emissive="#8dc6a9" emissiveIntensity={crafting?4:.6}/></mesh>
  </group>
  {!reduced&&<Sparkles count={crafting?70:12} scale={[.72,crafting?1.8:.45,.72]} size={crafting?4:2} speed={crafting?1.5:.18} color="#c6dfb2" opacity={.5}/>}
  {showHint&&<Html position={[0,.32,0]} center zIndexRange={[8,0]}><button className="desk-hint" onClick={onCreate}>＋ 写下一个新世界</button></Html>}
  <pointLight position={[0,.45,0]} color="#76b7a1" intensity={crafting?5:.45} distance={3}/>
 </group>;
}
function CameraRig({mode,selected,books,onMode,onNear,opening,resetToken,reduced,onLockChange,crafting,inspection}){
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
   move.normalize().multiplyScalar(dt*1.55);const next=camera.position.clone().add(move);next.x=THREE.MathUtils.clamp(next.x,...layout.bounds.x);next.z=THREE.MathUtils.clamp(next.z,...layout.bounds.z);next.y=1.62;
   const blocked=(x,z)=>layout.obstacles.some(o=>x>o.x[0]-.12&&x<o.x[1]+.12&&z>o.z[0]-.12&&z<o.z[1]+.12);
   // Slide along furniture instead of sticking on a diagonal approach.
   if(!blocked(next.x,camera.position.z))camera.position.x=next.x;
   if(!blocked(camera.position.x,next.z))camera.position.z=next.z;
   camera.position.y=next.y;
   let closest=null,d=1.9;for(const b of books){if(b.slot===null)continue;const p=new THREE.Vector3(...SLOTS[b.slot]);const dist=p.distanceTo(camera.position);if(dist<d){d=dist;closest=b.id}}
   if(closest!==nearestRef.current){nearestRef.current=closest;onNear(closest)}
  }else{
   const b=books.find(b=>b.id===selected);let pos=HOME.clone(),look=HOME_LOOK.clone();
   if(mode==='focus'&&b?.slot!=null){const p=new THREE.Vector3(...SLOTS[b.slot]);pos=p.clone().add(new THREE.Vector3(-.28,.34,1.45));look=p.clone().add(new THREE.Vector3(.12,.02,.1));}
   if(opening){pos=new THREE.Vector3(...layout.openingCamera);look=new THREE.Vector3(...layout.openingLook)}
   else if(crafting){pos=new THREE.Vector3(2.9,2.25,.12);look=new THREE.Vector3(.7,1.3,-2.3)}
   if(inspection?.side){pos=new THREE.Vector3(2.62,1.51,-1.33);look=new THREE.Vector3(.97,1.20,-1.96)}
   if(reduced||inspection){camera.position.copy(pos);target.current.copy(look)}else{camera.position.lerp(pos,1-Math.exp(-dt*(opening?5:2.2)));target.current.lerp(look,1-Math.exp(-dt*2.5))}camera.lookAt(target.current);
  }
 });
 return null;
}
function Performance({onMetrics}){const {gl}=useThree();const bucket=useRef({t:0,n:0});useFrame((_,dt)=>{if(dt>.2||document.hidden){bucket.current={t:0,n:0};return}bucket.current.t+=dt;bucket.current.n++;if(bucket.current.t>2){onMetrics({fps:Math.round(bucket.current.n/bucket.current.t),calls:gl.info.render.calls,triangles:gl.info.render.triangles});bucket.current={t:0,n:0}}});return null;}
export function LibraryScene({books,selected,mode,setMode,onSelect,onCreate,onReady,onNear,onMetrics,opening,crafting,appearing,reduced,resetToken,paused,onLockChange,inspection}){
 const [visible,setVisible]=useState(!document.hidden);
 useEffect(()=>{const changed=()=>setVisible(!document.hidden);document.addEventListener('visibilitychange',changed);return()=>document.removeEventListener('visibilitychange',changed)},[]);
 const selectedBook=books.find(b=>b.id===selected);
 return <Canvas frameloop={visible&&!paused?'always':'demand'} shadows="percentage" dpr={[1,1.5]} camera={{position:HOME.toArray(),fov:55,near:.05,far:30}} gl={{antialias:true,powerPreference:'high-performance'}} onCreated={({gl})=>{gl.toneMapping=THREE.ACESFilmicToneMapping;gl.toneMappingExposure=1.08;gl.shadowMap.type=THREE.PCFShadowMap}}>
  <color attach="background" args={['#141b22']}/><fog attach="fog" args={['#202329',11,28]}/>
  <ambientLight intensity={.12} color="#899bb8"/>
  <hemisphereLight args={['#758aa7','#3d2416',.38]}/>
  <directionalLight position={[1,5,-6]} color="#749ecd" intensity={.75}/>
  <pointLight position={[1.37,2.85,-3.05]} color="#729acd" intensity={9} distance={10} decay={2}/>
  <pointLight position={[2.07,1.42,-2.31]} color="#ffc57e" intensity={5} distance={6} castShadow shadow-mapSize={[1024,1024]} shadow-bias={-.001} shadow-normalBias={.025}/>
  <pointLight position={[-2.90,.67,-.88]} color="#ffa255" intensity={6} distance={7} castShadow shadow-mapSize={[512,512]} shadow-bias={-.002} shadow-normalBias={.045}/>
  <pointLight position={[-3.13,1.12,2.35]} color="#ffd295" intensity={5} distance={7} castShadow shadow-mapSize={[512,512]} shadow-bias={-.002} shadow-normalBias={.045}/>
  <pointLight position={[2.7,2.8,1.8]} color="#e9bf94" intensity={3} distance={9}/>
  <Suspense fallback={null}>
   <Room onReady={onReady}/>
   {books.filter(b=>b.slot!==null&&b.id!==crafting?.id&&!(opening&&selected===b.id)).map(b=><ProjectBook key={b.id} book={b} index={b.slot} onSelect={onSelect} selected={selected===b.id} opening={opening&&selected===b.id} reduced={reduced} appearing={appearing===b.id}/>)}
   {!opening&&<MagicTable onCreate={onCreate} crafting={crafting} reduced={reduced} showHint={mode==='overview'&&!crafting}/>}
   {crafting&&<CreatingBook key={crafting.id} book={crafting}/>}
   {opening&&selectedBook&&<OpeningBook book={selectedBook} inspectTime={inspection?.time??null}/>}
  </Suspense>
  {!reduced&&<Sparkles count={35} scale={[6.5,2.6,6.5]} position={[0,1.7,0]} size={1.4} speed={.07} color="#d6cdb0" opacity={.20}/>}
  <CameraRig mode={mode} selected={selected} books={books} onMode={setMode} onNear={onNear} opening={opening} crafting={crafting} resetToken={resetToken} reduced={reduced} onLockChange={onLockChange} inspection={inspection}/>
  <Performance onMetrics={onMetrics}/>
  <EffectComposer multisampling={0}><Bloom luminanceThreshold={1.25} intensity={.32} mipmapBlur/><Vignette eskil={false} offset={.23} darkness={.44}/></EffectComposer>
 </Canvas>;
}
useGLTF.preload('/assets/models/library-room.glb');useGLTF.preload('/assets/models/story-book.glb');useGLTF.preload('/assets/models/opening-hands.glb');
