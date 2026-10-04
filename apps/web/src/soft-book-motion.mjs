import {BOOK,MOTION,supportForSlot} from './book-support.mjs';
import {smoothRange} from './opening-motion.mjs';
const supports=[0,1,2].map(supportForSlot),paths=new Map();
let positions;
export function setBookMotion(buffer){if(positions?.buffer!==buffer){positions=new Int16Array(buffer);paths.clear()}}
const N=MOTION.cols+1,stride=MOTION.layers*N*2;
function pathAt(layer,time,config){
 const key=config*MOTION.layers+layer;
 let path=paths.get(key);
 if(path?.time===time)return path;
 if(!path){path={time,points:new Float64Array(N*4),directions:new Float64Array(N*4)};paths.set(key,path)}
 const t=Math.max(0,Math.min(MOTION.frames-1.000001,time*MOTION.fps)),frame=Math.floor(t),f=t-frame;
 const base=(config*MOTION.profiles*MOTION.frames+frame)*stride+layer*N*2,profileStride=MOTION.frames*stride;
 for(let profile=0;profile<2;profile++)for(let vertex=0;vertex<N;vertex++)for(let axis=0;axis<2;axis++){
  const i=base+profile*profileStride+vertex*2+axis;
  path.points[profile*N*2+vertex*2+axis]=((1-f)*positions[i]+f*positions[i+stride])/16000;
 }
 for(let profile=0;profile<2;profile++)for(let vertex=0;vertex<N;vertex++)for(let axis=0;axis<2;axis++){
  const base=profile*N*2;
  path.directions[base+vertex*2+axis]=path.points[base+Math.min(N-1,vertex+2)*2+axis]-path.points[base+Math.max(0,vertex-1)*2+axis];
 }
 path.time=time;return path;
}
export function sheetPoint(layer,u,v,time,offset,out,slot=0){
 const width=layer?BOOK.pageWidth:BOOK.coverWidth,depth=layer?BOOK.pageDepth:BOOK.coverDepth;
 out[2]=(v-.5)*depth;
 if(time===0){out[0]=BOOK.coverRoot+u*width;out[1]=BOOK.coverHeight-layer*.0016+offset;out[3]=0;return out;}
 const x=Math.max(0,Math.min(MOTION.cols-.000001,u*MOTION.cols)),i=Math.floor(x)*2,a=x-Math.floor(x);
 const config=Math.min(slot,2),support=supports[config],{points:p,directions:d}=pathAt(layer,time,config),j=i+N*2;
 const distance=Math.abs(out[2]-(support.z+.39)),w=1-smoothRange(distance,.026/support.scale+.006,.026/support.scale+.051),q=1-w;
 const x0=q*p[i]+w*p[j],y0=q*p[i+1]+w*p[j+1],x1=q*p[i+2]+w*p[j+2],y1=q*p[i+3]+w*p[j+3];
 const dx=q*d[i]+w*d[j],dy=q*d[i+1]+w*d[j+1],length=Math.hypot(dx,dy);
 out[0]=x0+(x1-x0)*a-dy/length*offset;out[1]=y0+(y1-y0)*a+dx/length*offset;out[3]=Math.atan2(dy,dx);return out;
}
