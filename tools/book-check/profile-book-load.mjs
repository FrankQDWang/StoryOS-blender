import {chromium} from 'playwright';
import fs from 'node:fs/promises';
const out='evidence/book-local-correction-20261004/performance';
const run=process.argv[2]??'before';
const fixture=JSON.parse(await fs.readFile(`${out}/benchmark-raw.json`)).fixture;
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
const page=await browser.newPage({viewport:{width:1512,height:751},deviceScaleFactor:1});
await page.addInitScript(fixture=>{
 try{localStorage.setItem('storyos.library.demo.v1',JSON.stringify(fixture))}catch{}
 window.__load={uploads:[],firstPaint:null};const p=WebGL2RenderingContext.prototype;
 for(const name of ['texImage2D','texSubImage2D','texStorage2D']){const original=p[name];p[name]=function(...args){const start=performance.now(),result=original.apply(this,args);window.__load.uploads.push({name,at:start,ms:performance.now()-start});return result}}
 const shaders=new WeakMap(),programs=new WeakMap(),active=new WeakMap();const shaderSource=p.shaderSource,attach=p.attachShader,use=p.useProgram;
 p.shaderSource=function(shader,source){shaders.set(shader,source.includes('RE_Direct_Physical'));return shaderSource.call(this,shader,source)};
 p.attachShader=function(program,shader){programs.set(program,programs.get(program)||shaders.get(shader));return attach.call(this,program,shader)};
 p.useProgram=function(program){active.set(this,program);return use.call(this,program)};
 const draw=p.drawElements;p.drawElements=function(...args){const result=draw.apply(this,args);if(document.querySelector('.room-caption')&&programs.get(active.get(this))&&this.canvas===document.querySelector('.scene canvas')&&window.__load.firstPaint===null){requestAnimationFrame(()=>{if(window.__load.firstPaint===null){this.finish();window.__load.firstPaint=performance.now()}})}return result};
},fixture);
const cdp=await page.context().newCDPSession(page);await cdp.send('Profiler.enable');
await page.goto('http://127.0.0.1:4182');await page.waitForFunction(()=>window.__load?.firstPaint);await page.waitForTimeout(200);
await cdp.send('Profiler.start');await page.reload();await page.waitForFunction(()=>window.__load?.firstPaint);
const {profile}=await cdp.send('Profiler.stop');const data=await page.evaluate(()=>window.__load);
const hits=new Map();for(const id of profile.samples??[])hits.set(id,(hits.get(id)??0)+1);
const hot=profile.nodes.map(n=>({name:n.callFrame.functionName,file:n.callFrame.url,line:n.callFrame.lineNumber,hits:hits.get(n.id)??0})).sort((a,b)=>b.hits-a.hits).slice(0,35);
await fs.writeFile(`${out}/profile-${run}.json`,JSON.stringify({data,hot,profile},null,2)+'\n');console.log(JSON.stringify({firstPaint:data.firstPaint,uploads:data.uploads.length,uploadMs:data.uploads.reduce((s,x)=>s+x.ms,0),hot:hot.slice(0,15)},null,2));
}finally{await browser.close()}
