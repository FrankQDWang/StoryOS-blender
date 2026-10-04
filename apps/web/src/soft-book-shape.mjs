import {openingPose,pagePose,smoothRange} from './opening-motion.mjs';

export const BOOK={coverRoot:-.345,coverWidth:.735,coverDepth:1,coverHeight:.115,leather:.007,
 pageRoot:-.345,pageWidth:.70,pageDepth:.925,blockTop:.095,blockThickness:.078};

// Arc-length parameterisation keeps the skin supple without stretching it.
function arc(u,width,angle,bend,out){
 const a=angle-bend,b=angle+bend*(2*u-1);
 if(Math.abs(bend)<.00001){out[0]=width*u*Math.cos(angle);out[1]=width*u*Math.sin(angle)}
 else{out[0]=width*(Math.sin(b)-Math.sin(a))/(2*bend);out[1]=width*(Math.cos(a)-Math.cos(b))/(2*bend)}
 out[3]=b;return out;
}
export function coverPoint(u,v,time,offset=0,out=[0,0,0,0]){
 const a=openingPose(time).angle,settled=smoothRange(time,1.85,2.75);
 // Project gravity onto the lifted cover: sag downward between binding and
 // fingers, with little transverse load when vertical. Keep the existing
 // stiffness coefficient and return to the original release/resting shape.
 const held=1-smoothRange(time,1.90,2.10);
 const load=-.58*Math.sin(a)+held*.58*Math.sin(a)*(1+Math.cos(a));
 const bend=.05*Math.exp(-a*3)+load*(1-settled)+.42*settled;
 arc(u,BOOK.coverWidth,a,bend,out);
 const ripple=.006*Math.sin(Math.PI*u)*Math.sin(v*Math.PI*2)*Math.sin(a);
 out[0]+=BOOK.coverRoot-Math.sin(out[3])*offset;
 out[1]+=BOOK.coverHeight-.032*smoothRange(time,1.9,2.65)+ripple+Math.cos(out[3])*offset;
 out[2]=(v-.5)*BOOK.coverDepth;
 return out;
}
export function backPoint(u,v,_time,offset=0,out=[0,0,0,0]){
 out[0]=-.38+.77*u;out[1]=.012+.003*Math.sin(u*Math.PI)*Math.cos((v-.5)*Math.PI)+offset;
 out[2]=(v-.5)*BOOK.coverDepth;out[3]=0;return out;
}
export function blockPoint(u,v,time,offset=0,out=[0,0,0,0]){
 const open=smoothRange(time,.82,2.5),gutter=.006*open*Math.exp(-u*12);
 out[0]=BOOK.pageRoot+BOOK.pageWidth*u;
 out[1]=BOOK.blockTop+gutter+.0015*Math.sin(u*Math.PI)*Math.cos(v*Math.PI*2)+offset;
 out[2]=(v-.5)*BOOK.pageDepth;out[3]=0;return out;
}
const leafPaths=new Map();
function leafPath(time,index){
 const cached=leafPaths.get(index);if(cached?.time===time)return cached;
 const pose=pagePose(time,index),steps=64,points=new Float64Array((steps+1)*3);
 const layer=.0012*(index+1),rootX=BOOK.pageRoot-layer*Math.sin(pose.angle);
 const rootY=BOOK.blockTop+.006*smoothRange(time,.82,2.5)+layer*Math.cos(pose.angle);
 const inset=-(BOOK.leather/2+.003+.0012*(3-index));
 const root=coverPoint(0,.5,time,inset);
 const resting=smoothRange(pose.progress,.60,1),rising=smoothRange(pose.progress,0,.2);
 const target=(u)=>{
  const p=coverPoint(u*BOOK.pageWidth/BOOK.coverWidth,.5,time,inset),bound=Math.pow(1-u,7);
  p[0]+=(rootX-root[0])*bound;p[1]+=(rootY-root[1])*bound;return p;
 };
 function tangent(u){
  const rest=-.006*smoothRange(time,.82,2.5)*12*Math.exp(-u*12)/BOOK.pageWidth;
  let a=Math.atan(rest)*(1-rising)+(pose.angle+pose.curl*.72*(2*u-1))*rising;
  if(resting){
   const before=target(Math.max(0,u-.001)),after=target(Math.min(1,u+.001));
   let targetAngle=Math.atan2(after[1]-before[1],after[0]-before[0]);if(targetAngle<0)targetAngle+=Math.PI*2;
   a+=(targetAngle-a)*resting;
  }
  return a;
 }
 points[0]=rootX;points[1]=rootY;points[2]=tangent(0);
 // Blend tangent angles, then integrate equal arc lengths. A settling page must
 // not shrink and grow as it changes from a turning curve to its resting shape.
 for(let i=1;i<=steps;i++){
  const a=tangent((i-.5)/steps),at=i*3,previous=at-3;
  points[at]=points[previous]+BOOK.pageWidth/steps*Math.cos(a);
  points[at+1]=points[previous+1]+BOOK.pageWidth/steps*Math.sin(a);points[at+2]=tangent(i/steps);
 }
 const path={time,points,steps,progress:pose.progress};leafPaths.set(index,path);return path;
}
export function leafPoint(u,v,time,index,offset=0,out=[0,0,0,0]){
 const path=leafPath(time,index),t=u*path.steps,i=Math.min(path.steps-1,Math.floor(t)),f=t-i;
 const a=i*3,b=a+3,points=path.points;
 out[3]=points[a+2]+(points[b+2]-points[a+2])*f;
 out[0]=points[a]+(points[b]-points[a])*f-Math.sin(out[3])*offset;
 out[1]=points[a+1]+(points[b+1]-points[a+1])*f+Math.cos(out[3])*offset
  +.0045*Math.sin(u*Math.PI)*Math.sin(v*Math.PI*2+index*.7)*Math.sin(path.progress*Math.PI);
 out[2]=(v-.5)*BOOK.pageDepth;return out;
}
export function gutterPoint(u,v,time,offset=0,out=[0,0,0,0]){
 const cover=coverPoint(0,(v-.5)*BOOK.pageDepth/BOOK.coverDepth+.5,time,-BOOK.leather/2);
 const top=blockPoint(0,v,time),q=1-u;
 const cx=cover[0]-.018*Math.cos(cover[3]),cy=cover[1]-.018*Math.sin(cover[3]);
 out[0]=q*q*q*cover[0]+3*q*q*u*cx+3*q*u*u*(top[0]-.012)+u*u*u*top[0];
 out[1]=q*q*q*cover[1]+3*q*q*u*cy+3*q*u*u*(top[1]-.003)+u*u*u*top[1]+offset;
 out[2]=(v-.5)*BOOK.pageDepth;out[3]=0;return out;
}
export function spinePoint(u,v,time,offset=0,out=[0,0,0,0]){
 const a=u*Math.PI,opening=smoothRange(time,.82,2.55);
 out[0]=-.38+.035*u-(.026+.006*opening)*Math.sin(a)-offset*Math.sin(a);
 out[1]=.012+(BOOK.coverHeight-.032*smoothRange(time,1.9,2.65)-.012)*(1-Math.cos(a))/2+offset*Math.cos(a);
 out[2]=(v-.5)*BOOK.coverDepth;out[3]=a;return out;
}
export function softHandOffset(side,time,out=[0,0,0]){
 const reach=smoothRange(time,.1,.72);
 if(side==='Left'){
  out[0]=0;out[1]=-.068*reach*(1-smoothRange(time,2,3.15));out[2]=0;return out;
 }
 const t=Math.min(time,1.83),a=openingPose(t).angle,lift=smoothRange(t,.9,1.7);
 const x=.265+.365,y=.15348+.00129*lift-.17;
 const oldX=-.365+x*Math.cos(a)-y*Math.sin(a),oldY=.17+x*Math.sin(a)+y*Math.cos(a);
 const point=coverPoint((.265-BOOK.coverRoot)/BOOK.coverWidth,.96497,t,-BOOK.leather/2);
 const weight=reach*(1-smoothRange(time,2.12,3.3));
 out[0]=(point[0]-oldX)*weight;out[1]=(point[1]-oldY)*weight;out[2]=0;return out;
}
