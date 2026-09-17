// The cover and the baked MakeHuman hand clips use this shared 3.5-second sequence.
import sequence from './opening-sequence.json' with {type:'json'};
export const OPENING_SECONDS = sequence.duration;
export function smoothRange(time, from, to) {
 const x=Math.max(0,Math.min(1,(time-from)/(to-from)));
 return x*x*(3-2*x);
}
export function openingPose(time) {
 const reach=smoothRange(time,...sequence.reach),release=smoothRange(time,...sequence.release);
 const angle=sequence.coverLift[2]*smoothRange(time,...sequence.coverLift)+sequence.coverSettle[2]*smoothRange(time,...sequence.coverSettle);
 return {reach,angle,grip:smoothRange(time,...sequence.grip)*(1-release),release,visible:time>0&&time<OPENING_SECONDS};
}
export function pagePose(time,index) {
 const order=2-index;
 const progress=smoothRange(time,sequence.pageStart+order*sequence.pageStagger,sequence.pageStart+order*sequence.pageStagger+sequence.pageDuration);
 return {angle:progress*(2.60+index*.025),curl:Math.sin(progress*Math.PI)*.20,lift:Math.sin(progress*Math.PI)*.014};
}
