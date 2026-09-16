import * as T from '../../apps/web/node_modules/three/build/three.module.js';
import fs from 'node:fs';
const l=JSON.parse(fs.readFileSync('apps/web/src/room-layout.json'));const camera=new T.PerspectiveCamera(l.home.fov,1849/851,.06,60);camera.position.fromArray(l.home.position);camera.lookAt(...l.home.lookAt);camera.updateMatrixWorld();
const jobs=[
 {i:0,book:true,corners:[[96,386],[232,382],[143,456],[279,449]],base:[180,666]},
 {i:1,book:true,corners:[[491,383],[553,380],[523,424],[587,419]],base:[543,540]},
 {i:2,book:true,corners:[[1337,393],[1401,396],[1296,430],[1367,438]],base:[1352,566]},
 {i:3,book:false,corners:[[1492,412],[1594,418],[1435,467],[1552,479]],base:[1518,617]},
 {i:4,book:false,corners:[[1641,450],[1810,462],[1564,536],[1744,560]],base:[1670,742]},
];
function projected(p,job){const [x,z,yaw,scale,pitch]=p;const q=new T.Euler(pitch,yaw,0,'YXZ');const pts=job.book?[[-.39,.229,-.5],[.39,.229,-.5],[-.39,.229,.5],[.39,.229,.5]]:[[-.51,.0375,-.405],[.51,.0375,-.405],[-.51,.0375,.405],[.51,.0375,.405]];
 const project=v=>{v.project(camera);return [1849*(v.x+1)/2,851*(1-v.y)/2]};return [...pts.map(v=>project(new T.Vector3(...v).multiplyScalar(scale).applyEuler(q).add(new T.Vector3(x,job.book?1.25:1.18,z)))),project(new T.Vector3(x,.15,z))]}
function loss(p,j){if(p[3]<.6||p[3]>1.25||Math.abs(p[2])>1.3||p[4]<.28||p[4]>.95)return 1e9;const points=projected(p,j),targets=[...j.corners,j.base];return points.reduce((s,v,i)=>s+(i===4?1:1)*((v[0]-targets[i][0])**2+(v[1]-targets[i][1])**2),0)}
const fits=[];
for(const job of jobs){const slot=l.slots[job.i];let p=[slot.position[0],slot.position[2],slot.yaw,slot.scale,l.lectern.pitch],steps=[.1,.2,.1,.03,.04];for(let iter=0;iter<2000;iter++){let changed=false;for(let k=0;k<5;k++){let best=loss(p,job),np=p;for(const sign of[-1,1]){let v=[...p];v[k]+=steps[k]*sign;const val=loss(v,job);if(val<best){best=val;np=v;changed=true}}p=np;}if(!changed){steps=steps.map(s=>s*.6);if(steps[0]<.00001)break}}
 fits.push({slot:job.i,x:p[0],z:p[1],yaw:p[2],scale:p[3],pitch:p[4],cost:loss(p,job),projected:projected(p,job),target:[...job.corners,job.base]});}
fs.writeFileSync('evidence/v013-a-rebuild/lectern-fit.json',JSON.stringify(fits,null,2));console.log(fits.map(({projected,target,...v})=>v));
