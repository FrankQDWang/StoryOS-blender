// Separate Vite-only inspection entry. Not included in the production HTML build.
import React,{useState,useEffect} from 'react';
import {createRoot} from 'react-dom/client';
import {LibraryScene} from './Scene';
import layout from './room-layout.json';
import {OPENING_SECONDS} from './opening-motion.mjs';
import './styles.css';

const params=new URLSearchParams(location.search);
const noop=()=>{};
const books=layout.slots.map((_,slot)=>({id:`review-${slot}`,slot,title:`检查书位 ${slot+1}`,color:['#32695b','#674051','#304767','#6d4b2b','#536650'][slot]}));
function Review(){
 const [slot,setSlot]=useState(Number(params.get('slot')??0));
 const [time,setTime]=useState(Number(params.get('time')??.8));
 const [playing,setPlaying]=useState(false),[speed,setSpeed]=useState(1);
 useEffect(()=>{
  if(!playing)return;
  let id,last;
  const tick=now=>{const delta=last==null?0:(now-last)/1000*speed;last=now;setTime(t=>Math.min(OPENING_SECONDS,t+delta));id=requestAnimationFrame(tick)};
  id=requestAnimationFrame(tick);return()=>cancelAnimationFrame(id);
 },[playing,speed]);
 useEffect(()=>{if(time>=OPENING_SECONDS)setPlaying(false)},[time]);
 const [metrics,setMetrics]=useState(null);
 const [samples,setSamples]=useState([]);
 const record=m=>{setMetrics(m);if(params.has('bench'))setSamples(rows=>rows.length<5?[...rows,m]:rows)};
 const view=params.get('view')??'opening';
 const handView=view==='opening'||view==='hands-side';
 const stand=layout.slots[slot],sideOffset=[1.25,1.05,1.1],c=Math.cos(stand.yaw),s=Math.sin(stand.yaw);
 const camera=view==='fire'?{position:[-1.6,1.15,1.10],target:[-4,.80,-1.15],fov:48}
  :view==='fire-side'?{position:[-2.5,1.4,-3.0],target:[-4,.90,-1.15],fov:48}
  :view==='hands-side'?{position:[stand.position[0]+sideOffset[0]*c+sideOffset[2]*s,stand.position[1]+sideOffset[1],stand.position[2]-sideOffset[0]*s+sideOffset[2]*c],target:[stand.position[0],stand.position[1]+.45,stand.position[2]],fov:48}:undefined;
 return <main className="app"><div className="scene"><LibraryScene books={books} selected={handView?books[slot].id:null}
  mode={handView?'focus':'overview'} setMode={noop} onSelect={noop} onCreate={noop} onReady={noop}
  onNear={noop} onMetrics={record} opening={handView} crafting={null} appearing={null} reduced={false}
  resetToken={0} paused={!playing&&!params.has('bench')&&!view.startsWith('fire')} onLockChange={noop} inspection={{time,camera}}/></div>
  <div style={{position:'fixed',top:12,left:12,display:'flex',gap:12,padding:12,background:'#151d20dd',color:'#fff',font:'13px sans-serif',zIndex:30}}>
   <label>书位 <select aria-label="书位" value={slot} onChange={e=>setSlot(Number(e.target.value))}>{books.map(b=><option key={b.slot} value={b.slot}>{b.slot+1}</option>)}</select></label>
   <label>时间 <input aria-label="时间" type="number" min="0" max={OPENING_SECONDS} step=".1" value={Math.round(time*100)/100} onChange={e=>{setPlaying(false);setTime(Number(e.target.value))}}/></label>
   <button onClick={()=>{setTime(0);setPlaying(true)}}>重播</button>
   <button onClick={()=>setPlaying(v=>!v)}>{playing?'暂停':'播放'}</button>
   <label>速度 <select aria-label="速度" value={speed} onChange={e=>setSpeed(Number(e.target.value))}><option value="1">正常</option><option value="0.25">四分之一</option></select></label>
   <output>{!playing&&!params.has('bench')&&!view.startsWith('fire')?'静帧检查':metrics?`${metrics.fps} FPS · p50 ${metrics.frameMs.toFixed(1)} ms · p95 ${metrics.p95Ms.toFixed(1)} ms · ${metrics.calls} calls · ${metrics.triangles} triangles`:''}</output>
  </div>{params.has('bench')&&<div style={{position:'fixed',right:12,bottom:12,padding:12,background:'#151d20ee',color:'#fff',font:'13px monospace'}}>
   <strong>{samples.length===5?'采样完成':'采样中'}</strong>
   <pre aria-label="性能样本">{JSON.stringify(samples,null,2)}</pre>
  </div>}</main>;
}
if(import.meta.env.DEV){
 const root=import.meta.hot?.data.root??createRoot(document.getElementById('root'));
 if(import.meta.hot)import.meta.hot.data.root=root;
 root.render(<Review/>);
}
