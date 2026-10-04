import layout from './room-layout.json' with {type:'json'};
import {smoothRange} from './opening-motion.mjs';

export const BOOK={coverRoot:-.345,coverWidth:.735,coverDepth:1,coverHeight:.103,leather:.004,
 pageRoot:-.345,pageWidth:.70,pageDepth:.925,blockTop:.095,blockThickness:.078};
export const MOTION={cols:32,fps:60,frames:211,layers:4,profiles:2,configurations:[0,1,2]};
export function supportForSlot(slot=0){
 const {scale,pitch}=layout.slots[slot];
 // Same plank dimensions and offset as build_library.py, in book coordinates.
 return {pitch,scale,edge:-.51,top:(-.07*Math.cos(pitch)+.048)/scale,lip:(-.07*Math.cos(pitch)+.084)/scale,z:.07*Math.sin(pitch)/scale,depth:.405};
}
export function gripPose(time,out=[0,0,0,0]){
 // The palm carries the lower fore-edge past the binding before opening its fingers.
 const a=2.28*smoothRange(time,.82,1.90),distance=.595-.035*Math.sin(a);
 out[0]=BOOK.coverRoot+distance*Math.cos(a);out[1]=BOOK.coverHeight+distance*Math.sin(a);
 out[2]=.465;out[3]=a;return out;
}
export function handClipTime(time){
 return time<=1.9?time*1.76/1.9:1.76+(time-1.9)*(3.5-1.76)/(3.5-1.9);
}
