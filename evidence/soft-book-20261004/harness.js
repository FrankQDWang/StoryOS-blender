(fixture=>{
 try{localStorage.setItem('storyos.library.demo.v1',JSON.stringify(fixture))}catch{}
 const sample=window.__bookBench={scenePaints:[],handDraw:null,clickStart:null,workspaceAt:null};
 const contexts=new Set(),shaders=new WeakMap(),programs=new WeakMap(),active=new WeakMap(),litDraws=new WeakMap();
 const proto=WebGL2RenderingContext.prototype;
 const shaderSource=proto.shaderSource,attachShader=proto.attachShader,useProgram=proto.useProgram;
 proto.shaderSource=function(shader,source){shaders.set(shader,{skin:source.includes('#define USE_SKINNING'),lit:source.includes('RE_Direct_Physical')});return shaderSource.call(this,shader,source)};
 proto.attachShader=function(program,shader){const old=programs.get(program)??{},next=shaders.get(shader)??{};programs.set(program,{skin:old.skin||next.skin,lit:old.lit||next.lit});return attachShader.call(this,program,shader)};
 proto.useProgram=function(program){contexts.add(this);active.set(this,program);return useProgram.call(this,program)};
 for(const method of ['drawElements','drawArrays']){
  const original=proto[method];proto[method]=function(...args){const result=original.apply(this,args);const p=programs.get(active.get(this));
   if(p?.lit)litDraws.set(this,(litDraws.get(this)??0)+1);
   if(sample.clickStart!==null&&sample.handDraw===null&&p?.skin&&p?.lit){this.finish();sample.handDraw=performance.now()}
   return result;
  };
 }
 let hasCaption=false;
 new MutationObserver(()=>{
  const caption=!!document.querySelector('.room-caption');
  if(caption&&!hasCaption){
   const painted=()=>{
    const canvas=document.querySelector('.scene canvas');
    const gl=[...contexts].find(gl=>gl.canvas===canvas&&litDraws.get(gl)>0);
    if(!gl){requestAnimationFrame(painted);return}
    requestAnimationFrame(()=>{gl.finish();sample.scenePaints.push(performance.now())});
   };
   requestAnimationFrame(painted);
  }
  hasCaption=caption;
  if(sample.clickStart!==null&&sample.workspaceAt===null&&document.querySelector('.workspace h1'))sample.workspaceAt=performance.now();
 }).observe(document,{childList:true,subtree:true});
 document.addEventListener('click',event=>{
  if(event.target.closest('button')?.textContent.includes('打开这本书')){sample.clickStart=performance.now();sample.handDraw=null;sample.workspaceAt=null}
 },true);
})({"version":1,"books":[{"id":"bench-0","slot":0,"materialId":"warm-umber","color":"#ac8058","title":"星海余烬","description":"群星熄灭之后，故事才刚刚开始。","words":0,"updatedAt":"2026-10-03T00:00:00Z"},{"id":"bench-1","slot":1,"materialId":"muted-pine","color":"#82927e","title":"守月人","description":"","words":0,"updatedAt":"2026-10-03T00:00:00Z"},{"id":"bench-2","slot":2,"materialId":"slate-blue","color":"#7e96b0","title":"寄往风中的信","description":"","words":0,"updatedAt":"2026-10-03T00:00:00Z"},{"id":"bench-3","slot":3,"materialId":"smoky-plum","color":"#a18490","title":"无题手稿·甲","description":"","words":0,"updatedAt":"2026-10-03T00:00:00Z"},{"id":"bench-4","slot":4,"materialId":"warm-ochre","color":"#c8a16a","title":"无题手稿·乙","description":"","words":0,"updatedAt":"2026-10-03T00:00:00Z"}],"lastBookId":"bench-0","reducedMotion":false,"sound":false});
setInterval(()=>{if(!document.body)return;let out=document.getElementById('book-bench-output');if(!out){out=document.createElement('output');out.id='book-bench-output';out.style.cssText='position:fixed;bottom:0;left:0;z-index:9999;font:9px monospace;background:#111;color:white;max-width:100vw;pointer-events:none';document.body.append(out)}const sample=window.__bookBench;out.dataset.ready=String(sample.scenePaints.length>0);out.dataset.opened=String(sample.workspaceAt!==null);out.textContent=JSON.stringify({...sample,hidden:document.hidden});},100);
