// Only injected by build.mjs. Never imported by the application's normal build.
import {useEffect} from '../../apps/web/node_modules/react';
import {useFrame,useThree} from '../../apps/web/node_modules/@react-three/fiber';
export function Probe(){
 const state=useThree();
 useEffect(()=>{
  const {gl,scene,camera,advance,setFrameloop,clock}=state,ctx=gl.getContext();
  const ext=ctx.getExtension('EXT_disjoint_timer_query_webgl2');
  const debug=ctx.getExtension('WEBGL_debug_renderer_info');
  const probe=window.__renderProbe={state,frames:[],passes:[],gpu:[],enabled:false,firstFrame:null,ext:!!ext,renderer:debug?ctx.getParameter(debug.UNMASKED_RENDERER_WEBGL):null};
  probe.step=(count=180)=>{setFrameloop('never');clock.elapsedTime=0;for(let i=1;i<=count;i++)advance(i/60,true);};
  probe.advanceFrames=(count)=>{for(let i=0;i<count;i++)advance(clock.elapsedTime+1/60,true)};
  probe.inventory=()=>{const lights=[],casters=[];scene.traverse(o=>{if(o.isLight)lights.push({type:o.type,position:o.position.toArray(),castShadow:o.castShadow,distance:o.distance,intensity:o.intensity});if(o.castShadow&&o.isMesh)casters.push({name:o.name,type:o.type,visible:o.visible,material:o.material?.name})});return {lights,casters}};
  const original=gl.render,shadow=gl.shadowMap.render,pending=[];
  let query=null,part=null,passStart=0,shadowMs=0,inMain=false;
  const begin=kind=>{part=kind;if(ext){query=ctx.createQuery();ctx.beginQuery(ext.TIME_ELAPSED_EXT,query)}};
  const end=()=>{if(query){ctx.endQuery(ext.TIME_ELAPSED_EXT);pending.push({query,part,frame:probe.frames.length});query=null}};
  gl.shadowMap.render=function(...args){if(!probe.enabled)return shadow.apply(this,args);const t=performance.now();const own=!query;if(own)begin('shadow');const result=shadow.apply(this,args);if(own)end();shadowMs+=performance.now()-t;if(inMain)begin('main');return result};
  gl.render=function(s,c,...args){if(!probe.enabled)return original.call(this,s,c,...args);inMain=s===scene;shadowMs=0;passStart=performance.now();if(!inMain)begin('post');const result=original.call(this,s,c,...args);end();probe.passes.push({kind:inMain?'main':'post',frame:probe.frames.length,cpuMs:performance.now()-passStart-shadowMs,shadowMs});inMain=false;return result};
  probe.poll=()=>{if(!pending.length)return;if(ext&&ctx.getParameter(ext.GPU_DISJOINT_EXT)){pending.forEach(p=>ctx.deleteQuery(p.query));pending.length=0;probe.disjoint=true;return}while(pending.length&&ctx.getQueryParameter(pending[0].query,ctx.QUERY_RESULT_AVAILABLE)){const p=pending.shift();probe.gpu.push({kind:p.part,frame:p.frame,ms:ctx.getQueryParameter(p.query,ctx.QUERY_RESULT)/1e6});ctx.deleteQuery(p.query)}};
  return()=>{gl.render=original;gl.shadowMap.render=shadow;pending.forEach(p=>ctx.deleteQuery(p.query))};
 },[state.gl,state.scene,state.camera]);
 useFrame((_,dt)=>{const p=window.__renderProbe;if(p){p.poll();if(p.enabled)p.frames.push({dt:dt*1000,calls:state.gl.info.render.calls,triangles:state.gl.info.render.triangles});}},-4);
 useFrame(()=>{const p=window.__renderProbe;if(p&&!p.firstFrame&&state.scene.children.some(o=>o.type==='Group'))p.firstFrame=performance.now();},2);
 return null;
}
