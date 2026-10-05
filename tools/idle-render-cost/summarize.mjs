import fs from 'node:fs/promises';
const folder=process.argv[2],data=JSON.parse(await fs.readFile(`${folder}/raw.json`));
const median=a=>a.length?[...a].sort((a,b)=>a-b)[Math.floor(a.length/2)]:null;
const mean=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:null;
const percentile=(a,p)=>a.length?[...a].sort((a,b)=>a-b)[Math.min(a.length-1,Math.floor(a.length*p))]:null;
const rows=data.rows.map(r=>{
 const frames=new Map();for(const x of r.gpu){if(!frames.has(x.frame))frames.set(x.frame,{shadow:0,main:0,post:0});frames.get(x.frame)[x.kind]+=x.ms;}
 const gpu=[...frames.values()].slice(2,-2);
 return {name:r.name,instrument:r.instrument,cpu:r.cpu,mainCPU:r.main,fps:1000/mean(r.raf.slice(1)),frameP50:median(r.raf.slice(1)),frameP95:percentile(r.raf.slice(1),.95),calls:median(r.frames.slice(2).map(f=>f.calls)),gpuFrame:median(gpu.map(f=>f.shadow+f.main+f.post)),gpuShadow:median(gpu.map(f=>f.shadow)),gpuMain:median(gpu.map(f=>f.main)),gpuPost:median(gpu.map(f=>f.post)),cpuShadow:mean(r.passes.filter(p=>p.kind==='main').map(p=>p.shadowMs)),cpuMain:mean(r.passes.filter(p=>p.kind==='main').map(p=>p.cpuMs)),cpuPost:gpu.length?r.passes.filter(p=>p.kind==='post').reduce((s,p)=>s+p.cpuMs,0)/frames.size:null,gpuTimer:r.gpuTimer,disjoint:r.disjoint};
});
await fs.writeFile(`${folder}/summary.json`,JSON.stringify({rows,errors:data.errors},null,2));console.table(rows);
