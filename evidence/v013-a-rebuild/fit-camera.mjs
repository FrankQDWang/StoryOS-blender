import * as THREE from '../../apps/web/node_modules/three/build/three.module.js';
import fs from 'node:fs';
const w=1849,h=851;
const pairs=[
 [[0,1.30,-4.12],[922,414],2],
 [[0,3.55,-4.10],[921,193],2],
 [[-1.22,2.48,-4.25],[797,295],1],
 [[1.22,2.48,-4.25],[1045,295],1],
 [[0,1.08,.6],[913,482],2],
 [[0,.08,.6],[913,657],1],
];
function camera(p){const [y,z,pitch,fov,x]=p;const c=new THREE.PerspectiveCamera(fov,w/h,.06,60);c.position.set(x,y,z);c.lookAt(x,y-Math.tan(pitch)*10,z-10);c.updateMatrixWorld();return c;}
function loss(p){if(p[0]<1.3||p[0]>3.5||p[1]<4||p[1]>9||p[2]<-.05||p[2]>.5||p[3]<25||p[3]>65)return 1e9;const c=camera(p);let s=0;for(const [v,q,weight] of pairs){const v2=new THREE.Vector3(...v).project(c);s+=weight*((w*(v2.x+1)/2-q[0])**2+(h*(1-v2.y)/2-q[1])**2)}return s;}
let p=[2.2,6.65,.13,53,0], steps=[.2,.5,.03,3,.1];
for(let iter=0;iter<5000;iter++){let changed=false;for(let j=0;j<5;j++){let best=loss(p),next=p;for(const sign of[-1,1]){let q=[...p];q[j]+=steps[j]*sign;let v=loss(q);if(v<best){best=v;next=q;changed=true}}p=next;}if(!changed){steps=steps.map(s=>s*.65);if(steps[1]<.0001)break;}}
const c=camera(p);const points=pairs.map(([world,target])=>{let v=new THREE.Vector3(...world).project(c);return{world,target,projection:[w*(v.x+1)/2,h*(1-v.y)/2]}});
const report={position:c.position.toArray(),lookAt:[p[4],p[0]-Math.tan(p[2])*10,p[1]-10],fov:p[3],cost:loss(p),points};
fs.writeFileSync('evidence/v013-a-rebuild/camera-fit.json',JSON.stringify(report,null,2));console.log(report);
