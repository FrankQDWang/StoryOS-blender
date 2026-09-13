// Development-only review surface. Uses the exact production assembly and room.
import React,{useState} from 'react';
import {LibraryScene} from './Scene';
import {initialLibrary} from './library-model.mjs';
const noop=()=>{};
export default function AnimationReview(){
 const [time,setTime]=useState(1.42),[side,setSide]=useState(false),[slot,setSlot]=useState(0);
 const book={...initialLibrary().books[0],slot};
 return <main className="app"><div className="scene"><LibraryScene books={[book]} selected={book.id} mode="focus" opening reduced={false} onReady={noop} setMode={noop} onSelect={noop} onCreate={noop} onNear={noop} onMetrics={noop} onLockChange={noop} inspection={{time,side}}/></div>
  <div style={{position:'absolute',top:20,left:20,zIndex:30,padding:14,background:'#13201de8',display:'flex',gap:12,alignItems:'center'}}>
   <strong>开书接触检查</strong>{[.8,1.42,1.9,2.3,2.7,3.5].map(t=><button key={t} aria-pressed={time===t} onClick={()=>setTime(t)}>{t}s</button>)}
   <button onClick={()=>setSide(s=>!s)}>{side?'正面镜头':'侧面镜头'}</button>
   <button onClick={()=>setSlot(s=>(s+1)%5)}>位置 {slot+1}</button>
   <a href="/">退出检查</a>
  </div>
 </main>;
}
