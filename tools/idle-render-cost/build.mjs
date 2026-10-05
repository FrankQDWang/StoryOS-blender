import {build} from '../../apps/web/node_modules/vite/dist/node/index.js';
import react from '../../apps/web/node_modules/@vitejs/plugin-react/dist/index.js';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const root=process.cwd();
const label=process.argv[2]??'baseline';
await build({root,configFile:false,resolve:{alias:{react:path.join(root,'apps/web/node_modules/react')}},publicDir:path.join(root,'public'),plugins:[react(),{
 name:'measurement-only-probe',enforce:'pre',transformIndexHtml:{order:'pre',handler:html=>html.replace('/src/main.jsx','/apps/web/src/main.jsx')},transform(code,id){
  if(process.env.SOURCE_REF&&id.startsWith(path.join(root,'apps/web/src/')))code=execFileSync('git',['show',process.env.SOURCE_REF+':'+path.relative(root,id)],{encoding:'utf8'});

  if(id.endsWith('/src/Scene.jsx'))return "import {Probe} from '../../../tools/idle-render-cost/Probe.jsx';\n"+code.replace("frameloop={visible&&!paused?'always':'demand'}","frameloop={window.__deterministic?'never':visible&&!paused?'always':'demand'}").replace('<Performance onMetrics={onMetrics}/>','<Performance onMetrics={onMetrics}/><Probe/>');
  return code;
 }
}],build:{outDir:path.join(root,'.cache/idle-render-cost',label),emptyOutDir:true,rollupOptions:{input:{app:path.join(root,'apps/web/index.html'),deterministic:path.join(root,'tools/idle-render-cost/deterministic.html')}}}});
