import {smoothRange} from './opening-motion.mjs';
import {BOOK,gripPose,handClipTime} from './book-support.mjs';
import {sheetPoint} from './soft-book-motion.mjs';
export {BOOK};
export function coverPoint(u,v,time,offset=0,out=[0,0,0,0],slot=0){return sheetPoint(0,u,v,time,offset,out,slot)}
export function leafPoint(u,v,time,index,offset=0,out=[0,0,0,0],slot=0){return sheetPoint(3-index,u,v,time,offset,out,slot)}
export function backPoint(u,v,_time,offset=0,out=[0,0,0,0]){
 out[0]=-.38+.77*u;out[1]=.012+.003*Math.sin(Math.PI*u)*Math.cos((v-.5)*Math.PI)+offset;out[2]=(v-.5)*BOOK.coverDepth;out[3]=0;return out;
}
export function blockPoint(u,v,_time,offset=0,out=[0,0,0,0]){
 out[0]=BOOK.pageRoot+BOOK.pageWidth*u;out[1]=BOOK.blockTop+.0015*Math.sin(Math.PI*u)*Math.cos(v*Math.PI*2)+offset;out[2]=(v-.5)*BOOK.pageDepth;out[3]=0;return out;
}
export function gutterPoint(u,v,time,offset=0,out=[0,0,0,0],slot=0){
 const cover=coverPoint(0,(v-.5)*BOOK.pageDepth/BOOK.coverDepth+.5,time,-BOOK.leather/2,undefined,slot),top=blockPoint(0,v,time),q=1-u;
 out[0]=q*q*q*cover[0]+3*q*q*u*(cover[0]-.01)+3*q*u*u*(top[0]-.01)+u*u*u*top[0];
 out[1]=q*cover[1]+u*top[1]+offset;out[2]=(v-.5)*BOOK.pageDepth;out[3]=0;return out;
}
export function spinePoint(u,v,_time,offset=0,out=[0,0,0,0]){
 const a=u*Math.PI;out[0]=-.38+.035*u-.026*Math.sin(a)-offset*Math.sin(a);
 out[1]=.012+(BOOK.coverHeight-.012)*(1-Math.cos(a))/2+offset*Math.cos(a);out[2]=(v-.5)*BOOK.coverDepth;out[3]=a;return out;
}
// Transform the preserved hand performance onto the input support trajectory.
// This trajectory is also the bake's constraint; hands never follow the solved cloth.
export function handSupportTransform(time){
 const clip=handClipTime(time),t=Math.min(clip,1.83),a=1.55*smoothRange(t,.82,1.83),lift=smoothRange(t,.9,1.7);
 const x=.630,y=.15348+.00129*lift-.17,old=[-.365+x*Math.cos(a)-y*Math.sin(a),.17+x*Math.sin(a)+y*Math.cos(a),.46497+.00030*lift];
 const target=gripPose(Math.min(time,1.90)),weight=smoothRange(time,.1,.72)*(1-smoothRange(time,2.2,3.3));
 return {angle:(target[3]-a)*weight,old,target,weight};
}
