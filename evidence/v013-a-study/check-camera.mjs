import fs from 'node:fs';
import layout from '../../apps/web/src/room-layout.json' with {type:'json'};
import {isWalkable,moveWithCollisions} from '../../apps/web/src/roaming.mjs';
const rotate=(x,z,a)=>({x:x*Math.cos(a)+z*Math.sin(a),z:-x*Math.sin(a)+z*Math.cos(a)});
const endpoints=layout.slots.map((s,index)=>{
 const pos=(x,z)=>{const d=rotate(x,z,s.yaw);return {x:s.position[0]+d.x,z:s.position[2]+d.z}};
 const approach=pos(0,1.1),nominal=pos(.05,1.9),opening=pos(.05,1.05);
 const focus=isWalkable(nominal)?nominal:moveWithCollisions(approach,{x:nominal.x-approach.x,z:nominal.z-approach.z});
 return {slot:index+1,approach,focus,opening,focusCorrection:Math.hypot(focus.x-nominal.x,focus.z-nominal.z),approachWalkable:isWalkable(approach),focusWalkable:isWalkable(focus),openingWalkable:isWalkable(opening)};
});
const passed=endpoints.every(x=>x.approachWalkable&&x.focusWalkable&&x.openingWalkable);
fs.writeFileSync(new URL('camera-clearance.json',import.meta.url),JSON.stringify({version:layout.version,passed,endpoints},null,2)+'\n');
console.log(JSON.stringify({passed,endpoints},null,2));if(!passed)process.exitCode=1;
