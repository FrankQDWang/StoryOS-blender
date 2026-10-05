import sharp from '../book-check/node_modules/sharp/dist/index.mjs';
import fs from 'node:fs/promises';
const [a,b,out]=process.argv.slice(2),rows=[];
for(const name of (await fs.readdir(a)).filter(n=>n.endsWith('.png')&&!n.includes('sheet')&&!n.includes('-diff'))){
 const x=await sharp(`${a}/${name}`).removeAlpha().raw().toBuffer({resolveWithObject:true});
 const y=await sharp(`${b}/${name}`).removeAlpha().raw().toBuffer({resolveWithObject:true});
 if(x.data.length!==y.data.length)throw new Error('size mismatch');
 let max=0,sum=0,changed=0,over2=0;const diff=Buffer.alloc(x.data.length);
 for(let i=0;i<x.data.length;i++){const d=Math.abs(x.data[i]-y.data[i]);diff[i]=Math.min(255,d*16);max=Math.max(max,d);sum+=d;if(d)changed++;if(d>2)over2++;}
 // Predeclared strict threshold: no channel differs by >2/255, mean <=0.01/255.
 const row={name,max,mean:sum/x.data.length,changedFraction:changed/x.data.length,over2,pass:max<=2&&sum/x.data.length<=.01};rows.push(row);
 if(!row.pass)await sharp(diff,{raw:x.info}).png().toFile(`${b}/${name.replace('.png','-diff.png')}`);
}
await fs.writeFile(out,JSON.stringify({threshold:{max:2,mean:.01},pass:rows.every(r=>r.pass),rows},null,2));console.log(rows);
